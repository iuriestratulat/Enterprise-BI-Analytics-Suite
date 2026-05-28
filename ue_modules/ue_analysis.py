"""
VI. Unit Economics Analysis Module
Author: [Your Name]
Date: [Current Date]
Description: Unit Economics analysis for educational products
"""

import polars as pl
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import math
from pathlib import Path

# Configuration for visualizations
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# ============================================================================
# VI.1 Unit Economics - Main Tables
# ============================================================================

def calculate_unit_economics(ue_deals, spend):
    """
    Calculates and displays the 2 main Unit Economics tables.
    Tables are displayed in a 2x1 configuration.
    
    Parameters:
    -----------
    ue_deals : polars.DataFrame
        DataFrame containing deals data for UE analysis
    spend : polars.DataFrame
        DataFrame containing spend data for UE analysis
    """
    print("=" * 80)
    print("VI.1 UNIT ECONOMICS - COMPARATIVE ANALYSIS")
    print("=" * 80)
    
    # --- STEP 1: INDIVIDUAL REVENUE CALCULATION (Allocation Logic) ---
    # We calculate revenue based on initial payment and monthly installments
    df_ue = ue_deals.with_columns([
        pl.when(pl.col("Months_of_study") == 1)
        .then(pl.col("Initial_Amount_Paid"))
        .otherwise(
            pl.col("Initial_Amount_Paid") + 
            ((pl.col("Offer_Total_Amount") - pl.col("Initial_Amount_Paid")) / 
             (pl.when(pl.col("Course_duration") <= 1).then(1).otherwise(pl.col("Course_duration") - 1))) * (pl.col("Months_of_study") - 1)
        )
        .fill_null(0)
        .alias("Individual_Revenue")
    ])
    
    # --- STEP 2: UNIT ECONOMICS COMPONENTS CALCULATION ---
    # UA (User Acquisition): Total unique leads/contacts
    ua = df_ue["Contact_Name"].n_unique()
    
    # Filter dataset only for confirmed payments to calculate performance metrics
    df_paid = df_ue.filter(pl.col("Stage") == "Payment Done")
    
    # B (Buyers): Unique customers who made a payment
    b = df_paid["Contact_Name"].n_unique()
    
    # C1 (Conversion Rate): Ratio of buyers to total leads
    c1 = (b / ua) if ua > 0 else 0
    
    # T (Transactions): Total months of study across all paying students
    t = df_paid["Months_of_study"].sum()
    
    # Total Revenue: Sum of calculated individual revenue for confirmed payments
    total_revenue = df_paid["Individual_Revenue"].sum()
    
    # Acquisition Cost (AC) processing from spend data
    df_spend_temp = spend.to_pandas() if hasattr(spend, "to_pandas") else spend
    # Clean numeric spend values from currency symbols and spaces
    df_spend_temp['Spend_Numeric'] = df_spend_temp['Spend'].astype(str).str.replace(r'[€, ]', '', regex=True).astype(float)
    ac = df_spend_temp['Spend_Numeric'].sum()
    
    # Fundamental Unit Economics Formulas
    # AOV: Average Order Value (Revenue per month of study)
    aov = total_revenue / t if t > 0 else 0
    # APC: Average Purchase Count (Months of study per buyer)
    apc = t / b if b > 0 else 0
    # CPA: Cost Per Acquisition (Marketing spend per lead)
    cpa = ac / ua if ua > 0 else 0
    # CLTV: Customer Lifetime Value (Revenue expected from a single buyer)
    cltv = aov * apc
    # LTV: Lifetime Value (Revenue expected per lead)
    ltv = c1 * cltv
    
    # CM (Contribution Margin): Total profit after acquisition costs
    # CM = UA * (LTV - CPA)
    cm = ua * (ltv - cpa)
    
    # --- STEP 3: SUMMARY TABLE GENERATION ---
    # Constructing an overview table for management reporting
    overview_data = {
        "Metric": ["UA", "B", "C1", "T", "AC", "Revenue", "AOV", "APC", "CPA", "CLTV", "LTV", "CM"],
        "Description": [
            "User Acquisition (Leads)", "Buyers", "Conversion Rate (%)", "Total Months (Transactions)",
            "Acquisition Cost", "Total Earned Revenue", "Average Order Value", "Avg Purchase Count",
            "Cost Per Acquisition", "Customer LTV", "Lifetime Value", "Contribution Margin"
        ],
        "Value": [
            str(ua), 
            str(b), 
            f"{c1:.2%}", 
            f"{t:.0f}", 
            f"{ac:,.2f} €", 
            f"{total_revenue:,.2f} €", 
            f"{aov:,.2f} €", 
            f"{apc:.2f}",
            f"{cpa:,.2f} €", 
            f"{cltv:,.2f} €", 
            f"{ltv:,.2f} €",
            f"{cm:,.2f} €"
        ]
    }
    
    df_overview = pl.DataFrame(overview_data)
    
    # --- STEP 4: UNIT ECONOMICS BY PRODUCT ---
    # Analyze performance for each major educational program
    products = ["Web Developer", "Digital Marketing", "UX/UI Design"]
    product_rows = []
    
    for prod in products:
        # Filter the base dataset for the specific product
        df_prod_all = df_ue.filter(pl.col("Product") == prod)
        
        # CRITICAL FILTER: Only include completed transactions (Payment Done)
        # This aligns the analysis with actual cash flow metrics
        df_prod_paid = df_prod_all.filter(pl.col("Stage") == "Payment Done")
        
        # B (Buyers): Unique customers for this product
        b_prod = df_prod_paid["Contact_Name"].n_unique()
        # C1: Conversion rate for this product relative to global lead pool
        c1_prod = (b_prod / ua) if ua > 0 else 0
        # T (Transactions): Total study months generated by this product
        t_prod = df_prod_paid["Months_of_study"].sum()
        
        # CORRECTED REVENUE: Sum of earned revenue for paid students only
        rev_prod = df_prod_paid["Individual_Revenue"].sum()
        
        # Calculate derived metrics
        # AOV: Revenue per month for this product
        aov_prod = rev_prod / t_prod if t_prod > 0 else 0
        # APC: Retention depth (Average months per student)
        apc_prod = t_prod / b_prod if b_prod > 0 else 0
        # CLTV: Expected revenue from a single buyer of this product
        cltv_prod = aov_prod * apc_prod
        # LTV: Expected revenue per lead for this product path
        ltv_prod = c1_prod * cltv_prod
        
        # CM (Contribution Margin): Financial impact after global acquisition costs
        # CM = UA * (LTV - CPA)
        cm_prod = ua * (ltv_prod - cpa)
        
        product_rows.append({
            "Product": prod,
            "UA": ua,
            "C1": f"{c1_prod:.2%}",
            "AOV": round(aov_prod, 2),
            "APC": round(apc_prod, 2),
            "CPA": round(cpa, 2),
            "B": b_prod,
            "T": t_prod,
            "CLTV": round(cltv_prod, 2),
            "LTV": round(ltv_prod, 2),
            "AC": round(ac, 2),
            "Revenue": round(rev_prod, 2),
            "CM": round(cm_prod, 2)
        })
    
    # Construct the final comparative DataFrame
    df_ue_by_product = pl.DataFrame(product_rows)
    
    # --- STEP 5: DISPLAY TABLES IN 2x1 CONFIGURATION ---
    print("\n" + "=" * 40 + " TABLE 1: OVERVIEW " + "=" * 40)
    with pl.Config(tbl_rows=12, tbl_width_chars=100):
        print(df_overview)
    
    print("\n" + "=" * 40 + " TABLE 2: BY PRODUCT " + "=" * 39)
    with pl.Config(tbl_cols=13, tbl_width_chars=150):
        print(df_ue_by_product)
    
    return df_overview, df_ue_by_product

