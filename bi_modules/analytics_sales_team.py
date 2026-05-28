import plotly.express as px
import plotly.graph_objects as go
import polars as pl

# ===================================================================
# HELPER FUNCTIONS
# ===================================================================

def calculate_owner_analysis(deals, calls):
    """
    Calculate comprehensive sales team performance metrics.
    """
    # 1. Prepare deals data
    deals_conversions = deals.with_columns([
        # Flag for successful conversions (initial payment > 0)
        pl.when(pl.col("Initial_Amount_Paid") > 0).then(1).otherwise(0).alias("Success_Flag"),
        
        # Calculate earned revenue (pro-rated based on months studied)
        pl.when(pl.col("Course_duration") > 0)
          .then((pl.col("Offer_Total_Amount") / pl.col("Course_duration")) * pl.col("Months_of_study").fill_null(0))
          .otherwise(pl.col("Initial_Amount_Paid"))
          .alias("Earned_Revenue"),
        
        # Calculate system processing time
        ((pl.col("Closing_Time").cast(pl.Datetime) - pl.col("Created_Time").cast(pl.Datetime))
         .dt.total_minutes()).alias("System_Time_Min")
    ]).filter(pl.col("Deal_Owner_Name").is_not_null())
    
    # 2. Aggregate deals by owner
    owner_deals = (
        deals_conversions
        .group_by("Deal_Owner_Name")
        .agg([
            pl.len().alias("Total_Leads"),
            pl.col("Success_Flag").sum().alias("Conversions"),
            pl.col("Earned_Revenue").sum().alias("Total_Earned_Revenue"),
            pl.col("System_Time_Min").sum().alias("Total_System_Min"),
            pl.col("Created_Time").min().alias("First_Deal"),
            pl.col("Created_Time").max().alias("Last_Deal")
        ])
        .with_columns([
            # Calculate tenure in days
            ((pl.col("Last_Deal") - pl.col("First_Deal")).dt.total_days() + 1).alias("Days_Active"),
            
            # Calculate conversion rate
            (pl.col("Conversions") / pl.col("Total_Leads") * 100).round(2).alias("Conv_Rate_%"),
            
            # Calculate system velocity (total system time per euro earned)
            (pl.when(pl.col("Total_Earned_Revenue") > 0)
             .then(pl.col("Total_System_Min") / pl.col("Total_Earned_Revenue"))
             .otherwise(0).round(2)).alias("Velocity_Min_per_Euro")
        ])
    )
    
    # 3. Aggregate calls by owner (if calls data is available)
    if calls is not None and "Call_Owner_Name" in calls.columns:
        owner_calls = (
            calls
            .filter(pl.col("Call_Owner_Name").is_not_null())
            .group_by("Call_Owner_Name")
            .agg([
                pl.len().alias("Total_Calls"),
                pl.col("Call_Duration_(in_seconds)").sum().alias("Total_Talk_Time_Sec")
            ])
            .with_columns([
                (pl.col("Total_Talk_Time_Sec") / 60).round(2).alias("Total_Talk_Time_Min")
            ])
        )
        
        # Join deals with calls
        owner_analysis = (
            owner_deals
            .join(owner_calls, left_on="Deal_Owner_Name", right_on="Call_Owner_Name", how="left")
            .with_columns([
                # Calculate calls per sale
                (pl.when(pl.col("Conversions") > 0)
                 .then(pl.col("Total_Calls") / pl.col("Conversions"))
                 .otherwise(0).round(1)).alias("Calls_per_Sale"),
                
                # Calculate talk time per euro earned
                (pl.when(pl.col("Total_Earned_Revenue") > 0)
                 .then(pl.col("Total_Talk_Time_Min") / pl.col("Total_Earned_Revenue"))
                 .otherwise(0).round(2)).alias("Min_per_Earned_Euro")
            ])
        )
    else:
        owner_analysis = owner_deals
    
    # 4. Add performance categories
    owner_analysis = owner_analysis.with_columns(
        pl.when(pl.col("Conv_Rate_%") <= 5).then(pl.lit("Critically Low (0-5%)"))
        .when(pl.col("Conv_Rate_%") <= 15).then(pl.lit("Average (5-15%)"))
        .otherwise(pl.lit("High Performance (>15%)"))
        .alias("Performance_Category")
    )
    
    return owner_analysis


# ===================================================================
# MAIN FUNCTIONS FOR DASHBOARD
# ===================================================================

