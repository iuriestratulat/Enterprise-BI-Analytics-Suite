"""
vi5_dashboard.py - Dashboard for VI.5 Hypothesis and testing method
Hypothesis framework and testing methodology for metric optimization
"""

import dash
from dash import dcc, html, dash_table
from ue_utils import COLORS_PRODUCTS

# ============================================================================
# DATA FOR SMART AND HADI - TRANSLATED TO ENGLISH
# ============================================================================

# 🌐 WEB DEVELOPER
SMART_WEB = {
    'specific': 'Optimize the sales script for the "Web Developer" product, emphasizing the long-term benefits of an IT career to justify the price point.',
    'measurable': 'Increase the C1 metric by at least 0.03%. Goal — growth from 0.75% to 0.78% and above.',
    'achievable': 'Realistic, as changing the speech script for managers does not require technical costs.',
    'relevant': 'Any increase in C1 for this product significantly affects Contribution Margin (CM).',
    'time_bound': 'The experiment will last 11 days, fitting into a two-week cycle.'
}

HADI_WEB = {
    'hypothesis': 'If we change the sales script highlighting the "employment guarantee", then C1 conversion will grow by at least 0.03%.',
    'action': '11-day A/B test: experimental group uses the new script, control group uses the standard one.',
    'data': 'Track UA and B for each group. Target — ~264 leads (132 per group).',
    'insight': 'If C1 ≥ 0.78% in the experimental group — implement the new script. If not — test another change.'
}

# 📱 DIGITAL MARKETING
SMART_DIGITAL = {
    'specific': 'Change the sales script for "Digital Marketing" by adding a section for proactive handling of price-related objections.',
    'measurable': 'Increase C1 by 0.04% (MDE). Goal — from 2.59% to 2.63% or higher.',
    'achievable': 'The goal is realistic — script change does not require technical resources.',
    'relevant': 'C1 growth has a direct positive impact on Revenue and CM.',
    'time_bound': 'The experiment will be conducted over 13 days.'
}

HADI_DIGITAL = {
    'hypothesis': 'If we add a section for proactive handling of price objections, then C1 conversion will increase.',
    'action': '13-day A/B test: Group A — old script, Group B — new script.',
    'data': 'Collect data daily: UA, B, C1. Sample size — ~323 leads per group.',
    'insight': 'If C1(B) > C1(A) with statistical significance — implement the new script.'
}

# 🎨 UX/UI DESIGN
SMART_UX = {
    'specific': 'Change the sales script for "UX/UI Design" by adding examples of successful alumni portfolios.',
    'measurable': 'Increase C1 by 0.04% (MDE). Goal — from 1.25% to 1.29% and higher.',
    'achievable': 'Alumni portfolios already exist — managers need to be trained.',
    'relevant': 'Conversion growth directly improves Unit Economics.',
    'time_bound': 'The experiment will last 10 days.'
}

HADI_UX = {
    'hypothesis': 'If we demonstrate visual "before and after" portfolios, then C1 conversion will grow by 0.04%.',
    'action': '10-day A/B test: half of the managers send portfolios.',
    'data': 'Sample size — about 247 leads total (124 per test branch).',
    'insight': 'If the portfolio variant shows a significant increase in C1 — implement the practice for everyone.'
}

# ============================================================================
# SMART CARD
# ============================================================================

def create_smart_card(smart_data, color):
    """
    Creates the SMART objectives card.
    """
    return html.Div([
        html.H4("🎯 SMART Objectives", style={
            'color': '#2c3e50', 
            'marginBottom': '20px',
            'borderBottom': f'3px solid {color}',
            'paddingBottom': '10px'
        }),
        html.Div([
            html.Div([
                html.Strong("S - Specific: "), 
                smart_data['specific']
            ], style={'marginBottom': '15px'}),
            
            html.Div([
                html.Strong("M - Measurable: "), 
                smart_data['measurable']
            ], style={'marginBottom': '15px'}),
            
            html.Div([
                html.Strong("A - Achievable: "), 
                smart_data['achievable']
            ], style={'marginBottom': '15px'}),
            
            html.Div([
                html.Strong("R - Relevant: "), 
                smart_data['relevant']
            ], style={'marginBottom': '15px'}),
            
            html.Div([
                html.Strong("T - Time-bound: "), 
                smart_data['time_bound']
            ], style={'marginBottom': '15px'})
        ], style={
            'padding': '20px',
            'backgroundColor': '#f8f9fa',
            'borderRadius': '10px',
            'border': f'2px solid {color}',
            'borderTop': f'5px solid {color}',
            'fontSize': '15px',
            'lineHeight': '1.6'
        })
    ])

