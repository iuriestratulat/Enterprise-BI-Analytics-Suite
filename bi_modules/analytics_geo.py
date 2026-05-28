# analytics_geo.py - VERSION WITHOUT EMOJIS
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64
import requests
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib import cm
# English comment: Import geographical mapping dictionaries for background analytics processing
from utilities.Countries import city_to_country
from utilities.DE_regions import city_to_state

# Import dictionaries from your existing modules inside the utilities package
try:
    from utilities.Countries import city_to_country
except ImportError:
    # Fallback dictionary if module is missing
    city_to_country = {}
    print("Warning: Countries module not found in utilities. Using empty city_to_country dictionary.")

try:
    from utilities.DE_regions import city_to_state
except ImportError:
    # Fallback dictionary if module is missing
    city_to_state = {}
    print("Warning: DE_regions module not found in utilities. Using empty city_to_state dictionary.")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def calculate_earned_revenue(df):
    """
    Calculates Earned Revenue according to the professor's formula.
    """
    return df.with_columns([
        ((pl.col("Offer_Total_Amount") / pl.col("Course_duration")) * pl.col("Months_of_study").fill_null(0)).alias("Earned_Revenue")
    ])

def get_city_mapping(df, mapping_dict, default_value="Other/Unknown"):
    """
    Applies city mapping.
    """
    return df.with_columns([
        pl.col("City").replace(mapping_dict, default=default_value).alias("Mapped_Location")
    ])

def safe_get_mapping(city, mapping_dict, default="Unknown"):
    """
    Safe function to get city mapping.
    """
    if not city:
        return default
    return mapping_dict.get(str(city).strip(), default)

# ============================================================================
# MAIN FUNCTIONS FOR EACH ANALYSIS
# ============================================================================

def get_geo_heatmap(df_deals):
    """
    Original geographic heatmap function (from your previous code)
    """
    # Existing implementation for Top Cities Heatmap
    top_cities = df_deals.filter(
        pl.col("City").is_not_null()
    ).group_by("City").agg([
        pl.count().alias("Count"),
        pl.mean("Real_Earned_Revenue").alias("Avg_Revenue")
    ]).sort("Count", descending=True).head(10)
    
    fig = px.scatter_geo(
        top_cities.to_pandas(),
        lat=50,
        lon=10,
        size="Count",
        color="Avg_Revenue",
        hover_name="City",
        title="Top Cities Heatmap",
        size_max=30,
        color_continuous_scale="Viridis"
    )
    
    fig.update_geos(
        visible=False,
        resolution=50,
        showcountries=True,
        countrycolor="Black",
        showsubunits=True,
        subunitcolor="Blue"
    )
    
    conclusion = """
    The heatmap shows the distribution of clients across major cities.
    The size of the points represents the number of clients, and the color represents the average revenue.
    """
    
    return fig, conclusion

def get_language_impact(df_deals):
    """
    Original language impact function (from your previous code)
    """
    language_data = df_deals.filter(
        pl.col("Level_of_Deutsch").is_not_null()
    ).group_by("Level_of_Deutsch").agg([
        pl.count().alias("Count"),
        pl.mean("Real_Earned_Revenue").alias("Avg_Revenue"),
        pl.mean("Months_of_study").alias("Avg_Months_Studied")
    ]).sort("Level_of_Deutsch")
    
    fig = px.bar(
        language_data.to_pandas(),
        x="Level_of_Deutsch",
        y="Avg_Revenue",
        color="Count",
        title="Language Impact on Revenue",
        labels={
            "Level_of_Deutsch": "German Language Level",
            "Avg_Revenue": "Average Revenue (€)",
            "Count": "Number of Students"
        },
        color_continuous_scale="Viridis"
    )
    
    conclusion = """
    Impact of German language proficiency on revenue.
    Higher proficiency levels tend to correlate with higher revenue and longer study periods.
    """
    
    return fig, conclusion

