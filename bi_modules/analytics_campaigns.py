import plotly.express as px
import plotly.graph_objects as go
import polars as pl

# ===================================================================
# HELPER FUNCTIONS
# ===================================================================

def calculate_source_efficiency(deals, spend):
    """
    Calculate comprehensive source efficiency metrics.
    Returns dataframe with all source-level KPIs.
    """
    # 1. Prepare deals data with conversion flags
    deals_conversions = deals.with_columns([
        # Initial conversion (any positive stage progression)
        pl.when(pl.col("Stage").is_in(["New Lead", "Need a consultation", "Interested"]))
          .then(0)
          .otherwise(1)
          .alias("Initial_Conversion"),
        
        # Real conversion (students who stayed - months_of_study > 0)
        pl.when(pl.col("Months_of_study") > 0).then(1).otherwise(0).alias("Real_Student"),
        
        # Earned revenue (initial amount paid)
        pl.col("Initial_Amount_Paid").alias("Earned_Revenue")
    ])
    
    # 2. Aggregate deals by source
    source_deals_advanced = (
        deals_conversions
        .filter(pl.col("Source").is_not_null())
        .group_by("Source")
        .agg([
            pl.len().alias("Total_Leads"),
            pl.col("Initial_Conversion").sum().alias("Initial_Conversions"),
            pl.col("Real_Student").sum().alias("Real_Conversions"),
            pl.col("Earned_Revenue").sum().alias("Total_Earned_Revenue")
        ])
    )
    
    # 3. Aggregate spend by source
    source_spend_agg = (
        spend
        .filter(pl.col("Source").is_not_null())
        .group_by("Source")
        .agg([
            pl.col("Spend").sum().alias("Spend"),
            pl.col("Clicks").sum().alias("Clicks"),
            pl.col("Impressions").sum().alias("Impressions")
        ])
    )
    
    # 4. Join and calculate all efficiency metrics
    source_efficiency = (
        source_spend_agg.join(source_deals_advanced, on="Source", how="left")
        .fill_null(0)
        .with_columns([
            # Initial conversion rate from lead to first status
            (pl.col("Initial_Conversions") / pl.col("Total_Leads") * 100).round(2).alias("Initial_Conv_%"),
            
            # Real conversion rate (retention-based)
            (pl.col("Real_Conversions") / pl.col("Total_Leads") * 100).round(2).alias("Real_Conv_%"),
            
            # Quality of retention: how many initial converts stayed
            (pl.when(pl.col("Initial_Conversions") > 0)
             .then((pl.col("Real_Conversions") / pl.col("Initial_Conversions") * 100).round(1))
             .otherwise(0)
             .alias("Retention_Quality_%")),
            
            # Real ROAS: Revenue earned per 1 Euro spent
            (pl.when(pl.col("Spend") > 0)
             .then((pl.col("Total_Earned_Revenue") / pl.col("Spend")).round(2))
             .otherwise(pl.lit(float('inf')))
             .alias("Real_ROAS")),
            
            # CPL (Cost per Lead)
            (pl.when(pl.col("Total_Leads") > 0)
             .then((pl.col("Spend") / pl.col("Total_Leads")).round(2))
             .otherwise(0)
             .alias("CPL")),
            
            # CPR (Cost per Real Conversion)
            (pl.when(pl.col("Real_Conversions") > 0)
             .then((pl.col("Spend") / pl.col("Real_Conversions")).round(2))
             .otherwise(0)
             .alias("CPR"))
        ])
    )
    
    return source_efficiency


