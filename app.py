import streamlit as st
import buckets
import expenses
import auth

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
            ["Money Buckets", "Monthly Expenses"]
        )

        if page == "Money Buckets":
            buckets.show_buckets_page()
        else:
            expenses.show_expenses_page()

if __name__ == "__main__":
    main()