def get_international_expansion(df_deals):
    """
    V.1 International Expansion
    """
    if not city_to_country:
        fig = go.Figure()
        fig.add_annotation(
            text="<b>The city_to_country dictionary is unavailable.</b><br><br>"
                 "Ensure that the Countries.py file exists and contains the city_to_country dictionary.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14)
        )
        fig.update_layout(title="V.1 International Expansion - Error", height=400)
        return fig, "Error: city_to_country dictionary is missing."
    
    all_countries = (
        df_deals.with_columns([
            pl.col("City").replace(city_to_country, default="Other/Unknown").alias("Country")
        ])
        .filter(pl.col("Country") != "Other/Unknown")
        .group_by("Country")
        .agg([
            pl.len().alias("Student_Count"),
            pl.when(pl.col("Course_duration") > 0)
            .then((pl.col("Offer_Total_Amount") / pl.col("Course_duration")) * pl.col("Months_of_study").fill_null(0))
            .otherwise(0).sum().alias("Total_Revenue")
        ])
    )
    
    if len(all_countries) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="<b>No data available for international analysis.</b><br><br>"
                 "Check city mapping in the city_to_country dictionary.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14)
        )
        fig.update_layout(title="V.1 International Expansion - No Data", height=400)
        return fig, "No data available for international analysis."
    
    de_data = all_countries.filter(pl.col("Country") == "Germany").to_pandas()
    de_count = de_data["Student_Count"].iloc[0] if not de_data.empty else 0
    de_rev = de_data["Total_Revenue"].iloc[0] if not de_data.empty else 0
    
    intl_markets = all_countries.filter(pl.col("Country") != "Germany").sort("Student_Count", descending=True)
    
    if len(intl_markets) == 0:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["Germany"],
            y=[de_count],
            text=[f"{de_count} students<br>{de_rev:,.0f} EUR"],
            textposition='auto',
            marker_color='blue'
        ))
        fig.update_layout(
            title="V.1 International Expansion: Only Germany Available",
            xaxis_title="Country",
            yaxis_title="Number of Students",
            height=400
        )
        conclusion = f"Only Germany data available: {de_count} students, {de_rev:,.0f} EUR revenue."
        return fig, conclusion
    
    fig = px.bar(
        intl_markets.to_pandas(),
        x="Country",
        y="Student_Count",
        color="Total_Revenue",
        title="V.1 International Expansion: Secondary Markets Analysis",
        labels={
            "Country": "International Market",
            "Student_Count": "Number of Students",
            "Total_Revenue": "Revenue (EUR)"
        },
        text_auto=True,
        color_continuous_scale="Viridis",
        template="plotly_white"
    )
    
    fig.add_annotation(
        dict(
            font=dict(color="black", size=12),
            x=0.95,
            y=0.95,
            showarrow=False,
            text=(f"<b>Primary Market (DACH)</b><br>"
                  f"Germany: {de_count} students<br>"
                  f"Earned Revenue: {de_rev:,.0f} EUR"),
            xref="paper",
            yref="paper",
            align="left",
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="#444",
            borderwidth=1,
            borderpad=10
        )
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        margin=dict(t=100, b=100, r=150),
        height=600
    )
    
    conclusion = f"""
    International Expansion Analysis - Secondary Markets.
    
    Germany (Primary Market): {de_count} students, {de_rev:,.0f} EUR revenue.
    
    International markets analyzed: {len(intl_markets)} countries.
    
    This chart analyzes the academy's presence in international markets, excluding 
    the main market (Germany) for a more detailed view of secondary markets.
    """
    
    return fig, conclusion

