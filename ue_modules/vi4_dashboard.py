"""
vi4_dashboard.py - Dashboard for VI.4 Which product metrics will influence CM
A/B Testing analysis for sample size determination
"""

import dash
from dash import dcc, html, dash_table
import pandas as pd
from ue_utils import format_number_no_currency_no_decimals

# ============================================================================
# INTERACTIVE CONTROLS
# ============================================================================

def create_controls():
    """
    Creates interactive controls for A/B testing parameters.
    """
    return html.Div(
        id='vi4-controls',
        style={'display': 'none'},
        children=[
            html.Div([
                html.H4("🎯 A/B Testing Parameters Configuration", 
                       style={'color': '#2c3e50', 'marginBottom': '20px'}),
                
                # REQUIRED_DAYS
                html.Div([
                    html.Label("📅 Max Test Days (REQUIRED_DAYS):", 
                              style={'fontWeight': 'bold'}),
                    dcc.Slider(
                        id='vi4-required-days',
                        min=7,
                        max=30,
                        step=1,
                        value=14,
                        marks={7: '7', 14: '14', 21: '21', 30: '30'}
                    )
                ], style={'marginBottom': '20px'}),
                
                # Target Effect (X) for each product
                html.Div([
                    html.Div([
                        html.Label("🌐 Web Developer X:", style={'fontWeight': 'bold'}),
                        dcc.Slider(
                            id='vi4-x-web',
                            min=0.005,
                            max=0.10,
                            step=0.005,
                            value=0.02,
                            marks={0.01: '1%', 0.02: '2%', 0.04: '4%', 
                                  0.06: '6%', 0.08: '8%', 0.10: '10%'}
                        )
                    ], style={'flex': '1', 'margin': '10px'}),
                    
                    html.Div([
                        html.Label("📱 Digital Marketing X:", style={'fontWeight': 'bold'}),
                        dcc.Slider(
                            id='vi4-x-dig',
                            min=0.005,
                            max=0.10,
                            step=0.005,
                            value=0.04,
                            marks={0.01: '1%', 0.02: '2%', 0.04: '4%', 
                                  0.06: '6%', 0.08: '8%', 0.10: '10%'}
                        )
                    ], style={'flex': '1', 'margin': '10px'}),
                    
                    html.Div([
                        html.Label("🎨 UX/UI Design X:", style={'fontWeight': 'bold'}),
                        dcc.Slider(
                            id='vi4-x-ux',
                            min=0.005,
                            max=0.10,
                            step=0.005,
                            value=0.025,
                            marks={0.01: '1%', 0.02: '2%', 0.04: '4%', 
                                  0.06: '6%', 0.08: '8%', 0.10: '10%'}
                        )
                    ], style={'flex': '1', 'margin': '10px'})
                ], style={'display': 'flex', 'flexWrap': 'wrap'})
            ], style={
                'padding': '20px',
                'backgroundColor': '#f0f8ff',
                'borderRadius': '10px',
                'margin': '20px'
            })
        ]
    )

# ============================================================================
# A/B TESTING RESULTS TABLE
# ============================================================================

