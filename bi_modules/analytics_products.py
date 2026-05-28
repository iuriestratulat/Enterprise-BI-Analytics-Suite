# analytics_products.py
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ============================================================================
# FINANCIAL CALCULATION UTILITY FUNCTIONS
# ============================================================================

def calculate_earned_revenue(df):
    """
    Calculates Earned Revenue according to the professor's formula.
    Formula: (Offer_Total_Amount / Course_duration) * Months_of_study
    """
    return df.with_columns([
        ((pl.col("Offer_Total_Amount") / pl.col("Course_duration")) * pl.col("Months_of_study").fill_null(0)).alias("Earned_Revenue")
    ])

def calculate_debts(df):
    """
    Calculates academy liabilities (refund risk) and student debts (uncollected revenue).
    """
    df_with_revenue = calculate_earned_revenue(df.filter(pl.col("Course_duration") > 0))
    
    # Academy Liabilities (refund risk)
    academy_liabilities = df_with_revenue.filter(
        ((pl.col("Initial_Amount_Paid") > 0) & (pl.col("Months_of_study") <= 0)) |
        ((pl.col("Months_of_study") > 0) & 
         (pl.col("Initial_Amount_Paid") > (pl.col("Offer_Total_Amount") / pl.col("Course_duration"))))
    ).with_columns([
        (pl.col("Initial_Amount_Paid") - pl.col("Earned_Revenue")).alias("Academy_Debt_Value")
    ]).filter(pl.col("Academy_Debt_Value") > 0)
    
    # Student Debts (uncollected revenue)
    student_debts = df_with_revenue.filter(
        (pl.col("Earned_Revenue") > pl.col("Initial_Amount_Paid"))
    ).with_columns([
        (pl.col("Earned_Revenue") - pl.col("Initial_Amount_Paid")).alias("Student_Debt_Value")
    ])
    
    return academy_liabilities, student_debts

# ============================================================================
# MAIN FUNCTIONS FOR EACH ANALYSIS
# ============================================================================

