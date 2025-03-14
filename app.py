import streamlit as st
import buckets
import expenses

st.set_page_config(
    page_title="Personal Finance Manager",
    page_icon="💰",
    layout="wide"
)

def main():
    st.title("Personal Finance Manager")
    
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