def get_revenue_share_germany_vs_world(df_deals):
    """
    V.2 Revenue Share: Germany vs. Rest of the World
    """
    if not city_to_country:
        fig = go.Figure()
        fig.add_annotation(
            text="<b>The city_to_country dictionary is unavailable.</b><br><br>"
                 "Ensure that the Countries.py file exists and contains the city_to_country dictionary.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14)
        )
        fig.update_layout(title="V.2 Revenue Share - Error", height=400)
        return fig, "Error: city_to_country dictionary is missing."
    
    global_revenue_split = (
        df_deals.with_columns([
            pl.col("City").replace(city_to_country, default="Other/Unknown").alias("Country")
        ])
        .with_columns([
            pl.when(pl.col("Course_duration") > 0)
            .then((pl.col("Offer_Total_Amount") / pl.col("Course_duration")) * pl.col("Months_of_study").fill_null(0))
            .otherwise(0).alias("Earned_Revenue")
        ])
        .with_columns([
            pl.when(pl.col("Country") == "Germany")
            .then(pl.lit("Germany (Primary Market)"))
            .otherwise(pl.lit("International (Other Countries)"))
            .alias("Market_Segment")
        ])
        .group_by("Market_Segment")
        .agg(pl.col("Earned_Revenue").sum().alias("Total_Revenue"))
    )
    
    if len(global_revenue_split) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="<b>No data available for revenue distribution analysis.</b>",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14)
        )
        fig.update_layout(title="V.2 Revenue Share - No Data", height=400)
        return fig, "No data available for revenue distribution analysis."
    
    fig = px.pie(
        global_revenue_split.to_pandas(),
        values="Total_Revenue",
        names="Market_Segment",
        title="V.2 Revenue Share: Germany vs. Rest of the World",
        color_discrete_sequence=["#1f77b4", "#ff7f0e"],
        hole=0.4,
        template="plotly_white"
    )
    
    fig.update_traces(
        textinfo="percent+label",
        pull=[0, 0.2]
    )
    
    total_revenue = global_revenue_split["Total_Revenue"].sum()
    germany_revenue = global_revenue_split.filter(
        pl.col("Market_Segment") == "Germany (Primary Market)"
    )["Total_Revenue"].sum()
    
    germany_percent = (germany_revenue / total_revenue * 100) if total_revenue > 0 else 0
    
    conclusion = f"""
    Revenue distribution between Germany and the rest of the world.
    
    Germany accounts for {germany_percent:.1f}% of total revenue,
    while international markets contribute {100 - germany_percent:.1f}%.
    
    Total Revenue: {total_revenue:,.0f} EUR
    - Germany: {germany_revenue:,.0f} EUR
    - International: {total_revenue - germany_revenue:,.0f} EUR
    
    This analysis shows the level of geographic revenue diversification.
    """
    
    return fig, conclusion

#########################################################################################################

