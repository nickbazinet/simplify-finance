import streamlit as st
import random
from typing import Dict, List

# Financial tips database organized by context
TIPS_DATABASE = {
    "savings": [
        "💡 Try the 50/30/20 rule: 50% needs, 30% wants, 20% savings",
        "💰 Set up automatic transfers to your savings account",
        "🎯 Small regular deposits add up over time!",
    ],
    "investing": [
        "📈 Consider diversifying your investment portfolio",
        "🏦 Take advantage of employer RRSP matching if available",
        "⏰ Time in the market beats timing the market",
    ],
    "budgeting": [
        "📝 Track every expense for a month to find saving opportunities",
        "🎮 Think of budgeting as a game - try to beat your high score!",
        "🎯 Set specific and achievable financial goals",
    ],
    "general": [
        "✨ Financial freedom is a journey, not a destination",
        "🌱 Your future self will thank you for saving today",
        "💪 Every financial decision counts - you've got this!",
    ]
}

def get_contextual_tip(context: str = "general") -> Dict[str, str]:
    """Get a random tip based on the context"""
    tips = TIPS_DATABASE.get(context, TIPS_DATABASE["general"])
    tip = random.choice(tips)
    return {
        "text": tip,
        "context": context
    }

def show_tip_widget(context: str = "general"):
    """Display a floating tip widget"""
    tip = get_contextual_tip(context)

    # Initialize session state for tip visibility
    if 'tip_visible' not in st.session_state:
        st.session_state.tip_visible = False

    # Add custom CSS for styling
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

    # Create container for the tip button in sidebar
    with st.sidebar:
        # Add spacer to push content to bottom
        st.markdown('<div style="flex: 1"></div>', unsafe_allow_html=True)

        # Divider before tips section
        st.markdown("---")

        # Tips section at the bottom
        if st.button("💡 Daily Tip", key="tip_button"):
            st.session_state.tip_visible = not st.session_state.tip_visible

        # Show tip if visible
        if st.session_state.tip_visible:
            st.info(tip['text'])

def get_context_from_page(page_name: str) -> str:
    """Determine the tip context based on the current page"""
    context_mapping = {
        "Money Buckets": "investing",
        "Monthly Expenses": "budgeting",
        "Financial Health Score": "savings"
    }
    return context_mapping.get(page_name, "general")