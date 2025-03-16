import streamlit as st
import pandas as pd
from utils import calculate_percentage
import database as db

def calculate_savings_score(buckets_df):
    """Calculate score based on savings and investment allocation"""
    total_amount = buckets_df['amount'].sum()
    if total_amount == 0:
        return 0

    # Calculate percentage in investment accounts (RRSP, TFSA)
    investment_amount = buckets_df[buckets_df['type'].isin(['RRSP', 'TFSA'])]['amount'].sum()
    investment_ratio = investment_amount / total_amount

    # Score from 0-100 based on investment ratio (target: 40%+ in investments)
    savings_score = min(100, (investment_ratio / 0.4) * 100)
    return savings_score

def calculate_diversification_score(buckets_df):
    """Calculate score based on portfolio diversification"""
    if buckets_df.empty:
        return 0

    total_amount = buckets_df['amount'].sum()
    if total_amount == 0:
        return 0

    # Calculate concentration in each type
    type_concentrations = (buckets_df.groupby('type')['amount'].sum() / total_amount)

    # Penalize if any single type is over 50% of portfolio
    max_concentration = type_concentrations.max()
    diversification_score = 100 - max(0, ((max_concentration - 0.5) * 200))

    # Bonus for having multiple types
    type_count_bonus = min(20, len(type_concentrations) * 5)

    return min(100, diversification_score + type_count_bonus)

def calculate_budget_score(expenses_df, budget_df):
    """Calculate score based on budget adherence"""
    if budget_df.empty or expenses_df.empty:
        return 0

    # Compare expenses against budget for each category
    merged_df = pd.merge(
        expenses_df.groupby('category')['amount'].sum().reset_index(),
        budget_df[['category', 'amount']],
        on='category',
        how='outer',
        suffixes=('_spent', '_budget')
    ).fillna(0)

    # Calculate adherence score for each category
    merged_df['adherence'] = 100 - abs((merged_df['amount_spent'] - merged_df['amount_budget']) 
                                     / merged_df['amount_budget'] * 100)
    merged_df['adherence'] = merged_df['adherence'].clip(0, 100)

    # Weight by budget amount
    total_budget = merged_df['amount_budget'].sum()
    if total_budget == 0:
        return 0

    weighted_score = (
        (merged_df['adherence'] * merged_df['amount_budget'])
        .sum() / total_budget
    )

    return weighted_score

def get_health_score(user_id):
    """Calculate overall financial health score"""
    # Get user's financial data
    buckets_df = db.get_buckets(user_id)
    current_month = pd.Timestamp.now().strftime('%Y-%m')
    expenses_df = db.get_expenses(user_id, current_month)
    budget_df = db.get_budget(user_id)  

    # Calculate individual scores
    savings_score = calculate_savings_score(buckets_df)
    diversification_score = calculate_diversification_score(buckets_df)
    budget_score = calculate_budget_score(expenses_df, budget_df)

    # Calculate weighted average (adjust weights as needed)
    weights = {
        'savings': 0.4,
        'diversification': 0.3,
        'budget': 0.3
    }

    overall_score = (
        savings_score * weights['savings'] +
        diversification_score * weights['diversification'] +
        budget_score * weights['budget']
    )

    return {
        'overall_score': round(overall_score, 1),
        'savings_score': round(savings_score, 1),
        'diversification_score': round(diversification_score, 1),
        'budget_score': round(budget_score, 1)
    }

def get_recommendations(scores):
    """Generate recommendations based on scores"""
    recommendations = []

    if scores['savings_score'] < 70:
        recommendations.append("Consider increasing your contributions to RRSP and TFSA accounts")

    if scores['diversification_score'] < 70:
        recommendations.append("Your portfolio could benefit from more diversification across different account types")

    if scores['budget_score'] < 70:
        recommendations.append("Try to stick closer to your monthly budget to improve your financial health")

    if not recommendations:
        recommendations.append("Great job! Keep maintaining your current financial habits")

    return recommendations

def show_health_score_page():
    """Display the financial health score dashboard"""
    st.header("Financial Health Score")

    user_id = st.session_state.user['id']
    scores = get_health_score(user_id)

    # Display overall score
    st.metric("Overall Financial Health Score", f"{scores['overall_score']}/100")

    # Display component scores
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Savings Score", f"{scores['savings_score']}/100")
    with col2:
        st.metric("Diversification Score", f"{scores['diversification_score']}/100")
    with col3:
        st.metric("Budget Score", f"{scores['budget_score']}/100")

    # Show recommendations
    st.subheader("Recommendations")
    recommendations = get_recommendations(scores)
    for rec in recommendations:
        st.write("•", rec)