# English comment: Streamlit page for Module IV - Products and Payments Analytics
import streamlit as st
import polars as pl

# Import all analytical dashboard functions from your products backend
from bi_modules.analytics_products import (
    get_revenue_by_payment_type,
    get_cash_velocity_micro_aging,
    get_avg_real_value_per_student,
    get_financial_risks_by_schedule,
    get_main_product_performance,
    get_financial_risks_by_product,
    get_product_performance_by_schedule,
    get_financial_risks_by_payment_method
)


# Page configuration
st.set_page_config(page_title="IV. Products and Payments", layout="wide")
st.title("📊 IV. Products and Payments Analysis")

st.markdown("""
<div style="background-color: #e8f8f5; padding: 20px; border-radius: 8px; border-left: 5px solid #1abc9c; margin-bottom: 25px;">
    <h4 style="margin-top:0; color: #1abc9c;">📋 Executive Summary & Strategic Scope</h4>
    <p style="font-size: 15px; color: #2c3e50; line-height: 1.6;">
        Focused on payment structures and long-term financial value. It analyzes the sustainability 
        of revenue, the consistency of recurring payments, and the risks of non-payment or refusal associated with each type of contract, 
        establishing safe limits for procurement budgets. 
    </p>
</div>
""", unsafe_allow_html=True)

# Optimized data loading with caching using Polars
@st.cache_data
def load_products_data():
    # This module reads data from deals_ready.parquet
    deals_df = pl.read_parquet("raw_and_clean_data/deals_ready.parquet")
    return deals_df

# Load the core dataset
df_deals = load_products_data()

# --- Dropdown Selector (Simulating the Dash Specific Analysis dropdown) ---
st.markdown("### Select Analysis Type")
analysis_option = st.selectbox(
    "Choose specific analysis:",
    [
        "IV.1 Distribution of Real Earned Revenue by Payment Type",
        "IV.2 Cash Velocity: Micro-Aging & Real Revenue Quality",
        "IV.3 Average Real Value per Student: Evening vs. Morning",
        "IV.4 Potential Financial Risks by Schedule",
        "IV.5 Main Product Performance",
        "IV.6 Potential Financial Risks by Product",
        "IV.7 Real Revenue: Product Performance by Schedule",
        "IV.8 Potential Financial Risks by Payment Method"
    ]
)

st.markdown("---")

# --- Dynamic Content Execution based on User Selection ---
# English comment: Render chart IV.1 forcing custom layout parameters by disabling Streamlit theme override
if analysis_option == "IV.1 Distribution of Real Earned Revenue by Payment Type":
    fig, conclusion = get_revenue_by_payment_type(df_deals)
    # Added theme=None to preserve your update_layout settings
    st.plotly_chart(fig, use_container_width=True, theme=None)
    st.success(conclusion)

elif analysis_option == "IV.2 Cash Velocity: Micro-Aging & Real Revenue Quality":
    fig, conclusion = get_cash_velocity_micro_aging(df_deals)
    st.plotly_chart(fig, use_container_width=True)
    st.success(conclusion)

# English comment: Render chart IV.3 without Streamlit theme to fix the bottom legend overlap
elif analysis_option == "IV.3 Average Real Value per Student: Evening vs. Morning":
    fig, conclusion = get_avg_real_value_per_student(df_deals)
    # Added theme=None here as well
    st.plotly_chart(fig, use_container_width=True, theme=None)
    st.success(conclusion)

elif analysis_option == "IV.4 Potential Financial Risks by Schedule":
    fig, conclusion = get_financial_risks_by_schedule(df_deals)
    st.plotly_chart(fig, use_container_width=True)
    st.success(conclusion)

elif analysis_option == "IV.5 Main Product Performance":
    fig, conclusion = get_main_product_performance(df_deals)
    st.plotly_chart(fig, use_container_width=True)
    st.success(conclusion)

elif analysis_option == "IV.6 Potential Financial Risks by Product":
    fig, conclusion = get_financial_risks_by_product(df_deals)
    st.plotly_chart(fig, use_container_width=True)
    st.success(conclusion)

elif analysis_option == "IV.7 Real Revenue: Product Performance by Schedule":
    fig, conclusion = get_product_performance_by_schedule(df_deals)
    st.plotly_chart(fig, use_container_width=True)
    st.success(conclusion)

elif analysis_option == "IV.8 Potential Financial Risks by Payment Method":
    fig, conclusion = get_financial_risks_by_payment_method(df_deals)
    st.plotly_chart(fig, use_container_width=True)
    st.success(conclusion)