def get_product_revenue(df_deals):
    """
    Simplified analysis for Product Revenue Mix.
    """
    product_revenue = df_deals.filter(
        pl.col("Real_Earned_Revenue").is_not_null() & 
        (pl.col("Real_Earned_Revenue") > 0)
    ).group_by("Product").agg([
        pl.sum("Real_Earned_Revenue").alias("Total_Revenue"),
        pl.count().alias("Number_of_Sales"),
        pl.mean("Real_Earned_Revenue").alias("Average_Revenue_per_Sale")
    ]).sort("Total_Revenue", descending=True)
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Revenue Distribution by Product", "Number of Sales"),
        specs=[[{'type': 'pie'}, {'type': 'bar'}]]
    )
    
    fig.add_trace(
        go.Pie(
            labels=product_revenue["Product"].to_list(),
            values=product_revenue["Total_Revenue"].to_list(),
            hole=0.3,
            textinfo='label+percent',
            name="Revenue"
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=product_revenue["Product"].to_list(),
            y=product_revenue["Number_of_Sales"].to_list(),
            text=product_revenue["Number_of_Sales"].to_list(),
            textposition='auto',
            marker_color='lightblue',
            name="Sales"
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title_text="Product Revenue Mix",
        showlegend=True
    )
    
    conclusion = """
    This analysis shows the distribution of real earned revenue by product. The pie chart indicates 
    the percentage contribution of each product to total revenue, while the bar chart shows sales volume.
    """
    
    return fig, conclusion

def get_quality_distribution(df_deals):
    """
    Revenue quality distribution by product.
    """
    quality_data = df_deals.filter(
        pl.col("Quality_Score").is_not_null()
    ).group_by(["Product", "Quality_Score"]).agg([
        pl.count().alias("Count"),
        pl.mean("Real_Earned_Revenue").alias("Avg_Revenue")
    ])
    
    fig = px.bar(
        quality_data.to_pandas(),
        x="Product",
        y="Count",
        color="Quality_Score",
        title="Quality Distribution by Product",
        barmode="stack",
        labels={"Count": "Number of Deals", "Quality_Score": "Quality Category"},
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    conclusion = """
    Distribution of quality scores by product shows how deals are categorized based on quality.
    Products with higher scores indicate better revenue quality and customer retention.
    """
    
    return fig, conclusion

def get_revenue_by_payment_type(df_deals):
    """
    IV.1. Distribution of Real Earned Revenue by Payment Type
    """
    # Filter and calculate real revenue
    vi1_analysis = df_deals.filter(
        (pl.col("Payment_Type").is_not_null()) & 
        (pl.col("Course_duration") > 0)
    ).with_columns([
        ((pl.col("Offer_Total_Amount") / pl.col("Course_duration")) * pl.col("Months_of_study").fill_null(0)).alias("Earned_Revenue"),
        (pl.col("Initial_Amount_Paid") - ((pl.col("Offer_Total_Amount") / pl.col("Course_duration")) * pl.col("Months_of_study").fill_null(0))).alias("Financial_Gap")
    ])
    
    # Aggregate by payment type
    payment_stats = (
        vi1_analysis.group_by("Payment_Type")
        .agg([
            pl.len().alias("Total_Deals"),
            pl.col("Earned_Revenue").sum().alias("Total_Earned_Revenue"),
            pl.col("Financial_Gap").filter(pl.col("Financial_Gap") < 0).sum().alias("Total_Debt")
        ])
        .with_columns([
            (pl.col("Total_Debt").abs() / pl.col("Total_Earned_Revenue") * 100).alias("Debt_Risk_%")
        ])
        .sort("Total_Earned_Revenue", descending=True)
    )
    
    # Chart 1: Revenue Distribution (Donut)
    fig1 = px.pie(
        payment_stats.to_pandas(),
        values="Total_Earned_Revenue",
        names="Payment_Type",
        hole=0.5,
        title="IV.1 Distribution of Real Earned Revenue by Payment Type",
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    
    # Chart 2: Debt Risk (Bar Chart)
    fig2 = px.bar(
        payment_stats.to_pandas(),
        x="Payment_Type",
        y="Debt_Risk_%",
        color="Debt_Risk_%",
        title="IV.1 Financial Risk: Debt Ratio per Payment Method",
        labels={"Debt_Risk_%": "Debt as % of Revenue"},
        text_auto=".2f",
        template="plotly_white",
        color_continuous_scale="Reds"
    )
    
    # Combine charts
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Revenue Distribution by Payment Type", "Debt Risk by Payment Method"),
        specs=[[{'type': 'pie'}, {'type': 'bar'}]]
    )
    
    fig.add_trace(fig1.data[0], row=1, col=1)
    fig.add_trace(fig2.data[0], row=1, col=2)
    
    fig.update_layout(
        title_text="IV.1. Distribution of Real Earned Revenue by Payment Type",
            showlegend=True,
            height=550,  # Slightly increased height
            # Position the legend safely on the right side, vertically centered
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.1
            ),
            # Add bottom margin to give the axis labels room to breathe
            margin=dict(b=100)
    )
    
    conclusion = """
    This analysis shows the distribution of real revenue by payment type and the associated debt risk.
    Payment methods with a higher risk percentage indicate potential collection issues or refusals.
    """
    
    return fig, conclusion

def get_cash_velocity_micro_aging(df_deals):
    """
    IV.2 Cash Velocity: Micro-Aging & Real Revenue Quality
    """
    sales_cycle_micro = (
        df_deals.filter(
            (pl.col("Initial_Amount_Paid") > 0) & 
            (pl.col("Course_duration") > 0)
        )
        .with_columns([
            pl.col("Closing_Time").fill_null(pl.col("Created_Time")).alias("Fixed_Closing_Time")
        ])
        .with_columns([
            ((pl.col("Fixed_Closing_Time").cast(pl.Datetime) - 
              pl.col("Created_Time").cast(pl.Datetime)).dt.total_days()).alias("Days_to_Close"),
            ((pl.col("Offer_Total_Amount") / pl.col("Course_duration")) * pl.col("Months_of_study").fill_null(0)).alias("Earned_Revenue")
        ])
        .filter(pl.col("Days_to_Close") >= 0)
        .with_columns(
            pl.when(pl.col("Days_to_Close") == 0).then(pl.lit("Same Day"))
            .when(pl.col("Days_to_Close") == 1).then(pl.lit("1 Day"))
            .when(pl.col("Days_to_Close") <= 3).then(pl.lit("2-3 Days"))
            .when(pl.col("Days_to_Close") <= 7).then(pl.lit("4-7 Days"))
            .when(pl.col("Days_to_Close") <= 14).then(pl.lit("2 Weeks"))
            .otherwise(pl.lit("> 2 Weeks"))
            .alias("Micro_Cycle")
        )
    )
    
    micro_summary = (
        sales_cycle_micro.group_by("Micro_Cycle")
        .agg([
            pl.len().alias("Number_of_Deals"),
            pl.col("Earned_Revenue").sum().alias("Total_Real_Revenue")
        ])
        .with_columns(
            pl.col("Micro_Cycle").replace({
                "Same Day": 1, "1 Day": 2, "2-3 Days": 3, 
                "4-7 Days": 4, "2 Weeks": 5, "> 2 Weeks": 6
            }).cast(pl.Int8).alias("Sort_Order")
        )
        .sort("Sort_Order")
    )
    
    fig = px.bar(
        micro_summary.to_pandas(),
        x="Micro_Cycle",
        y="Number_of_Deals",
        color="Total_Real_Revenue",
        text="Number_of_Deals",
        title="IV.2 Cash Velocity: Micro-Aging & Real Revenue Quality",
        labels={
            "Number_of_Deals": "Deals Closed", 
            "Total_Real_Revenue": "Real Earned Revenue (€)"
        },
        template="plotly_white",
        color_continuous_scale="Viridis",
        width=1100,
        height=500
    )
    
    fig.update_traces(
        textposition='outside', 
        textfont_size=14,
        cliponaxis=False
    )
    
    fig.update_layout(
        title_font_size=22,
        xaxis_title="Time from Lead Creation to Close",
        yaxis_title="Volume of Deals",
        yaxis=dict(range=[0, micro_summary["Number_of_Deals"].max() * 1.2]),
        coloraxis_colorbar=dict(title="Real Revenue (€)", yanchor="top", y=1, x=1.05)
    )
    
    conclusion = """
    Cash Velocity analysis shows how quickly deals close and what real revenue is generated 
    in each time category. Faster closing speed is usually associated with safer revenue 
    and lower risk.
    """
    
    return fig, conclusion

def get_avg_real_value_per_student(df_deals):
    """
    IV.3 Average Real Value per Student: Evening vs. Morning
    """
    real_value_analysis = (
        df_deals.filter(
            (pl.col("Initial_Amount_Paid") > 0) & 
            (pl.col("Education_Type").is_not_null()) &
            (pl.col("Payment_Type") != "Reservation") &
            (pl.col("Course_duration") > 0)
        )
        .with_columns([
            ((pl.col("Offer_Total_Amount") / pl.col("Course_duration")) * pl.col("Months_of_study").fill_null(0)).alias("Real_Value")
        ])
        .group_by(["Education_Type", "Payment_Type"])
        .agg([
            pl.len().alias("Number_of_Payments"),
            pl.col("Real_Value").mean().round(2).alias("Avg_Real_Value"),
            pl.col("Real_Value").sum().alias("Total_Earned_Revenue")
        ])
    )
    
    fig = px.scatter(
        real_value_analysis.to_pandas(),
        x="Payment_Type",
        y="Avg_Real_Value",
        size="Total_Earned_Revenue",
        color="Education_Type",
        hover_name="Education_Type",
        title="IV.3 Average Real Value per Student: Evening vs. Morning",
        labels={
            "Avg_Real_Value": "Average Real Value per Student (€)",
            "Payment_Type": "Payment Method",
            "Total_Earned_Revenue": "Total Real Revenue (€)"
        },
        template="plotly_white",
        size_max=150,
        width=1000,
        height=500
    )
    
    fig.update_layout(
        title_font_size=22,
            xaxis=dict(title="Payment Method", tickangle=30),
            yaxis_title="Avg Real Value Realized (€)",
            height=550,  # Increased height slightly for better bubble spacing
            # Move legend from the bottom to the right side to mirror Dash layout
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02,
                bgcolor="rgba(255, 255, 255, 0.5)",
                bordercolor="Black",
                borderwidth=1
            ),
            # Add proper margins so rotated text doesn't clip
            margin=dict(t=100, b=120, l=70, r=150)
    )
    
    conclusion = """
    This analysis compares the average real value per student between morning and evening groups.
    Bubble size represents total generated revenue. Differences between payment methods 
    may indicate student preferences or different pricing strategies.
    """
    
    return fig, conclusion