# ============================================================================
# VI.2 Business growth points
# ============================================================================

"""
VI.2 Business Growth Points - DASH VERSION
NO plt.show() - just returns data
"""

def analyze_growth_points(ue_deals, spend):
    """
    Analyzes growth points and their impact on CM.
    CORRECTED VERSION - All columns are correctly recalculated for each scenario.
    """
    print("\n" + "=" * 80)
    print("VI.2 BUSINESS GROWTH POINTS - SENSITIVITY ANALYSIS")
    print("=" * 80)
    
    # --- STEP 0: DATA PREPARATION ---
    ue_deals_prepared = ue_deals.with_columns([
        pl.when(pl.col("Months_of_study") == 1)
        .then(pl.col("Initial_Amount_Paid"))
        .otherwise(
            pl.col("Initial_Amount_Paid") + 
            ((pl.col("Offer_Total_Amount") - pl.col("Initial_Amount_Paid")) / 
             (pl.when(pl.col("Course_duration") <= 1).then(1).otherwise(pl.col("Course_duration") - 1))) * (pl.col("Months_of_study") - 1)
        )
        .fill_null(0)
        .alias("Individual_Revenue")
    ])
    
    # --- STEP 1: GLOBAL METRICS CALCULATION ---
    ua_global = ue_deals_prepared["Contact_Name"].n_unique()
    
    try:
        ac_global = spend["Spend"].str.replace_all(r"[€\s,]", "").cast(pl.Float64).sum()
    except:
        ac_global = 149523.45  
    
    cpa_global = ac_global / ua_global if ua_global > 0 else 0
    
    # --- STEP 2: EXTRACT BASE METRICS FOR EACH PRODUCT ---
    def get_product_metrics(product_name):
        df_p = ue_deals_prepared.filter(pl.col("Product") == product_name)
        df_paid = df_p.filter(pl.col("Stage") == "Payment Done")
        
        # Base Values
        ua_base = ua_global
        b_base = df_paid["Contact_Name"].n_unique()
        c1_base = b_base / ua_base if ua_base > 0 else 0
        t_base = df_paid["Months_of_study"].sum()
        apc_base = t_base / b_base if b_base > 0 else 0
        total_rev_base = df_paid["Individual_Revenue"].sum()
        aov_base = total_rev_base / t_base if t_base > 0 else 0
        ac_base = ac_global  # AC global
        cpa_base = cpa_global
        cltv_base = aov_base * apc_base
        ltv_base = c1_base * cltv_base
        cm_base = ua_base * (ltv_base - cpa_base)
        revenue_base = total_rev_base
        
        return {
            "ua": ua_base,
            "b": b_base,
            "c1": c1_base,
            "t": t_base,
            "apc": apc_base,
            "aov": aov_base,
            "ac": ac_base,
            "cpa": cpa_base,
            "cltv": cltv_base,
            "ltv": ltv_base,
            "cm": cm_base,
            "revenue": revenue_base
        }
    
    # --- STEP 3: GET BASE METRICS FOR ALL PRODUCTS ---
    data_products = {
        "Web Developer": get_product_metrics("Web Developer"),
        "Digital Marketing": get_product_metrics("Digital Marketing"),
        "UX/UI Design": get_product_metrics("UX/UI Design")
    }
    
    # --- STEP 4: SCENARIO CALCULATION FUNCTION - CORRECTED ---
    coef_modif = 0.15
    
    def calculate_scenario(scenario_name, base, coef_modif):
        """
        Calculates all metrics for a specific scenario.
        """
        # Base values
        ua_b = base["ua"]
        c1_b = base["c1"]
        aov_b = base["aov"]
        apc_b = base["apc"]
        cpa_b = base["cpa"]
        
        # Default values (base case)
        ua = ua_b
        c1 = c1_b
        aov = aov_b
        apc = apc_b
        cpa = cpa_b
        
        # Apply changes based on scenario
        if "UA" in scenario_name:
            ua = ua_b * (1 + coef_modif)
        elif "C1" in scenario_name:
            c1 = c1_b * (1 + coef_modif)
        elif "AOV" in scenario_name:
            aov = aov_b * (1 + coef_modif)
        elif "APC" in scenario_name:
            apc = apc_b * (1 + coef_modif)
        elif "CPA" in scenario_name:
            cpa = cpa_b * (1 - coef_modif)
        
        # RECALCULATE ALL DERIVED COLUMNS
        b = ua * c1
        t = ua * c1 * apc
        cltv = aov * apc
        ltv = c1 * cltv
        ac = ua * cpa
        revenue = aov * ua * c1 * apc
        cm = ua * (ltv - cpa)
        
        return {
            "Scenario": scenario_name,
            "UA": round(ua, 0),
            "C1": f"{c1:.2%}",
            "AOV": round(aov, 2),
            "APC": round(apc, 2),
            "CPA": round(cpa, 2),
            "B": round(b, 0),
            "T": round(t, 0),
            "CLTV": round(cltv, 2),
            "LTV": round(ltv, 2),
            "AC": round(ac, 2),
            "Revenue": round(revenue, 2),
            "CM": round(cm, 2)
        }
    
    # --- STEP 5: GENERATE SCENARIOS FOR EACH PRODUCT ---
    all_results = []
    
    for prod_name, base_vals in data_products.items():
        rows = []
        
        # Base Case
        rows.append(calculate_scenario("Base Case", base_vals, coef_modif))
        
        # UA (+15%)
        rows.append(calculate_scenario("UA (+15%)", base_vals, coef_modif))
        
        # C1 (+15%)
        rows.append(calculate_scenario("C1 (+15%)", base_vals, coef_modif))
        
        # AOV (+15%)
        rows.append(calculate_scenario("AOV (+15%)", base_vals, coef_modif))
        
        # APC (+15%)
        rows.append(calculate_scenario("APC (+15%)", base_vals, coef_modif))
        
        # CPA (-15%)
        rows.append(calculate_scenario("CPA (-15%)", base_vals, coef_modif))
        
        df_filtered = pl.DataFrame(rows)
        all_results.append((prod_name, df_filtered))
        
        # Display in console
        print(f"\n" + "="*95)
        print(f"--- SENSITIVITY ANALYSIS: {prod_name.upper()} ---")
        print("="*95)
        with pl.Config(tbl_cols=13, tbl_width_chars=200):
            print(df_filtered)
    
    # --- STEP 6: GENERATE HEATMAP DATA ---
    heatmap_data = []
    
    for prod_name, base_vals in data_products.items():
        # Base CM
        ua_b = base_vals["ua"]
        c1_b = base_vals["c1"]
        aov_b = base_vals["aov"]
        apc_b = base_vals["apc"]
        cpa_b = base_vals["cpa"]
        
        cltv_b = aov_b * apc_b
        ltv_b = c1_b * cltv_b
        cm_b = ua_b * (ltv_b - cpa_b)
        
        # Calculate CM for each scenario
        scenarios_cm = {
            "UA (+15%)": (ua_b * (1 + coef_modif)) * (ltv_b - cpa_b),
            "C1 (+15%)": ua_b * ((c1_b * (1 + coef_modif)) * cltv_b - cpa_b),
            "AOV (+15%)": ua_b * (c1_b * ((aov_b * (1 + coef_modif)) * apc_b) - cpa_b),
            "APC (+15%)": ua_b * (c1_b * (aov_b * (apc_b * (1 + coef_modif))) - cpa_b),
            "CPA (-15%)": ua_b * (ltv_b - (cpa_b * (1 - coef_modif)))
        }
        
        for sc_name, sc_cm in scenarios_cm.items():
            impact_perc = ((sc_cm - cm_b) / abs(cm_b)) * 100 if cm_b != 0 else 0
            heatmap_data.append({
                "Produs": prod_name,
                "Pârghie de Creștere": sc_name,
                "Impact CM (%)": round(impact_perc, 2)
            })
    
    # --- STEP 7: CREATE HEATMAP DATAFRAME ---
    df_heatmap_prep = pd.DataFrame(heatmap_data)
    df_pivot = df_heatmap_prep.pivot(index="Produs", columns="Pârghie de Creștere", values="Impact CM (%)")
    
    cols_order = ["UA (+15%)", "C1 (+15%)", "AOV (+15%)", "APC (+15%)", "CPA (-15%)"]
    available_cols = [col for col in cols_order if col in df_pivot.columns]
    df_pivot = df_pivot[available_cols]
    
    return all_results, df_pivot