def create_ab_table(ab_results, daily_traffic, required_days):
    """
    Creates the table with A/B testing analysis results.
    Transposed format: Metric | Web Developer | Digital Marketing | UX/UI Design
    """
    if ab_results is None:
        return html.Div("Data unavailable for A/B testing analysis")
    
    try:
        # Convert to pandas DataFrame
        df = ab_results.to_pandas()
        
        # Add row with daily traffic for context
        traffic_row = pd.DataFrame([{
            'Metric': 'Daily Traffic',
            'Web Developer': format_number_no_currency_no_decimals(daily_traffic),
            'Digital Marketing': format_number_no_currency_no_decimals(daily_traffic),
            'UX/UI Design': format_number_no_currency_no_decimals(daily_traffic)
        }])
        
        df = pd.concat([traffic_row, df], ignore_index=True)
        
        return html.Div([
            html.H4("🧪 A/B Testing Analysis - Sample Size", 
                   style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '20px'}),
            
            html.Div([
                html.P(f"📊 Max Testing Period: {required_days} days", 
                      style={'textAlign': 'center', 'fontSize': '16px', 
                            'fontWeight': 'bold', 'color': '#3498db'}),
                html.P("Formula: n = (16 * p * (1-p)) / X² | Power = 80%, Confidence = 95%", 
                      style={'textAlign': 'center', 'fontSize': '14px', 'color': '#7f8c8d'})
            ], style={'marginBottom': '20px'}),
            
            dash_table.DataTable(
                id='vi4-ab-table',
                data=df.to_dict('records'),
                columns=[
                    {'name': 'Metric', 'id': 'Metric', 'type': 'text'},
                    {'name': 'Web Developer', 'id': 'Web Developer', 'type': 'text'},
                    {'name': 'Digital Marketing', 'id': 'Digital Marketing', 'type': 'text'},
                    {'name': 'UX/UI Design', 'id': 'UX/UI Design', 'type': 'text'}
                ],
                style_table={
                    'overflowX': 'auto',
                    'borderRadius': '10px',
                    'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                    'marginBottom': '30px'
                },
                style_cell={
                    'textAlign': 'center',
                    'padding': '12px 8px',
                    'fontSize': '14px',
                    'fontFamily': 'Arial, sans-serif',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'minWidth': '120px'
                },
                style_header={
                    'backgroundColor': '#2c3e50',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                    'border': '1px solid #34495e',
                    'padding': '12px 8px'
                },
                style_data={
                    'border': '1px solid #ecf0f1'
                },
                style_data_conditional=[
                    # Highlight Daily Traffic Row
                    {
                        'if': {'filter_query': '{Metric} = "Daily Traffic"'},
                        'backgroundColor': '#f8f9fa',
                        'fontWeight': 'bold'
                    },
                    # Highlight UA_global Row
                    {
                        'if': {'filter_query': '{Metric} = "UA_global"'},
                        'backgroundColor': '#ebf5fb'
                    },
                    # Status OK - green
                    {
                        'if': {
                            'column_id': 'Web Developer', 
                            'filter_query': '{Metric} = "Status" && {Web Developer} contains "OK"'
                        },
                        'color': '#27ae60',
                        'fontWeight': 'bold'
                    },
                    {
                        'if': {
                            'column_id': 'Digital Marketing',
                            'filter_query': '{Metric} = "Status" && {Digital Marketing} contains "OK"'
                        },
                        'color': '#27ae60',
                        'fontWeight': 'bold'
                    },
                    {
                        'if': {
                            'column_id': 'UX/UI Design',
                            'filter_query': '{Metric} = "Status" && {UX/UI Design} contains "OK"'
                        },
                        'color': '#27ae60',
                        'fontWeight': 'bold'
                    },
                    # Status TOO LONG - red
                    {
                        'if': {
                            'column_id': 'Web Developer',
                            'filter_query': '{Metric} = "Status" && {Web Developer} contains "TOO LONG"'
                        },
                        'color': '#e74c3c',
                        'fontWeight': 'bold'
                    },
                    {
                        'if': {
                            'column_id': 'Digital Marketing',
                            'filter_query': '{Metric} = "Status" && {Digital Marketing} contains "TOO LONG"'
                        },
                        'color': '#e74c3c',
                        'fontWeight': 'bold'
                    },
                    {
                        'if': {
                            'column_id': 'UX/UI Design',
                            'filter_query': '{Metric} = "Status" && {UX/UI Design} contains "TOO LONG"'
                        },
                        'color': '#e74c3c',
                        'fontWeight': 'bold'
                    }
                ],
                style_cell_conditional=[
                    {
                        'if': {'column_id': 'Metric'},
                        'minWidth': '200px',
                        'textAlign': 'left',
                        'fontWeight': 'bold',
                        'backgroundColor': '#f8f9fa'
                    }
                ],
                sort_action='none',
                page_action='none'
            )
        ])
        
    except Exception as e:
        print(f"Error creating A/B testing table: {e}")
        return html.Div(f"Error processing data: {str(e)}")

# ============================================================================
# INTERPRETATION AND RECOMMENDATIONS
# ============================================================================

def create_interpretation_section():
    """
    Creates the interpretation section for A/B testing.
    """
    return html.Div([
        html.H4("📖 How to interpret A/B Testing results:", 
               style={'color': '#2c3e50', 'marginBottom': '15px', 'fontWeight': 'bold'}),
        
        html.Div([
            html.Div([
                html.Strong("✅ Status OK: "),
                "The test can be completed within the set day limit with the current target effect."
            ], style={'marginBottom': '10px', 'color': '#27ae60'}),
            
            html.Div([
                html.Strong("⚠️ Status TOO LONG: "),
                "The test requires more time than the limit. Adjust X (target effect) to fit the test."
            ], style={'marginBottom': '10px', 'color': '#e74c3c'}),
            
            html.Div([
                html.Strong("💡 Suggestion: "),
                "Recommended X value to fit the test within the day limit."
            ], style={'marginBottom': '20px', 'color': '#3498db'}),
            
            html.Hr(style={'margin': '20px 0'}),
            
            html.H5("🧮 Calculation Formula:", style={'marginBottom': '10px', 'color': '#2c3e50'}),
            html.P("n = (16 * p * (1-p)) / X²", 
                  style={'fontSize': '18px', 'fontWeight': 'bold', 'textAlign': 'center'}),
            html.P("where:", style={'marginTop': '10px'}),
            html.Ul([
                html.Li("n = sample size per variant (control or test)"),
                html.Li("p = current conversion rate"),
                html.Li("X = minimum detectable effect (target effect)"),
                html.Li("Statistical Power = 80% (standard)"),
                html.Li("Confidence Level = 95% (α = 0.05)")
            ]),
            
            html.H5("📊 Total Traffic = n × 2 (control + test)", 
                   style={'marginTop': '20px', 'marginBottom': '10px', 'color': '#2c3e50'}),
            html.P("Days Needed = Total Traffic / Daily Traffic", style={'fontStyle': 'italic'})
        ], style={
            'lineHeight': '1.6',
            'padding': '20px',
            'backgroundColor': '#f8f9fa',
            'borderRadius': '10px',
            'border': '1px solid #dee2e6'
        })
    ])

