import streamlit as st
from customersegm import load_data

def tampilkan_dashboard():
    st.title("📊 Retail Transaction Project")
    st.caption("Customer Segmentation & Business Insight")

    st.markdown("""
    This project analyzes retail transaction data to understand customer behavior 
    using **RFM segmentation** and **cohort-based retention analysis**.  
    The insights are used to support data-driven business decisions.
    """)

    df = load_data()

    st.subheader("📄 Data Preview")
    st.write(f"Total rows: {df.shape[0]:,}")
    st.write(f"Total columns: {df.shape[1]}")

    st.dataframe(df.head())