def get_financial_risks_by_schedule(df_deals):
    """
    IV.4 Potential financial risks by Schedule
    """
    df_debts = df_deals.filter(pl.col("Course_duration") > 0).with_columns([
        ((pl.col("Offer_Total_Amount") / pl.col("Course_duration")) * pl.col("Months_of_study").fill_null(0)).alias("Earned_Revenue")
    ])
    
    # 1. Calculate Academy Liabilities
    academy_liabilities = df_debts.filter(
        ((pl.col("Initial_Amount_Paid") > 0) & (pl.col("Months_of_study") <= 0)) |
        ((pl.col("Months_of_study") > 0) & 
         (pl.col("Initial_Amount_Paid") > (pl.col("Offer_Total_Amount") / pl.col("Course_duration"))))
    ).with_columns([
        (pl.col("Initial_Amount_Paid") - pl.col("Earned_Revenue")).alias("Academy_Debt_Value")
    ]).filter(pl.col("Academy_Debt_Value") > 0)
    
    # 2. Calculate Student Debt
    student_debts = df_debts.filter(
        (pl.col("Earned_Revenue") > pl.col("Initial_Amount_Paid"))
    ).with_columns([
        (pl.col("Earned_Revenue") - pl.col("Initial_Amount_Paid")).alias("Student_Debt_Value")
    ])
    
    # Define colors for Education Type
    education_color_map = {
        "Morning": "#FF9F43",  # Warm Orange
        "Evening": "#48CAE4"   # Light Blue
    }
    
    # Create subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Academy Liability: Refund Risk by Education Type", 
                       "Student Debt: Uncollected Revenue by Education Type"),
        specs=[[{'type': 'box'}, {'type': 'box'}]]
    )
    
    # Chart 1: Academy Liability
    if len(academy_liabilities) > 0:
        for edu_type in academy_liabilities["Education_Type"].unique().to_list():
            subset = academy_liabilities.filter(pl.col("Education_Type") == edu_type)
            fig.add_trace(
                go.Box(
                    y=subset["Academy_Debt_Value"].to_list(),
                    name=edu_type,
                    marker_color=education_color_map.get(edu_type, "#000000"),
                    boxpoints='all',
                    jitter=0.3,
                    pointpos=-1.8
                ),
                row=1, col=1
            )
    
    # Chart 2: Student Debt
    if len(student_debts) > 0:
        for edu_type in student_debts["Education_Type"].unique().to_list():
            subset = student_debts.filter(pl.col("Education_Type") == edu_type)
            fig.add_trace(
                go.Box(
                    y=subset["Student_Debt_Value"].to_list(),
                    name=edu_type,
                    marker_color=education_color_map.get(edu_type, "#000000"),
                    boxpoints='all',
                    jitter=0.3,
                    pointpos=-1.8,
                    showlegend=False
                ),
                row=1, col=2
            )
    
    fig.update_layout(
        title_text="IV.4 Potential Financial Risks by Schedule",
        showlegend=True,
        height=500,
        boxmode='group'
    )
    
    fig.update_yaxes(title_text="Refund Amount (€)", row=1, col=1)
    fig.update_yaxes(title_text="Debt Amount (€)", row=1, col=2)
    
    # Calculate summaries
    total_academy_debt = academy_liabilities["Academy_Debt_Value"].sum()
    total_student_debt = student_debts["Student_Debt_Value"].sum()
    
    conclusion = f"""
    Analysis of financial risks by schedule shows the distribution of academy liabilities and student debts.
    
    **Executive Liquidity & Operational Risk Assessment by Schedule Profile:**

    * **Deferred Liabilities & Refund Risk Exposure by Schedule (Left Chart):** This matrix isolates structural anomalies where the academy holds unearned revenue obligations or deferred liabilities across different educational shifts (Morning vs. Evening). It tracks student accounts where advanced tuition fees or down-payments were processed, but the realized curriculum delivery does not yet match the cash input. Higher financial density in specific schedule cohorts calls for strict liquidity matching and ring-fenced cash reserves, as these unearned capital pools are subject to clawbacks or immediate reimbursement requests upon sudden student withdrawal.

    * **Accounts Receivable Distribution & Schedule-Driven Bad Debt (Right Chart):** This visualization models the structural concentration of uncollected capital from students who consumed active educational modules ahead of their actual invoice clearance cycles, categorized by their schedule preference. Outliers and high values within specific schedule brackets indicate systematic collection friction, highlighting segments where payment discipline is weak or payment tracking is lagging. Executive intervention requires immediate schedule-specific dunning automation, tighter enforcement of financial compliance, and automated platform lockouts for persistent debtors to stop ongoing operational capital leakage.
    """
    
    return fig, conclusion