# ============================================================================
# METRICS INFLUENCING CM
# ============================================================================

def create_metrics_impact_section():
    """
    Creates the section about product metrics influencing CM and testing methods.
    """
    return html.Div([
        html.H4("📊 Product Metrics Influencing CM", 
               style={'color': '#2c3e50', 'marginBottom': '20px', 'fontWeight': 'bold'}),
        
        html.Div([
            # Conversion Rate (C1)
            html.Div([
                html.H5("🔄 Conversion Rate (C1)", style={'color': '#27ae60'}),
                html.P("Direct impact on LTV and implicitly on CM. A 1% increase in conversion can generate +X% in CM."),
                html.P(html.Strong("A/B Testing:"), " Landing page optimization, sales script A/B testing.")
            ], style={
                'flex': '1', 'padding': '20px', 'backgroundColor': '#e8f8f5',
                'borderRadius': '10px', 'margin': '10px', 'border': '1px solid #27ae60'
            }),
            
            # Average Order Value (AOV)
            html.Div([
                html.H5("💰 Average Order Value (AOV)", style={'color': '#e67e22'}),
                html.P("Increasing average order value boosts CLTV and LTV. Direct impact on revenue."),
                html.P(html.Strong("A/B Testing:"), " Upselling, premium packages, payment options.")
            ], style={
                'flex': '1', 'padding': '20px', 'backgroundColor': '#fef5e7',
                'borderRadius': '10px', 'margin': '10px', 'border': '1px solid #e67e22'
            }),
            
            # Average Purchase Count (APC)
            html.Div([
                html.H5("📚 Average Purchase Count (APC)", style={'color': '#9b59b6'}),
                html.P("Student retention increases total revenue. A client who studies longer generates more revenue."),
                html.P(html.Strong("A/B Testing:"), " Gamification, community, 1-on-1 mentorship.")
            ], style={
                'flex': '1', 'padding': '20px', 'backgroundColor': '#f4ecf7',
                'borderRadius': '10px', 'margin': '10px', 'border': '1px solid #9b59b6'
            }),
            
            # Cost Per Acquisition (CPA)
            html.Div([
                html.H5("💸 Cost Per Acquisition (CPA)", style={'color': '#e74c3c'}),
                html.P("Reducing CPA directly increases CM. Especially effective for low-margin products."),
                html.P(html.Strong("A/B Testing:"), " Campaign optimization, targeting, acquisition channel.")
            ], style={
                'flex': '1', 'padding': '20px', 'backgroundColor': '#fadbd8',
                'borderRadius': '10px', 'margin': '10px', 'border': '1px solid #e74c3c'
            })
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '20px'})
    ])

# ============================================================================
# CONCLUSIONS
# ============================================================================

def create_conclusion_section():
    """
    Creates the conclusion section for VI.4.
    """
    return html.Div([
        html.H4("📊 Metrics Influencing CM", 
               style={'color': '#2c3e50', 'marginBottom': '15px'}),
        html.P("This analysis determines the feasibility of A/B testing:"),
        html.Ul([
            html.Li("✅ Status OK: The test can be completed within the day limit"),
            html.Li("⚠️ Status TOO LONG: Adjust X to fit the test duration"),
            html.Li("🎯 Target Effect (X): The smaller the X, the larger the required sample size")
        ])
    ])

# ============================================================================
# COMPLETE LAYOUT
# ============================================================================

def get_vi4_layout(df_transposed, daily_traffic, required_days):
    """
    Returns the complete layout for VI.4.
    """
    graphs = html.Div([
        create_ab_table(df_transposed, daily_traffic, required_days)  # ← Title is already in create_ab_table
    ])
    
    tables = ""
    
    conclusion = html.Div([
        create_conclusion_section(),
        html.Hr(style={'margin': '30px 0', 'borderColor': '#bdc3c7'}),
        create_interpretation_section(),
        html.Hr(style={'margin': '30px 0', 'borderColor': '#bdc3c7'}),
        create_metrics_impact_section()
    ])
    
    return graphs, tables, conclusion