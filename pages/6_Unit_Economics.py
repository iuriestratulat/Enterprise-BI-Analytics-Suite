# English comment: Streamlit page for Module VI - Unit Economics with dynamic multi-product metrics frameworks, organized execution blocks, and actionable business insights
import streamlit as st
import polars as pl
import pandas as pd
from utilities.data_loader import load_parquet_from_gcs

# Import backend analytical functions
from ue_modules.ue_analysis import (
    calculate_unit_economics,
    analyze_growth_points,
    analyze_product_metrics_impact
)

# Import common formatting utility functions and configurations
from ue_modules.ue_utils import (
    format_number_2decimals, format_number_no_currency_no_decimals, format_integer,
    cm_to_number, COLORS_PRODUCTS
)

# Page configuration
st.set_page_config(page_title="VI. Unit Economics", layout="wide")
st.title("📊 VI. Unit Economics & Product Strategy")

st.markdown("""
<div style="background-color: #ebf5fb; padding: 20px; border-radius: 8px; border-left: 5px solid #2980b9; margin-bottom: 25px;">
    <h4 style="margin-top:0; color: #2980b9; font-weight: bold;">📋 Executive Summary & Strategic Scope</h4>
    <p style="font-size: 15px; color: #2c3e50; line-height: 1.6; margin-bottom: 0;">
        <b>The core profitability engine of the enterprise dashboard.</b> This module unifies all atomic metrics into 
        a synchronized mathematical architecture to derive baseline Contribution Margins (CM). It integrates dynamic 
        sensitivity analysis, rigorous A/B testing sample size sizing, and structured SMART/HADI optimization cycles.
    </p>
</div>
""", unsafe_allow_html=True)

# --- CUSTOM CSS INJECTION FOR ULTRA-COMPACT KPI CARDS ---
# English comment: Inject custom CSS override to safely shrink font sizes in st.metric cards, preventing truncation (text clipping) on smaller screens
st.markdown("""
    <style>
        /* Target the metric value inside the Streamlit card */
        [data-testid="stMetricValue"] {
            font-size: 16px !important;
            font-weight: 800 !important;
        }
        /* Target the metric label/title inside the Streamlit card */
        [data-testid="stMetricLabel"] p {
            font-size: 12px !important;
            font-weight: 600 !important;
            white-space: nowrap !important;
        }
    </style>
""", unsafe_allow_html=True)

# Optimized data loading with caching
@st.cache_data
def load_ue_data():
     # Reading cleaned parquet files from the isolated secure data directory
    deals_df = load_parquet_from_gcs("deals_ready.parquet")
    spend_df = load_parquet_from_gcs("spend_ready.parquet")
    return deals_df, spend_df

ue_deals, spend = load_ue_data()

# --- Extended Local KPI Configuration to prevent KeyError for short codes like AC and Revenue ---
LOCAL_KPI_CONFIG = {
    'UA': {'color': '#3498db', 'icon': '👥', 'title': 'User Acquisition'},
    'C1': {'color': '#9b59b6', 'icon': '📈', 'title': 'Conversion Rate'},
    'AOV': {'color': '#1abc9c', 'icon': '💵', 'title': 'Avg Order Value'},
    'APC': {'color': '#34495e', 'icon': '📊', 'title': 'Avg Purchase Count'},
    'CPA': {'color': '#e74c3c', 'icon': '💸', 'title': 'Cost Per Acquisition'},
    'B': {'color': '#2ecc71', 'icon': '🛒', 'title': 'Buyers'},
    'T': {'color': '#e67e22', 'icon': '🔄', 'title': 'Total Months'},
    'CLTV': {'color': '#d35400', 'icon': '🏆', 'title': 'Customer LTV'},
    'LTV': {'color': '#27ae60', 'icon': '🎯', 'title': 'Lifetime Value'},
    'AC': {'color': '#95a5a6', 'icon': '💳', 'title': 'Acquisition Cost'},
    'Revenue': {'color': '#f1c40f', 'icon': '💰', 'title': 'Total Revenue'},
    'CM': {'color': '#8e44ad', 'icon': '💪', 'title': 'Contribution Margin'},
}

