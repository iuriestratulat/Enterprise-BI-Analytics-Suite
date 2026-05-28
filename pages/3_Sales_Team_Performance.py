# English comment: Streamlit page for Module III - Sales Team Performance Analytics
import streamlit as st
import polars as pl
from utilities.data_loader import load_parquet_from_gcs

# Import analytical functions from your sales team backend
from bi_modules.analytics_sales_team import (
    get_manager_performance_matrix,
    get_zero_conversion_agents,
    get_lifecycle_per_euro,
    get_calls_vs_revenue_velocity
)

# Page configuration
st.set_page_config(page_title="III. Sales Team Performance", layout="wide")
st.title("📊 III. Sales Team Performance Analysis")

st.markdown("""
<div style="background-color: #fcf3cf; padding: 20px; border-radius: 8px; border-left: 5px solid #f1c40f; margin-bottom: 25px;">
    <h4 style="margin-top:0; color: #d4ac0d; font-weight: bold;">📋 Executive Summary & Strategic Scope</h4>
    <p style="font-size: 15px; color: #2c3e50; line-height: 1.6; margin-bottom: 0;">
        This section tracks institutional pipeline velocity and human capital operational efficiency inside the CRM system. 
        It isolates stage-to-stage transition times, assesses manager-specific close-rate distributions, and flags pipeline bottlenecks, 
        ensuring strict alignment with corporate customer-response SLA benchmarks.
    </p>
</div>
""", unsafe_allow_html=True)


# Optimized data loading with caching using Polars
@st.cache_data
def load_sales_data():
    # Reading cleaned parquet files from the isolated secure data directory
    deals_df = load_parquet_from_gcs("deals_ready.parquet")
    calls_df = load_parquet_from_gcs("calls_ready.parquet")
    return deals_df, calls_df


# Load datasets
deals, calls = load_sales_data()

# --- Dropdown Selector (Simulating the Dash Specific Analysis dropdown) ---
st.markdown("### Select Analysis Type")
analysis_option = st.selectbox(
    "Choose specific analysis:",
    [
        "III.1 Manager Performance Matrix",
        "III.2 Leads Handled by Agents with 0 Conversions",
        "III.3 Lifecycle per 1€ of Earned Revenue",
        "III.4 Average Calls to Close vs. Revenue Velocity"
    ]
)

st.markdown("---")

# --- Dynamic Content Execution based on User Selection ---
if analysis_option == "III.1 Manager Performance Matrix":
    fig, conclusion = get_manager_performance_matrix(deals, calls)
    st.plotly_chart(fig, use_container_width=True)
    st.success(conclusion)

elif analysis_option == "III.2 Leads Handled by Agents with 0 Conversions":
    fig, conclusion = get_zero_conversion_agents(deals, calls)
    st.plotly_chart(fig, use_container_width=True)
    st.success(conclusion)

elif analysis_option == "III.3 Lifecycle per 1€ of Earned Revenue":
    fig, conclusion = get_lifecycle_per_euro(deals, calls)
    st.plotly_chart(fig, use_container_width=True)
    st.success(conclusion)

elif analysis_option == "III.4 Average Calls to Close vs. Revenue Velocity":
    fig, conclusion = get_calls_vs_revenue_velocity(deals, calls)
    st.plotly_chart(fig, use_container_width=True)
    st.success(conclusion)