def get_manager_performance_matrix(deals, calls):
    """
    III.1 Manager Performance Matrix
    Bubble chart showing experience vs efficiency.
    """
    owner_analysis = calculate_owner_analysis(deals, calls)
    
    # Filter for active managers with some leads
    active_managers = owner_analysis.filter(pl.col("Total_Leads") > 0)
    
    if active_managers.height == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No data for active managers",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(title="III.1 Manager Performance Matrix: No Data")
        return fig, "⚠️ No managers with assigned leads."
    
    # Create bubble chart
    fig = px.scatter(
        active_managers.to_pandas(),
        x="Days_Active",
        y="Conv_Rate_%",
        size="Total_Earned_Revenue",
        color="Performance_Category",
        color_discrete_map={
            "Critically Low (0-5%)": "red",
            "Average (5-15%)": "blue",
            "High Performance (>15%)": "green"
        },
        hover_name="Deal_Owner_Name",
        text="Deal_Owner_Name",
        title="III.1 Manager Performance Matrix: Experience vs. Efficiency",
        labels={
            "Days_Active": "Tenure (Days Active)",
            "Conv_Rate_%": "Conversion Rate (%)",
            "Total_Earned_Revenue": "Real Earned Revenue (€)",
            "Performance_Category": "Performance Tier"
        },
        template="plotly_white",
        size_max=60,
        width=1100,
        height=700
    )
    
    # Add average conversion rate line
    avg_conv = active_managers["Conv_Rate_%"].mean()
    fig.add_hline(
        y=avg_conv, 
        line_dash="dot", 
        line_color="red",
        annotation_text=f"Average ({avg_conv:.1f}%)",
        annotation_position="top right"
    )
    
    fig.update_traces(textposition='top center')
    
    fig.update_layout(
        title_x=0.5,
        legend=dict(
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            bgcolor="white",
            bordercolor="Black",
            borderwidth=1
        ),
        yaxis=dict(range=[-5, active_managers["Conv_Rate_%"].max() * 1.2]),
        margin=dict(t=100, b=80, l=70, r=220)
    )
    
    conclusion = (
        "📊 **Conclusion III.1 Manager Performance Matrix:**\n"
        "- **Green** = High Performance (>15% conversion)\n"
        "- **Blue** = Average Performance (5-15% conversion)\n"
        "- **Red** = Critical Performance (<5% conversion)\n"
        "- **Bubble Size** = Real Revenue Generated\n"
        f"- **Overall Average:** {avg_conv:.1f}% conversion\n"
        "- **Recommendation:** Pair experienced mentors (right side) with low performers (red)."
    )
    
    return fig, conclusion


def get_zero_conversion_agents(deals, calls):
    """
    III.2 Leads Handled by Agents with 0 Conversions
    Diagnostic for resource leaks in sales team.
    """
    owner_analysis = calculate_owner_analysis(deals, calls)
    
    # Filter for zero conversion agents
    zero_sales_agents = (
        owner_analysis
        .filter(pl.col("Conversions") == 0)
        .sort("Total_Leads", descending=True)
    )
    
    if zero_sales_agents.height == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="✓ All agents have at least one conversion!",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="green")
        )
        fig.update_layout(title="III.2 Zero Conversion Agents: No Issues Found")
    else:
        # Create bar chart for zero conversion agents
        fig = px.bar(
            zero_sales_agents.to_pandas(),
            x="Deal_Owner_Name",
            y="Total_Leads",
            color="Days_Active",
            title="III.2 Diagnostic: Leads Handled by Agents with 0 Conversions",
            labels={
                "Total_Leads": "Number of Leads Wasted",
                "Deal_Owner_Name": "Agent Name",
                "Days_Active": "Days Active in CRM"
            },
            template="plotly_white",
            color_continuous_scale="OrRd",
            width=850,
            height=600
        )
        
        fig.update_layout(
            title_x=0.5,
            xaxis_tickangle=-45,
            margin=dict(t=80, b=120, l=60, r=60)
        )
    
    conclusion = (
        "🔍 **Conclusion III.2 Zero Conversion Agents:**\n"
        f"- Agents with 0 conversions: {zero_sales_agents.height}\n"
        f"- Total wasted leads: {zero_sales_agents['Total_Leads'].sum() if zero_sales_agents.height > 0 else 0}\n"
        "- **Dark Red** = longer activity without results.\n"
        "- **Recommendation:** Analyze training and resources allocated to these agents."
    )
    
    return fig, conclusion


