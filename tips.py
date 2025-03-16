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
    """Display a subtle tip widget"""
    tip = get_contextual_tip(context)

    # CSS for subtle animations
    st.markdown("""
        <style>
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .tip-container {
            border: 1px solid #e6e6e6;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
            background: #fafafa;
            animation: fadeIn 0.8s ease-out;
            transition: all 0.2s ease;
        }
        .tip-container:hover {
            background: #f6f6f6;
            border-color: #d1d1d1;
        }
        .tip-text {
            font-size: 0.95em;
            color: #424242;
        }
        </style>
        """, unsafe_allow_html=True)

    # Display the tip with subtle styling
    st.markdown(f"""
        <div class="tip-container">
            <div class="tip-text">{tip['text']}</div>
        </div>
    """, unsafe_allow_html=True)

def get_context_from_page(page_name: str) -> str:
    """Determine the tip context based on the current page"""
    context_mapping = {
        "Money Buckets": "investing",
        "Monthly Expenses": "budgeting",
        "Financial Health Score": "savings"
    }
    return context_mapping.get(page_name, "general")