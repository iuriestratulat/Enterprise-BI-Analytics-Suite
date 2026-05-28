# English comment: Streamlit page for Module I - Time Series Analysis
import streamlit as st
import polars as pl
from utilities.data_loader import load_parquet_from_gcs

# Import functions directly from your existing analytics backend
from bi_modules.analytics_time_series import(
    get_leads_vs_calls_trend,
    get_speed_to_revenue,
    get_cycle_time_by_quality
)

# Page configuration
st.set_page_config(page_title="I. Time Series Analysis", layout="wide")
st.title("📊 I. Time Series Analysis")

st.markdown("""
<div style="background-color: #f4f6f7; padding: 20px; border-radius: 8px; border-left: 5px solid #2c3e50; margin-bottom: 25px;">
    <h4 style="margin-top:0; color: #2c3e50; font-weight: bold;">📋 Executive Summary & Strategic Scope</h4>
    <p style="font-size: 15px; color: #2c3e50; line-height: 1.6; margin-bottom: 0;">
        This module models historical lead generation velocities and operational call volumes across structural time horizons. 
        By executing advanced cohort sequencing and trend decomposition, it isolates systemic seasonal patterns, 
        evaluates baseline funnel inflows, and equips management with predictable capacity forecasting models.
    </p>
</div>
""", unsafe_allow_html=True)

# Optimized data loading with caching using Polars
@st.cache_data
def load_data():
    # Reading cleaned parquet files from the isolated secure data directory
    deals_df = load_parquet_from_gcs("deals_ready.parquet")
    calls_df = load_parquet_from_gcs("calls_ready.parquet")
    return deals_df, calls_df

# Load the datasets
deals, calls = load_data()

# --- Dropdown Selector (Simulating the Dash Specific Analysis dropdown) ---
st.markdown("### Select Analysis Type")
analysis_option = st.selectbox(
    "Choose specific analysis:",
    [
        "I.1 Leads vs Calls Trend",
        "I.2 Speed to Revenue (Initial Amount > 0)",
        "I.3 Cycle Time Analysis by Lead Quality"
    ]
)

st.markdown("---")

# --- Dynamic Content Generation ---
if analysis_option == "I.1 Leads vs Calls Trend":
    # Call your backend function
    fig, conclusion = get_leads_vs_calls_trend(deals, calls)
    
    # Render the interactive Plotly chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Render conclusions inside a nice clean alert box (Green/Success background)
    st.success(conclusion)

elif analysis_option == "I.2 Speed to Revenue (Initial Amount > 0)":
    # Call your backend function
    fig, conclusion = get_speed_to_revenue(deals)
    
    # Render chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Render conclusions inside an alert box
    st.success(conclusion)

elif analysis_option == "I.3 Cycle Time Analysis by Lead Quality":
    # Call your backend function
    fig, conclusion = get_cycle_time_by_quality(deals)
    
    # Render chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Render conclusions inside an alert box
    st.success(conclusion)