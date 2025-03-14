import streamlit as st
import plotly.express as px
import database as db
import pandas as pd

def show_buckets_page():
    st.header("Money Buckets")
    user_id = st.session_state.user['id']

    # Add new bucket
    with st.form("add_bucket"):
        st.subheader("Add New Bucket")
        bucket_name = st.text_input("Bucket Name")
        bucket_type = st.selectbox(
            "Bucket Type",
            ["RRSP", "TFSA", "Cash", "Crypto", "Non-Registered"]
        )
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        submitted = st.form_submit_button("Add Bucket")

        if submitted and bucket_name:
            db.add_bucket(user_id, bucket_name, amount, bucket_type)
            st.success(f"Added {bucket_name} bucket!")
            st.rerun()

    # Display existing buckets
    buckets_df = db.get_buckets(user_id)

    if not buckets_df.empty:
        # Show buckets table
        st.subheader("Your Buckets")
        for idx, row in buckets_df.iterrows():
            col1, col2, col3, col4 = st.columns([2, 1, 2, 1])
            with col1:
                st.write(row['name'])
            with col2:
                st.write(row['type'])
            with col3:
                new_amount = st.number_input(
                    "Amount",
                    value=float(row['amount']),
                    key=f"bucket_{row['id']}",
                    format="%.2f"
                )
                if new_amount != row['amount']:
                    db.update_bucket(row['id'], new_amount, user_id)
                    st.rerun()
            with col4:
                st.write(f"${row['amount']:,.2f}")

        # Distribution pie chart by type
        st.subheader("Money Distribution by Type")
        type_distribution = buckets_df.groupby('type')['amount'].sum().reset_index()
        fig = px.pie(
            type_distribution,
            values='amount',
            names='type',
            title='Distribution of Money by Account Type'
        )
        st.plotly_chart(fig)

        # Distribution pie chart by bucket
        st.subheader("Money Distribution by Bucket")
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

        # Show percentages by type
        st.write("Percentage Distribution by Type:")
        type_percentages = (type_distribution['amount'] / total_money * 100).round(2)
        for type_name, pct in zip(type_distribution['type'], type_percentages):
            st.write(f"{type_name}: {pct}%")

        # Show percentages by bucket
        st.write("Percentage Distribution by Bucket:")
        bucket_percentages = (buckets_df['amount'] / total_money * 100).round(2)
        for name, pct in zip(buckets_df['name'], bucket_percentages):
            st.write(f"{name}: {pct}%")
    else:
        st.info("No buckets created yet. Add your first bucket above!")