"""
vi2_dashboard.py - Dashboard for VI.2 Business growth points
"""

import dash
from dash import dcc, html, dash_table
import plotly.express as px
import pandas as pd
from ue_utils import format_number_2decimals, format_integer, COLORS_PRODUCTS

# ============================================================================
# HEATMAP
# ============================================================================

def create_heatmap_figure(heatmap_df):
    """
    Creates a heatmap for sensitivity analysis.
    """
    if heatmap_df is None or heatmap_df.empty:
        return px.imshow([[0]], text_auto=True, title="Data unavailable")
    
    try:
        if hasattr(heatmap_df, 'to_pandas'):
            heatmap_df = heatmap_df.to_pandas()
        
        # Define the logical order for growth levers
        column_order = ["UA (+15%)", "C1 (+15%)", "AOV (+15%)", "APC (+15%)", "CPA (-15%)"]
        available_columns = [col for col in column_order if col in heatmap_df.columns]
        heatmap_df = heatmap_df[available_columns]
        
        fig = px.imshow(
            heatmap_df,
            text_auto=".1f",
            aspect="auto",
            color_continuous_scale="RdYlGn",
            title="🔥 Business Growth Points Matrix",
            labels=dict(x="Growth Lever", y="Product", color="CM Impact (%)")
        )
        
        fig.update_layout(
            height=400,
            width=800,
            title_x=0.5,
            title_font_size=18,
            title_font_color="#2c3e50",
            xaxis_title_font_size=14,
            yaxis_title_font_size=14
        )
        
        fig.update_traces(
            texttemplate='%{z:.1f}%',
            textfont=dict(size=12, color="black")
        )
        
        return fig
    except Exception as e:
        # English log for developers
        print(f"Error creating heatmap: {e}")
        return px.imshow([[0]], text_auto=True, title="Loading error")

# ============================================================================
# SENSITIVITY TABLE - COMPLETE WITH 13 COLUMNS
# ============================================================================

