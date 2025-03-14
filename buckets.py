import streamlit as st
import plotly.express as px
import database as db
import pandas as pd

def show_buckets_page():
    st.header("Money Buckets")
    
    # Add new bucket
    with st.form("add_bucket"):
        st.subheader("Add New Bucket")
        bucket_name = st.text_input("Bucket Name")
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        submitted = st.form_submit_button("Add Bucket")
        
        if submitted and bucket_name:
            db.add_bucket(bucket_name, amount)
            st.success(f"Added {bucket_name} bucket!")
            st.rerun()

    # Display existing buckets
    buckets_df = db.get_buckets()
    
    if not buckets_df.empty:
        # Show buckets table
        st.subheader("Your Buckets")
        for idx, row in buckets_df.iterrows():
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(row['name'])
            with col2:
                new_amount = st.number_input(
                    "Amount",
                    value=float(row['amount']),
                    key=f"bucket_{row['id']}",
                    format="%.2f"
                )
                if new_amount != row['amount']:
                    db.update_bucket(row['id'], new_amount)
                    st.rerun()
            with col3:
                st.write(f"${row['amount']:,.2f}")
        
        # Distribution pie chart
        st.subheader("Money Distribution")
        fig = px.pie(
            buckets_df,
            values='amount',
            names='name',
            title='Distribution of Money Across Buckets'
        )
        st.plotly_chart(fig)
        
        # Summary statistics
        st.subheader("Summary")
        total_money = buckets_df['amount'].sum()
        st.metric("Total Money", f"${total_money:,.2f}")
        
        # Show percentages
        st.write("Percentage Distribution:")
        percentages = (buckets_df['amount'] / total_money * 100).round(2)
        for name, pct in zip(buckets_df['name'], percentages):
            st.write(f"{name}: {pct}%")
    else:
        st.info("No buckets created yet. Add your first bucket above!")
