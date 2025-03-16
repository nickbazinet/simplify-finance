import streamlit as st
import database as db

def init_session_state():
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'show_register' not in st.session_state:
        st.session_state.show_register = False

def toggle_register():
    st.session_state.show_register = not st.session_state.show_register

def show_login_page():
    st.title("Welcome to Personal Finance Manager")

    # Login form
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            user = db.verify_user(username, password)
            if user:
                st.session_state.user = user
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")

    # Registration toggle button
    st.button("New User? Register Here", on_click=toggle_register)

    # Registration section
    if st.session_state.show_register:
        st.markdown("---")
        st.subheader("Register New Account")

        with st.form("register_form"):
            new_username = st.text_input("Choose Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Choose Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            register_submitted = st.form_submit_button("Register")

            if register_submitted:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                elif not new_username or not new_email or not new_password:
                    st.error("Please fill all fields")
                else:
                    if db.create_user(new_username, new_password, new_email):
                        st.success("Registration successful! Please login.")
                        st.session_state.show_register = False  # Hide registration form after successful registration
                        st.rerun() # Rerun to reflect changes
                    else:
                        st.error("Username or email already exists")

def show_logout_button():
    # Add custom CSS for the logout button
    st.markdown("""
        <style>
        .stButton > button {
            border-radius: 20px !important;
            padding: 8px 16px !important;
            background-color: #f0f2f6 !important;
            border: none !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
            transition: all 0.2s ease;
            width: 100%;
            margin-top: 20px;
            color: #262730 !important;
            font-weight: 500 !important;
        }
        .stButton > button:hover {
            background-color: #e0e2e6 !important;
            box-shadow: 0 3px 8px rgba(0,0,0,0.15) !important;
            color: #0f1116 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

def check_authentication():
    return st.session_state.user is not None