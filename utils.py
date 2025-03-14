from datetime import datetime

def format_currency(amount):
    return f"${amount:,.2f}"

def get_current_month():
    return datetime.now().strftime("%Y-%m")

def calculate_percentage(part, whole):
    return (part / whole * 100) if whole != 0 else 0