def get_regional_management_dashboard(df_deals, df_spend):
    """
    V.3 Regional Management Dashboard - 1x4 Version with ALL original information
    WITHOUT EMOJIS
    """
    if not city_to_state:
        return get_error_figure("The city_to_state dictionary is unavailable.")
    
    try:
        df_all = df_deals.to_pandas()
        df_all['State'] = df_all['City'].map(city_to_state).fillna('Rest of Germany')
        
        df_all['Earned_Revenue'] = (
            (df_all['Offer_Total_Amount'] / df_all['Course_duration']) * df_all['Months_of_study'].fillna(0)
        )
        
        df_spend_pd = df_spend.to_pandas()
        df_spend_pd['Spend_Clean'] = df_spend_pd['Spend'].replace('[EUR, ]', '', regex=True).astype(float)
        total_marketing_investment = df_spend_pd['Spend_Clean'].sum()
        
        total_active_students = df_all[df_all['Months_of_study'] > 0].shape[0]
        real_cac_value = total_marketing_investment / total_active_students if total_active_students > 0 else 0
        
        state_analysis = df_all.groupby('State').agg(
            Total_Earned_Revenue=('Earned_Revenue', 'sum'),
            Total_Leads=('Id', 'count'),
            Active_Student_Count=('Months_of_study', lambda x: (x > 0).sum()),
            Avg_Months_Study=('Months_of_study', 'mean')
        ).reset_index()
        
        duration_counts = df_all.groupby(['State', 'Course_duration']).size().reset_index(name='c')
        top_duration = duration_counts.sort_values(['State', 'c'], ascending=[True, False]).drop_duplicates('State')
        
        final_stats = state_analysis.merge(top_duration[['State', 'Course_duration']], on='State')
        
        final_stats['Ad_Spend_Real'] = final_stats['Active_Student_Count'] * real_cac_value
        final_stats['ROAS_Earned'] = (final_stats['Total_Earned_Revenue'] / final_stats['Ad_Spend_Real']).round(2)
        
        url_geo = "https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/master/2_bundeslaender/3_mittel.geo.json"
        
        try:
            germany_gdf = gpd.read_file(url_geo)
        except Exception as e:
            print(f"Error loading map: {e}")
            return get_error_figure(f"Error loading map: {str(e)}")
        
        if germany_gdf.empty:
            return get_error_figure("GeoJSON map is empty.")
        
        merged = germany_gdf.merge(final_stats, left_on='name', right_on='State', how='left').fillna(0)
        
        fig, axes = plt.subplots(1, 4, figsize=(28, 10))
        plt.subplots_adjust(wspace=0.12, hspace=0)
        
        map_configs = [
            (axes[0], 'ROAS_Earned', '1. Real Efficiency: ROAS (Earned Revenue)', 'Greens', 'efficiency'),
            (axes[1], 'Avg_Months_Study', '2. Retention: Average Months Studied', 'Purples', 'retention'),
            (axes[2], 'Ad_Spend_Real', '3. Real Investment: Marketing Spend per State', 'Oranges', 'investment'),
            (axes[3], 'Total_Earned_Revenue', '4. Strategic Value: Real Earned Revenue', 'Blues', 'strategic')
        ]

        for ax, col, title, cmap, label_type in map_configs:
            merged.plot(
                column=col, 
                cmap=cmap, 
                ax=ax, 
                linewidth=0.8, 
                edgecolor='0.3', 
                legend=True,
                legend_kwds={
                    'shrink': 0.6,
                    'aspect': 25,
                    'location': 'right', 
                    'pad': 0.02,
                    'label': 'Value'
                }
            )
            
            ax.set_title(title, fontsize=14, weight='bold', pad=15)
            
            for idx, row in merged.iterrows():
                if row['Total_Leads'] > 0:
                    centroid = row['geometry'].centroid
                    x, y = centroid.x, centroid.y
                    
                    if row['name'] == 'Brandenburg': 
                        x += 0.8; y += 0.5
                    elif row['name'] == 'Berlin': 
                        y -= 0.3
                    elif row['name'] == 'Niedersachsen': 
                        y -= 0.6  
                    elif row['name'] == 'Bremen':
                        y += 0.2
                    elif row['name'] == 'Hamburg': 
                        y -= 0.2
                    elif row['name'] == 'Schleswig-Holstein': 
                        y += 0.3
                    elif row['name'] == 'Saarland': 
                        y -= 0.1
                    
                    if label_type == 'efficiency':
                        txt = f"{row['name']}\nROAS: {row['ROAS_Earned']:.2f}\nDur: {int(row['Course_duration'])} months"
                    elif label_type == 'retention':
                        txt = f"{row['name']}\nAvg: {row['Avg_Months_Study']:.1f} months"
                    elif label_type == 'investment':
                        invest_val = row['Ad_Spend_Real']
                        if invest_val >= 1000000:
                            invest_str = f"{invest_val/1000000:.1f}M EUR"
                        elif invest_val >= 1000:
                            invest_str = f"{invest_val/1000:.0f}k EUR"
                        else:
                            invest_str = f"{invest_val:.0f} EUR"
                        
                        txt = f"{row['name']}\nActive: {int(row['Active_Student_Count'])}\nCost: {invest_str}"
                    else:
                        revenue_val = row['Total_Earned_Revenue']
                        if revenue_val >= 1000000:
                            revenue_str = f"{revenue_val/1000000:.1f}M EUR"
                        elif revenue_val >= 1000:
                            revenue_str = f"{revenue_val/1000:.0f}k EUR"
                        else:
                            revenue_str = f"{revenue_val:.0f} EUR"
                        
                        txt = f"{row['name']}\n{int(row['Active_Student_Count'])} Active\n{revenue_str}"
                    
                    ax.text(
                        x, y, txt, 
                        fontsize=9, 
                        ha='center', 
                        weight='bold',
                        linespacing=1.2,
                        bbox=dict(
                            facecolor='white', 
                            alpha=0.85, 
                            edgecolor='darkgray', 
                            boxstyle='round,pad=0.4',
                            linewidth=0.8
                        )
                    )
            ax.axis('off')
        
        plt.suptitle(
            f"Regional Management Dashboard: Earned Revenue Analysis (Global CAC: {real_cac_value:.2f}EUR)", 
            fontsize=16, 
            weight='bold', 
            y=1.05
        )
        
        plt.figtext(
            0.5, 0.01,
            f"TOTALS: Marketing Investment: {total_marketing_investment:,.0f}EUR | "
            f"Earned Revenue: {final_stats['Total_Earned_Revenue'].sum():,.0f}EUR | "
            f"Active Students: {total_active_students}",
            ha="center", 
            fontsize=11,
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8)
        )
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=130, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        buf.seek(0)
        
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        image_src = f'data:image/png;base64,{image_base64}'
        
        fig_dash = go.Figure()
        
        fig_dash.add_layout_image(
            dict(
                source=image_src,
                xref="paper", yref="paper",
                x=0, y=1,
                sizex=1, sizey=1,
                xanchor="left", yanchor="top"
            )
        )
        
        fig_dash.update_xaxes(showgrid=False, zeroline=False, visible=False)
        fig_dash.update_yaxes(showgrid=False, zeroline=False, visible=False)
        
        fig_dash.update_layout(
            title="V.3 Regional Management Dashboard",
            height=800,
            margin=dict(l=0, r=0, t=60, b=0)
        )
        
        conclusion = f"""
        REGIONAL MANAGEMENT DASHBOARD - COMPLETE ANALYSIS
        
        KEY GLOBAL METRICS:
        * Real Global CAC (Cost Per Acquisition): {real_cac_value:.2f}EUR
        * Total Marketing Investment: {total_marketing_investment:,.0f}EUR
        * Total Earned Revenue: {final_stats['Total_Earned_Revenue'].sum():,.0f}EUR
        * Total Active Students (started course): {total_active_students}
        * Total Leads/Contacts: {final_stats['Total_Leads'].sum()}
        
        ANALYSIS BY FEDERAL STATE ({len(final_stats)} states analyzed):
        
        1. REAL EFFICIENCY (ROAS) - Map 1 (green):
           - Measures marketing investment profitability
           - ROAS = Earned Revenue / Marketing Investment
           - Values > 1 indicate profitability
        
        2. STUDENT RETENTION - Map 2 (purple):
           - Average number of study months completed
           - Indicator of student satisfaction and persistence
           - Higher values = more engaged students
        
        3. REAL INVESTMENT - Map 3 (orange):
           - Real marketing cost allocated per state
           - Calculated: Active Students × Global CAC
           - Reflects budget distribution across regions
        
        4. STRATEGIC VALUE - Map 4 (blue):
           - Real revenue obtained from each state
           - Based on formula: (Total Value / Course Duration) × Months Studied
           - Primary indicator of financial contribution
        
        MAP LABEL LEGEND:
        * Federal State Name
        * Specific Metric Value (ROAS, Avg Months, Cost, Revenue)
        * Additional Info (course duration, active students)
        
        OPTIMIZED FOR 27" MONITOR - All 4 perspectives visible simultaneously.
        """
        
        return fig_dash, conclusion
        
    except Exception as e:
        print(f"Error in regional management dashboard: {e}")
        import traceback
        traceback.print_exc()
        return get_error_figure(f"Error creating dashboard: {str(e)}")