def get_lifecycle_per_euro(deals, calls):
    """
    III.3 Lifecycle per 1€ of Earned Revenue
    Analysis of system processing time vs revenue efficiency.
    """
    owner_analysis = calculate_owner_analysis(deals, calls)
    
    # Filter for managers with earned revenue
    velocity_data = (
        owner_analysis
        .filter(
            (pl.col("Total_Earned_Revenue") > 0) & 
            (pl.col("Velocity_Min_per_Euro") > 0)
        )
        .sort("Velocity_Min_per_Euro")
    )
    
    if velocity_data.height == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No data for velocity analysis",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(title="III.3 Lifecycle per 1€: No Data")
        return fig, "⚠️ No data available to calculate system velocity."
    
    # Create bar chart
    fig = px.bar(
        velocity_data.to_pandas(),
        x="Deal_Owner_Name",
        y="Velocity_Min_per_Euro",
        text="Velocity_Min_per_Euro",
        title="III.3 System Velocity: Lead Lifecycle per 1€ of Earned Revenue",
        labels={
            "Velocity_Min_per_Euro": "System Minutes per 1€",
            "Deal_Owner_Name": "Sales Manager"
        },
        template="plotly_white",
        color="Velocity_Min_per_Euro",
        color_continuous_scale="RdYlGn_r",  # Reversed: green is better (faster)
        width=1000,
        height=650
    )
    
    fig.update_traces(texttemplate='%{text:.1f} min', textposition='outside')
    
    fig.update_layout(
        title_x=0.5,
        xaxis_tickangle=-45,
        yaxis_title="Minutes per 1€ Earned",
        coloraxis_colorbar=dict(title="Min/€", thickness=20)
    )
    
    # Add efficiency analysis for top and bottom performers
    fastest = velocity_data.head(1)["Deal_Owner_Name"].item()
    slowest = velocity_data.tail(1)["Deal_Owner_Name"].item()
    fastest_time = velocity_data.head(1)["Velocity_Min_per_Euro"].item()
    slowest_time = velocity_data.tail(1)["Velocity_Min_per_Euro"].item()
    
    conclusion = (
        "⚡ **Conclusion III.3 Lifecycle per 1€:**\n"
        f"- **Fastest:** {fastest} ({fastest_time:.1f} min/€)\n"
        f"- **Slowest:** {slowest} ({slowest_time:.1f} min/€)\n"
        f"- **Difference:** {slowest_time/fastest_time:.1f}x slower\n\n"
        "📝 **Important Note:**\n"
        "1. This is processing time in CRM (lead creation → closing).\n"
        "2. This is NOT talk time.\n"
        "3. Lower value = faster pipeline processing.\n"
        "4. **Recommendation:** Implement automation for agents with values > 5 min/€."
    )
    
    return fig, conclusion


def get_calls_vs_revenue_velocity(deals, calls):
    """
    III.4 Average Calls to Close vs. Revenue Velocity
    Efficiency analysis of sales effort vs results.
    """
    if calls is None or "Call_Owner_Name" not in calls.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="Call data not available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(title="III.4 Calls to Close: Calls Data Required")
        return fig, "⚠️ Call data is required for this analysis."
    
    owner_analysis = calculate_owner_analysis(deals, calls)
    
    # Filter for managers with conversions
    efficiency_data = (
        owner_analysis
        .filter(
            (pl.col("Conversions") > 0) & 
            (pl.col("Calls_per_Sale") > 0) &
            (pl.col("Min_per_Earned_Euro") > 0)
        )
        .sort("Calls_per_Sale")
    )
    
    if efficiency_data.height == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No data for efficiency analysis",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(title="III.4 Calls to Close: No Data")
        return fig, "⚠️ No data available to calculate efficiency."
    
    # Create bar chart for sales efficiency
    fig = px.bar(
        efficiency_data.to_pandas(),
        x="Deal_Owner_Name",
        y="Calls_per_Sale",
        color="Min_per_Earned_Euro",
        color_continuous_scale="RdYlGn_r",
        title="III.4 Sales Efficiency: Average Calls to Close vs. Revenue Velocity",
        labels={
            "Deal_Owner_Name": "Sales Agent",
            "Calls_per_Sale": "Avg. Calls to Close 1 Deal",
            "Min_per_Earned_Euro": "Min. Talk Time per 1€ Real Value"
        },
        text="Calls_per_Sale",
        template="plotly_white",
        width=1100,
        height=700
    )
    
    fig.update_traces(
        texttemplate='%{text:.1f} calls', 
        textposition='outside',
        textfont_size=12
    )
    
    fig.update_layout(
        title_x=0.5,
        xaxis_tickangle=-45,
        yaxis_title="Calls required per 1 Sale",
        coloraxis_colorbar=dict(title="Min/€ Real Value", thickness=20),
        yaxis=dict(range=[0, efficiency_data["Calls_per_Sale"].max() * 1.25]),
        margin=dict(t=100, b=100, l=70, r=100)
    )
    
    # Calculate averages for context
    avg_calls = efficiency_data["Calls_per_Sale"].mean()
    avg_time = efficiency_data["Min_per_Earned_Euro"].mean()
    best_performer = efficiency_data.sort("Calls_per_Sale").head(1)["Deal_Owner_Name"].item()
    best_calls = efficiency_data.sort("Calls_per_Sale").head(1)["Calls_per_Sale"].item()
    
    conclusion = (
        "🎯 **Conclusion III.4 Calls to Close vs. Revenue Velocity:**\n"
        f"- **Avg calls/sale:** {avg_calls:.1f} calls\n"
        f"- **Avg time/€:** {avg_time:.2f} minutes\n"
        f"- **Most efficient:** {best_performer} ({best_calls:.1f} calls/sale)\n\n"
        "📊 **Interpretation:**\n"
        "- **Calls/Sale** = Average number of calls to close a deal.\n"
        "- **Min/€** = Total talk time invested per 1€ revenue.\n"
        "- **Green** = High efficiency (less time per euro).\n"
        "- **Red** = Low efficiency (more time per euro).\n"
        "- **Recommendation:** Optimize scripts and follow-up technique."
    )
    
    return fig, conclusion