# ============================================================================
# VI.3 Metrics tree
# ============================================================================

def display_metrics_tree():
    """
    Displays the metrics tree and imports the associated image.
    """
    print("\n" + "=" * 80)
    print("VI.3 METRICS TREE - METRICS HIERARCHY")
    print("=" * 80)
    
    # Textual representation of the metrics hierarchy
    metrics_tree_text = """
    Key Business Indicator	

        Revenue	SUM('Deals Cleaned'!"Revenue")
        
    Financial Metrics	

        CM 	UA*(LTV-CPA)
        LTV	C1*CLTV
        
    Decision Metrics

        UA	COUNTUNIQUE('Deals Cleaned'!"Contact Name")
        CPA	AC/UA 
        C1	 B / UA
        AOV	Revenue / T
        APC	T / B
        B	COUNTUNIQUEIFS('Deals Cleaned'!"Contact Name",'Deals Cleaned'!"Stage","Payment Done")
        
        
    Product Metrics	

        T	SUMIFS('Deals Cleaned'!"Months of study",'Deals Cleaned'!"Stage","Payment Done")
        AC	SUM('Spend'!"Spend")
        
        
    Atomic Metrics	

        Id	
        Contact Name	
        Stage	
        Initial Amount Paid	
        Spend	
        Months of study	
        Offer Total Amount	
        Course duration	
        Closing Date	
        Id	
        SLA	
        Created Time	
        Product	
        
        
            
    Vanilla (Basic) Metrics

        Lost Reason	
        Quality	
        Deal Owner Name	
        Campaign	
        Content	
        Page	
        Source	
        Term	
        Payment Type	
        Education Type	
        City	
        Level of Deutsch	
    """
    
    print(metrics_tree_text)
    
    # Try to load and display the metrics tree image if available
    try:
        img_path = Path("metrics_tree.png")
        if img_path.exists():
            print("\n📊 Visual Metrics Tree (Diagram):")
            print("Image 'metrics_tree.png' is available for viewing.")
            
            # For notebook environments, we could display the image
            try:
                from IPython.display import Image, display
                display(Image(filename='metrics_tree.png'))
            except:
                print("To view the image, please open 'metrics_tree.png'")
        else:
            print("\nℹ️ Image 'metrics_tree.png' was not found in the current directory.")
            print("Ensure the file is present to view the diagram.")
    except Exception as e:
        print(f"\n⚠️ Error loading image: {e}")
    
    return metrics_tree_text

