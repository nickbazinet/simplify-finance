import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import database as db
from datetime import datetime
import pandas as pd

def show_expenses_page():
    st.header("Monthly Expenses")
    user_id = st.session_state.user['id']

    # Month selection with custom format
    current_date = datetime.today()
    months_list = pd.date_range(
        start=pd.Timestamp('2024-01-01'),
        end=current_date,
        freq='MS'  # Month Start frequency
    ).strftime("%Y-%m").tolist()

    selected_month = st.selectbox(
        "Select Month",
        months_list,
        index=len(months_list)-1,  # Default to current month
        format_func=lambda x: datetime.strptime(x, "%Y-%m").strftime("%B %Y")
    )

    # Initialize session state for success messages
    if 'budget_success' not in st.session_state:
        st.session_state.budget_success = None
    if 'expense_success' not in st.session_state:
        st.session_state.expense_success = None

    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Add Expense", "Set Budget", "Analysis"])

    # Add Expense Tab
    with tab1:
        with st.form("add_expense"):
            st.subheader("Add New Expense")
            category = st.selectbox(
                "Category",
                ["Housing", "Utilities", "Transportation", "Food", "Restaurants",  "Insurance", "Entertainment",
                 "Shopping & Personal Care", "Household Supplies", "Vacations", "Hobby", "Miscellaneous"]
            )
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")
            description = st.text_input("Description")
            submitted = st.form_submit_button("Add Expense")

            if submitted:
                # Use the selected month and current day
                expense_date = datetime.strptime(selected_month + "-01", "%Y-%m-%d").replace(
                    day=datetime.today().day
                ).date()
                db.add_expense(user_id, category, amount, expense_date, description)
                st.session_state.expense_success = "Expense added successfully!"
                st.rerun()

        # Display expense success message
        if st.session_state.expense_success:
            st.success(st.session_state.expense_success)
            st.session_state.expense_success = None

    # Set Budget Tab
    with tab2:
        col1, col2 = st.columns([1, 1])

        # Add new budget form
        with col1:
            with st.form("set_budget"):
                st.subheader("Set Monthly Budget")
                budget_category = st.selectbox(
                    "Category",
                    ["Housing", "Utilities", "Transportation", "Food", "Restaurants", "Insurance", "Entertainment",
                     "Shopping & Personal Care", "Household Supplies", "Vacations", "Hobby", "Miscellaneous"],
                    key="budget_category"
                )
                budget_amount = st.number_input("Budget Amount", min_value=0.0, format="%.2f", key="budget_amount")
                budget_submitted = st.form_submit_button("Set Budget")

                if budget_submitted:
                    db.set_budget(user_id, budget_category, budget_amount)
                    st.session_state.budget_success = f"Budget set for {budget_category}!"
                    st.rerun()

            # Display budget success message
            if st.session_state.budget_success:
                st.success(st.session_state.budget_success)
                st.session_state.budget_success = None

        # Display existing budgets
        with col2:
            st.subheader("Current Budget Settings")
            budget_df = db.get_budget(user_id)

            if not budget_df.empty:
                for _, row in budget_df.iterrows():
                    with st.container():
                        cols = st.columns([2, 2, 1])
                        with cols[0]:
                            st.write(row['category'])
                        with cols[1]:
                            st.write(f"${row['amount']:,.2f}")
                        with cols[2]:
                            if st.button("🗑️", key=f"delete_{row['category']}"):
                                db.delete_budget(user_id, row['category'])
                                st.success(f"Deleted budget for {row['category']}")
                                st.rerun()
                        st.divider()
            else:
                st.info("No budgets set yet.")

    # Analysis Tab
    with tab3:
        expenses_df = db.get_expenses(user_id, selected_month)
        budget_df = db.get_budget(user_id)

        if not expenses_df.empty or not budget_df.empty:
            st.subheader("Monthly Budget vs Actual Expenses")

            # Prepare data for comparison
            categories = ["Housing", "Transportation", "Food", "Utilities", "Entertainment", "Other"]
            expense_by_category = expenses_df.groupby('category')['amount'].sum().reindex(categories).fillna(0)
            budget_by_category = budget_df.set_index('category')['amount'].reindex(categories).fillna(0)

            # Create bar chart for budget vs actual
            fig = go.Figure(data=[
                go.Bar(name='Budget', x=categories, y=budget_by_category, marker_color='lightblue'),
                go.Bar(name='Actual', x=categories, y=expense_by_category, marker_color='lightgreen')
            ])

            fig.update_layout(
                barmode='group',
                title='Budget vs Actual Expenses by Category',
                yaxis_title='Amount ($)',
                xaxis_title='Category'
            )
            st.plotly_chart(fig, use_container_width=True)

            # Display summary metrics
            total_budget = budget_by_category.sum()
            total_spent = expense_by_category.sum()
            remaining = total_budget - total_spent

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Budget", f"${total_budget:,.2f}")
            with col2:
                st.metric("Total Spent", f"${total_spent:,.2f}")
            with col3:
                st.metric(
                    "Remaining Budget",
                    f"${remaining:,.2f}",
                    delta=f"${remaining:,.2f}"
                )

            # Detailed breakdown table
            st.subheader("Detailed Breakdown")
            breakdown_df = pd.DataFrame({
                'Category': categories,
                'Budget': budget_by_category.map('${:,.2f}'.format),
                'Actual': expense_by_category.map('${:,.2f}'.format),
                'Remaining': (budget_by_category - expense_by_category).map('${:,.2f}'.format),
                'Budget Used %': (expense_by_category / budget_by_category * 100).fillna(0).map('{:.1f}%'.format)
            })
            st.dataframe(
                breakdown_df,
                hide_index=True,
                use_container_width=True
            )

            # Show detailed expenses
            st.subheader("Recent Expenses")
            if not expenses_df.empty:
                # Create columns for the table
                col1, col2, col3, col4, col5 = st.columns([2, 2, 3, 1.5, 0.5])

                # Headers
                with col1:
                    st.write("**Date**")
                with col2:
                    st.write("**Category**")
                with col3:
                    st.write("**Description**")
                with col4:
                    st.write("**Amount**")
                with col5:
                    st.write("**Action**")

                # Display each expense with delete button
                for idx, row in expenses_df.sort_values('date', ascending=False).iterrows():
                    with col1:
                        st.write(pd.to_datetime(row['date']).strftime('%Y-%m-%d'))
                    with col2:
                        st.write(row['category'])
                    with col3:
                        st.write(row['description'] if row['description'] else "-")
                    with col4:
                        st.write(f"${row['amount']:,.2f}")
                    with col5:
                        if st.button("🗑️", key=f"delete_expense_{row['id']}"):
                            db.delete_expense(row['id'], user_id)
                            st.success("Expense deleted!")
                            st.rerun()
            else:
                st.info("No expenses recorded for this month.")
        else:
            st.info("No expenses or budget set yet.")