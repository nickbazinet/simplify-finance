import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import database as db
from datetime import datetime
import pandas as pd

def show_expenses_page():
    st.header("Monthly Expenses")
    user_id = st.session_state.user['id']

    # Date selection with valid format
    date = st.date_input(
        "Select Month",
        value=datetime.today(),
        format="YYYY/MM/DD"  # Using supported format
    )
    selected_month = date.strftime("%Y-%m")

    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Add Expense", "Set Budget", "Analysis"])

    # Add Expense Tab
    with tab1:
        with st.form("add_expense"):
            st.subheader("Add New Expense")
            category = st.selectbox(
                "Category",
                ["Housing", "Transportation", "Food", "Utilities", "Entertainment", "Other"]
            )
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")
            expense_date = st.date_input("Date", value=date)
            description = st.text_input("Description")
            submitted = st.form_submit_button("Add Expense")

            if submitted:
                db.add_expense(user_id, category, amount, expense_date, description)
                st.success("Expense added!")
                st.rerun()

    # Set Budget Tab
    with tab2:
        with st.form("set_budget"):
            st.subheader("Set Monthly Budget")
            budget_category = st.selectbox(
                "Category",
                ["Housing", "Transportation", "Food", "Utilities", "Entertainment", "Other"],
                key="budget_category"
            )
            budget_amount = st.number_input("Budget Amount", min_value=0.0, format="%.2f", key="budget_amount")
            budget_submitted = st.form_submit_button("Set Budget")

            if budget_submitted:
                db.set_budget(user_id, budget_category, budget_amount, selected_month)
                st.success("Budget set!")
                st.rerun()

    # Analysis Tab
    with tab3:
        expenses_df = db.get_expenses(user_id, selected_month)
        budget_df = db.get_budget(user_id, selected_month)

        if not expenses_df.empty:
            st.subheader("Monthly Expenses Analysis")

            # Group expenses by category
            expense_by_category = expenses_df.groupby('category').agg({
                'amount': ['sum', 'count']
            }).reset_index()
            expense_by_category.columns = ['category', 'total_amount', 'transaction_count']

            # Merge with budget data
            if not budget_df.empty:
                analysis_df = expense_by_category.merge(
                    budget_df[['category', 'amount']],
                    on='category',
                    how='outer',
                    suffixes=('_spent', '_budget')
                ).fillna(0)

                # Calculate percentages and remaining budget
                analysis_df['budget_used_percent'] = (analysis_df['total_amount'] / analysis_df['amount']) * 100
                analysis_df['remaining_budget'] = analysis_df['amount'] - analysis_df['total_amount']

                # Display summary table
                st.write("Summary by Category:")
                summary_df = pd.DataFrame({
                    'Category': analysis_df['category'],
                    'Total Spent': analysis_df['total_amount'].map('${:,.2f}'.format),
                    'Budget': analysis_df['amount'].map('${:,.2f}'.format),
                    'Remaining': analysis_df['remaining_budget'].map('${:,.2f}'.format),
                    'Budget Used': analysis_df['budget_used_percent'].map('{:.1f}%'.format),
                    'Transactions': analysis_df['transaction_count'].map('{:,.0f}'.format)
                })
                st.dataframe(
                    summary_df,
                    hide_index=True,
                    use_container_width=True
                )

            # Display detailed expenses
            st.write("Detailed Expenses:")
            expenses_df['date'] = pd.to_datetime(expenses_df['date']).dt.strftime('%Y-%m-%d')
            detailed_df = pd.DataFrame({
                'Date': expenses_df['date'],
                'Category': expenses_df['category'],
                'Description': expenses_df['description'],
                'Amount': expenses_df['amount'].map('${:,.2f}'.format)
            })
            st.dataframe(
                detailed_df.sort_values('Date', ascending=False),
                hide_index=True,
                use_container_width=True
            )

            # Summary statistics
            total_spent = expenses_df['amount'].sum()
            total_budget = budget_df['amount'].sum() if not budget_df.empty else 0
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Spent", f"${total_spent:,.2f}")
            with col2:
                st.metric("Total Budget", f"${total_budget:,.2f}")
            with col3:
                remaining = total_budget - total_spent
                st.metric("Remaining Budget", f"${remaining:,.2f}")
        else:
            st.info("No expenses recorded for this month yet.")