# --- Helper function to format Streamlit card values into standard investment format ---
def format_card_value(metric_name, raw_value):
    try:
        if isinstance(raw_value, str):
            raw_value = raw_value.replace('€', '').replace(',', '').strip()
        
        val_float = float(raw_value)
        currency_metrics = ['AOV', 'CPA', 'CLTV', 'LTV', 'AC', 'Revenue', 'CM']
        
        if metric_name in currency_metrics:
            if val_float >= 1_000_000:
                return f"€ {val_float / 1_000_000:.2f} M"
            elif val_float >= 1_000:
                return f"€ {val_float / 1_000:.2f} K"
            else:
                return f"€ {val_float:.2f}"
        elif metric_name == 'C1':
            if val_float < 1.0:
                return f"{val_float * 100:.2f}%"
            return f"{val_float:.2f}%"
        elif metric_name == 'APC':
            return f"{val_float:.2f}"
        else:
            if val_float >= 1_000:
                return f"{val_float / 1_000:.2f} K"
            return f"{int(val_float)}"
    except:
        return str(raw_value)

# --- Helper function for Metric Interpretation Styled Containers (Matches Diagram Levels) ---
def render_level_box(title, content, color, border_color):
    st.markdown(f"""
        <div style="
            background-color: {color}; 
            padding: 20px; 
            border-radius: 10px; 
            border: 1px solid {border_color}; 
            margin-bottom: 15px;
            color: #2c3e50;
        ">
            <h5 style="margin-top: 0; font-weight: bold; color: #2c3e50;">{title}</h5>
            <div style="font-size: 15px; line-height: 1.6;">
                {content}
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- Dropdown Selector for Sub-modules ---
st.markdown("### Select Analysis Type")
analysis_option = st.selectbox(
    "Choose specific analysis:",
    [
        "VI.1 Unit Economics Summary & Product Matrix",
        "VI.2 Business Growth Points (Sensitivity Analysis)",
        "VI.3 Metrics Tree Hierarchy",
        "VI.4 Product Metrics Impact (A/B Testing Sample Size)",
        "VI.5 Hypotheses and Testing Method Framework"
    ]
)

st.markdown("---")

# ============================================================================
# SUB-MODULE EXECUTION LOGIC
# ============================================================================


# >>>========================================================================
# EXECUTION LOGIC VI.1: Unit Economics Summary & Product Matrix
# ============================================================================
if analysis_option == "VI.1 Unit Economics Summary & Product Matrix":
    df_overview, df_ue_by_product = calculate_unit_economics(ue_deals, spend)
    
    st.subheader("📋 Global Unit Economics Overview")
    metrics_dict = {row['Metric']: row['Value'] for row in df_overview.iter_rows(named=True)}
        
    # Explicit horizontal table ordering alignment
    ST_KPI_ORDER = ['UA', 'C1', 'AOV', 'APC', 'CPA', 'B', 'T', 'CLTV', 'LTV', 'AC', 'Revenue', 'CM']
    
    cols = st.columns(len(ST_KPI_ORDER))
    for idx, metric in enumerate(ST_KPI_ORDER):
        if metric in metrics_dict:
            config = LOCAL_KPI_CONFIG[metric]
            formatted_val = format_card_value(metric, metrics_dict[metric])
            with cols[idx]:
                st.metric(label=f"{config['icon']} {metric}", value=formatted_val, help=config['title'])
                
    st.markdown("---")
    st.subheader("📊 Unit Economics per Product")
    
    df_prod_pd = df_ue_by_product.to_pandas()
    product_order = ['Web Developer', 'Digital Marketing', 'UX/UI Design']
    df_prod_pd['Product'] = pd.Categorical(df_prod_pd['Product'], categories=product_order, ordered=True)
    df_prod_pd = df_prod_pd.sort_values('Product').reset_index(drop=True)
    
    for col in ['AOV', 'CPA', 'CLTV', 'LTV', 'AC', 'Revenue', 'CM']:
        df_prod_pd[col] = df_prod_pd[col].apply(lambda x: f"€ {x:,.2f}")
    
    st.dataframe(df_prod_pd, use_container_width=True)
    
    st.markdown("---")
    st.subheader("💡 Executive Insights and Recommendations")
    df_ue_by_product_pd = df_ue_by_product.to_pandas()
    best_product_row = df_ue_by_product_pd.loc[df_ue_by_product_pd['CM'].idxmax()]
    worst_product_row = df_ue_by_product_pd.loc[df_ue_by_product_pd['CM'].idxmin()]
    
    ins_col1, ins_col2, ins_col3 = st.columns(3)
    with ins_col1:
        st.success(f"""**🏆 Best Performing Product**\n### {best_product_row['Product']}\n* **CM:** € {best_product_row['CM']:,.2f}\n* **C1:** {best_product_row['C1']}\n* **LTV:** € {best_product_row['LTV']:,.2f}\n\n👉 *Recommendation: Budget scaling.*""")
    with ins_col2:
        st.error(f"""**⚠️ Opportunity for Improvement**\n### {worst_product_row['Product']}\n* **CM:** € {worst_product_row['CM']:,.2f}\n* **C1:** {worst_product_row['C1']}\n* **CPA:** € {worst_product_row['CPA']:,.2f}\n\n👉 *Recommendation: Optimize top funnel.*""")
    with ins_col3:
        avg_conv_float = df_ue_by_product_pd['C1'].apply(lambda x: float(str(x).strip('%')) / 100).mean()
        st.info(f"""**📊 Global Business Health**\n* **Revenue:** {format_card_value('Revenue', metrics_dict.get('Revenue', 0))}\n* **CM:** {format_card_value('CM', metrics_dict.get('CM', 0))}\n* **Avg Conversion:** {avg_conv_float:.2%}\n* **Leads Funnel:** {metrics_dict.get('UA', '0')} leads → {format_integer(metrics_dict.get('B', '0'))} buyers""")

    st.markdown("---")
    
    with st.expander("📖 Metric Interpretation"):
        st.markdown("""
        * **👥 UA (User Acquisition):** Total number of unique leads/contacts.  
          *Formula:* `UA = COUNTUNIQUE('deals'['Contact Name'])`
        * **📈 C1 (Conversion Rate):** Percentage of leads that become paying customers.  
          *Formula:* `C1 = B / UA`
        * **💵 AOV (Average Order Value):** Average value per month of study.  
          *Formula:* `AOV = Revenue / T`
        * **📊 APC (Average Purchase Count):** Average number of study months per customer.  
          *Formula:* `APC = T / B`
        * **💸 CPA (Cost Per Acquisition):** Average cost per lead acquisition.  
          *Formula:* `CPA = AC / UA`
        * **🛒 B (Buyers):** Number of unique customers who made a payment.  
          *Formula:* `B = COUNTUNIQUE('deals'['Contact Name']) WHERE Stage = 'Payment Done'`
        * **🔄 T (Transactions):** Total study months generated by paying customers.  
          *Formula:* `T = SUM('deals'['Months of study']) WHERE Stage = 'Payment Done'`
        * **💎 CLTV (Customer Lifetime Value):** Total expected value from a single customer.  
          *Formula:* `CLTV = AOV × APC` *(Assumes COGS = 0 and 1COGS = 0. Real Formula: (AOV-COGS)*APC-1COGS)*
        * **🎯 LTV (Lifetime Value):** Total expected value from a lead.  
          *Formula:* `LTV = C1 × CLTV`
        * **💰 AC (Acquisition Cost):** Total marketing cost for lead acquisition.  
          *Formula:* `AC = SUM('spend'['Spend'])`
        * **🎛️ Revenue:** Total earned revenue, calculated based on initial payments and monthly installments.  
          *Formula:* `Revenue = SUM(Initial_Amount_Paid + ((Offer_Total - Initial) / (Duration - 1)) × (Months - 1))`
        * **🏁 CM (Contribution Margin):** Profit after deducting acquisition costs. Key profitability indicator.  
          *Formula:* `CM = UA × (LTV - CPA)`
        """)


# >>>========================================================================
# EXECUTION LOGIC VI.2: Business Growth Points (Sensitivity Analysis)
# ============================================================================

elif analysis_option == "VI.2 Business Growth Points (Sensitivity Analysis)":
    all_results, df_pivot = analyze_growth_points(ue_deals, spend)
    st.subheader("📈 Sensitivity Analysis: Growth Levers Impact on CM (%)")
    
    st.dataframe(df_pivot.style.background_gradient(cmap="RdYlGn", axis=1).format("{:,.2f}%"), use_container_width=True)
    
    st.markdown("---")
    st.markdown("#### 📖 How to interpret the heatmap:")
    st.markdown("""
    * 🟢 **Green colors:** High positive impact on profit. The darker the green, the stronger the impact.
    * 🟡 **Yellow colors:** Moderate impact (0-10%). Improvements bring profit, but not significantly.
    * 🔴 **Red colors:** Low or negative impact. Optimizing these metrics does not bring significant benefits.
    """)
    
    st.markdown("---")
    st.subheader("🔍 Granular Product Scenario Simulations")
    tab_web, tab_dig, tab_ux = st.tabs(["Web Developer", "Digital Marketing", "UX/UI Design"])
    
    for prod_name, df_filtered in all_results:
        df_filtered_pd = df_filtered.to_pandas()
        for col in ['AOV', 'CPA', 'CLTV', 'LTV', 'AC', 'Revenue', 'CM']:
            df_filtered_pd[col] = df_filtered_pd[col].apply(lambda x: f"€ {x:,.2f}")
            
        if prod_name == "Web Developer":
            with tab_web: st.dataframe(df_filtered_pd, use_container_width=True, hide_index=True)
        elif prod_name == "Digital Marketing":
            with tab_dig: st.dataframe(df_filtered_pd, use_container_width=True, hide_index=True)
        elif prod_name == "UX/UI Design":
            with tab_ux: st.dataframe(df_filtered_pd, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("#### 💡 Strategic Recommendations")
    st.markdown("""
    * **Priority 1 - Magic Levers:** C1 (Conversion) and APC (Retention) have a multiplier impact - optimize these first!
    * **Priority 2 - Cost Reduction:** CPA has a direct impact on profit - especially effective for low-margin products.
    * **Priority 3 - Value Growth:** AOV and UA bring linear growth - invest in these after optimizing conversion.
    """)


# >>>========================================================================
# EXECUTION LOGIC VI.3: Metrics Tree Hierarchy & Colored Interpretations
# ============================================================================
elif analysis_option == "VI.3 Metrics Tree Hierarchy":
    st.subheader("🌳 Unit Economics Metrics Tree Hierarchy")
    
    try:
        st.image("metrics_tree.png", caption="VI.3 Visual Metrics Hierarchy Tree Model", use_container_width=True)
    except:
        st.warning("ℹ️ Image 'metrics_tree.png' not found in root path directory.")
        
    st.markdown("---")
    st.subheader("📖 Metric Interpretation")
    st.markdown("Explanations are color-coded to match the hierarchical levels in the diagram above:")

    render_level_box(
        "🥇 Level 1 - Business KPI (Lavender)", 
        "<b>CM (Contribution Margin):</b> Profit after deducting acquisition costs. The key indicator of business profitability. <br><b>Formula: CM = UA × (LTV - CPA)</b>",
        "#dedaff", "#d0c4e5"
    )
    
    render_level_box(
        "🥈 Level 2 - Financial Metrics (Light Blue)", 
        "<b>Revenue:</b> The final financial indicator. Total revenue collected from customers based on initial payments and installments.",
        "#c6dcff", "#b0c8e5"
    )
    
    render_level_box(
        "🥉 Level 3 - Decision Metrics (Mint Green)", 
        """<b>UA (User Acquisition):</b> Total number of unique leads/contacts. <br>
           <b>CPA (Cost Per Acquisition):</b> Average cost to acquire a lead. Formula: <b>CPA = AC / UA</b> <br>
           <b>C1 (Conversion Rate):</b> Percentage of leads that become buyers. Formula: <b>C1 = B / UA</b> <br>
           <b>AOV (Average Order Value):</b> Average value per study month. Formula: <b>AOV = Revenue / T</b> <br>
           <b>APC (Average Purchase Count):</b> Avg months of study per customer. Formula: <b>APC = T / B</b>""",
        "#adf0c7", "#8ed6a8"
    )
    
    render_level_box(
        "📦 Level 4 - Product Metrics (Peach)", 
        """<b>T (Transactions):</b> Total study months generated by paying customers. <br>
           <b>AC (Acquisition Cost):</b> Total marketing cost for lead acquisition. <br>
           <b>CLTV (Customer Lifetime Value):</b> Expected value from a single buyer. Formula: <b>CLTV = AOV × APC</b> <br>
           <b>B (Buyers):</b> Number of unique customers who made a payment. <br>
           <b>LTV (Lifetime Value):</b> Total expected value from a single lead. Formula: <b>LTV = C1 × CLTV</b>""",
        "#f8d3af", "#e6b88a"
    )
    
    render_level_box(
        "🔬 Level 5 - Atomic Metrics (Cream Yellow)", 
        "<b>Raw Data:</b> Basic data points extracted from CRM: Contact Name, Stage, Initial Amount Paid, Spend, Months of study, Offer Total Amount, Course duration, Product.",
        "#fff6b6", "#e6dc8a"
    )

    st.markdown("---")
    
    with st.expander("🧮 Mathematical Relationships Between Metrics"):
        f_col1, f_col2 = st.columns(2)
        
        with f_col1:
            st.markdown("**Fundamental Formulas:**")
            st.code("""C1 = B / UA
AOV = Revenue / T
APC = T / B
CPA = AC / UA
CLTV = AOV × APC
LTV = C1 × CLTV
CM = UA × (LTV - CPA)""", language="text")
            
        with f_col2:
            st.markdown("**Calculation Example:**")
            st.code("""For a product with:
- UA = 100 leads
- B = 20 customers
- Revenue = €10,000
- T = 100 months
- AC = €5,000

→ C1 = 20%
→ AOV = €100
→ APC = 5 months
→ CPA = €50
→ CLTV = €500
→ LTV = €100
→ CM = €5,000""", language="text")


# >>>========================================================================
# EXECUTION LOGIC VI.4: Product Metrics Impact (A/B Testing Sample Size)
# ============================================================================
elif analysis_option == "VI.4 Product Metrics Impact (A/B Testing Sample Size)":
    st.subheader("🎯 A/B Testing Parameters Configuration")
    
    with st.container(border=True):
        ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns(4)
        
        with ctrl_col1:
            required_days = st.slider("📅 Max Test Days:", min_value=7, max_value=30, value=12, step=1)
        with ctrl_col2:
            x_web = st.slider("🌐 Web Developer X:", min_value=0.005, max_value=0.10, value=0.02, step=0.005, format="%.3f")
        with ctrl_col3:
            x_dig = st.slider("📱 Digital Marketing X:", min_value=0.005, max_value=0.10, value=0.05, step=0.005, format="%.3f")
        with ctrl_col4:
            x_ux = st.slider("🎨 UX/UI Design X:", min_value=0.005, max_value=0.10, value=0.025, step=0.005, format="%.3f")

    st.markdown("---")
    st.subheader("🧪 A/B Testing Analysis - Sample Size")
    
    st.markdown(f"<p style='text-align: center; font-size: 16px; font-weight: bold; color: #3498db;'>📊 Max Testing Period: {required_days} days</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 14px; color: #7f8c8d; margin-top: -10px;'>Formula: n = (16 * p * (1-p)) / X² | Power = 80%, Confidence = 95%</p>", unsafe_allow_html=True)
    
    df_transposed, ab_setup = analyze_product_metrics_impact(
        ue_deals, 
        spend, 
        REQUIRED_DAYS=required_days,
        x_web=x_web,
        x_dig=x_dig,
        x_ux=x_ux
    )
    
    df_ab_pd = df_transposed.to_pandas()
    
    ua_global = ue_deals["Contact_Name"].n_unique()
    days_total = (ue_deals["Created_Time"].max() - ue_deals["Created_Time"].min()).days
    daily_traffic_val = int(ua_global / days_total) if days_total > 0 else 0
    
    traffic_row = pd.DataFrame([{
        'Metric': 'Daily Traffic',
        'Web Developer': str(daily_traffic_val),
        'Digital Marketing': str(daily_traffic_val),
        'UX/UI Design': str(daily_traffic_val)
    }])
    df_ab_pd = pd.concat([traffic_row, df_ab_pd], ignore_index=True)
    
    def style_status_cells(val):
        if str(val).strip() == "OK":
            return 'background-color: #d4edda; color: #155724; font-weight: bold;'
        elif "TOO LONG" in str(val):
            return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
        return ''

    styled_df = df_ab_pd.style.applymap(style_status_cells)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    status_row = df_ab_pd[df_ab_pd['Metric'] == 'Status']
    has_warnings = False
    if not status_row.empty:
        for col in ['Web Developer', 'Digital Marketing', 'UX/UI Design']:
            if "TOO LONG" in str(status_row[col].values[0]):
                has_warnings = True
                break

    st.markdown("### 📢 Executive Decision Status")
    if has_warnings:
        st.error("""
        **⚠️ CRITICAL ALERT: Insufficient Testing Time Detected!** Some experiments require too many days due to current traffic velocity or a target effect size (X) that is too small. 
        Please check the **'Suggestion'** row above to see the recommended adjustments for parameter X, or extend the maximum test duration using the slider.
        """)
    else:
        st.success("""
        **✅ OPTIMAL TIMELINE: All Tests Are Feasible!** With the currently selected parameters, the collected daily traffic volume fully allows for the successful completion of all A/B experiments within the established time frame.
        """)
    
    with st.expander("ℹ️ Statistical Evaluation Guide & Legend"):
        st.markdown("""
        **📋 A/B Testing Statistical Decision Guidelines:**
        1. **STATUS 'OK':** The test can be fully executed and successfully finalized within the chosen day limit, using the selected target effect size.
        2. **STATUS '⚠️ TOO LONG':** Traffic velocity is too low. The required data collection period exceeds the maximum time limit.
        3. **SUGGESTION:** Follow the auto-computed alternative Minimum Detectable Effect (MDE / X) to enforce statistical significance within the given time window.
        """)

    with st.expander("📊 Product Metrics Influencing CM"):
        st.markdown("""
        * **🔄 Conversion Rate (C1):** Direct impact on LTV and implicitly on CM. A 1% increase in conversion can generate exponential growth in CM. *A/B Testing areas:* Landing page optimization, sales script testing.
        * **💰 Average Order Value (AOV):** Increasing average order value boosts CLTV and LTV. Direct impact on global contract values. *A/B Testing areas:* Upselling strategies, tier packages, structural bundles.
        * **📚 Average Purchase Count (APC):** Student retention increases total customer equity. A client who studies longer generates superior baseline margin. *A/B Testing areas:* Gamification modules, community building, mentorship networks.
        * **💸 Cost Per Acquisition (CPA):** Reducing CPA directly increases bottom-line CM. Extremely effective for optimizing competitive channels. *A/B Testing areas:* Ad campaign optimization, targeting adjustments, algorithmic splits.
        """)

    with st.expander("🧮 Calculation Formula"):
        st.markdown("""
        The required sample size per variant is evaluated using standard sample size determination metrics:
        """)
        st.code("""
n = (16 * p * (1-p)) / X²

where:
- n = sample size per variant (control or test group)
- p = current baseline conversion rate
- X = minimum detectable effect (target effect size)
- Statistical Power = 80% (industry standard)
- Confidence Level = 95% (alpha = 0.05)

Total Traffic Needed = n × 2 (control + test variant pools)
Days Needed = Total Traffic Needed / Average Daily Traffic
        """, language="text")


# >>>========================================================================
# EXECUTION LOGIC VI.5: Hypotheses and Testing Method Framework
# ============================================================================
elif analysis_option == "VI.5 Hypotheses and Testing Method Framework":
    st.subheader("📋 Metric Optimization Hypotheses & Framework Strategy")
    st.markdown("Select a specific field of study below to inspect its operational optimization hypothesis under the SMART and HADI frameworks:")

    if "selected_product_ue" not in st.session_state:
        st.session_state.selected_product_ue = "Web Developer"

    tile_col1, tile_col2, tile_col3 = st.columns(3)
    
    with tile_col1:
        is_active = st.session_state.selected_product_ue == "Web Developer"
        title_prefix = "🔵 " if is_active else "⚪ "
        if st.button(f"{title_prefix}Web Developer", use_container_width=True, key="btn_web"):
            st.session_state.selected_product_ue = "Web Developer"
            st.rerun()
            
    with tile_col2:
        is_active = st.session_state.selected_product_ue == "Digital Marketing"
        title_prefix = "🟠 " if is_active else "⚪ "
        if st.button(f"{title_prefix}Digital Marketing", use_container_width=True, key="btn_dig"):
            st.session_state.selected_product_ue = "Digital Marketing"
            st.rerun()
            
    with tile_col3:
        is_active = st.session_state.selected_product_ue == "UX/UI Design"
        title_prefix = "🟣 " if is_active else "⚪ "
        if st.button(f"{title_prefix}UX/UI Design", use_container_width=True, key="btn_ux"):
            st.session_state.selected_product_ue = "UX/UI Design"
            st.rerun()

    product_data = {
        "Web Developer": {
            "smart": {
                "Specific": 'Optimize the sales script for the "Web Developer" product, emphasizing the long-term benefits of an IT career to justify the price point.',
                "Measurable": 'Increase the C1 metric by at least 0.03%. Goal — growth from 0.75% to 0.78% and above.',
                "Achievable": 'Realistic, as changing the speech script for managers does not require technical costs.',
                "Relevant": 'Any increase in C1 for this product significantly affects Contribution Margin (CM).',
                "Time-bound": 'The experiment will last 11 days, fitting into a two-week cycle.'
            },
            "hadi": {
                "Hypothesis": 'If we change the sales script highlighting the "employment guarantee", then C1 conversion will grow by at least 0.03%.',
                "Action": '11-day A/B test: experimental group uses the new script, control group uses the standard one.',
                "Data": 'Track UA and B for each group. Target — ~264 leads (132 per group).',
                "Insight": 'If C1 ≥ 0.78% in the experimental group — implement the new script. If not — test another change.'
            },
            "color": COLORS_PRODUCTS['Web Developer'],
            "summary": "Employment guarantee context • 11 days cycle • +0.03% C1 Target"
        },
        "Digital Marketing": {
            "smart": {
                "Specific": 'Change the sales script for "Digital Marketing" by adding a section for proactive handling of price-related objections.',
                "Measurable": 'Increase C1 by 0.04% (MDE). Goal — from 2.59% to 2.63% or higher.',
                "Achievable": 'The goal is realistic — script change does not require technical resources.',
                "Relevant": 'C1 growth has a direct positive impact on Revenue and CM.',
                "Time-bound": 'The experiment will be conducted over 13 days.'
            },
            "hadi": {
                "Hypothesis": 'If we add a section for proactive handling of price objections, then C1 conversion will increase.',
                "Action": '13-day A/B test: Group A — old script, Group B — new script.',
                "Data": 'Collect data daily: UA, B, C1. Sample size — ~323 leads per group.',
                "Insight": 'If C1(B) > C1(A) with statistical significance — implement the new script.'
            },
            "color": COLORS_PRODUCTS['Digital Marketing'],
            "summary": "Price objection handling context • 13 days cycle • +0.04% C1 Target"
        },
        "UX/UI Design": {
            "smart": {
                "Specific": 'Change the sales script for "UX/UI Design" by adding examples of successful alumni portfolios.',
                "Measurable": 'Increase C1 by 0.04% (MDE). Goal — from 1.25% to 1.29% and higher.',
                "Achievable": 'Alumni portfolios already exist — managers need to be trained.',
                "Relevant": 'Conversion growth directly improves Unit Economics.',
                "Time-bound": 'The experiment will last 10 days.'
            },
            "hadi": {
                "Hypothesis": 'If we demonstrate visual "before and after" portfolios, then C1 conversion will grow by 0.04%.',
                "Action": '10-day A/B test: half of the managers send portfolios.',
                "Data": 'Sample size — about 247 leads total (124 per test branch).',
                "Insight": 'If the portfolio variant shows a significant increase in C1 — implement the practice for everyone.'
            },
            "color": COLORS_PRODUCTS['UX/UI Design'],
            "summary": "Visual portfolio context • 10 days cycle • +0.04% C1 Target"
        }
    }

    current_prod = st.session_state.selected_product_ue
    data = product_data[current_prod]

    st.markdown(f"""
    <div style='padding: 15px; border-left: 6px solid {data['color']}; background-color: #f8f9fa; border-radius: 4px; margin-bottom: 25px;'>
        <h4 style='margin: 0; color: #2c3e50;'>🎯 Active Profile: {current_prod} Analysis</h4>
        <p style='margin: 5px 0 0 0; font-size: 14px; color: #7f8c8d; font-weight: 500;'>{data['summary']}</p>
    </div>
    """, unsafe_allow_html=True)

    block_smart, block_hadi = st.columns(2)

    with block_smart:
        st.markdown("#### 🎯 SMART Objectives Framework")
        df_smart = pd.DataFrame(list(data['smart'].items()), columns=["Dimension", "Description"])
        st.table(df_smart)

    with block_hadi:
        st.markdown("#### 🔄 HADI Optimization Cycle")
        df_hadi = pd.DataFrame(list(data['hadi'].items()), columns=["Stage", "Operational Logic"])
        st.table(df_hadi)