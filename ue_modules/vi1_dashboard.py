"""
vi1_dashboard.py - Dashboard for VI.1 Unit Economics
FINAL VERSION - IDENTICAL ORDER in cards and table
"""

import dash
from dash import html, dash_table
import pandas as pd
from ue_utils import (
    format_number_2decimals, format_number_no_currency_no_decimals, format_integer,
    get_metrics_dict, cm_to_number, COLORS_PRODUCTS
)

# ============================================================================
# KPI CONFIGURATION - IDENTICAL ORDER AS IN THE TABLE
# ============================================================================

# 🔥 MANDATORY ORDER: UA | C1 | AOV | APC | CPA | B | T | CLTV | LTV | AC | Revenue | CM
KPI_ORDER = ['UA', 'C1', 'AOV', 'APC', 'CPA', 'B', 'T', 'CLTV', 'LTV', 'AC', 'Revenue', 'CM']

KPI_CONFIG = {
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

# ============================================================================
# KPI CARDS - IDENTICAL ORDER AS THE TABLE
# ============================================================================

def create_kpi_cards(metrics_dict):
    """
    Creates KPI cards for main metrics.
    ORDER: UA | C1 | AOV | APC | CPA | B | T | CLTV | LTV | AC | Revenue | CM
    """
    kpi_cards = []
    
    for metric in KPI_ORDER:
        if metric in metrics_dict:
            config = KPI_CONFIG[metric]
            original_value = metrics_dict[metric]
            
            # Specific formatting based on metric type
            if metric == 'B':
                display_value = format_number_no_currency_no_decimals(original_value)
            elif metric in ['C1', 'APC']:
                display_value = original_value
            elif metric in ['UA', 'T']:
                display_value = format_integer(original_value)
            else:
                display_value = format_number_2decimals(original_value)
            
            card = html.Div([
                html.Div([
                    html.Span(config['icon'], style={'fontSize': '20px', 'marginRight': '8px'}),
                    html.Span(config['title'], style={'fontSize': '14px', 'fontWeight': '600', 'color': '#2c3e50'})
                ], style={'marginBottom': '8px'}),
                html.Div(display_value, style={
                    'margin': '5px 0', 
                    'color': config['color'],
                    'fontSize': '22px',
                    'fontWeight': 'bold',
                    'whiteSpace': 'nowrap',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis'
                }),
                html.Div(metric, style={
                    'fontSize': '11px',
                    'color': '#7f8c8d',
                    'textTransform': 'uppercase',
                    'letterSpacing': '1px'
                })
            ], style={
                'padding': '12px 8px',
                'margin': '0 5px',
                'backgroundColor': 'white',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'flex': '1',
                'minWidth': '110px',
                'maxWidth': '130px',
                'textAlign': 'center',
                'borderTop': f'3px solid {config["color"]}'
            })
            kpi_cards.append(card)
    
    return html.Div(kpi_cards, style={
        'display': 'flex', 
        'flexDirection': 'row',
        'flexWrap': 'nowrap',
        'justifyContent': 'space-between',
        'gap': '8px',
        'margin': '15px 0',
        'padding': '5px',
        'overflowX': 'auto',
        'minWidth': '100%'
    })

# ============================================================================
# PRODUCT TABLE - CORRECT COLUMN ORDER
# ============================================================================

def create_product_table(df_by_product):
    """
    Creates the table for Unit Economics per Product.
    - FIXED PRODUCT ORDER: Web Developer, Digital Marketing, UX/UI Design
    - COLUMN ORDER: Product | UA | C1 | AOV | APC | CPA | B | T | CLTV | LTV | AC | Revenue | CM
    """
    if df_by_product is None:
        return html.Div()
    
    df_pd = df_by_product.to_pandas()
    
    # 🔥 FIXED PRODUCT ORDER
    product_order = ['Web Developer', 'Digital Marketing', 'UX/UI Design']
    df_pd['Product'] = pd.Categorical(df_pd['Product'], categories=product_order, ordered=True)
    df_pd = df_pd.sort_values('Product')
    
    table_data = []
    for _, row in df_pd.iterrows():
        table_data.append({
            'Product': row['Product'],
            'UA': format_integer(row['UA']),
            'C1': row['C1'],
            'AOV': format_number_2decimals(f"€{row['AOV']:,.2f}"),
            'APC': f"{row['APC']:.2f}",
            'CPA': format_number_2decimals(f"€{row['CPA']:,.2f}"),
            'B': format_integer(row['B']),
            'T': format_integer(row['T']),
            'CLTV': format_number_2decimals(f"€{row['CLTV']:,.2f}"),
            'LTV': format_number_2decimals(f"€{row['LTV']:,.2f}"),
            'AC': format_number_2decimals(f"€{row['AC']:,.2f}"),
            'Revenue': format_number_2decimals(f"€{row['Revenue']:,.2f}"),
            'CM': format_number_2decimals(f"€{row['CM']:,.2f}")
        })
    
    # 🔥 CORRECT COLUMN ORDER
    columns = [
        {'name': 'Product', 'id': 'Product', 'type': 'text'},
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
    ]
    
    # Conditional coloring based on CM
    style_data_conditional = [
        {'if': {'column_id': 'CM'}, 'fontWeight': 'bold'},
        {'if': {'column_id': 'Product'}, 'fontWeight': 'bold', 'backgroundColor': '#f8f9fa'},
        {'if': {'column_id': 'AC'}, 'fontWeight': 'bold'},
        {'if': {'column_id': 'Revenue'}, 'fontWeight': 'bold'},
    ]
    
    for idx, row in enumerate(table_data):
        try:
            cm_num = cm_to_number(row['CM'])
            if cm_num > 5000:
                bg_color = '#d5f4e6'
            elif cm_num > 0:
                bg_color = '#e8f8f5'
            elif cm_num == 0:
                bg_color = '#fef9e7'
            else:
                bg_color = '#fadbd8'
            style_data_conditional.append({
                'if': {'row_index': idx},
                'backgroundColor': bg_color
            })
        except:
            pass
    
    # Column alignment styling
    style_cell_conditional = [
        {'if': {'column_id': 'Product'}, 'minWidth': '180px', 'textAlign': 'left', 'fontWeight': 'bold'},
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
    ]
    
    return html.Div([
        html.H4("📊 Unit Economics per Product", style={
            'color': '#2c3e50', 'marginBottom': '20px', 'textAlign': 'center'
        }),
        dash_table.DataTable(
            id='product-ue-table',
            data=table_data,
            columns=columns,
            style_table={
                'overflowX': 'auto',
                'borderRadius': '10px',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                'marginBottom': '30px'
            },
            style_cell={
                'textAlign': 'left',
                'padding': '12px 8px',
                'fontSize': '14px',
                'fontFamily': 'Arial, sans-serif',
                'whiteSpace': 'normal',
                'height': 'auto',
                'minWidth': '80px',
                'maxWidth': '150px'
            },
            style_header={
                'backgroundColor': '#2c3e50',
                'color': 'white',
                'fontWeight': 'bold',
                'textAlign': 'center',
                'border': '1px solid #34495e',
                'padding': '12px 8px'
            },
            style_data={'border': '1px solid #ecf0f1'},
            style_data_conditional=style_data_conditional,
            style_cell_conditional=style_cell_conditional,
            sort_action='native',
            filter_action='native',
            page_action='native',
            page_size=5
        )
    ], style={'marginTop': '20px', 'marginBottom': '30px'})

# ============================================================================
# INSIGHTS AND RECOMMENDATIONS
# ============================================================================

def create_insights(metrics_dict, df_by_product):
    """
    Creates the section for insights and recommendations.
    """
    if df_by_product is None:
        return html.Div()
    
    df_pd = df_by_product.to_pandas()
    df_pd['CM_Numeric'] = df_pd['CM'].apply(cm_to_number)
    
    best_idx = df_pd['CM_Numeric'].idxmax()
    worst_idx = df_pd['CM_Numeric'].idxmin()
    
    best_product = df_pd.loc[best_idx]
    worst_product = df_pd.loc[worst_idx]
    
    avg_conversion = df_pd['C1'].apply(lambda x: float(str(x).strip('%')) / 100).mean()
    
    return html.Div([
        html.H4("📊 Insights and Recommendations", style={
            'color': '#2c3e50', 'marginBottom': '20px',
            'borderBottom': '2px solid #3498db', 'paddingBottom': '10px'
        }),
        html.Div([
            # Best Performing Product
            html.Div([
                html.H5("🏆 Best Performing Product", style={'color': '#27ae60'}),
                html.P(f"{best_product['Product']}", style={'fontSize': '18px', 'fontWeight': 'bold'}),
                html.P(f"Contribution Margin: {format_number_2decimals(f'€{best_product["CM"]}')}"),
                html.P(f"Conversion Rate: {best_product['C1']}"),
                html.P(f"Lifetime Value: {format_number_2decimals(f'€{best_product["LTV"]}')}"),
                html.P("👉 Recommendation: Allocate additional budget to this product")
            ], style={'padding': '15px', 'backgroundColor': '#d5f4e6', 'borderRadius': '10px',
                     'margin': '5px', 'flex': '1', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
            
            # Opportunity for Improvement
            html.Div([
                html.H5("⚠️ Opportunity for Improvement", style={'color': '#e74c3c'}),
                html.P(f"{worst_product['Product']}", style={'fontSize': '18px', 'fontWeight': 'bold'}),
                html.P(f"Contribution Margin: {format_number_2decimals(f'€{worst_product["CM"]}')}"),
                html.P(f"Conversion Rate: {worst_product['C1']}"),
                html.P(f"Cost Per Acquisition: {format_number_2decimals(f'€{worst_product["CPA"]}')}"),
                html.P("👉 Recommendation: Optimize CPA and conversion")
            ], style={'padding': '15px', 'backgroundColor': '#fadbd8', 'borderRadius': '10px',
                     'margin': '5px', 'flex': '1', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
            
            # Business Health
            html.Div([
                html.H5("📊 Business Health", style={'color': '#3498db'}),
                html.P(f"Total Revenue: {format_number_2decimals(metrics_dict.get('Revenue', '€0'))}"),
                html.P(f"Total CM: {format_number_2decimals(metrics_dict.get('CM', '€0'))}"),
                html.P(f"Avg. Conversion: {avg_conversion:.2%}"),
                html.P(f"Lead to Buyer: {metrics_dict.get('UA', '0')} → "
                      f"{format_number_no_currency_no_decimals(metrics_dict.get('B', '0'))}"),
                html.P("👉 Recommendation: Focus on increasing LTV")
            ], style={'padding': '15px', 'backgroundColor': '#d6eaf8', 'borderRadius': '10px',
                     'margin': '5px', 'flex': '1', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '15px'})
    ])

# ============================================================================
# METRIC INTERPRETATION
# ============================================================================

def create_interpretation():
    """
    Creates the section for metric interpretation with full formulas.
    """
    return html.Div([
        html.H4("📖 Metric Interpretation:", 
               style={'color': '#2c3e50', 'marginTop': '30px', 
                     'marginBottom': '20px', 'fontWeight': 'bold'}),
        
        html.Div([
            # User Acquisition
            html.Div([
                html.Strong("UA (User Acquisition): "),
                "Total number of unique leads/contacts. ",
                html.Strong("Formula: UA = COUNTUNIQUE('deals'['Contact Name'])")
            ], style={'marginBottom': '12px'}),
            
            # Conversion Rate
            html.Div([
                html.Strong("C1 (Conversion Rate): "),
                "Percentage of leads that become paying customers. ",
                html.Strong("Formula: C1 = B / UA")
            ], style={'marginBottom': '12px'}),
            
            # Average Order Value
            html.Div([
                html.Strong("AOV (Average Order Value): "),
                "Average value per month of study. ",
                html.Strong("Formula: AOV = Revenue / T")
            ], style={'marginBottom': '12px'}),
            
            # Average Purchase Count
            html.Div([
                html.Strong("APC (Average Purchase Count): "),
                "Average number of study months per customer. ",
                html.Strong("Formula: APC = T / B")
            ], style={'marginBottom': '12px'}),
            
            # Cost Per Acquisition
            html.Div([
                html.Strong("CPA (Cost Per Acquisition): "),
                "Average cost per lead acquisition. ",
                html.Strong("Formula: CPA = AC / UA")
            ], style={'marginBottom': '12px'}),
            
            # Buyers
            html.Div([
                html.Strong("B (Buyers): "),
                "Number of unique customers who made a payment. ",
                html.Strong("Formula: B = COUNTUNIQUE('deals'['Contact Name']) WHERE Stage = 'Payment Done'")
            ], style={'marginBottom': '12px'}),
            
            # Transactions
            html.Div([
                html.Strong("T (Transactions): "),
                "Total study months generated by paying customers. ",
                html.Strong("Formula: T = SUM('deals'['Months of study']) WHERE Stage = 'Payment Done'")
            ], style={'marginBottom': '12px'}),
            
            # Customer Lifetime Value
            html.Div([
                html.Strong("CLTV (Customer Lifetime Value): "),
                "Total expected value from a single customer. ",
                html.Strong("Formula: CLTV = AOV × APC"),
                " (Assumes COGS = 0 and 1COGS = 0. Real Formula: (AOV-COGS)*APC-1COGS)"
            ], style={'marginBottom': '12px'}),
            
            # Lifetime Value
            html.Div([
                html.Strong("LTV (Lifetime Value): "),
                "Total expected value from a lead. ",
                html.Strong("Formula: LTV = C1 × CLTV")
            ], style={'marginBottom': '12px'}),
            
            # Acquisition Cost
            html.Div([
                html.Strong("AC (Acquisition Cost): "),
                "Total marketing cost for lead acquisition. ",
                html.Strong("Formula: AC = SUM('spend'['Spend'])")
            ], style={'marginBottom': '12px'}),
            
            # Revenue
            html.Div([
                html.Strong("Revenue: "),
                "Total earned revenue, calculated based on initial payments and monthly installments. ",
                html.Strong("Formula: Revenue = SUM(Initial_Amount_Paid + ((Offer_Total - Initial) / (Duration - 1)) × (Months - 1))")
            ], style={'marginBottom': '12px'}),
            
            # Contribution Margin
            html.Div([
                html.Strong("CM (Contribution Margin): "),
                "Profit after deducting acquisition costs. Key profitability indicator. ",
                html.Strong("Formula: CM = UA × (LTV - CPA)")
            ], style={'marginBottom': '12px'})
            
        ], style={
            'lineHeight': '1.6',
            'padding': '20px',
            'backgroundColor': '#f8f9fa',
            'borderRadius': '10px',
            'border': '1px solid #dee2e6'
        })
    ], style={'marginTop': '30px'})

# ============================================================================
# COMPLETE LAYOUT
# ============================================================================

def get_vi1_layout(df_overview, df_by_product):
    """
    Returns the complete layout for VI.1.
    """
    metrics_dict = {}
    if df_overview is not None:
        df_pd = df_overview.to_pandas()
        for _, row in df_pd.iterrows():
            metrics_dict[row['Metric']] = row['Value']
    
    graphs = html.Div([
        html.H3("📋 Unit Economics Overview", 
               style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '15px'}),
        create_kpi_cards(metrics_dict)
    ])
    
    tables = create_product_table(df_by_product)
    
    conclusion = html.Div([
        create_insights(metrics_dict, df_by_product),
        create_interpretation()
    ])
    
    return graphs, tables, conclusion