"""
vi3_dashboard.py - Dashboard for VI.3 Metrics tree
"""

import dash
from dash import dcc, html
import base64
from pathlib import Path
from ue_utils import COLORS_VI3

# ============================================================================
# IMAGE LOADING
# ============================================================================

def load_metrics_tree_image():
    """
    Loads the metrics_tree.png image and converts it to base64 string.
    """
    image_path = Path("metrics_tree.png")
    
    if not image_path.exists():
        return None
    
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        return f"data:image/png;base64,{encoded_string}"
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

def create_image_section():
    """
    Creates the section containing the metrics tree image.
    """
    encoded_image = load_metrics_tree_image()
    
    if encoded_image:
        return html.Div([
            html.H3("🌳 Unit Economics Metrics Tree", 
                   style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '20px'}),
            html.Div([
                html.Img(src=encoded_image, style={
                    'width': '100%', 
                    'maxWidth': '1200px', 
                    'height': 'auto',
                    'display': 'block', 
                    'margin': '0 auto', 
                    'borderRadius': '10px',
                    'boxShadow': '0 4px 8px rgba(0,0,0,0.1)'
                })
            ], style={'textAlign': 'center', 'padding': '20px'})
        ])
    else:
        return html.Div([
            html.H3("🌳 Unit Economics Metrics Tree", 
                   style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '20px'}),
            html.Div([
                html.H4("⚠️ Image metrics_tree.png not found", 
                       style={'color': '#e74c3c', 'textAlign': 'center'}),
                html.P("Please place the metrics_tree.png file in the same directory.", 
                      style={'textAlign': 'center', 'color': '#7f8c8d'})
            ])
        ])

# ============================================================================
# LEVEL-BY-LEVEL EXPLANATIONS - NO GRAY BACKGROUND
# ============================================================================

def create_nivel1_section():
    """Level 1 - Business KPI - CM"""
    return html.Div([
        html.H5("🥇 Level 1 - Business KPI", 
               style={'color': '#2c3e50', 'marginBottom': '10px', 'fontWeight': 'bold'}),
        html.Div([
            html.Strong("CM (Contribution Margin): "),
            "Profit after deducting acquisition costs. The key indicator of business profitability. ",
            "Formula: CM = UA × (LTV - CPA)"
        ], style={'padding': '10px 5px'})
    ], style={'marginBottom': '20px', 'padding': '20px', 
             'backgroundColor': COLORS_VI3['nivel1'], 
             'borderRadius': '10px', 'border': '1px solid #d0c4e5', 
             'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'})

def create_nivel2_section():
    """Level 2 - Financial Metrics - Revenue"""
    return html.Div([
        html.H5("🥈 Level 2 - Financial Metrics", 
               style={'color': '#2c3e50', 'marginBottom': '10px', 'fontWeight': 'bold'}),
        html.Div([
            html.Strong("Revenue: "),
            "The final financial indicator. Total revenue collected from customers."
        ], style={'padding': '10px 5px'})
    ], style={'marginBottom': '20px', 'padding': '20px', 
             'backgroundColor': COLORS_VI3['nivel2'], 
             'borderRadius': '10px', 'border': '1px solid #b0c8e5', 
             'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'})

def create_nivel3_section():
    """Level 3 - Decision Metrics - UA, CPA, C1, AOV, APC"""
    return html.Div([
        html.H5("🥉 Level 3 - Decision Metrics", 
               style={'color': '#2c3e50', 'marginBottom': '15px', 'fontWeight': 'bold'}),
        html.Div([
            html.Div([html.Strong("UA: "), "User Acquisition - Total number of unique leads/contacts"], 
                    style={'marginBottom': '12px'}),
            html.Div([html.Strong("CPA: "), "Cost Per Acquisition - Average cost to acquire a single lead. Formula: CPA = AC / UA"], 
                    style={'marginBottom': '12px'}),
            html.Div([html.Strong("C1: "), "Conversion Rate - Percentage of leads that become paying customers. Formula: C1 = B / UA (lead → customer)"], 
                    style={'marginBottom': '12px'}),
            html.Div([html.Strong("AOV: "), "Average Order Value - Average value per study month. Formula: AOV = Revenue / T"], 
                    style={'marginBottom': '12px'}),
            html.Div([html.Strong("APC: "), "Average Purchase Count - Average number of study months per customer. Formula: APC = T / B"], 
                    style={'marginBottom': '0px'})
        ], style={'padding': '5px'})
    ], style={'marginBottom': '20px', 'padding': '20px', 
             'backgroundColor': COLORS_VI3['nivel3'], 
             'borderRadius': '10px', 'border': '1px solid #8ed6a8', 
             'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'})