#########################################################################################################

def get_error_figure(message):
    """Creates a figure with an error message for Dash"""
    fig = go.Figure()
    fig.add_annotation(
        text=f"<b>Error</b><br>{message}",
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=14),
        align="center"
    )
    fig.update_layout(
        title="V.3 Regional Management Dashboard - Error",
        height=400,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    return fig, message


def get_market_density(df_deals):
    """
    V.4 Market Density
    """
    deals_prepared = df_deals.with_columns(
        pl.col("City").cast(pl.String).fill_null("Unknown")
    )
    
    top_cities = (
        deals_prepared.group_by("City")
        .len()
        .sort("len", descending=True)
        .head(10)["City"]
        .to_list()
    )
    
    activation_map = (
        deals_prepared.filter(
            (pl.col("City").is_in(top_cities)) & 
            (pl.col("Level_of_Deutsch").is_not_null()) &
            (pl.col("Months_of_study") > 0)
        )
        .group_by(["City", "Level_of_Deutsch"])
        .agg(pl.len().alias("Active_Student_Count"))
    )
    
    if len(activation_map) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="<b>No data available for market density analysis.</b><br><br>"
                 "Check if there are active students (Months_of_study > 0) with specified German levels.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14)
        )
        fig.update_layout(title="V.4 Market Density - No Data", height=400)
        return fig, "No data available for market density analysis."
    
    fig = px.density_heatmap(
        activation_map.to_pandas(),
        x="Level_of_Deutsch",
        y="City",
        z="Active_Student_Count",
        title="V.4 Market Density: Number of Active Students by Language Level and City",
        labels={
            "Level_of_Deutsch": "German Level",
            "City": "City",
            "Active_Student_Count": "Active Students (N)"
        },
        color_continuous_scale="Blues",
        category_orders={"Level_of_Deutsch": ["A0", "A1", "A2", "B1", "B2", "C1"]},
        template="plotly_white",
        text_auto=True
    )
    
    total_active = activation_map["Active_Student_Count"].sum()
    avg_per_city = activation_map.group_by("City").agg(
        pl.col("Active_Student_Count").sum()
    )["Active_Student_Count"].mean()
    
    conclusion = f"""
    Market Density: Distribution of active students by language level and city.
    
    General Statistics:
    - Total active students in top 10 cities: {total_active}
    - Average active students per city: {avg_per_city:.1f}
    - Number of city-level combinations analyzed: {len(activation_map)}
    
    The heatmap shows the concentration of active students (those who effectively started studies)
    based on German language level and city.
    
    Darker areas indicate higher concentrations of students.
    """
    
    return fig, conclusion