# ============================================================================
# HADI CARD
# ============================================================================

def create_hadi_card(hadi_data, color):
    """
    Creates the HADI cycle card.
    """
    return html.Div([
        html.H4("🔄 HADI Cycle", style={
            'color': '#2c3e50', 
            'marginBottom': '20px',
            'borderBottom': f'3px solid {color}',
            'paddingBottom': '10px'
        }),
        html.Div([
            html.Div([
                html.Strong("H - Hypothesis: "), 
                hadi_data['hypothesis']
            ], style={'marginBottom': '15px'}),
            
            html.Div([
                html.Strong("A - Action: "), 
                hadi_data['action']
            ], style={'marginBottom': '15px'}),
            
            html.Div([
                html.Strong("D - Data: "), 
                hadi_data['data']
            ], style={'marginBottom': '15px'}),
            
            html.Div([
                html.Strong("I - Insight: "), 
                hadi_data['insight']
            ], style={'marginBottom': '15px'})
        ], style={
            'padding': '20px',
            'backgroundColor': '#f8f9fa',
            'borderRadius': '10px',
            'border': f'2px solid {color}',
            'borderTop': f'5px solid {color}',
            'fontSize': '15px',
            'lineHeight': '1.6'
        })
    ])

# ============================================================================
# PRODUCT TABS
# ============================================================================

def create_tabs():
    """
    Creates navigation tabs to switch between products.
    """
    return html.Div([
        html.H3("🎯 Hypothesis and Testing Framework", 
               style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '30px'}),
        
        html.Div([
            html.Div(
                "🌐 WEB DEVELOPER",
                id='vi5-tab-web',
                n_clicks=0,
                style={
                    'padding': '12px 24px',
                    'margin': '0 5px',
                    'backgroundColor': COLORS_PRODUCTS['Web Developer'],
                    'color': 'white',
                    'borderRadius': '8px 8px 0 0',
                    'cursor': 'pointer',
                    'fontWeight': 'bold',
                    'fontSize': '16px',
                    'display': 'inline-block',
                    'boxShadow': '0 -2px 5px rgba(0,0,0,0.05)',
                    'border': 'none',
                    'transition': 'all 0.3s',
                    'opacity': '1'
                }
            ),
            html.Div(
                "📱 DIGITAL MARKETING",
                id='vi5-tab-digital',
                n_clicks=0,
                style={
                    'padding': '12px 24px',
                    'margin': '0 5px',
                    'backgroundColor': COLORS_PRODUCTS['Digital Marketing'],
                    'color': 'white',
                    'borderRadius': '8px 8px 0 0',
                    'cursor': 'pointer',
                    'fontWeight': 'bold',
                    'fontSize': '16px',
                    'display': 'inline-block',
                    'boxShadow': '0 -2px 5px rgba(0,0,0,0.05)',
                    'border': 'none',
                    'transition': 'all 0.3s',
                    'opacity': '1'
                }
            ),
            html.Div(
                "🎨 UX/UI DESIGN",
                id='vi5-tab-ux',
                n_clicks=0,
                style={
                    'padding': '12px 24px',
                    'margin': '0 5px',
                    'backgroundColor': COLORS_PRODUCTS['UX/UI Design'],
                    'color': 'white',
                    'borderRadius': '8px 8px 0 0',
                    'cursor': 'pointer',
                    'fontWeight': 'bold',
                    'fontSize': '16px',
                    'display': 'inline-block',
                    'boxShadow': '0 -2px 5px rgba(0,0,0,0.05)',
                    'border': 'none',
                    'transition': 'all 0.3s',
                    'opacity': '1'
                }
            )
        ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '30px'}),
        
        html.Div(id='vi5-smart-hadi-content', style={'padding': '20px'})
    ])