def create_nivel4_section():
    """Level 4 - Product Metrics - T, AC, CLTV, B, LTV"""
    return html.Div([
        html.H5("📦 Level 4 - Product Metrics", 
               style={'color': '#2c3e50', 'marginBottom': '15px', 'fontWeight': 'bold'}),
        html.Div([
            html.Div([html.Strong("T: "), "Transactions - Total study months generated by paying customers."], 
                    style={'marginBottom': '12px'}),
            html.Div([html.Strong("AC: "), "Acquisition Cost - Total acquisition cost from marketing campaigns."], 
                    style={'marginBottom': '12px'}),
            html.Div([html.Strong("CLTV: "), "Customer Lifetime Value - Total expected value from a single customer. Formula: CLTV = AOV × APC"], 
                    style={'marginBottom': '12px'}),
            html.Div([html.Strong("B: "), "Buyers - Number of unique customers who made a payment."], 
                    style={'marginBottom': '12px'}),
            html.Div([html.Strong("LTV: "), "Lifetime Value - Total expected value from a single lead. Formula: LTV = C1 × CLTV"], 
                    style={'marginBottom': '0px'})
        ], style={'padding': '5px'})
    ], style={'marginBottom': '20px', 'padding': '20px', 
             'backgroundColor': COLORS_VI3['nivel4'], 
             'borderRadius': '10px', 'border': '1px solid #e6b88a', 
             'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'})

def create_nivel5_section():
    """Level 5 - Atomic Metrics - raw data"""
    return html.Div([
        html.H5("🔬 Level 5 - Atomic Metrics", 
               style={'color': '#2c3e50', 'marginBottom': '15px', 'fontWeight': 'bold'}),
        html.P(
            "Raw data from the database, the primary source for all calculations:",
            style={'fontSize': '14px', 'color': '#2c3e50', 'marginBottom': '15px'}
        ),
        html.Div([
            html.Div([
                html.Span("• Contact Name  ", style={'marginRight': '20px'}),
                html.Span("• Stage  ", style={'marginRight': '20px'}),
                html.Span("• Initial Amount Paid  ", style={'marginRight': '20px'}),
                html.Span("• Spend  ", style={'marginRight': '20px'}),
                html.Span("• Months of study", style={'marginRight': '20px'}),
            ], style={'marginBottom': '10px'}),
            html.Div([
                html.Span("• Offer Total Amount  ", style={'marginRight': '20px'}),
                html.Span("• Course duration  ", style={'marginRight': '20px'}),
                html.Span("• Product", style={'marginRight': '20px'}),
            ])
        ])
    ], style={'marginBottom': '20px', 'padding': '20px', 
             'backgroundColor': COLORS_VI3['nivel5'], 
             'borderRadius': '10px', 'border': '1px solid #e6dc8a', 
             'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'})

def create_explanations_section():
    """
    Creates the complete explanation section for all levels.
    """
    return html.Div([
        html.H4("📖 Metric Interpretation:", 
               style={'color': '#2c3e50', 'marginBottom': '20px', 'fontWeight': 'bold'}),
        html.Div([
            create_nivel1_section(),
            create_nivel2_section(),
            create_nivel3_section(),
            create_nivel4_section(),
            create_nivel5_section()
        ])
    ])

# ============================================================================
# MATHEMATICAL FORMULAS AND EXAMPLE
# ============================================================================

