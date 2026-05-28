# English comment: Streamlit page for Module II - Campaign and Source Effectiveness Analytics
import streamlit as st
import polars as pl
from utilities.data_loader import load_parquet_from_gcs

# Import all analytical dashboard functions from your campaigns backend
from bi_modules.analytics_campaigns import (
    get_conversion_by_source,
    get_marketing_matrix,
    get_campaign_audit,
    get_top_campaigns_by_roas,
    get_marketing_source_efficiency,
    get_marketing_channels_efficiency,
    get_financial_efficiency
)

# Page configuration
st.set_page_config(page_title="II. Campaign Effectiveness", layout="wide")
st.title("📊 II. Campaign and Source Effectiveness")

st.markdown("""
<div style="background-color: #fef5e7; padding: 20px; border-radius: 8px; border-left: 5px solid #e67e22; margin-bottom: 25px;">
    <h4 style="margin-top:0; color: #d35400; font-weight: bold;">📋 Executive Summary & Strategic Scope</h4>
    <p style="font-size: 15px; color: #2c3e50; line-height: 1.6; margin-bottom: 0;">
        This compartment evaluates macro-marketing capital efficiency across acquisition channels. 
        By cross-referencing multi-channel advertising expenditures with downstream conversion results, it computes data-driven 
        Real ROAS and asset allocation models, allowing traffic managers to scale profitable traffic and eliminate cost leakages.
    </p>
</div>
""", unsafe_allow_html=True)

# Optimized data loading with caching
@st.cache_data
def load_campaign_data():
    # Reading cleaned parquet files from the isolated secure data directory
    deals_df = load_parquet_from_gcs("deals_ready.parquet")
    spend_df = load_parquet_from_gcs("spend_ready.parquet")
    return deals_df, spend_df

# Load the core datasets
deals, spend = load_campaign_data()

# --- Dropdown Selector (Simulating the Dash Specific Analysis dropdown) ---
st.markdown("### Select Analysis Type")
analysis_option = st.selectbox(
    "Choose specific analysis:",
    [
        "II.1 Marketing Matrix: Volume vs. Real Success",
        "II.2 Campaign Audit: Volume vs. Retention vs. Profitability",
        "II.3 Top Campaigns by Real ROAS",
        "II.4 Conversion Rate by Source",
        "II.5 Marketing Source Efficiency: Volume vs. Quality vs. Profit",
        "II.6 Marketing Channels Efficiency",
        "II.7 Financial Efficiency: Expenses vs. Revenue"
    ]
)

st.markdown("---")

# --- Dynamic Content Execution based on User Selection ---
if analysis_option == "II.1 Marketing Matrix: Volume vs. Real Success":
    fig, conclusion = get_marketing_matrix(deals, spend)
    st.plotly_chart(fig, use_container_width=True)
    st.success(conclusion)

elif analysis_option == "II.2 Campaign Audit: Volume vs. Retention vs. Profitability":
    fig, conclusion = get_campaign_audit(deals, spend)
    st.plotly_chart(fig, use_container_width=True)
    st.success(conclusion)

elif analysis_option == "II.3 Top Campaigns by Real ROAS":
    fig, conclusion = get_top_campaigns_by_roas(deals, spend)
    st.plotly_chart(fig, use_container_width=True)
    st.success(conclusion)

elif analysis_option == "II.4 Conversion Rate by Source":
    fig, conclusion = get_conversion_by_source(deals)
    st.plotly_chart(fig, use_container_width=True)
    st.success(conclusion)

elif analysis_option == "II.5 Marketing Source Efficiency: Volume vs. Quality vs. Profit":
    fig, conclusion = get_marketing_source_efficiency(deals, spend)
    st.plotly_chart(fig, use_container_width=True)
    st.success(conclusion)

elif analysis_option == "II.6 Marketing Channels Efficiency":
    fig, conclusion = get_marketing_channels_efficiency(deals, spend)
    st.plotly_chart(fig, use_container_width=True)
    st.success(conclusion)

elif analysis_option == "II.7 Financial Efficiency: Expenses vs. Revenue":
    fig, conclusion = get_financial_efficiency(deals, spend)
    st.plotly_chart(fig, use_container_width=True)
    st.success(conclusion)