# ============================================================================
# CONTENT FOR EACH PRODUCT
# ============================================================================

def get_web_content():
    """
    Returns content for Web Developer.
    """
    return html.Div([
        html.H3("🌐 Web Developer", style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '30px'}),
        html.Div([
            html.Div([
                create_smart_card(SMART_WEB, COLORS_PRODUCTS['Web Developer'])
            ], style={'flex': '1', 'margin': '10px'}),
            html.Div([
                create_hadi_card(HADI_WEB, COLORS_PRODUCTS['Web Developer'])
            ], style={'flex': '1', 'margin': '10px'})
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '20px'})
    ])

def get_digital_content():
    """
    Returns content for Digital Marketing.
    """
    return html.Div([
        html.H3("📱 Digital Marketing", style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '30px'}),
        html.Div([
            html.Div([
                create_smart_card(SMART_DIGITAL, COLORS_PRODUCTS['Digital Marketing'])
            ], style={'flex': '1', 'margin': '10px'}),
            html.Div([
                create_hadi_card(HADI_DIGITAL, COLORS_PRODUCTS['Digital Marketing'])
            ], style={'flex': '1', 'margin': '10px'})
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '20px'})
    ])

def get_ux_content():
    """
    Returns content for UX/UI Design.
    """
    return html.Div([
        html.H3("🎨 UX/UI Design", style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '30px'}),
        html.Div([
            html.Div([
                create_smart_card(SMART_UX, COLORS_PRODUCTS['UX/UI Design'])
            ], style={'flex': '1', 'margin': '10px'}),
            html.Div([
                create_hadi_card(HADI_UX, COLORS_PRODUCTS['UX/UI Design'])
            ], style={'flex': '1', 'margin': '10px'})
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '20px'})
    ])

# ============================================================================
# ACTIVE TAB DETERMINATION
# ============================================================================

def get_active_tab(click_web, click_digital, click_ux):
    """
    Determines which tab is active based on clicks.
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        return 'Web Developer'
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'vi5-tab-web':
        return 'Web Developer'
    elif trigger_id == 'vi5-tab-digital':
        return 'Digital Marketing'
    elif trigger_id == 'vi5-tab-ux':
        return 'UX/UI Design'
    else:
        return 'Web Developer'

def get_tab_content(active_tab):
    """
    Returns content for the active tab.
    """
    if active_tab == 'Web Developer':
        return get_web_content()
    elif active_tab == 'Digital Marketing':
        return get_digital_content()
    else:
        return get_ux_content()

# ============================================================================
# CONCLUSIONS AND METHODOLOGY
# ============================================================================

def create_conclusion_section():
    """
    Creates the conclusion section for VI.5.
    """
    return html.Div([
        html.H4("📋 Testing Methodology", 
               style={'color': '#2c3e50', 'marginBottom': '20px'}),
        html.P("HADI Framework and SMART objectives for each product:", 
               style={'marginBottom': '15px'}),
        html.Ul([
            html.Li([
                html.Strong("🌐 Web Developer: "),
                "Employment guarantee, 11 days, +0.03% C1"
            ], style={
                'marginBottom': '10px', 
                'padding': '8px', 
                'backgroundColor': '#ebf5fb', 
                'borderRadius': '5px'
            }),
            html.Li([
                html.Strong("📱 Digital Marketing: "),
                "Price objection handling, 13 days, +0.04% C1"
            ], style={
                'marginBottom': '10px', 
                'padding': '8px', 
                'backgroundColor': '#fef5e7', 
                'borderRadius': '5px'
            }),
            html.Li([
                html.Strong("🎨 UX/UI Design: "),
                "Visual portfolio, 10 days, +0.04% C1"
            ], style={
                'marginBottom': '10px', 
                'padding': '8px', 
                'backgroundColor': '#f4ecf7', 
                'borderRadius': '5px'
            })
        ], style={'listStyleType': 'none', 'paddingLeft': '0'})
    ])

# ============================================================================
# COMPLETE LAYOUT
# ============================================================================

def get_vi5_layout():
    """
    Returns the complete layout for VI.5.
    """
    graphs = html.Div([
        create_tabs()
    ])
    
    tables = ""
    
    conclusion = create_conclusion_section()
    
    return graphs, tables, conclusion