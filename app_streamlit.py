# English comment: Core landing engine for the Enterprise Business Intelligence Suite. Orchestrates multi-page reporting and exhibits technical architecture benchmarks.
import streamlit as st

# Configure the main workspace layout
st.set_page_config(
    page_title="Enterprise BI Analytics Suite",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- GLOBAL CSS FOR PROFESSIONAL LAYOUT ---
st.markdown("""
    <style>
        [data-testid="stMetricValue"] {
            font-size: 16px !important;
            font-weight: 800 !important;
        }
        [data-testid="stMetricLabel"] p {
            font-size: 12px !important;
            font-weight: 600 !important;
            white-space: nowrap !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.title("🚀 Enterprise Business Intelligence Analytics Suite")
st.markdown("### 📊 Data Analytics & BI Solutions Engineer")
st.markdown("---")

# --- EXECUTIVE CASE STUDY & ARCHITECTURE BANNER ---
# English comment: Structured markdown containers to instantly sell the project's data engineering rigor to technical clients
st.markdown("""
<div style="background-color: #f8f9fa; padding: 22px; border-radius: 8px; border-left: 6px solid #2ecc71; margin-bottom: 25px;">
    <h4 style="margin-top: 0; color: #27ae60; font-weight: bold;">🛠️ Engineering Architecture & Data Pipeline Summary</h4>
    <p style="font-size: 14.5px; color: #2c3e50; line-height: 1.6; margin-bottom: 12px;">
        This interactive platform is engineered to ingest, clean, and model highly fragmented production CRM data alongside multi-channel marketing expenditures. Instead of basic spreadsheets, this system acts as a unified source of truth for executive decision-making.
    </p>
    <ul style="font-size: 14px; color: #34495e; line-height: 1.6; margin-left: -15px;">
        <li><b>🤖 Core Data Engineering:</b> Heavy data cleaning, deduplication, and pipeline normalization executed entirely using <b>Python (Polars & Pandas)</b>.</li>
        <li><b>⚡ Storage Performance Optimization:</b> Cleaned datasets are compressed and stored in <b>.parquet (Apache Parquet) format</b>. This columnar storage reduces file size by up to 85% compared to raw CSVs and ensures ultra-fast, vectorized query reading execution inside Streamlit.</li>
        <li><b>📈 Business Framework Integration:</b> Translates complex corporate data pools into actionable <b>Unit Economics (UA, C1, LTV, CPA, CM)</b> structures, backed by automated statistical <b>A/B Testing MDE</b> calculations and structured <b>SMART / HADI</b> experimentation cycles.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("#### 🧭 Interactive Analytical Compartments")
st.markdown("Select a specific infrastructure module from the **left sidebar navigation** to run deep interactive assessments:")

# --- TWO-COLUMN MODULAR OVERVIEW ---
col_left, col_right = st.columns(2)

with col_left:
    with st.container(border=True):
        st.markdown("##### 📈 I. Time Series Analysis")
        st.markdown(
            "<p style='font-size: 13.5px; color: #7f8c8d;'>"
            "Evaluates operational sales velocities, volume movements, seasonal contact spikes, and historical sign-up baselines."
            "</p>", unsafe_allow_html=True
        )
    
    with st.container(border=True):
        st.markdown("##### 🎯 II. Campaign Effectiveness")
        st.markdown(
            "<p style='font-size: 13.5px; color: #7f8c8d;'>"
            "Calculates multi-channel marketing efficiency, tracking ROAS metrics and spending allocations across dynamic acquisition layers."
            "</p>", unsafe_allow_html=True
        )
        
    with st.container(border=True):
        st.markdown("##### ⏳ III. Sales Team Performance")
        st.markdown(
            "<p style='font-size: 13.5px; color: #7f8c8d;'>"
            "Monitors CRM stage transition timelines, operational pipeline speed, and service-level agreement (SLA) fulfillment flags."
            "</p>", unsafe_allow_html=True
        )

with col_right:
    with st.container(border=True):
        st.markdown("##### 💳 IV. Products and Payments")
        st.markdown(
            "<p style='font-size: 13.5px; color: #7f8c8d;'>"
            "Examines dynamic multi-currency collections, subscription cash flow structures, and transactional default risks."
            "</p>", unsafe_allow_html=True
        )
        
    with st.container(border=True):
        st.markdown("##### 🗺️ V. Geographic Analysis")
        st.markdown(
            "<p style='font-size: 13.5px; color: #7f8c8d;'>"
            "Maps localized customer density on interactive GeoJSON layers, cross-referencing demand velocity with language tier criteria."
            "</p>", unsafe_allow_html=True
        )
        
    with st.container(border=True):
        st.markdown("##### 🏁 VI. Unit Economics & Strategy")
        st.markdown(
            "<p style='font-size: 13.5px; color: #7f8c8d;'>"
            "The mathematical engine: evaluates product Contribution Margins, runs sensitivity metrics, and charts statistical sample sizes."
            "</p>", unsafe_allow_html=True
        )

st.markdown("---")
st.markdown("<p style='text-align: center; color: #7f8c8d; font-size: 13px;'>💼 Built with robust production engineering practices: Polars Engine • Apache Parquet • Plotly Interactive Visualizations</p>", unsafe_allow_html=True)