def create_formulas_section():
    """
    Creates the section with mathematical relationships and calculation example.
    """
    return html.Div([
        html.H4("🧮 Mathematical Relationships Between Metrics", 
               style={'color': '#2c3e50', 'marginBottom': '20px', 'fontWeight': 'bold'}),
        
        html.Div([
            # Fundamental Formulas
            html.Div([
                html.H5("Fundamental Formulas:", style={'color': '#3498db', 'marginBottom': '15px'}),
                html.Ul([
                    html.Li("C1 = B / UA", style={'marginBottom': '8px', 'fontSize': '16px'}),
                    html.Li("AOV = Revenue / T", style={'marginBottom': '8px', 'fontSize': '16px'}),
                    html.Li("APC = T / B", style={'marginBottom': '8px', 'fontSize': '16px'}),
                    html.Li("CPA = AC / UA", style={'marginBottom': '8px', 'fontSize': '16px'}),
                    html.Li("CLTV = AOV × APC", style={'marginBottom': '8px', 'fontSize': '16px'}),
                    html.Li("LTV = C1 × CLTV", style={'marginBottom': '8px', 'fontSize': '16px'}),
                    html.Li("CM = UA × (LTV - CPA)", style={'marginBottom': '8px', 'fontSize': '16px', 'fontWeight': 'bold'})
                ], style={'listStyleType': 'none', 'paddingLeft': '0'})
            ], style={
                'padding': '20px',
                'backgroundColor': '#ebf5fb',
                'borderRadius': '10px',
                'flex': '1',
                'margin': '10px',
                'border': '1px solid #b0c8e5'
            }),
            
            # Calculation Example
            html.Div([
                html.H5("Calculation Example:", style={'color': '#e67e22', 'marginBottom': '15px'}),
                html.P("For a product with:", style={'marginBottom': '10px', 'fontWeight': 'bold'}),
                html.Ul([
                    html.Li("UA = 100 leads", style={'marginBottom': '5px'}),
                    html.Li("B = 20 customers", style={'marginBottom': '5px'}),
                    html.Li("Revenue = €10,000", style={'marginBottom': '5px'}),
                    html.Li("T = 100 months", style={'marginBottom': '5px'}),
                    html.Li("AC = €5,000", style={'marginBottom': '15px'})
                ], style={'listStyleType': 'none', 'paddingLeft': '0'}),
                html.Div([
                    html.Div("→ C1 = 20%", style={'marginBottom': '8px', 'padding': '5px'}),
                    html.Div("→ AOV = €100", style={'marginBottom': '8px', 'padding': '5px'}),
                    html.Div("→ APC = 5 months", style={'marginBottom': '8px', 'padding': '5px'}),
                    html.Div("→ CPA = €50", style={'marginBottom': '8px', 'padding': '5px'}),
                    html.Div("→ CLTV = €500", style={'marginBottom': '8px', 'padding': '5px'}),
                    html.Div("→ LTV = €100", style={'marginBottom': '8px', 'padding': '5px'}),
                    html.Div("→ CM = €5,000", style={'padding': '8px', 'backgroundColor': '#fef9e7', 'borderRadius': '5px', 'fontWeight': 'bold'})
                ])
            ], style={
                'padding': '20px',
                'backgroundColor': '#fef5e7',
                'borderRadius': '10px',
                'flex': '1',
                'margin': '10px',
                'border': '1px solid #e6b88a'
            })
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '20px'})
    ])

# ============================================================================
# NEW DROP-DOWN SECTION: MATHEMATICAL RELATIONSHIPS & CALCULATION EXAMPLE
# ============================================================================