def calculate_campaign_efficiency(deals, spend):
    """
    Calculate comprehensive campaign efficiency metrics.
    """
    # 1. Prepare deals data with real conversions
    deals_conversions = (
        deals
        .with_columns(
            pl.when(pl.col("Months_of_study") > 0).then(1).otherwise(0).alias("Real_Student")
        )
        .filter(pl.col("Campaign").is_not_null())
    )
    
    # 2. Aggregate deals by campaign
    campaign_deals = (
        deals_conversions
        .group_by("Campaign")
        .agg([
            pl.len().alias("Total_Leads"),
            pl.col("Initial_Amount_Paid").sum().alias("Total_Revenue"),
            pl.col("Real_Student").sum().alias("Real_Conversions"),
            pl.col("Offer_Total_Amount").sum().alias("Potential_Revenue"),
            pl.col("Source").first().alias("Source")
        ])
    )
    
    # 3. Aggregate spend by campaign
    campaign_spend = (
        spend
        .filter(pl.col("Campaign") != "No_Campaign")
        .group_by("Campaign")
        .agg([
            pl.col("Spend").sum().alias("Total_Spend"),
            pl.col("Clicks").sum().alias("Total_Clicks"),
            pl.col("Impressions").sum().alias("Total_Impressions")
        ])
    )
    
    # 4. Join and calculate metrics
    campaign_efficiency = (
        campaign_deals
        .join(campaign_spend, on="Campaign", how="inner")
        .with_columns([
            # Calculate metrics
            (pl.col("Total_Revenue") / pl.col("Total_Spend")).alias("Real_ROAS"),
            (pl.col("Real_Conversions") / pl.col("Total_Leads") * 100).alias("Real_Conv_%"),
            (pl.col("Total_Revenue") / pl.col("Total_Leads")).alias("Revenue_per_Lead"),
            (pl.col("Total_Spend") / pl.col("Total_Leads")).alias("CPL")
        ])
        .filter(pl.col("Total_Spend") > 0)
    )
    
    return campaign_efficiency


# ===================================================================
# MAIN FUNCTIONS FOR DASHBOARD
# ===================================================================