def create_sensitivity_table(product_name, sensitivity_data):
    """
    Creates the COMPLETE 13-column table for sensitivity analysis.
    All values are calculated DYNAMICALLY based on input data.
    Formulas used:
    - B = UA × C1
    - T = B × APC = UA × C1 × APC
    - CLTV = AOV × APC
    - LTV = C1 × CLTV
    - AC = UA × CPA
    - Revenue = T × AOV
    - CM = UA × (LTV - CPA)
    """
    
    product_data = None
    for prod, df in sensitivity_data:
        if prod == product_name:
            product_data = df.to_pandas()
            break
    
    if product_data is None:
        return html.Div("Data unavailable for this product")
    
    table_data = []
    
    for _, row in product_data.iterrows():
        scenario = row['Scenario']
        
        # Scenario mapping labels
        if scenario == 'Base Case':
            scenario_display = '📊 Base Case'
        elif 'UA' in scenario:
            scenario_display = '📈 UA (+15%)'
        elif 'C1' in scenario:
            scenario_display = '🔄 C1 (+15%)'
        elif 'AOV' in scenario:
            scenario_display = '💰 AOV (+15%)'
        elif 'APC' in scenario:
            scenario_display = '📚 APC (+15%)'
        elif 'CPA' in scenario:
            scenario_display = '💸 CPA (-15%)'
        else:
            scenario_display = scenario
        
        # ✅ BASE VALUES - direct from analysis
        ua_value = f"{int(row['UA']):,}"
        c1_value = row['C1']
        aov_value = format_number_2decimals(row['AOV'])
        apc_value = f"{row['APC']:.2f}"
        cpa_value = format_number_2decimals(row['CPA'])
        
        # ✅ DYNAMIC CALCULATIONS - extracted from rows
        b_value = f"{int(row['B']):,}" if 'B' in row else "0"
        t_value = f"{int(row['T']):,}" if 'T' in row else "0"
        cltv_value = format_number_2decimals(row['CLTV']) if 'CLTV' in row else "€0"
        ltv_value = format_number_2decimals(row['LTV']) if 'LTV' in row else "€0"
        ac_value = format_number_2decimals(row['AC']) if 'AC' in row else "€0"
        
        # ✅ CRITICAL CHECK - Revenue and CM must exist in the data
        revenue_value = format_number_2decimals(row['Revenue']) if 'Revenue' in row else "€0"
        cm_value = format_number_2decimals(row['CM']) if 'CM' in row else "€0"
        
        # ORDER IDENTICAL TO TABLE: UA | C1 | AOV | APC | CPA | B | T | CLTV | LTV | AC | Revenue | CM
        table_data.append({
            'Scenario': scenario_display,
            'UA': ua_value,
            'C1': c1_value,
            'AOV': aov_value,
            'APC': apc_value,
            'CPA': cpa_value,
            'B': b_value,
            'T': t_value,
            'CLTV': cltv_value,
            'LTV': ltv_value,
            'AC': ac_value,
            'Revenue': revenue_value,
            'CM': cm_value
        })
    
    return html.Div([
        html.H4(f"📊 Sensitivity Analysis: {product_name}", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '20px'}),
        
        dash_table.DataTable(
            id=f'sensitivity-table-{product_name.lower().replace(" ", "-")}',
            data=table_data,
            columns=[
                {'name': 'Scenario', 'id': 'Scenario', 'type': 'text'},
                {'name': 'UA', 'id': 'UA', 'type': 'text'},
                {'name': 'C1', 'id': 'C1', 'type': 'text'},
                {'name': 'AOV', 'id': 'AOV', 'type': 'text'},
                {'name': 'APC', 'id': 'APC', 'type': 'text'},
                {'name': 'CPA', 'id': 'CPA', 'type': 'text'},
                {'name': 'Buyers (B)', 'id': 'B', 'type': 'text'},
                {'name': 'Months (T)', 'id': 'T', 'type': 'text'},
                {'name': 'CLTV', 'id': 'CLTV', 'type': 'text'},
                {'name': 'LTV', 'id': 'LTV', 'type': 'text'},
                {'name': 'AC', 'id': 'AC', 'type': 'text'},
                {'name': 'Revenue', 'id': 'Revenue', 'type': 'text'},
                {'name': 'CM', 'id': 'CM', 'type': 'text'}
            ],
            style_table={
                'overflowX': 'auto',
                'borderRadius': '10px',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                'marginBottom': '30px'
            },
            style_cell={
                'textAlign': 'center',
                'padding': '10px 6px',
                'fontSize': '13px',
                'fontFamily': 'Arial, sans-serif',
                'minWidth': '70px'
            },
            style_header={
                'backgroundColor': '#2c3e50',
                'color': 'white',
                'fontWeight': 'bold',
                'textAlign': 'center',
                'border': '1px solid #34495e'
            },
            style_data={'border': '1px solid #ecf0f1'},
            style_data_conditional=[
                # Highlight Base Case Row
                {
                    'if': {'filter_query': '{Scenario} = "📊 Base Case"'},
                    'backgroundColor': '#f8f9fa',
                    'fontWeight': 'bold'
                },
                # Highlight CM Column
                {
                    'if': {'column_id': 'CM'},
                    'fontWeight': 'bold',
                    'backgroundColor': '#fef9e7'
                },
                # Highlight Revenue Column
                {
                    'if': {'column_id': 'Revenue'},
                    'fontWeight': 'bold'
                },
                # Color coding for percentages
                {
                    'if': {'column_id': 'C1', 'filter_query': '{C1} contains "%"'},
                    'color': '#27ae60'
                }
            ],
            style_cell_conditional=[
                {'if': {'column_id': 'Scenario'}, 'minWidth': '140px', 'textAlign': 'left', 'fontWeight': 'bold'},
                {'if': {'column_id': 'UA'}, 'textAlign': 'right'},
                {'if': {'column_id': 'C1'}, 'textAlign': 'center'},
                {'if': {'column_id': 'AOV'}, 'textAlign': 'right'},
                {'if': {'column_id': 'APC'}, 'textAlign': 'center'},
                {'if': {'column_id': 'CPA'}, 'textAlign': 'right'},
                {'if': {'column_id': 'B'}, 'textAlign': 'right'},
                {'if': {'column_id': 'T'}, 'textAlign': 'right'},
                {'if': {'column_id': 'CLTV'}, 'textAlign': 'right'},
                {'if': {'column_id': 'LTV'}, 'textAlign': 'right'},
                {'if': {'column_id': 'AC'}, 'textAlign': 'right'},
                {'if': {'column_id': 'Revenue'}, 'textAlign': 'right'},
                {'if': {'column_id': 'CM'}, 'textAlign': 'right', 'fontWeight': 'bold'}
            ],
            sort_action='none',
            page_action='none'
        )
    ])

# ============================================================================
# INTERPRETATION SECTION
# ============================================================================

