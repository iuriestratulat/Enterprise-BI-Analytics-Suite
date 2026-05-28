# English comment: Streamlit page for Module V - Geographic and Regional Analytics
import streamlit as st
import polars as pl
from utilities.data_loader import load_parquet_from_gcs

# Import all analytical and mapping functions from your geographic backend
from bi_modules.analytics_geo import (
    get_international_expansion,
    get_revenue_share_germany_vs_world,
    get_regional_management_dashboard,
    get_market_density,
    get_regional_leadership
)

# Page configuration
st.set_page_config(page_title="V. Geographic Analysis", layout="wide")
st.title("📊 V. Geographic Analysis")

st.markdown("""
<div style="background-color: #f5eef8; padding: 20px; border-radius: 8px; border-left: 5px solid #9b59b6; margin-bottom: 25px;">
    <h4 style="margin-top:0; color: #9b59b6;">📋 Executive Summary & Strategic Scope</h4>
    <p style="font-size: 15px; color: #2c3e50; line-height: 1.6;">
        This module models customer density and the geographic profiles of demand. 
        By correlating regional maps with German language proficiency levels, 
        it provides clear insights for targeting marketing campaigns and optimally allocating native educational resources.
    </p>
</div>
""", unsafe_allow_html=True)

# Optimized data loading with caching
@st.cache_data
def load_data():
    # Reading cleaned parquet files from the isolated secure data directory
    deals_df = load_parquet_from_gcs("deals_ready.parquet")
    spend_df = load_parquet_from_gcs("spend_ready.parquet")
    return deals_df, spend_df

# Load the datasets
df_deals, df_spend = load_geo_data()

# --- Dropdown Selector (Simulating the Dash Specific Analysis dropdown) ---
st.markdown("### Select Analysis Type")
analysis_option = st.selectbox(
    "Choose specific analysis:",
    [
        "V.1 International Expansion",
        "V.2 Revenue Share: Germany vs. Rest of the World",
        "V.3 Regional Management Dashboard",
        "V.4 Market Density",
        "V.5 Regional Leadership"
    ]
)

st.markdown("---")

# --- Dynamic Content Execution based on User Selection ---
if analysis_option == "V.1 International Expansion":
    fig, conclusion = get_international_expansion(df_deals)
    st.plotly_chart(fig, use_container_width=True)
    st.success(conclusion)

elif analysis_option == "V.2 Revenue Share: Germany vs. Rest of the World":
    fig, conclusion = get_revenue_share_germany_vs_world(df_deals)
    st.plotly_chart(fig, use_container_width=True)
    st.success(conclusion)

elif analysis_option == "V.3 Regional Management Dashboard":
    # This function requires both df_deals and df_spend to compute CAC and ROAS
    fig, conclusion = get_regional_management_dashboard(df_deals, df_spend)
    # We pass theme=None because this function outputs a pre-rendered Matplotlib image layout inside Plotly
    st.plotly_chart(fig, use_container_width=True, theme=None)
    st.success(conclusion)

elif analysis_option == "V.4 Market Density":
    fig, conclusion = get_market_density(df_deals)
    st.plotly_chart(fig, use_container_width=True)
    st.success(conclusion)

elif analysis_option == "V.5 Regional Leadership":
    fig, conclusion = get_regional_leadership(df_deals)
    st.plotly_chart(fig, use_container_width=True, theme=None)
    st.success(conclusion)