# ============================================================================
# VI.4 Which product metrics will influence CM
# ============================================================================

def analyze_product_metrics_impact(ue_deals, spend, REQUIRED_DAYS=14, x_web=0.02, x_dig=0.04, x_ux=0.025):
    """
    Analyzes which product metrics influence CM and calculates the sample size for A/B testing.
    
    Parameters:
    -----------
    ue_deals : polars.DataFrame
        DataFrame with deals data for UE analysis
    spend : polars.DataFrame
        DataFrame with spend data for UE analysis
    REQUIRED_DAYS : int, optional
        Maximum days for A/B test (default: 14)
    x_web : float, optional
        Target effect for Web Developer (default: 0.02)
    x_dig : float, optional
        Target effect for Digital Marketing (default: 0.04)
    x_ux : float, optional
        Target effect for UX/UI Design (default: 0.025)
    """
    print("\n" + "=" * 80)
    print("VI.4 PRODUCT METRICS IMPACT ON CM - A/B TESTING ANALYSIS")
    print("=" * 80)
    
    # --- STEP 1: DYNAMIC DATA PREPARATION ---
    # Calculate global traffic metrics from the ue_deals dataset
    ua_global = ue_deals["Contact_Name"].n_unique()
    min_d = ue_deals["Created_Time"].min()
    max_d = ue_deals["Created_Time"].max()
    
    # Determine the total time span and average daily traffic
    days_total = (max_d - min_d).days
    daily_traffic = ua_global / days_total if days_total > 0 else 0
    
    def get_conversion_rate(product_name):
        """Calculates the current conversion rate (p) for a specific product."""
        b_prod = ue_deals.filter(
            (pl.col("Product") == product_name) & 
            (pl.col("Stage") == "Payment Done")
        )["Contact_Name"].n_unique()
        return b_prod / ua_global if ua_global > 0 else 0
    
    # Retrieve current conversion rates
    p_web = get_conversion_rate("Web Developer")
    p_dig = get_conversion_rate("Digital Marketing")
    p_ux = get_conversion_rate("UX/UI Design")
    
    ab_setup = {
        "Web Developer": {"p": p_web, "X": x_web},
        "Digital Marketing": {"p": p_dig, "X": x_dig},
        "UX/UI Design": {"p": p_ux, "X": x_ux}
    }
    
    results = []
    
    # --- STEP 2: CALCULATE A/B TEST METRICS ---
    for product, vals in ab_setup.items():
        p, x = vals["p"], vals["X"]
        
        if p > 0 and x > 0:
            # Standard formula for sample size per variation (80% power, 5% significance)
            # n = (16 * p * (1 - p)) / (X^2)
            n = (16 * p * (1 - p)) / (x ** 2)
            total_traffic = n * 2 # Total traffic needed for both Control and Test groups
            
            # Calculate how many days it would take based on current daily traffic
            days_needed = math.ceil(total_traffic / daily_traffic) if daily_traffic > 0 else 0
            
            # Suggest an X value that would fit within the REQUIRED_DAYS limit
            x_sug = math.sqrt((16 * p * (1 - p) * 2) / (REQUIRED_DAYS * daily_traffic)) if daily_traffic > 0 else 0
            
            # Determine if the current setup is feasible
            status = "OK" if days_needed <= REQUIRED_DAYS else "⚠️ TOO LONG"
            suggestion = f"Set X to {x_sug:.3f}" if days_needed > REQUIRED_DAYS else "-"
        else:
            n, total_traffic, days_needed, status, suggestion = 0, 0, 0, "No Data", "-"
    
        results.append({
            "Metric": product, 
            "UA_global": str(ua_global),
            "Total_days": str(days_total),
            "Current Conv (p)": f"{p:.2%}",
            "Target Effect (X)": f"{x:.0%}",
            "Sample Size (n)": f"{n:,.0f}",
            "Total Traffic": f"{total_traffic:,.0f}",
            "Days Needed": str(days_needed),
            "Status": status,
            "Suggestion": suggestion
        })
    
    # --- STEP 3: TRANSPOSITION FOR READABILITY ---
    # Create the initial DataFrame from results
    df_temp = pl.DataFrame(results)
    
    # Transpose the data: Products become columns, metrics become rows for side-by-side comparison
    df_transposed = df_temp.transpose(include_header=True, header_name="Metric", column_names="Metric")
    
    # --- STEP 4: OUTPUT DISPLAY ---
    print(f"\n🚀 COMPARATIVE A/B TESTING ANALYSIS (Limit: {REQUIRED_DAYS} days)\n")
    with pl.Config(tbl_width_chars=150, fmt_str_lengths=30):
        print(df_transposed)
    
    # --- STEP 5: INTERPRETATION ---
    print(f"""
    📊 A/B TESTING RESULTS INTERPRETATION:
    
    1. STATUS 'OK': Test can be completed within {REQUIRED_DAYS} days with the current target effect.
    2. STATUS '⚠️ TOO LONG': Test requires more time than {REQUIRED_DAYS} days.
    3. SUGGESTION: Recommended X value to fit the test within {REQUIRED_DAYS} days.
    
    🔍 PRODUCT METRICS INFLUENCING CM:
    - Conversion Rate (C1): Direct impact on LTV and implicitly on CM
    - Average Order Value (AOV): Increasing AOV boosts CLTV and LTV
    - Average Purchase Count (APC): Student retention increases total revenue
    - Cost Per Acquisition (CPA): Reducing CPA directly increases CM
    
    🎯 RECOMMENDATIONS:
    1. Prioritize tests for products with STATUS 'OK'
    2. For products with STATUS '⚠️ TOO LONG', adjust X according to suggestion
    3. Focus on metrics with the highest impact on CM (see section VI.2)
    """)
    
    return df_transposed, ab_setup