def get_main_product_performance(df_deals):
    """
    IV.5 Main Product Performance
    """
    df_analysis = df_deals.filter(pl.col("Course_duration") > 0).with_columns([
        ((pl.col("Offer_Total_Amount") / pl.col("Course_duration")) * pl.col("Months_of_study").fill_null(0)).alias("Earned_Revenue")
    ])
    
    product_revenue = (
        df_analysis.group_by("Product")
        .agg(pl.col("Earned_Revenue").sum().alias("Total_Earned_Revenue"))
        .sort("Total_Earned_Revenue", descending=True)
    )
    
    fig = px.bar(
        product_revenue.to_pandas(),
        x="Product",
        y="Total_Earned_Revenue",
        title="IV.5 Main Product Performance (Real Earned Revenue)",
        labels={"Total_Earned_Revenue": "Net Revenue (€)"},
        template="plotly_white",
        color_discrete_sequence=['#2ecc71'],
        text_auto='.2s'
    )
    
    fig.update_layout(
        xaxis_tickangle=45,
        height=500
    )
    
    conclusion = """
    Performance of main products based on Real Earned Revenue.
    This metric reflects revenue proportional to study months completed, offering a more 
    accurate view of each product's contribution to actual cash flow.
    """
    
    return fig, conclusion

def get_financial_risks_by_product(df_deals):
    """
    IV.6 Potential financial risks by product
    """
    academy_liabilities, student_debts = calculate_debts(df_deals)
    
    # Extract unique products and create color palette
    unique_products = df_deals["Product"].unique().to_list()
    colors = px.colors.qualitative.Prism
    product_color_map = {product: colors[i % len(colors)] for i, product in enumerate(unique_products)}
    
    # Create subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Academy Liability Analysis (Refund Risk)", 
                       "Student Debt Analysis (Uncollected Revenue)"),
        specs=[[{'type': 'histogram'}, {'type': 'histogram'}]]
    )
    
    # Chart 1: Academy Debt
    if len(academy_liabilities) > 0:
        for product in academy_liabilities["Product"].unique().to_list():
            subset = academy_liabilities.filter(pl.col("Product") == product)
            fig.add_trace(
                go.Histogram(
                    x=subset["Academy_Debt_Value"].to_list(),
                    name=product,
                    marker_color=product_color_map.get(product, "#000000"),
                    opacity=0.7,
                    nbinsx=20
                ),
                row=1, col=1
            )
    
    # Chart 2: Student Debt
    if len(student_debts) > 0:
        for product in student_debts["Product"].unique().to_list():
            subset = student_debts.filter(pl.col("Product") == product)
            fig.add_trace(
                go.Histogram(
                    x=subset["Student_Debt_Value"].to_list(),
                    name=product,
                    marker_color=product_color_map.get(product, "#000000"),
                    opacity=0.7,
                    nbinsx=20,
                    showlegend=False
                ),
                row=1, col=2
            )
    
    fig.update_layout(
        title_text="IV.6 Potential Financial Risks by Product",
        barmode='overlay',
        showlegend=True,
        height=500,
        bargap=0.1
    )
    
    fig.update_xaxes(title_text="Refund amount to student (€)", row=1, col=1)
    fig.update_xaxes(title_text="Student debt to academy (€)", row=1, col=2)
    fig.update_yaxes(title_text="Count", row=1, col=1)
    fig.update_yaxes(title_text="Count", row=1, col=2)
    
    # Calculate summaries
    total_academy_debt = academy_liabilities["Academy_Debt_Value"].sum()
    total_student_debt = student_debts["Student_Debt_Value"].sum()
    
    conclusion = f"""
    Analysis of financial risks by product.
    
    Academy Liabilities (left): Situations where the academy "owes" the student - 
    initial payment exceeds the value of study months completed.
    
    Student Debts (right): Situations where students have completed more modules than they paid for.
    
    Totals:
    - Academy Liabilities: {total_academy_debt:.2f} €
    - Student Debts: {total_student_debt:.2f} €
    """
    
    return fig, conclusion

