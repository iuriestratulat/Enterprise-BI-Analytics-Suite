"""
ue_utils.py - Common utility functions for all Unit Economics modules
"""

import polars as pl
import pandas as pd
import numpy as np

# ============================================================================
# NUMBER FORMATTING WITH 2 DECIMALS
# ============================================================================

def format_number_2decimals(value):
    """
    Formats numbers with 2 decimals and K/M suffixes.
    Example: 15234.56 -> €15.23K, 1234567.89 -> €1.23M
    """
    try:
        if isinstance(value, str):
            if '€' in value and ('K' in value or 'M' in value):
                return value
            clean_value = value.replace('€', '').replace(',', '')
            value = float(clean_value)
        
        if value >= 1_000_000:
            return f"€{value/1_000_000:.2f}M"
        elif value >= 1_000:
            return f"€{value/1_000:.2f}K"
        else:
            return f"€{value:.2f}"
    except:
        return str(value)

def format_number_no_currency_no_decimals(value):
    """
    Formats numbers without € symbol and without decimals.
    Example: 845 -> 845, 15234 -> 15,234
    """
    try:
        if isinstance(value, str):
            clean_value = value.replace('€', '').replace(',', '')
            if 'K' in clean_value:
                return clean_value
            elif 'M' in clean_value:
                return clean_value
            else:
                value = float(clean_value)
        
        return f"{int(value):,}"
    except:
        return str(value)

def format_integer(value):
    """
    Formats integers with thousands separator.
    Example: 15234 -> 15,234
    """
    try:
        if isinstance(value, str):
            value = float(value.replace(',', ''))
        return f"{int(value):,}"
    except:
        return str(value)

def format_percentage(value):
    """
    Formats values as percentage.
    Example: 0.1234 -> 12.34%
    """
    try:
        if isinstance(value, str):
            if '%' in value:
                return value
            value = float(value)
        return f"{value:.2%}"
    except:
        return str(value)

# ============================================================================
# COMMON CALCULATIONS
# ============================================================================

def get_daily_traffic(df_deals):
    """
    Calculates the average daily traffic from the data.
    """
    try:
        ua_global = df_deals["Contact_Name"].n_unique()
        min_d = df_deals["Created_Time"].min()
        max_d = df_deals["Created_Time"].max()
        days_total = (max_d - min_d).days
        return ua_global / days_total if days_total > 0 else 0
    except:
        return 0

def get_metrics_dict(df_overview):
    """
    Converts the overview DataFrame into a dictionary.
    """
    metrics_dict = {}
    if df_overview is not None:
        try:
            df_pd = df_overview.to_pandas()
            for _, row in df_pd.iterrows():
                metrics_dict[row['Metric']] = row['Value']
        except:
            pass
    return metrics_dict

def cm_to_number(cm_str):
    """
    Converts a CM string (e.g., €12.5K) into a numeric value.
    """
    try:
        val = str(cm_str).replace('€', '').replace(',', '')
        if 'K' in val:
            return float(val.replace('K', '')) * 1000
        elif 'M' in val:
            return float(val.replace('M', '')) * 1000000
        else:
            return float(val)
    except:
        return 0

# ============================================================================
# STYLES AND CONSTANTS
# ============================================================================

def get_default_tab_style():
    """
    Default style for tabs (hidden).
    """
    return {'display': 'none'}

# Colors for VI.3 Metrics Tree Levels
COLORS_VI3 = {
    'nivel1': '#dedaff',  # Lavender
    'nivel2': '#c6dcff',  # Light Blue
    'nivel3': '#adf0c7',  # Mint
    'nivel4': '#f8d3af',  # Peach
    'nivel5': '#fff6b6',  # Cream
}

# Colors for Products
COLORS_PRODUCTS = {
    'Web Developer': '#3498db',   # Blue
    'Digital Marketing': '#e67e22', # Orange
    'UX/UI Design': '#9b59b6',    # Purple
}

# KPI Configuration for VI.1
KPI_CONFIG = {
    'UA': {'color': '#3498db', 'icon': '👥', 'title': 'User Acquisition'},
    'B': {'color': '#2ecc71', 'icon': '🛒', 'title': 'Buyers'},
    'C1': {'color': '#9b59b6', 'icon': '📈', 'title': 'Conversion Rate'},
    'T': {'color': '#e67e22', 'icon': '🔄', 'title': 'Total Months'},
    'Revenue': {'color': '#f1c40f', 'icon': '💰', 'title': 'Total Revenue'},
    'AOV': {'color': '#1abc9c', 'icon': '💵', 'title': 'Avg Order Value'},
    'APC': {'color': '#34495e', 'icon': '📊', 'title': 'Avg Purchase Count'},
    'CPA': {'color': '#e74c3c', 'icon': '💸', 'title': 'Cost Per Acquisition'},
    'CLTV': {'color': '#d35400', 'icon': '🏆', 'title': 'Customer LTV'},
    'LTV': {'color': '#27ae60', 'icon': '🎯', 'title': 'Lifetime Value'},
    'CM': {'color': '#8e44ad', 'icon': '💪', 'title': 'Contribution Margin'},
}

# Order of KPIs for display consistency
KPI_ORDER = ['UA', 'B', 'C1', 'T', 'Revenue', 'AOV', 'APC', 'CPA', 'CLTV', 'LTV', 'CM']