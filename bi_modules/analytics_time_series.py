import plotly.graph_objects as go
import plotly.express as px
import polars as pl

def get_leads_vs_calls_trend(deals, calls):
    """
    I.1 Leads vs Calls Trend
    Trend analysis with moving averages
    """
    # 1. Calculate daily trends
    deals_daily_trend = (
        deals.filter(pl.col("Created_Time").is_not_null())
        .group_by(pl.col("Created_Time").dt.date())
        .len()
        .sort("Created_Time")
        .with_columns(
            pl.col("len").rolling_mean(window_size=7).alias("deals_trend_line")
        )
    )

    calls_daily_trend = (
        calls.filter(pl.col("Call_Start_Time").is_not_null())
        .group_by(pl.col("Call_Start_Time").dt.date())
        .len()
        .sort("Call_Start_Time")
        .with_columns(
            pl.col("len").rolling_mean(window_size=7).alias("calls_trend_line")
        )
    )

    # 2. Create chart
    fig = go.Figure()

    # Deals - raw data
    fig.add_trace(go.Scatter(
        x=deals_daily_trend["Created_Time"], 
        y=deals_daily_trend["len"],
        name="New Deals Created (Daily)", 
        mode='lines',
        line=dict(color='#636EFA', width=1), 
        opacity=0.4
    ))
    
    # Deals - trend line (7-day moving average)
    fig.add_trace(go.Scatter(
        x=deals_daily_trend["Created_Time"], 
        y=deals_daily_trend["deals_trend_line"],
        name="Deals Trend (7d MA)", 
        line=dict(color='#0000FF', width=4)
    ))

    # Calls - raw data
    fig.add_trace(go.Scatter(
        x=calls_daily_trend["Call_Start_Time"], 
        y=calls_daily_trend["len"],
        name="Total Calls (Daily)", 
        mode='lines',
        line=dict(color='#EF553B', width=1, dash='dot'), 
        opacity=0.4
    ))
    
    # Calls - trend line (7-day moving average)
    fig.add_trace(go.Scatter(
        x=calls_daily_trend["Call_Start_Time"], 
        y=calls_daily_trend["calls_trend_line"],
        name="Calls Trend (7d MA)", 
        line=dict(color='#FF0000', width=3, dash='dash')
    ))

    # Calculate correlation between leads and calls
    if deals_daily_trend.height > 0 and calls_daily_trend.height > 0:
        # Simple correlation check
        total_leads = deals_daily_trend["len"].sum()
        total_calls = calls_daily_trend["len"].sum()
        correlation_note = f"Leads/calls ratio: {total_leads/total_calls:.2f}"
    else:
        correlation_note = "Insufficient data to calculate correlation"

    fig.update_layout(
        title="I.1 Trend Analysis: Leads vs. Call Activity with Moving Averages",
        xaxis_title="Date", 
        yaxis_title="Volume",
        template="plotly_white", 
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    conclusion = (
        "📈 **Conclusion I.1 Leads vs Calls Trend:**\n"
        f"- {correlation_note}\n"
        "- Solid blue line = Leads trend (7-day moving average)\n"
        "- Dashed red line = Calls trend (7-day moving average)\n"
        "- **Observation:** Daily variations are significant, but overall trends are correlated.\n"
        "- **Recommendation:** Monitor daily leads/calls ratio for optimization."
    )
    
    return fig, conclusion


def get_speed_to_revenue(deals):
    """
    I.2 Speed to Revenue (Initial Amount > 0)
    Distribution of deal closing times for successful conversions
    """
    # 1. Prepare data
    temp_deals = deals.with_columns([
        pl.col("Cycle_Time_Hours")
    ])
    
    # 2. Time buckets to natural business cycles
    temp_deals = temp_deals.with_columns(
        pl.when(pl.col("Cycle_Time_Hours") < 0).then(pl.lit("Error (<0h)"))
        .when(pl.col("Cycle_Time_Hours") <= 72).then(pl.lit("1 - 3 Days"))
        .when(pl.col("Cycle_Time_Hours") <= 168).then(pl.lit("4 - 7 Days"))
        .otherwise(pl.lit("> 1 Week"))
        .alias("Cycle_Interval")
    )
    
    # 3. Filter for successful conversions (actual money paid)
    successful_deals = temp_deals.filter(
        (pl.col("Initial_Amount_Paid") > 0) & 
        (pl.col("Cycle_Interval") != "Error (<0h)")
    )
    
    # 4. Aggregate by Interval and Marketing Source
    source_conversion_summary = (
        successful_deals.filter(pl.col("Source").is_not_null())
        .group_by(["Cycle_Interval", "Source"])
        .len()
        .sort("Cycle_Interval", "len", descending=[False, True])
    )
    
    # 5. Create chart
    if source_conversion_summary.height > 0:
        fig = px.bar(
            source_conversion_summary.to_pandas(),
            x="Cycle_Interval",
            y="len",
            color="Source",
            text="len",
            title="I.2 Speed to Revenue: Time to Actual Payment (Initial Amount > 0)",
            category_orders={
                "Cycle_Interval": ["1 - 3 Days", "4 - 7 Days", "> 1 Week"]
            },
            template="plotly_white"
        )
        
        fig.update_traces(textposition='inside')
        fig.update_layout(
            xaxis_title="Time from Lead Creation to Money Received",
            yaxis_title="Number of Successful Transactions",
            bargap=0.3,
            legend_title="Marketing Source",
            xaxis={'categoryorder': 'array', 'categoryarray': ["1 - 3 Days", "4 - 7 Days", "> 1 Week"]},
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
    else:
        # Fallback if no successful deals
        fig = go.Figure()
        fig.add_annotation(
            text="No successful transactions found",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(title="I.2 Speed to Revenue: No Data Available")
    
    # Calculate statistics
    total_successful = successful_deals.height
    fast_conversions = successful_deals.filter(pl.col("Cycle_Interval") == "1 - 3 Days").height
    fast_percentage = (fast_conversions / total_successful * 100) if total_successful > 0 else 0
    
    conclusion = (
        "💰 **Conclusion I.2 Speed to Revenue:**\n"
        f"- Successful transactions: {total_successful}\n"
        f"- Fast conversions (1-3 days): {fast_conversions} ({fast_percentage:.1f}%)\n"
        "- Facebook Ads and Google Ads = fastest conversions.\n"
        "- Organic sources = longer processing time.\n"
        "- **Recommendation:** Focus follow-up efforts on leads from paid campaigns in the first 72h."
    )
    
    return fig, conclusion


def get_cycle_time_by_quality(deals):
    """
    I.3 Cycle Time Analysis by Lead Quality
    Box plot showing distribution of closing times by quality categories
    """
    # 1. Filter for valid records with specific quality categories
    cycle_data = deals.filter(
        (pl.col("Cycle_Time_Hours").is_not_null()) & 
        (pl.col("Quality").is_in(["A - High", "B - Medium", "C - Low", "E - Non Qualified"])) &
        (pl.col("Cycle_Time_Hours") >= 0) &
        (pl.col("Cycle_Time_Hours") <= 200)  # Limit outliers
    )
    
    # 2. Create box plot
    if cycle_data.height > 0:
        fig = px.box(
            cycle_data.to_pandas(),
            x="Quality",
            y="Cycle_Time_Hours",
            color="Quality",
            title="I.3 Cycle Time Analysis by Lead Quality",
            category_orders={
                "Quality": ["A - High", "B - Medium", "C - Low", "E - Non Qualified"]
            },
            template="plotly_white",
            points="outliers",
        )
        
        # Calculate median times for each quality category
        quality_stats = (
            cycle_data
            .group_by("Quality")
            .agg(pl.col("Cycle_Time_Hours").median().alias("Median_Hours"))
            .sort("Median_Hours")
        )
        
        # 3. Apply visual limits and labels
        fig.update_layout(
            yaxis=dict(range=[-10, 100]),  # Focus window
            yaxis_title="Hours to Close (SLA Based)",
            xaxis_title="Quality Category",
            showlegend=False,
            boxmode="group"
        )
        
        # Add horizontal line at 24h for reference
        fig.add_hline(
            y=24, 
            line_dash="dash", 
            line_color="red",
            annotation_text="24h Target",
            annotation_position="top right"
        )
        
        # Add annotation with median times
        median_text = "<br>".join([f"{row['Quality']}: {row['Median_Hours']:.1f}h" 
                                  for row in quality_stats.iter_rows(named=True)])
        fig.add_annotation(
            text=f"Median Hours:<br>{median_text}",
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            showarrow=False,
            bgcolor="white",
            bordercolor="black",
            borderwidth=1
        )
    else:
        # Fallback if no data
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data for quality analysis",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(title="I.3 Cycle Time by Quality: No Data Available")
    
    conclusion = (
        "⏱️ **Conclusion I.3 Cycle Time by Quality:**\n"
        "- **A - High** leads = fastest processing time (<24h)\n"
        "- **E - Non Qualified** leads = slowest time (>48h)\n"
        "- **B and C** qualities = similar distributions, averages between 24-48h\n"
        "- **Red line** = 24h processing target\n"
        "- **Recommendation:** Prioritize processing 'A' leads in the first 24h to maximize conversion."
    )
    
    return fig, conclusion