def get_product_performance_by_schedule(df_deals):
    """
    IV.7 Real Revenue: Product Performance by Schedule
    """
    df_analysis = df_deals.filter(
        (pl.col("Course_duration") > 0) & 
        (pl.col("Education_Type").is_not_null())
    ).with_columns([
        ((pl.col("Offer_Total_Amount") / pl.col("Course_duration")) * pl.col("Months_of_study").fill_null(0)).alias("Earned_Revenue")
    ])
    
    product_edu_revenue = (
        df_analysis.group_by(["Product", "Education_Type"])
        .agg(pl.col("Earned_Revenue").sum().alias("Total_Earned_Revenue"))
        .sort("Total_Earned_Revenue", descending=True)
    )
    
    fig = px.bar(
        product_edu_revenue.to_pandas(),
        x="Product",
        y="Total_Earned_Revenue",
        color="Education_Type",
        title="IV.7 Real Revenue: Product Performance by Schedule",
        barmode="group",
        template="plotly_white",
        color_discrete_map={"Morning": "#2ecc71", "Evening": "#3498db"},
        text_auto='.2s'
    )
    
    fig.update_layout(
        xaxis_tickangle=45,
        height=500
    )
    
    conclusion = """
    Product performance by schedule type (morning vs. evening).
    This analysis helps identify products that perform better in specific time slots,
    aiding in the optimization of offerings and educational resources.
    """
    
    return fig, conclusion