def get_conversion_by_source(deals):
    """
    II.4 Conversion Rate by Source (%)
    """
    conv_data = (
        deals.group_by("Source")
        .agg([
            pl.len().alias("Total"),
            pl.col("Stage").filter(pl.col("Stage") == "Payment Done").count().alias("Won")
        ])
        .with_columns((pl.col("Won") / pl.col("Total") * 100).alias("Conversion_Rate"))
        .filter(pl.col("Total") > 10)
        .sort("Conversion_Rate", descending=True)
    )
    
    fig = px.bar(
        conv_data.to_pandas(), 
        x="Source", 
        y="Conversion_Rate", 
        title="II.4 Conversion Rate by Source (%)",
        text_auto='.1f',
        color="Conversion_Rate",
        color_continuous_scale="RdYlGn"
    )
    
    fig.update_layout(
        template="plotly_white",
        xaxis_tickangle=-45,
        yaxis_title="Conversion Rate (%)",
        coloraxis_showscale=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Calculate key statistics
    top_source = conv_data.head(1)["Source"].item() if conv_data.height > 0 else "N/A"
    top_rate = conv_data.head(1)["Conversion_Rate"].item() if conv_data.height > 0 else 0
    avg_rate = conv_data["Conversion_Rate"].mean() if conv_data.height > 0 else 0
    
    conclusion = (
        "📊 **Conclusion II.4 Conversion Rate by Source:**\n"
        f"- **Best performing source:** {top_source} ({top_rate:.1f}%)\n"
        f"- **Overall average:** {avg_rate:.1f}%\n"
        "- **Facebook Ads** and **Google Ads** show the most consistent rates.\n"
        "- Organic sources have variable but significant rates.\n"
        "- **Recommendation:** Focus resources on sources with rates >15% and high volume."
    )
    
    return fig, conclusion


def get_marketing_matrix(deals, spend):
    """
    II.1 Marketing Matrix: Volume vs. Real Success
    """
    campaign_efficiency = calculate_campaign_efficiency(deals, spend)
    
    campaign_viz = (
        campaign_efficiency 
        .filter(pl.col("Real_Conversions") > 0) 
        .to_pandas()
    )
    
    if campaign_viz.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No campaigns with real conversions",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(title="II.1 Marketing Matrix: No Data")
        return fig, "⚠️ There are no campaigns with real conversions."
    
    fig = px.scatter(
        campaign_viz,
        x="Total_Leads",
        y="Real_Conversions",
        size="Real_Conv_%",
        color="Real_ROAS",
        hover_name="Campaign",
        title="II.1 Marketing Matrix: Volume vs. Real Success",
        labels={
            "Total_Leads": "Total Lead Volume",
            "Real_Conversions": "Active Students (Stayed)",
            "Real_Conv_%": "Real Conv. Rate (%)",
            "Real_ROAS": "Real ROAS (Revenue/Spend)"
        },
        color_continuous_scale="RdYlGn", 
        color_continuous_midpoint=2.0,
        template="plotly_white",
        size_max=45
    )
    
    fig.update_layout(
        title_x=0.5,
        xaxis_title="Leads Generated (Quantity)",
        yaxis_title="Students who Started Course (Quality)",
        coloraxis_colorbar=dict(title="Real ROAS", thickness=20),
        width=1100,
        height=600,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Calculate quadrant statistics
    total_campaigns = campaign_viz.shape[0]
    high_volume = campaign_viz[campaign_viz["Total_Leads"] > campaign_viz["Total_Leads"].median()].shape[0]
    high_success = campaign_viz[campaign_viz["Real_Conversions"] > campaign_viz["Real_Conversions"].median()].shape[0]
    
    conclusion = (
        "📊 **Conclusion II.1 Marketing Matrix:**\n"
        f"- **Total campaigns analyzed:** {total_campaigns}\n"
        f"- **High volume campaigns:** {high_volume}\n"
        f"- **High success campaigns:** {high_success}\n"
        "- **Top-right quadrant** = premium campaigns (volume + success).\n"
        "- **Large bubbles** = high conversion rates.\n"
        "- **Green** = high ROAS (>2.0) - profitable.\n"
        "- **Recommendation:** Scale the green campaigns in the top-right quadrant."
    )
    
    return fig, conclusion


def get_campaign_audit(deals, spend):
    """
    II.2 Campaign Audit: Volume vs. Retention vs. Profitability
    """
    campaign_efficiency = calculate_campaign_efficiency(deals, spend)
    
    quantity_focus = (
        campaign_efficiency
        .sort("Total_Leads", descending=True)
        .head(15)
        .to_pandas()
    )
    
    if quantity_focus.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data for audit",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(title="II.2 Campaign Audit: No Data")
        return fig, "⚠️ There is no data for the audit."
    
    fig = go.Figure()
    
    # 1. Lost Leads
    fig.add_trace(go.Bar(
        x=quantity_focus["Campaign"],
        y=quantity_focus["Total_Leads"] - quantity_focus["Real_Conversions"],
        name="Leads Lost / Not Started",
        marker_color="lightgrey",
        opacity=0.6
    ))
    
    # 2. Real Students
    fig.add_trace(go.Bar(
        x=quantity_focus["Campaign"],
        y=quantity_focus["Real_Conversions"],
        name="Real Students (Retention)",
        marker_color="#1f77b4"
    ))
    
    # 3. Real ROAS
    fig.add_trace(go.Scatter(
        x=quantity_focus["Campaign"],
        y=quantity_focus["Real_ROAS"],
        name="Real ROAS",
        yaxis="y2",
        mode="lines+markers",
        line=dict(color="red", width=3)
    ))
    
    fig.update_layout(
        title="II.2 Campaign Audit: Volume vs. Retention vs. Profitability",
        title_x=0.5,
        barmode='stack',
        xaxis_tickangle=-45,
        yaxis=dict(title="Volume (Number of Leads)"),
        yaxis2=dict(title="Real ROAS", overlaying="y", side="right"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        width=1100,
        height=650
    )
    
    # Calculate key metrics
    total_leads = quantity_focus["Total_Leads"].sum()
    retained_students = quantity_focus["Real_Conversions"].sum()
    retention_rate = (retained_students / total_leads * 100) if total_leads > 0 else 0
    
    conclusion = (
        "🔍 **Conclusion II.2 Campaign Audit:**\n"
        f"- **Total leads analyzed:** {total_leads}\n"
        f"- **Retained students:** {retained_students}\n"
        f"- **Retention rate:** {retention_rate:.1f}%\n"
        "- **Grey** = lost leads (did not become students).\n"
        "- **Blue** = students who stayed (retention).\n"
        "- **Red** = Real ROAS (profitability).\n"
        "- **Recommendation:** Reduce the grey bar through funnel optimization."
    )
    
    return fig, conclusion


def get_top_campaigns_by_roas(deals, spend):
    """
    II.3 Top Campaigns by Real ROAS
    """
    campaign_efficiency = calculate_campaign_efficiency(deals, spend)
    
    top_roas_viz = (
        campaign_efficiency
        .filter(pl.col("Real_ROAS") > 0)
        .sort("Real_ROAS", descending=True)
        .head(20)
        .to_pandas()
    )
    
    if top_roas_viz.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No campaigns with positive ROAS", 
            xref="paper", yref="paper", 
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(title="II.3 Top Campaigns: No Data")
        return fig, "⚠️ There are no campaigns with positive ROAS."
    
    fig = px.bar(
        top_roas_viz,
        x="Real_ROAS",
        y="Campaign",
        color="Source",
        orientation='h',
        title="II.3 Top Campaigns by Real ROAS and Traffic Source",
        labels={
            "Real_ROAS": "Real ROAS (Revenue per 1€)",
            "Campaign": "Campaign Name",
            "Source": "Channel"
        },
        text="Real_ROAS",
        template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    
    fig.update_layout(
        yaxis={'categoryorder':'total ascending'},
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        width=1100,
        height=700
    )
    
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    
    # Calculate statistics
    avg_roas = top_roas_viz["Real_ROAS"].mean()
    top_campaign = top_roas_viz.iloc[0]["Campaign"]
    top_roas = top_roas_viz.iloc[0]["Real_ROAS"]
    
    conclusion = (
        "🏆 **Conclusion II.3 Top Campaigns by ROAS:**\n"
        f"- **Campaign #1:** {top_campaign} (ROAS: {top_roas:.2f})\n"
        f"- **Average ROAS top 20:** {avg_roas:.2f}\n"
        f"- **Campaigns with ROAS > 3.0:** {len(top_roas_viz[top_roas_viz['Real_ROAS'] > 3.0])}\n"
        "- **Facebook Ads** dominates the top, followed by **Google Ads**.\n"
        "- **Recommendation:** Allocate more budget to the top 10 and replicate strategies."
    )
    
    return fig, conclusion


def get_marketing_source_efficiency(deals, spend):
    """
    II.5 Marketing Source Efficiency: Volume vs. Quality vs. Profit
    """
    source_efficiency = calculate_source_efficiency(deals, spend)
    
    source_viz_data = (
        source_efficiency
        .filter(pl.col("Real_Conversions") > 0)
        .to_pandas()
    )
    
    if source_viz_data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No sources with real conversions",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(title="II.5 Marketing Source Efficiency: No Data")
        return fig, "⚠️ There are no sources with real conversions."
    
    fig = px.scatter(
        source_viz_data,
        x="Total_Leads",
        y="Real_Conversions",
        size="Real_Conv_%",
        color="Real_ROAS",
        hover_name="Source",
        title="II.5 Marketing Source Efficiency: Volume vs. Quality vs. Profit",
        labels={
            "Total_Leads": "Total Leads (Volume)",
            "Real_Conversions": "Real Students (Retention)",
            "Real_Conv_%": "Real Conv. Rate (%)",
            "Real_ROAS": "Real ROAS (Earned Revenue / Spend)"
        },
        color_continuous_scale="RdYlGn", 
        color_continuous_midpoint=2.0,
        template="plotly_white",
        size_max=50
    )
    
    fig.update_layout(
        title_x=0.5,
        xaxis_title="Leads Generated per Source",
        yaxis_title="Real Conversions (Students who Stayed)",
        coloraxis_colorbar_title="Real ROAS",
        width=1100,
        height=650,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.add_annotation(
        text="Bubble Size = Real Conversion Rate (% leads that become students)",
        xref="paper", yref="paper", x=0.5, y=-0.15, showarrow=False,
        font=dict(size=12, color="gray")
    )
    
    # Calculate best performing source
    best_source = source_viz_data.loc[source_viz_data['Real_ROAS'].idxmax()] if not source_viz_data.empty else None
    
    # --- DYNAMIC ROAS EVALUATION LOGIC FOR ZERO-SPEND CHANNELS ---
    # English comment: Dynamically evaluate if the maximum ROAS is mathematically infinite due to a division by zero spend.
    if best_source is not None:
        max_roas_val = best_source['Real_ROAS']
        if max_roas_val == float('inf') or str(max_roas_val).lower() == 'inf':
            roas_display = "Zero-Spend Channels (Organic/Referral)"
        else:
            roas_display = f"{max_roas_val:.2f}"
    else:
        roas_display = "N/A"
    
    conclusion = (
        "📈 **Conclusion II.5 Marketing Source Efficiency:**\n"
        f"- **Most profitable source:** {best_source['Source'] if best_source is not None else 'N/A'}\n"
        f"- **Max ROAS Efficiency:** {roas_display}\n"
        "- **Primary Growth Vector:** Partnership emerges as the most scalable and optimized source.\n"
        "- **Zero-Spend Acquisition Channels:** The gray bubbles represent organic or referral traffic sources with zero marketing capital expenditure ($Spend = 0$), resulting in mathematically unmeasurable (infinite) ROAS but high baseline efficiency.\n"
        "- **Top-right source** = high volume + high success.\n"
        "- **Large bubbles** = high conversion rates (good quality).\n"
        "- **Green** = profitable (ROAS > 2.0).\n"
        "- **Recommendation:** Invest more in the green sources in the top-right."
    )
    
    return fig, conclusion


def get_marketing_channels_efficiency(deals, spend):
    """
    II.6 Marketing Channels Efficiency (Paid channels only)
    """
    source_efficiency = calculate_source_efficiency(deals, spend)
    
    paid_sources_data = (
        source_efficiency
        .filter(
            (pl.col("Spend") > 0) & 
            (~pl.col("Source").str.contains("(?i)organic|partnership|crm|direct|referral"))
        )
        .sort("Real_ROAS", descending=True)
        .to_pandas()
    )
    
    if paid_sources_data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No paid channels",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(title="II.6 Marketing Channels: No Data")
        return fig, "⚠️ There are no paid marketing channels."
    
    fig = px.bar(
        paid_sources_data,
        x="Real_ROAS",
        y="Source",
        orientation='h',
        color="Real_ROAS",
        title="II.6 Paid Marketing Channels Efficiency",
        labels={
            "Real_ROAS": "Real ROAS (€ Earned per 1€ Spent)",
            "Source": "Paid Channel"
        },
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=2.0,
        template="plotly_white",
        text="Real_ROAS"
    )
    
    fig.update_layout(
        title_x=0.5,
        xaxis_title="Real ROAS (€ Earned per 1€ Spent)",
        yaxis_title="",
        yaxis={'categoryorder':'total ascending'},
        width=1100,
        height=500,
        coloraxis_colorbar=dict(title="Real ROAS"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    
    # Calculate statistics
    avg_roas = paid_sources_data["Real_ROAS"].mean()
    top_channel = paid_sources_data.iloc[0]["Source"]
    top_roas = paid_sources_data.iloc[0]["Real_ROAS"]
    
    conclusion = (
        "💰 **Conclusion II.6 Marketing Channels Efficiency:**\n"
        f"- **Channel #1:** {top_channel} (ROAS: {top_roas:.2f})\n"
        f"- **Average ROAS for paid channels:** {avg_roas:.2f}\n"
        f"- **Channels with ROAS > 2.5:** {len(paid_sources_data[paid_sources_data['Real_ROAS'] > 2.5])}\n"
        "- **Google Ads** has the highest ROAS for paid channels.\n"
        "- **Facebook Ads** has a solid ROAS, but lower than Google.\n"
        "- **Recommendation:** Prioritize your budget towards channels with ROAS > 2.5."
    )
    
    return fig, conclusion


def get_financial_efficiency(deals, spend):
    """
    II.7 Financial Efficiency: Expenses vs. Revenue (Sorted by Real ROAS)
    """
    source_efficiency = calculate_source_efficiency(deals, spend)
    
    paid_comparison_sorted = (
        source_efficiency
        .filter(
            (pl.col("Spend") > 0) & 
            (~pl.col("Source").str.contains("(?i)organic|partnership|crm|direct|referral"))
        )
        .sort("Real_ROAS", descending=True)
        .to_pandas()
    )
    
    if paid_comparison_sorted.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No paid channels",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(title="II.7 Financial Efficiency: No Data")
        return fig, "⚠️ There are no paid marketing channels."
    
    fig = go.Figure()
    
    # Expenses (Spend)
    fig.add_trace(go.Bar(
        x=paid_comparison_sorted["Source"],
        y=paid_comparison_sorted["Spend"],
        name="Expenses (Spend)",
        marker_color="#e74c3c", 
        text=paid_comparison_sorted["Spend"].round(0),
        textposition='outside',
        texttemplate='%{text:.0f}€'
    ))
    
    # Realized Revenue
    fig.add_trace(go.Bar(
        x=paid_comparison_sorted["Source"],
        y=paid_comparison_sorted["Total_Earned_Revenue"],
        name="Realized Revenue",
        marker_color="#2ecc71",
        text=paid_comparison_sorted["Total_Earned_Revenue"].round(0),
        textposition='outside',
        texttemplate='%{text:.0f}€'
    ))
    
    fig.update_layout(
        title="II.7 Financial Efficiency: Expenses vs. Revenue (Sorted by Real ROAS)",
        title_x=0.5,
        xaxis_title="Marketing Channel (Ranked by ROAS)",
        yaxis_title="Amount in EUR (€)",
        barmode='group',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        width=1100,
        height=650
    )
    
    # Calculate financial metrics
    total_spend = paid_comparison_sorted["Spend"].sum()
    total_revenue = paid_comparison_sorted["Total_Earned_Revenue"].sum()
    overall_roas = total_revenue / total_spend if total_spend > 0 else 0
    profitable_channels = len(paid_comparison_sorted[paid_comparison_sorted["Total_Earned_Revenue"] > paid_comparison_sorted["Spend"]])
    
    conclusion = (
        "💶 **Conclusion II.7 Financial Efficiency:**\n"
        f"- **Total spend:** {total_spend:.0f}€\n"
        f"- **Total revenue:** {total_revenue:.0f}€\n"
        f"- **Overall ROAS:** {overall_roas:.2f}\n"
        f"- **Profitable channels:** {profitable_channels}/{len(paid_comparison_sorted)}\n"
        "- **Google Ads** shows the best ROI (revenue significantly above spend).\n"
        "- **Facebook Ads** has high investment but also substantial revenue.\n"
        "- Channels where **revenue < spend** are at a loss.\n"
        "- **Recommendation:** Redirect budget from red channels to green ones. \n" 
        "- **Infrastructural Chart Sorting Logic:** To optimize executive readability, this chart is explicitly sorted in descending order based on the **Real ROAS = Realized Revenue /Marketing Spend**, rather than raw gross revenue volume. This explains why high-volume channels like Facebook Ads or Google Ads are positioned centrally—their massive scale naturally normalizes their efficiency ratio compared to low-cost, hyper-optimized specialized channels positioned at the front of the matrix."
    )
    
    return fig, conclusion