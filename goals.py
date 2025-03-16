import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, date
import database as db

def calculate_goal_progress(goal_id):
    """Calculate percentage progress towards goal"""
    current = db.calculate_goal_current_amount(goal_id)
    goal_df = db.get_goals(st.session_state.user['id'])
    target = goal_df[goal_df['id'] == goal_id]['target_amount'].iloc[0]
    return (current / target * 100) if target > 0 else 0

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:,.2f}"

def show_goals_page():
    st.header("Financial Goals")
    user_id = st.session_state.user['id']

    # Get user's buckets for selection
    buckets_df = db.get_buckets(user_id)

    # Add new goal section
    with st.form("add_goal"):
        st.subheader("Set New Financial Goal")
        col1, col2 = st.columns(2)

        with col1:
            goal_name = st.text_input("Goal Name")
            target_amount = st.number_input("Target Amount ($)", min_value=0.0, format="%.2f")
            selected_buckets = st.multiselect(
                "Select Buckets to Track",
                options=buckets_df['id'].tolist(),
                format_func=lambda x: buckets_df[buckets_df['id'] == x]['name'].iloc[0]
            )

        with col2:
            category = st.selectbox(
                "Category",
                ["Savings", "Investment", "Emergency Fund", "Retirement", "Major Purchase", "Other"]
            )
            deadline = st.date_input("Target Date", min_value=date.today())

        submitted = st.form_submit_button("Add Goal")
        if submitted and goal_name and target_amount > 0:
            # Add goal with initial current_amount as 0
            db.add_goal(user_id, goal_name, target_amount, 0, deadline, category)
            # Get the newly created goal's ID
            goals_df = db.get_goals(user_id)
            new_goal_id = goals_df[goals_df['name'] == goal_name]['id'].iloc[-1]
            # Link selected buckets
            db.link_goal_to_buckets(new_goal_id, selected_buckets)
            st.success("Goal added successfully!")
            st.rerun()

    # Display existing goals
    goals_df = db.get_goals(user_id)

    if not goals_df.empty:
        st.subheader("Your Financial Goals")

        # Progress visualization
        for _, goal in goals_df.iterrows():
            current_amount = db.calculate_goal_current_amount(goal['id'])
            progress = calculate_goal_progress(goal['id'])
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
                        format_currency(current_amount),
                        format_currency(current_amount - goal['target_amount'])
                    )
                    st.write(f"Target: {format_currency(goal['target_amount'])}")
                    st.write(f"Days left: {max(0, days_left)}")

                    # Show linked buckets
                    linked_buckets = db.get_goal_buckets(goal['id'])
                    if not linked_buckets.empty:
                        st.write("Linked Buckets:")
                        for _, bucket in linked_buckets.iterrows():
                            st.write(f"• {bucket['name']}: {format_currency(bucket['amount'])}")

                    # Update bucket selection
                    new_bucket_selection = st.multiselect(
                        "Update Tracked Buckets",
                        options=buckets_df['id'].tolist(),
                        default=linked_buckets['id'].tolist() if not linked_buckets.empty else [],
                        format_func=lambda x: buckets_df[buckets_df['id'] == x]['name'].iloc[0],
                        key=f"buckets_{goal['id']}"
                    )

                    if new_bucket_selection != (linked_buckets['id'].tolist() if not linked_buckets.empty else []):
                        db.link_goal_to_buckets(goal['id'], new_bucket_selection)
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
        total_current = sum(db.calculate_goal_current_amount(goal_id) for goal_id in goals_df['id'])
        overall_progress = (total_current / total_target * 100) if total_target > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Goals Value", format_currency(total_target))
        with col2:
            st.metric("Current Progress", format_currency(total_current))
        with col3:
            st.metric("Overall Progress", f"{overall_progress:.1f}%")
    else:
        st.info("No financial goals set yet. Add your first goal above!")