def get_financial_risks_by_payment_method(df_deals):
    """
    IV.8 Potential financial risks by payment method
    """
    academy_liabilities, student_debts = calculate_debts(df_deals)
    
    # Colors for payment types
    unique_payments = df_deals["Payment_Type"].unique().to_list()
    pay_palette = px.colors.qualitative.Vivid
    payment_color_map = {pt: pay_palette[i % len(pay_palette)] for i, pt in enumerate(unique_payments)}
    
    # Filter for critical refunds (>= 1500€)
    major_refunds_pay = academy_liabilities.filter(pl.col("Academy_Debt_Value") >= 1500)
    
    # Create subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("High-Risk Refunds by Payment Type (>= 1500€)", 
                       "Student Debt Distribution by Payment Type"),
        specs=[[{'type': 'histogram'}, {'type': 'histogram'}]]
    )
    
    # Chart 1: High-risk refunds
    if len(major_refunds_pay) > 0:
        for payment_type in major_refunds_pay["Payment_Type"].unique().to_list():
            subset = major_refunds_pay.filter(pl.col("Payment_Type") == payment_type)
            fig.add_trace(
                go.Histogram(
                    x=subset["Academy_Debt_Value"].to_list(),
                    name=payment_type,
                    marker_color=payment_color_map.get(payment_type, "#000000"),
                    opacity=0.7,
                    nbinsx=15
                ),
                row=1, col=1
            )
    
    # Chart 2: Student debt distribution
    if len(student_debts) > 0:
        for payment_type in student_debts["Payment_Type"].unique().to_list():
            subset = student_debts.filter(pl.col("Payment_Type") == payment_type)
            fig.add_trace(
                go.Histogram(
                    x=subset["Student_Debt_Value"].to_list(),
                    name=payment_type,
                    marker_color=payment_color_map.get(payment_type, "#000000"),
                    opacity=0.7,
                    nbinsx=20,
                    showlegend=False
                ),
                row=1, col=2
            )
    
    fig.update_layout(
        title_text="IV.8 Potential Financial Risks by Payment Method",
        barmode='overlay',
        showlegend=True,
        height=500,
        bargap=0.1
    )
    
    fig.update_xaxes(title_text="Refund Risk Amount (€)", row=1, col=1)
    fig.update_xaxes(title_text="Student Debt Amount (€)", row=1, col=2)
    fig.update_yaxes(title_text="Count", row=1, col=1)
    fig.update_yaxes(title_text="Count", row=1, col=2)
    
    # Calculate financial summary
    df_debts = calculate_earned_revenue(df_deals.filter(pl.col("Course_duration") > 0))
    pay_summary = (
        df_debts.group_by("Payment_Type")
        .agg([
            pl.col("Earned_Revenue").sum().alias("Total_Earned"),
            pl.col("Initial_Amount_Paid").sum().alias("Total_Collected")
        ])
        .with_columns([
            (pl.col("Total_Collected") - pl.col("Total_Earned")).alias("Net_Financial_Position")
        ])
        .sort("Net_Financial_Position", descending=False)
    )
       
        # English comment: Update the static placeholders with advanced corporate finance risks metrics and liquidity exposures descriptions
    conclusion = """
    📈 **Executive Liquidity & Counterparty Risk Assessment:**

    * **Deferred Liabilities & Refund Risk Exposure (Left Chart):** This matrix isolates structural anomalies where the academy holds unearned revenue obligations or essentially "owes" the active customer pipeline. It tracks high-risk accounts where premium upfront down-payments ($\geq 1500€$) were processed but the curriculum was not commenced, alongside cohorts whose advanced prepayments exceed the value of delivered study modules. These capital assets represent operating deferred liabilities rather than recognized net margin; sustained growth in this cluster requires conservative cash reserves to absorb reimbursement claims during contract liquidations.

    * **Student Accounts Receivable & Capital Leakage (Right Chart):** This visualization models bad debt distribution from student pools who actively consumed educational modules without establishing valid invoice clearances. This structural imbalance represents immediate uncollected capital leakage and operational loss. High volume across these bands signals an urgent operational mandate to reinforce counterparty payment discipline, optimize the collection workflow, and enforce platform access suspensions for chronic debtors.
    """
    
    return fig, conclusion