def create_mathematical_relationships_section():
    """
    Creates a collapsible drop-down section containing formulas and a calculation example.
    """
    return html.Details([
        html.Summary(
            "🧮 Mathematical Relationships Between Metrics",
            style={
                'fontSize': '18px',
                'fontWeight': 'bold',
                'color': '#2c3e50',
                'cursor': 'pointer',
                'padding': '10px',
                'backgroundColor': '#eaeded',
                'borderRadius': '5px',
                'marginBottom': '15px'
            }
        ),
        html.Div([
            # Container 1: Fundamental Formulas
            html.Div([
                html.H5("Fundamental Formulas:", style={'fontWeight': 'bold', 'color': '#2c3e50', 'borderBottom': '1px solid #bdc3c7', 'paddingBottom': '5px'}),
                html.Pre(
                    "C1 = B / UA\n"
                    "AOV = Revenue / T\n"
                    "APC = T / B\n"
                    "CPA = AC / UA\n"
                    "CLTV = AOV × APC\n"
                    "LTV = C1 × CLTV\n"
                    "CM = UA × (LTV - CPA)",
                    style={
                        'fontFamily': 'monospace',
                        'fontSize': '14px',
                        'lineHeight': '1.6',
                        'backgroundColor': '#ffffff',
                        'padding': '15px',
                        'borderRadius': '5px',
                        'border': '1px solid #e2e8f0'
                    }
                )
            ], style={
                'flex': '1',
                'minWidth': '300px',
                'margin': '10px',
                'backgroundColor': '#f8f9fa',
                'padding': '15px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
            }),

            # Container 2: Calculation Example
            html.Div([
                html.H5("Calculation Example:", style={'fontWeight': 'bold', 'color': '#2c3e50', 'borderBottom': '1px solid #bdc3c7', 'paddingBottom': '5px'}),
                html.Pre(
                    "For a product with:\n"
                    "UA = 100 leads\n"
                    "B = 20 customers\n"
                    "Revenue = €10,000\n"
                    "T = 100 months\n"
                    "AC = €5,000\n\n"
                    "→ C1 = 20%\n"
                    "→ AOV = €100\n"
                    "→ APC = 5 months\n"
                    "→ CPA = €50\n"
                    "→ CLTV = €500\n"
                    "→ LTV = €100\n"
                    "→ CM = €5,000",
                    style={
                        'fontFamily': 'monospace',
                        'fontSize': '14px',
                        'lineHeight': '1.6',
                        'backgroundColor': '#ffffff',
                        'padding': '15px',
                        'borderRadius': '5px',
                        'border': '1px solid #e2e8f0'
                    }
                )
            ], style={
                'flex': '1',
                'minWidth': '300px',
                'margin': '10px',
                'backgroundColor': '#f8f9fa',
                'padding': '15px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
            })
        ], style={
            'display': 'flex',
            'flexWrap': 'wrap',
            'justifyContent': 'space-between',
            'marginTop': '10px'
        })
    ], style={
        'border': '1px solid #d5dbdb',
        'borderRadius': '5px',
        'padding': '10px',
        'marginTop': '20px',
        'backgroundColor': '#fcfcfc'
    })

# ============================================================================
# CONCLUSIONS AND SUMMARY
# ============================================================================

def create_conclusion_section():
    """
    Creates the conclusion section for VI.3.
    """
    return html.Div([
        html.H4("🌳 Unit Economics Metrics Tree", 
               style={'color': '#2c3e50', 'marginBottom': '15px'}),
        html.P("This diagram shows the hierarchical relationship between all metrics, from atomic data to key business indicators."),
        html.P("Each level has a specific color to facilitate identification:"),
        html.Ul([
            html.Li("🥇 Level 1 - Business KPI: CM (Contribution Margin) - #dedaff", 
                   style={'backgroundColor': '#dedaff', 'padding': '5px 10px', 'borderRadius': '5px', 'marginBottom': '5px'}),
            html.Li("🥈 Level 2 - Financial Metrics: Revenue - #c6dcff", 
                   style={'backgroundColor': '#c6dcff', 'padding': '5px 10px', 'borderRadius': '5px', 'marginBottom': '5px'}),
            html.Li("🥉 Level 3 - Decision Metrics: UA, CPA, C1, AOV, APC - #adf0c7", 
                   style={'backgroundColor': '#adf0c7', 'padding': '5px 10px', 'borderRadius': '5px', 'marginBottom': '5px'}),
            html.Li("📦 Level 4 - Product Metrics: T, AC, CLTV, B, LTV - #f8d3af", 
                   style={'backgroundColor': '#f8d3af', 'padding': '5px 10px', 'borderRadius': '5px', 'marginBottom': '5px'}),
            html.Li("🔬 Level 5 - Atomic Metrics: raw data - #fff6b6", 
                   style={'backgroundColor': '#fff6b6', 'padding': '5px 10px', 'borderRadius': '5px'})
        ])
    ])

# ============================================================================
# COMPLETE LAYOUT
# ============================================================================

def get_vi3_layout():
    """
    Returns the complete layout for VI.3.
    """
    graphs = html.Div([
        create_image_section(),
        html.Hr(style={'margin': '40px 0', 'borderColor': '#bdc3c7'}),
        create_explanations_section(),
        html.Hr(style={'margin': '40px 0', 'borderColor': '#bdc3c7'}),
        create_formulas_section()
    ])
    
    tables = ""
    
    conclusion = create_conclusion_section()
    
    return graphs, tables, conclusion