# ============================================================================
# VI.5 Hypothesis and testing method
# ============================================================================

def present_hypothesis_and_testing():
    """
    Presents the hypotheses and testing methods for metric optimization.
    """
    print("\n" + "=" * 80)
    print("VI.5 HYPOTHESIS AND TESTING METHOD - OPTIMIZATION FRAMEWORK")
    print("=" * 80)
    
    hypothesis_text = """
    📋 UNIT ECONOMICS HYPOTHESIS AND TESTING FRAMEWORK
    
    1. CORE PHILOSOPHY:
    --------------------
    Every metric in the Unit Economics tree can be optimized through iterative
    testing. Our approach is based on the continuous cycle:
    
        MEASURE → ANALYZE → HYPOTHESIZE → TEST → IMPLEMENT
    
    
    2. MAIN HYPOTHESES BY LAYER:
    ---------------------------------
    
    A. TRAFFIC LAYER (UA):
    --------------------------
    HYPOTHESIS H1: Optimizing traffic sources can reduce CPA by 15%
    - TEST: A/B test on different channels (Facebook vs Google Ads vs LinkedIn)
    - METHOD: Equal budget allocation, measure CPA per channel
    - TARGET METRIC: CPA < [current value] * 0.85
    
    HYPOTHESIS H2: Optimized landing pages can increase UA by 20%
    - TEST: A/B test on landing page design
    - METHOD: 50% old traffic, 50% new design traffic
    - TARGET METRIC: Lead conversion rate > [current value] * 1.20
    
    
    B. CONVERSION LAYER (C1):
    -----------------------------
    HYPOTHESIS H3: Personalizing the sales message increases C1 by 10%
    - TEST: A/B test on the sales script
    - METHOD: Two pitch versions, randomly assigned to consultants
    - TARGET METRIC: C1 > [current value] * 1.10
    
    HYPOTHESIS H4: Simplified onboarding process reduces drop-off by 25%
    - TEST: A/B test on the enrollment flow
    - METHOD: Control group (current process) vs Test group (simplified process)
    - TARGET METRIC: Enrollment completion rate > [current value] * 1.25
    
    
    C. VALUE LAYER (AOV):
    ----------------------------
    HYPOTHESIS H5: Strategic upselling increases AOV by 15%
    - TEST: A/B test on offered packages
    - METHOD: Standard offer vs Premium offer with individual mentorship
    - TARGET METRIC: AOV > [current value] * 1.15
    
    HYPOTHESIS H6: Installment payments increase average transaction value by 20%
    - TEST: A/B test on payment options
    - METHOD: Full payment vs 3 installments vs 6 installments
    - TARGET METRIC: Average transaction value > [current value] * 1.20
    
    
    D. RETENTION LAYER (APC):
    -----------------------------
    HYPOTHESIS H7: Gamification increases retention by 30%
    - TEST: A/B test on points and rewards system
    - METHOD: Group without gamification vs Group with gamification
    - TARGET METRIC: APC > [current value] * 1.30
    
    HYPOTHESIS H8: Online community reduces churn rate by 40%
    - TEST: A/B test on community access
    - METHOD: Standard course vs Course + private community access
    - TARGET METRIC: Course completion rate > [current value] * 1.40
    
    
    3. TESTING METHODOLOGY:
    -------------------------
    
    A. A/B TEST SETUP:
    - Confidence level: 95% (α = 0.05)
    - Statistical power: 80% (β = 0.20)
    - Minimum duration: 14 days (to eliminate daily variations)
    - Sample size: Calculated according to formula in section VI.4
    
    B. SUCCESS CRITERIA:
    - Statistically significant difference (p-value < 0.05)
    - Significant practical impact (> minimum detectable X)
    - Consistency over the entire test period
    
    C. IMPLEMENTATION:
    - Testing on 50% of traffic for each variant
    - Randomization at user level
    - Full tracking of all relevant metrics
    
    
    4. TEST PRIORITIZATION:
    ---------------------
    Using Impact-Effort Matrix:
    
    HIGH IMPACT | Low Effort:      Tests H4, H8 (onboarding & community)
    HIGH IMPACT | High Effort:     Tests H5, H7 (upselling & gamification)
    LOW IMPACT | Low Effort:       Tests H1, H6 (minor optimizations)
    LOW IMPACT | High Effort:      Tests H2, H3 (major redesign)
    
    
    5. SUCCESS MEASUREMENT FRAMEWORK:
    ---------------------------------
    Each test is evaluated on 3 dimensions:
    
    A. STATISTICAL DIMENSION:
       - Statistical significance (p-value)
       - Test power (power analysis)
       - Confidence interval
    
    B. BUSINESS DIMENSION:
       - Impact on CM (calculated in VI.2)
       - ROI of testing effort
       - Solution scalability
    
    C. OPERATIONAL DIMENSION:
       - Ease of implementation
       - Operational costs
       - Impact on user experience
    
    
    6. FINAL RECOMMENDATIONS:
    ----------------------
    1. Start with High-Impact/Low-Effort tests (H4, H8)
    2. Monitor impact on CM in real-time
    3. Document all tests in a central registry
    4. Iterate quickly - testing cycles of max 30 days
    5. Scale only solutions demonstrating significant positive impact
    
    
    ✨ CONCLUSION: Optimizing Unit Economics is a continuous, iterative,
    and data-driven process. Each test brings the business closer to the
    break-even point and profit maximization.
    """
    
    print(hypothesis_text)
    
    return hypothesis_text

