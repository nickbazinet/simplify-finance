import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import database as db
from datetime import datetime
import pandas as pd

def show_expenses_page():
    st.header("Monthly Expenses")

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
                db.add_expense(category, amount, expense_date, description)
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
                db.set_budget(budget_category, budget_amount, selected_month)
                st.success("Budget set!")
                st.rerun()

    # Analysis Tab
    with tab3:
        expenses_df = db.get_expenses(selected_month)
        budget_df = db.get_budget(selected_month)

        if not expenses_df.empty:
            # Monthly spending by category
            st.subheader("Monthly Spending by Category")
            expense_by_category = expenses_df.groupby('category')['amount'].sum().reset_index()

            # Compare with budget
            if not budget_df.empty:
                budget_vs_actual = expense_by_category.merge(
                    budget_df[['category', 'amount']],
                    on='category',
                    how='outer',
                    suffixes=('_actual', '_budget')
                ).fillna(0)

                fig = go.Figure(data=[
                    go.Bar(name='Actual', x=budget_vs_actual['category'], y=budget_vs_actual['amount_actual']),
                    go.Bar(name='Budget', x=budget_vs_actual['category'], y=budget_vs_actual['amount_budget'])
                ])
                fig.update_layout(barmode='group', title='Budget vs Actual Spending')
                st.plotly_chart(fig)

                # Budget analysis
                st.subheader("Budget Analysis")
                for _, row in budget_vs_actual.iterrows():
                    actual = row['amount_actual']
                    budget = row['amount_budget']
                    if budget > 0:
                        percentage = (actual / budget) * 100
                        st.write(f"{row['category']}:")
                        st.progress(min(percentage, 100) / 100)
                        if actual > budget:
                            st.warning(f"Over budget by ${actual - budget:,.2f}")
                        else:
                            st.success(f"Under budget by ${budget - actual:,.2f}")

            # Expense timeline
            st.subheader("Daily Expenses Timeline")
            expenses_df['date'] = pd.to_datetime(expenses_df['date'])
            fig = px.line(
                expenses_df.groupby('date')['amount'].sum().reset_index(),
                x='date',
                y='amount',
                title='Daily Spending Pattern'
            )
            st.plotly_chart(fig)

            # Summary statistics
            total_spent = expenses_df['amount'].sum()
            st.metric("Total Spent This Month", f"${total_spent:,.2f}")
        else:
            st.info("No expenses recorded for this month yet.")