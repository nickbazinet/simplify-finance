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

    # Add custom CSS for the floating tip
    st.markdown("""
        <style>
        .floating-tip-container {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
        }
        .tip-icon {
            width: 40px;
            height: 40px;
            background: #f0f2f6;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 24px;
            border: none;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            transition: all 0.2s ease;
        }
        .tip-icon:hover {
            transform: scale(1.05);
            box-shadow: 0 3px 8px rgba(0,0,0,0.15);
        }
        .tip-content {
            display: none;
            position: absolute;
            bottom: 50px;
            right: 0;
            width: 250px;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            font-size: 0.95em;
            color: #424242;
            animation: fadeIn 0.3s ease-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .tip-content.show {
            display: block;
        }
        </style>
    """, unsafe_allow_html=True)

    # Create a unique key for this tip widget
    widget_key = f"tip_{context}_{random.randint(1000, 9999)}"

    # Initialize session state for this tip widget
    if widget_key not in st.session_state:
        st.session_state[widget_key] = False

    # JavaScript for handling click events
    st.markdown(f"""
        <div class="floating-tip-container">
            <button class="tip-icon" onclick="toggleTip('{widget_key}')">💡</button>
            <div id="{widget_key}" class="tip-content">
                {tip['text']}
            </div>
        </div>
        <script>
            function toggleTip(id) {{
                const content = document.getElementById(id);
                content.classList.toggle('show');
            }}
        </script>
    """, unsafe_allow_html=True)

def get_context_from_page(page_name: str) -> str:
    """Determine the tip context based on the current page"""
    context_mapping = {
        "Money Buckets": "investing",
        "Monthly Expenses": "budgeting",
        "Financial Health Score": "savings"
    }
    return context_mapping.get(page_name, "general")