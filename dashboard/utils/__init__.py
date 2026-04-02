"""
Dashboard utilities package.

This package contains utility modules for the Streamlit dashboard:
- data_loader: Functions to load data and models with caching
- visualizations: Functions to create interactive Plotly charts
"""

from .data_loader import (
    load_latest_data,
    load_model,
    load_raw_nifty_data,
    load_raw_institutional_data,
    get_data_summary,
    clear_cache
)

from .visualizations import (
    plot_nifty_trend,
    plot_institutional_flows,
    plot_correlation_heatmap,
    plot_prediction_gauge,
    plot_volatility_trend,
    plot_cumulative_flows,
    plot_return_distribution,
    plot_feature_importance
)

__all__ = [
    # Data loader functions
    'load_latest_data',
    'load_model',
    'load_raw_nifty_data',
    'load_raw_institutional_data',
    'get_data_summary',
    'clear_cache',
    
    # Visualization functions
    'plot_nifty_trend',
    'plot_institutional_flows',
    'plot_correlation_heatmap',
    'plot_prediction_gauge',
    'plot_volatility_trend',
    'plot_cumulative_flows',
    'plot_return_distribution',
    'plot_feature_importance'
]
