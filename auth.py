import streamlit as st
import database as db

def init_session_state():
    if 'user' not in st.session_state:
        st.session_state.user = None

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
    
    # Registration section
    st.markdown("---")
    st.subheader("New User? Register Here")
    
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
                else:
                    st.error("Username or email already exists")

def show_logout_button():
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

def check_authentication():
    return st.session_state.user is not None