def create_interpretation_section():
    """
    Creates the interpretation section for the VI.2 dashboard.
    """
    return html.Div([
        html.H4("📖 How to interpret the heatmap:", 
               style={'color': '#2c3e50', 'marginBottom': '15px', 'fontWeight': 'bold'}),
        
        html.Div([
            html.Div([
                html.Strong("🟢 Green colors: "),
                "High positive impact on profit. The darker the green, the stronger the impact."
            ], style={'marginBottom': '10px', 'color': '#27ae60'}),
            
            html.Div([
                html.Strong("🟡 Yellow colors: "),
                "Moderate impact (0-10%). Improvements bring profit, but not significantly."
            ], style={'marginBottom': '10px', 'color': '#f39c12'}),
            
            html.Div([
                html.Strong("🔴 Red colors: "),
                "Low or negative impact. Optimizing these metrics does not bring significant benefits."
            ], style={'marginBottom': '10px', 'color': '#e74c3c'}),
            
            html.Hr(style={'margin': '20px 0'}),
            
            html.H5("💡 Strategic Recommendations:", style={'marginBottom': '10px', 'color': '#2c3e50'}),
            
            html.Ul([
                html.Li([
                    html.Strong("Priority 1 - Magic Levers: "),
                    "C1 (Conversion) and APC (Retention) have a multiplier impact - optimize these first!"
                ], style={'marginBottom': '8px'}),
                
                html.Li([
                    html.Strong("Priority 2 - Cost Reduction: "),
                    "CPA has a direct impact on profit - especially effective for low-margin products."
                ], style={'marginBottom': '8px'}),
                
                html.Li([
                    html.Strong("Priority 3 - Value Growth: "),
                    "AOV and UA bring linear growth - invest in these after optimizing conversion."
                ], style={'marginBottom': '8px'})
            ])
        ], style={
            'lineHeight': '1.6',
            'padding': '20px',
            'backgroundColor': '#f8f9fa',
            'borderRadius': '10px',
            'border': '1px solid #dee2e6'
        })
    ])

# ============================================================================
# CONTROL TABS
# ============================================================================

def create_tabs():
    """
    Creates navigation tabs for switching between products.
    """
    return html.Div(
        id='vi2-tabs',
        style={'display': 'none'},
        children=[
            html.Div([
                html.Div("🌐 WEB DEVELOPER", id='vi2-tab-web', n_clicks=0, style={}),
                html.Div("📱 DIGITAL MARKETING", id='vi2-tab-digital', n_clicks=0, style={}),
                html.Div("🎨 UX/UI DESIGN", id='vi2-tab-ux', n_clicks=0, style={})
            ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '20px'})
        ]
    )

def get_active_tab(click_web, click_digital, click_ux):
    """
    Determines which tab is active based on clicks.
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        return 'Web Developer'
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'vi2-tab-web':
        return 'Web Developer'
    elif trigger_id == 'vi2-tab-digital':
        return 'Digital Marketing'
    elif trigger_id == 'vi2-tab-ux':
        return 'UX/UI Design'
    else:
        return 'Web Developer'

def get_tab_styles(active_tab):
    """
    Returns styles for the 3 tabs based on the active selection.
    """
    def create_style(product, active, color):
        return {
            'padding': '12px 24px',
            'margin': '0 5px',
            'backgroundColor': color if product == active else '#bdc3c7',
            'color': 'white',
            'borderRadius': '8px 8px 0 0',
            'cursor': 'pointer',
            'fontWeight': 'bold',
            'fontSize': '16px',
            'display': 'inline-block',
            'boxShadow': '0 -2px 5px rgba(0,0,0,0.05)',
            'border': 'none',
            'transition': 'all 0.3s',
            'opacity': '1' if product == active else '0.7',
            'transform': 'scale(1.02)' if product == active else 'scale(1)',
            'borderBottom': '3px solid white' if product == active else 'none'
        }
    
    style_web = create_style('Web Developer', active_tab, COLORS_PRODUCTS['Web Developer'])
    style_digital = create_style('Digital Marketing', active_tab, COLORS_PRODUCTS['Digital Marketing'])
    style_ux = create_style('UX/UI Design', active_tab, COLORS_PRODUCTS['UX/UI Design'])
    
    return style_web, style_digital, style_ux

# ============================================================================
# COMPLETE LAYOUT
# ============================================================================

def get_vi2_layout(active_tab, sensitivity_results, heatmap_df):
    """
    Returns the complete layout for the VI.2 section.
    """
    graphs = html.Div([
        html.H3("🔥 Business Growth Points Matrix", 
               style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '20px'}),
        dcc.Graph(figure=create_heatmap_figure(heatmap_df))
    ])
    
    tables = create_sensitivity_table(active_tab, sensitivity_results)
    
    conclusion = create_interpretation_section()
    
    return graphs, tables, conclusion