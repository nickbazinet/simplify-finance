import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, date
import database as db

def calculate_goal_progress(current, target):
    """Calculate percentage progress towards goal"""
    return (current / target * 100) if target > 0 else 0

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:,.2f}"

def show_goals_page():
    st.header("Financial Goals")
    user_id = st.session_state.user['id']

    # Add new goal section
    with st.form("add_goal"):
        st.subheader("Set New Financial Goal")
        col1, col2 = st.columns(2)
        
        with col1:
            goal_name = st.text_input("Goal Name")
            target_amount = st.number_input("Target Amount ($)", min_value=0.0, format="%.2f")
            current_amount = st.number_input("Current Amount ($)", min_value=0.0, format="%.2f")
        
        with col2:
            category = st.selectbox(
                "Category",
                ["Savings", "Investment", "Emergency Fund", "Retirement", "Major Purchase", "Other"]
            )
            deadline = st.date_input("Target Date", min_value=date.today())

        submitted = st.form_submit_button("Add Goal")
        if submitted and goal_name and target_amount > 0:
            db.add_goal(user_id, goal_name, target_amount, current_amount, deadline, category)
            st.success("Goal added successfully!")
            st.rerun()

    # Display existing goals
    goals_df = db.get_goals(user_id)
    
    if not goals_df.empty:
        st.subheader("Your Financial Goals")
        
        # Progress visualization
        for _, goal in goals_df.iterrows():
            progress = calculate_goal_progress(goal['current_amount'], goal['target_amount'])
            days_left = (pd.to_datetime(goal['deadline']) - pd.Timestamp.now()).days
            
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**{goal['name']}** ({goal['category']})")
                    
                    # Progress bar using plotly
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = progress,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        gauge = {
                            'axis': {'range': [0, 100]},
                            'bar': {'color': "rgb(50, 168, 82)"},
                            'steps': [
                                {'range': [0, 33], 'color': "rgb(255, 235, 235)"},
                                {'range': [33, 66], 'color': "rgb(235, 255, 235)"},
                                {'range': [66, 100], 'color': "rgb(220, 255, 220)"}
                            ]
                        }
                    ))
                    
                    fig.update_layout(
                        height=150,
                        margin=dict(l=20, r=20, t=20, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.metric(
                        "Current Amount",
                        format_currency(goal['current_amount']),
                        format_currency(goal['current_amount'] - goal['target_amount'])
                    )
                    st.write(f"Target: {format_currency(goal['target_amount'])}")
                    st.write(f"Days left: {max(0, days_left)}")
                    
                    # Update progress
                    new_amount = st.number_input(
                        "Update Progress",
                        value=float(goal['current_amount']),
                        key=f"update_{goal['id']}",
                        format="%.2f"
                    )
                    if new_amount != goal['current_amount']:
                        db.update_goal_progress(goal['id'], new_amount, user_id)
                        st.rerun()
                
                st.divider()

        # Overall goals summary
        st.subheader("Goals Summary")
        
        # Create pie chart of goals by category
        fig_pie = px.pie(
            goals_df,
            values='target_amount',
            names='category',
            title='Goals Distribution by Category'
        )
        st.plotly_chart(fig_pie)
        
        # Summary metrics
        total_target = goals_df['target_amount'].sum()
        total_current = goals_df['current_amount'].sum()
        overall_progress = calculate_goal_progress(total_current, total_target)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Goals Value", format_currency(total_target))
        with col2:
            st.metric("Current Progress", format_currency(total_current))
        with col3:
            st.metric("Overall Progress", f"{overall_progress:.1f}%")
    else:
        st.info("No financial goals set yet. Add your first goal above!")