#########################################################################################################

def get_regional_leadership(df_deals):
    """
    V.5 Regional Leadership - Version for Dash with Matplotlib->PNG conversion
    WITHOUT EMOJIS
    """
    import matplotlib
    matplotlib.use('Agg')
    
    if not city_to_state:
        return get_error_figure("The city_to_state dictionary is unavailable.")
    
    try:
        print("DEBUG: Starting V.5 Regional Leadership...")
        
        import pandas as pd
        
        df_vol = df_deals.to_pandas()
        df_vol['State'] = df_vol['City'].map(city_to_state).fillna('Rest of Germany')
        
        active_vol = df_vol[df_vol['Months_of_study'] > 0].groupby(
            ['State', 'Level_of_Deutsch']
        ).size().reset_index(name='Student_Count')
        
        print(f"DEBUG: Active students found: {len(active_vol)} records")
        
        if len(active_vol) == 0:
            return get_error_figure("No active students (Months_of_study > 0) for regional leadership analysis.")
        
        dominant_volume = active_vol.sort_values(
            ['State', 'Student_Count'], ascending=[True, False]
        ).drop_duplicates('State')
        
        print(f"DEBUG: States with dominant level identified: {len(dominant_volume)}")
        
        url_geo = "https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/master/2_bundeslaender/3_mittel.geo.json"
        
        try:
            germany_gdf = gpd.read_file(url_geo)
            print(f"DEBUG: GeoJSON loaded for V.5")
        except Exception as e:
            print(f"ERROR loading map V.5: {str(e)}")
            return get_error_figure(f"Error loading map: {str(e)}")
        
        if germany_gdf.empty:
            return get_error_figure("GeoJSON map is empty for V.5.")
        
        merged_vol_map = germany_gdf.merge(dominant_volume, left_on='name', right_on='State', how='left')
        
        fig = plt.figure(figsize=(20, 12))
        
        ax1 = plt.subplot(1, 2, 1)
        
        merged_vol_map.plot(
            column='Level_of_Deutsch',
            cmap='Set3',
            linewidth=0.8, 
            ax=ax1, 
            edgecolor='0.4', 
            legend=True,
            legend_kwds={
                'title': "Dominant Level (by Volume)", 
                'loc': 'upper left',
                'title_fontsize': 10,
                'fontsize': 9
            }
        )
        
        for idx, row in merged_vol_map.iterrows():
            if not pd.isna(row['Level_of_Deutsch']):
                centroid = row['geometry'].centroid
                x, y = centroid.x, centroid.y
                
                adjustments = {
                    'Brandenburg': (0.8, 0.5),
                    'Berlin': (0, -0.3),
                    'Bremen': (0, 0.2),
                    'Hamburg': (0, -0.2),
                    'Schleswig-Holstein': (0, 0.3),
                    'Saarland': (0, -0.1),
                    'Niedersachsen': (0, -0.5)
                }
                
                if row['name'] in adjustments:
                    dx, dy = adjustments[row['name']]
                    x += dx
                    y += dy
                
                ax1.text(
                    x, y, 
                    f"{row['name']}\n{row['Level_of_Deutsch']}\n({int(row['Student_Count'])} stud.)", 
                    fontsize=9, 
                    ha='center', 
                    weight='bold', 
                    bbox=dict(
                        facecolor='white', 
                        alpha=0.8, 
                        edgecolor='gray',
                        boxstyle='round,pad=0.3'
                    )
                )
        
        ax1.set_title('V.5 Regional Leadership: Dominant German Language Level per State', 
                     fontsize=14, weight='bold', pad=15)
        ax1.axis('off')
        
        active_vol_sorted = active_vol.sort_values(
            ['State', 'Student_Count'], ascending=[True, False]
        )
        
        def format_volume_label(group):
            items = []
            for _, row in group.iterrows():
                level = row['Level_of_Deutsch']
                count = int(row['Student_Count'])
                items.append(f"{level} ({count} stud.)")
            return ", ".join(items)
        
        summary_vol_table = active_vol_sorted.groupby('State').apply(
            format_volume_label
        ).reset_index(name='Level Distribution (by Volume)')
        
        ax2 = plt.subplot(1, 2, 2)
        ax2.axis('tight')
        ax2.axis('off')
        
        table_data = summary_vol_table.values.tolist()
        table_data_with_header = [['Federal State', 'Language Level Distribution (sorted by volume)']] + table_data
        
        table = ax2.table(
            cellText=table_data_with_header,
            cellLoc='left', 
            loc='center',
            colWidths=[0.3, 0.7]
        )
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.8)
        
        for i in range(2):
            table[(0, i)].set_facecolor('#4a6fa5')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        for i in range(1, len(table_data_with_header)):
            if i % 2 == 0:
                color = '#f2f2f2'
            else:
                color = '#ffffff'
            
            for j in range(2):
                table[(i, j)].set_facecolor(color)
        
        ax2.set_title('Detailed Distribution: Student Volume per Language Level', 
                     fontsize=14, weight='bold', pad=20, y=1.05)
        
        plt.suptitle(
            'REGIONAL LEADERSHIP ANALYSIS: German Language Level Distribution in Germany', 
            fontsize=16, 
            weight='bold', 
            y=0.98
        )
        
        total_students = active_vol['Student_Count'].sum()
        unique_levels = active_vol['Level_of_Deutsch'].nunique()
        
        plt.figtext(
            0.5, 0.02,
            f"STATISTICS: Total Active Students Analyzed: {total_students} | "
            f"Unique Language Levels: {unique_levels} | "
            f"States Analyzed: {len(summary_vol_table)}",
            ha="center", 
            fontsize=11,
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8)
        )
        
        plt.tight_layout(rect=[0, 0.05, 1, 0.95])
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=130, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        buf.seek(0)
        
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        image_src = f'data:image/png;base64,{image_base64}'
        
        fig_dash = go.Figure()
        
        fig_dash.add_layout_image(
            dict(
                source=image_src,
                xref="paper", yref="paper",
                x=0, y=1,
                sizex=1, sizey=1,
                xanchor="left", yanchor="top"
            )
        )
        
        fig_dash.update_xaxes(visible=False)
        fig_dash.update_yaxes(visible=False)
        
        fig_dash.update_layout(
            title="V.5 Regional Leadership - Map and Language Level Distribution",
            height=800,
            margin=dict(l=0, r=0, t=60, b=0)
        )
        
        conclusion = f"""
        V.5 REGIONAL LEADERSHIP - COMPLETE ANALYSIS
        
        STATISTICAL SUMMARY:
        * Total active students analyzed: {total_students}
        * Unique German language levels identified: {unique_levels}
        * Federal states analyzed: {len(summary_vol_table)}
        
        2-IN-1 VISUALIZATION:
        
        1. GEOGRAPHIC MAP (left):
           - Displays the DOMINANT German language level in each state
           - Different colors represent different levels (A1, A2, B1, etc.)
           - Labels show: State Name | Dominant Level | Student Count
        
        2. DISTRIBUTION TABLE (right):
           - Complete list of all levels for each state
           - Sorted descending by student count
           - Allows detailed distribution analysis
        
        RESULTS INTERPRETATION:
        * The dominant level indicates which student category is most frequent in the region
        * The detailed distribution shows all levels present in each state
        * This information is crucial for:
          - Personalizing educational content by region
          - Allocating teaching resources
          - Regionalized marketing strategies
        
        MAP COLORS (Set3 palette):
        * Each color represents a different German language level
        * Legend explains color correspondence
        """
        
        print("DEBUG: V.5 completed successfully!")
        return fig_dash, conclusion
        
    except Exception as e:
        print(f"ERROR in V.5 Regional Leadership: {str(e)}")
        import traceback
        traceback.print_exc()
        return get_error_figure(f"Error in V.5: {str(e)}")
        
######################################################################################################### 

# ============================================================================
# INTEGRATION FUNCTIONS WITH DASH (for compatibility)
# ============================================================================

def get_geo_heatmap_simple(df_deals):
    """Simplified version for Dash"""
    return get_geo_heatmap(df_deals)

def get_language_impact_simple(df_deals):
    """Simplified version for Dash"""
    return get_language_impact(df_deals)