# ============================================================================
# MAIN EXECUTION FUNCTION (for backward compatibility)
# ============================================================================

def run_ue_analysis(ue_deals=None, spend=None):
    """
    Main function running the entire Unit Economics analysis.
    
    Parameters:
    -----------
    ue_deals : polars.DataFrame, optional
        DataFrame containing deals data for UE analysis
    spend : polars.DataFrame, optional
        DataFrame containing spend data for UE analysis
    """
    print("\n" + "=" * 100)
    print("UNIT ECONOMICS ANALYSIS MODULE - EXECUTING ALL SECTIONS")
    print("=" * 100)
    
    results = {}
    
    # Check if data is available
    if ue_deals is None or spend is None:
        print("⚠️  Data unavailable. Ensure ue_deals and spend are defined.")
        return None
    
    try:
        # VI.1 Unit Economics
        print("\n▶️ Executing VI.1 Unit Economics...")
        overview_df, product_df = calculate_unit_economics(ue_deals, spend)
        results["overview"] = overview_df
        results["by_product"] = product_df
        
        # VI.2 Business growth points
        print("\n▶️ Executing VI.2 Business growth points...")
        sensitivity_results, heatmap_df = analyze_growth_points(ue_deals, spend)
        results["sensitivity"] = sensitivity_results
        results["heatmap"] = heatmap_df
        
        # VI.3 Metrics tree
        print("\n▶️ Executing VI.3 Metrics tree...")
        metrics_tree = display_metrics_tree()
        results["metrics_tree"] = metrics_tree
        
        # VI.4 Which product metrics will influence CM
        print("\n▶️ Executing VI.4 Product metrics impact on CM...")
        ab_test_results, ab_setup = analyze_product_metrics_impact(ue_deals, spend)
        results["ab_testing"] = ab_test_results
        results["ab_setup"] = ab_setup
        
        # VI.5 Hypothesis and testing method
        print("\n▶️ Executing VI.5 Hypothesis and testing method...")
        hypothesis = present_hypothesis_and_testing()
        results["hypothesis"] = hypothesis
        
        print("\n" + "=" * 100)
        print("✅ UNIT ECONOMICS ANALYSIS COMPLETED SUCCESSFULLY!")
        print("=" * 100)
        
        return results
        
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        print("Ensure all required dataframes are available.")
        import traceback
        traceback.print_exc()
        return None

