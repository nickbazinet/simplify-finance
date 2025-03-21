import streamlit as st
import database as db
from authlib.integrations.requests_client import OAuth2Session
import os
import json
from datetime import datetime, timedelta

# Auth0 configuration
AUTH0_CLIENT_ID = os.environ['AUTH0_CLIENT_ID']
AUTH0_CLIENT_SECRET = os.environ['AUTH0_CLIENT_SECRET']
AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN']

# Get Replit domain from environment variables
REPL_SLUG = os.environ.get('REPL_SLUG', 'bucketbudget')  # Your Repl name
REPL_OWNER = os.environ.get('REPL_OWNER')  # Your Replit username

# Construct callback URL
if os.environ.get('REPL_ID'):  # We're on Replit
    AUTH0_CALLBACK_URL = f"https://{REPL_SLUG}.{REPL_OWNER}.repl.co/callback"
else:  # Local development
    AUTH0_CALLBACK_URL = "https://finance-simplify.streamlit.app/callback"

def init_session_state():
    """Initialize session state variables"""
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'auth_tokens' not in st.session_state:
        st.session_state.auth_tokens = None

def get_auth0_client():
    """Create Auth0 OAuth2 client"""
    return OAuth2Session(
        client_id=AUTH0_CLIENT_ID,
        client_secret=AUTH0_CLIENT_SECRET,
        scope='openid profile email'
    )

def get_auth0_authorize_url():
    """Get Auth0 authorization URL"""
    client = get_auth0_client()
    auth_url = f"https://{AUTH0_DOMAIN}/authorize"
    return client.create_authorization_url(
        auth_url,
        redirect_uri=AUTH0_CALLBACK_URL
    )[0]

def handle_auth0_callback(code):
    """Handle Auth0 callback and token exchange"""
    client = get_auth0_client()
    token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
    tokens = client.fetch_token(
        token_url,
        authorization_response=f"{AUTH0_CALLBACK_URL}?code={code}",
        redirect_uri=AUTH0_CALLBACK_URL
    )

    # Get user info from Auth0
    userinfo_url = f"https://{AUTH0_DOMAIN}/userinfo"
    resp = client.get(userinfo_url)
    userinfo = resp.json()

    # Create or update user in database
    user = db.get_or_create_auth0_user(
        auth0_id=userinfo['sub'],
        email=userinfo.get('email', ''),
        name=userinfo.get('name', '')
    )

    return user, tokens

def show_login_page():
    """Display Auth0 login page"""
    st.title("Welcome to Personal Finance Manager")

    # Center the login button with custom styling
    st.markdown("""
        <style>
        .auth0-login {
            display: flex;
            justify-content: center;
            margin-top: 2rem;
        }
        .auth0-button {
            background-color: #635DFF;
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 4px;
            text-decoration: none;
            font-weight: 500;
            transition: background-color 0.2s;
        }
        .auth0-button:hover {
            background-color: #4B45FF;
        }
        </style>
    """, unsafe_allow_html=True)

    # Show login button
    st.markdown(f"""
        <div class="auth0-login">
            <a href="{get_auth0_authorize_url()}" target="_self" class="auth0-button">
                Login with Auth0
            </a>
        </div>
    """, unsafe_allow_html=True)

    # Handle Auth0 callback
    query_params = st.query_params
    if 'code' in query_params:
        code = query_params['code']
        try:
            user, tokens = handle_auth0_callback(code)
            st.session_state.user = user
            st.session_state.auth_tokens = tokens
            st.rerun()
        except Exception as e:
            st.error(f"Authentication failed: {str(e)}")

def show_logout_button():
    """Display logout button in sidebar"""
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.auth_tokens = None
        st.rerun()

def check_authentication():
    """Check if user is authenticated"""
    return st.session_state.user is not None