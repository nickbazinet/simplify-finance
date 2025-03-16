import streamlit as st
import buckets
import expenses
import auth
import financial_health
import tips
import goals

st.set_page_config(
    page_title="Personal Finance Manager",
    page_icon="💰",
    layout="wide"
)

def main():
    # Initialize session state
    auth.init_session_state()

    if not auth.check_authentication():
        auth.show_login_page()
    else:
        st.title("Personal Finance Manager")

        # Show logout button in sidebar
        auth.show_logout_button()

        # Navigation
        page = st.sidebar.radio(
            "Navigate to",
            ["Money Buckets", "Monthly Expenses", "Financial Goals", "Financial Health Score"]
        )

        # Show contextual tip at the top of the sidebar
        tips.show_tip_widget(tips.get_context_from_page(page))

        if page == "Money Buckets":
            buckets.show_buckets_page()
        elif page == "Monthly Expenses":
            expenses.show_expenses_page()
        elif page == "Financial Goals":
            goals.show_goals_page()
        else:
            financial_health.show_health_score_page()

if __name__ == "__main__":
    main()