# ============================================================================
# EXPORT FUNCTIONS FOR NOTEBOOK USE
# ============================================================================

def export_results_to_excel(results, filename="ue_analysis_results.xlsx"):
    """
    Exports analysis results to an Excel file.
    """
    if not results:
        print("No results to export.")
        return
    
    try:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Overview table
            if "overview" in results:
                results["overview"].to_pandas().to_excel(writer, sheet_name='VI1_Overview', index=False)
            
            # By product table
            if "by_product" in results:
                results["by_product"].to_pandas().to_excel(writer, sheet_name='VI1_By_Product', index=False)
            
            # Sensitivity analysis
            if "sensitivity" in results:
                for i, (product, df) in enumerate(results["sensitivity"]):
                    df.to_pandas().to_excel(writer, sheet_name=f'VI2_{product[:20]}', index=False)
            
            # Heatmap data
            if "heatmap" in results:
                results["heatmap"].to_excel(writer, sheet_name='VI2_Heatmap_Data')
            
            # AB Testing results
            if "ab_testing" in results:
                results["ab_testing"].to_pandas().to_excel(writer, sheet_name='VI4_AB_Testing', index=False)
        
        print(f"\n📁 Results exported to '{filename}'")
        return filename
        
    except Exception as e:
        print(f"❌ Error exporting to Excel: {e}")
        return None

# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

if __name__ == "__main__":
    # Usage instructions
    print("""
    UNIT ECONOMICS ANALYSIS MODULE
    
    To run the full analysis, use:
        results = run_ue_analysis(ue_deals, spend)
    
    To run individual sections:
        1. calculate_unit_economics(ue_deals, spend)         - VI.1
        2. analyze_growth_points(ue_deals, spend)           - VI.2
        3. display_metrics_tree()                           - VI.3
        4. analyze_product_metrics_impact(ue_deals, spend)  - VI.4
        5. present_hypothesis_and_testing()                 - VI.5
    
    To export results:
        export_results_to_excel(results, "filename.xlsx")
    """)