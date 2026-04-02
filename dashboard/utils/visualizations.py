"""
Visualization Utilities for Dashboard

This module provides functions to create interactive Plotly charts
for the Streamlit dashboard.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional, List
import numpy as np


def plot_nifty_trend(
    df: pd.DataFrame,
    date_col: str = 'Date',
    price_col: str = 'Close',
    title: str = 'NIFTY Index Trend'
) -> go.Figure:
    """
    Create an interactive line chart showing NIFTY trend over time.
    
    Args:
        df: DataFrame with NIFTY data
        date_col: Name of date column
        price_col: Name of price column
        title: Chart title
        
    Returns:
        Plotly Figure object
    """
    fig = go.Figure()
    
    # Add closing price line
    fig.add_trace(go.Scatter(
        x=df[date_col],
        y=df[price_col],
        mode='lines',
        name='NIFTY Close',
        line=dict(color='#1f77b4', width=2),
        hovertemplate='<b>Date:</b> %{x}<br><b>Close:</b> ₹%{y:,.2f}<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Price (₹)',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def plot_institutional_flows(
    df: pd.DataFrame,
    date_col: str = 'Date',
    fii_col: str = 'FII_Net',
    dii_col: str = 'DII_Net',
    title: str = 'FII vs DII Net Flows'
) -> go.Figure:
    """
    Create a dual-axis chart comparing FII and DII flows.
    
    Args:
        df: DataFrame with institutional flow data
        date_col: Name of date column
        fii_col: Name of FII net flow column
        dii_col: Name of DII net flow column
        title: Chart title
        
    Returns:
        Plotly Figure object
    """
    fig = go.Figure()
    
    # Add FII flows
    fig.add_trace(go.Scatter(
        x=df[date_col],
        y=df[fii_col],
        mode='lines',
        name='FII Net Flow',
        line=dict(color='#2ca02c', width=2),
        hovertemplate='<b>Date:</b> %{x}<br><b>FII Net:</b> ₹%{y:,.0f} Cr<extra></extra>'
    ))
    
    # Add DII flows
    fig.add_trace(go.Scatter(
        x=df[date_col],
        y=df[dii_col],
        mode='lines',
        name='DII Net Flow',
        line=dict(color='#ff7f0e', width=2),
        hovertemplate='<b>Date:</b> %{x}<br><b>DII Net:</b> ₹%{y:,.0f} Cr<extra></extra>'
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Net Flow (₹ Crores)',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def plot_correlation_heatmap(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    title: str = 'Correlation Heatmap'
) -> go.Figure:
    """
    Create a correlation heatmap for specified columns.
    
    Args:
        df: DataFrame with data
        columns: List of column names to include (if None, uses numeric columns)
        title: Chart title
        
    Returns:
        Plotly Figure object
    """
    # Select columns
    if columns is None:
        # Use all numeric columns
        numeric_df = df.select_dtypes(include=[np.number])
    else:
        numeric_df = df[columns]
    
    # Compute correlation matrix
    corr_matrix = numeric_df.corr()
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation"),
        hovertemplate='<b>%{x}</b> vs <b>%{y}</b><br>Correlation: %{z:.3f}<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title=title,
        template='plotly_white',
        height=600,
        xaxis=dict(tickangle=-45),
        yaxis=dict(tickangle=0)
    )
    
    return fig


def plot_prediction_gauge(
    probability: float,
    title: str = 'Market Direction Prediction'
) -> go.Figure:
    """
    Create a gauge chart showing prediction probability.
    
    Args:
        probability: Prediction probability (0-1)
        title: Chart title
        
    Returns:
        Plotly Figure object
    """
    # Determine color based on probability
    if probability >= 0.6:
        color = "#2ca02c"  # Green for bullish
        prediction = "UP"
    elif probability <= 0.4:
        color = "#d62728"  # Red for bearish
        prediction = "DOWN"
    else:
        color = "#ff7f0e"  # Orange for neutral
        prediction = "NEUTRAL"
    
    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=probability * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"{title}<br><span style='font-size:0.8em;color:gray'>Prediction: {prediction}</span>"},
        number={'suffix': "%", 'font': {'size': 40}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 40], 'color': '#ffcccc'},
                {'range': [40, 60], 'color': '#ffffcc'},
                {'range': [60, 100], 'color': '#ccffcc'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 50
            }
        }
    ))
    
    # Update layout
    fig.update_layout(
        height=400,
        template='plotly_white'
    )
    
    return fig


def plot_volatility_trend(
    df: pd.DataFrame,
    date_col: str = 'Date',
    volatility_col: str = 'Volatility',
    title: str = 'Market Volatility Trend'
) -> go.Figure:
    """
    Create a line chart showing volatility over time.
    
    Args:
        df: DataFrame with volatility data
        date_col: Name of date column
        volatility_col: Name of volatility column
        title: Chart title
        
    Returns:
        Plotly Figure object
    """
    fig = go.Figure()
    
    # Add volatility line
    fig.add_trace(go.Scatter(
        x=df[date_col],
        y=df[volatility_col],
        mode='lines',
        name='Volatility',
        line=dict(color='#d62728', width=2),
        fill='tozeroy',
        fillcolor='rgba(214, 39, 40, 0.2)',
        hovertemplate='<b>Date:</b> %{x}<br><b>Volatility:</b> %{y:.2f}%<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Volatility (%)',
        hovermode='x unified',
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    return fig


def plot_cumulative_flows(
    df: pd.DataFrame,
    date_col: str = 'Date',
    fii_col: str = 'FII_Net',
    dii_col: str = 'DII_Net',
    title: str = 'Cumulative Institutional Flows'
) -> go.Figure:
    """
    Create a chart showing cumulative institutional flows over time.
    
    Args:
        df: DataFrame with institutional flow data
        date_col: Name of date column
        fii_col: Name of FII net flow column
        dii_col: Name of DII net flow column
        title: Chart title
        
    Returns:
        Plotly Figure object
    """
    # Calculate cumulative flows
    df_copy = df.copy()
    df_copy['FII_Cumulative'] = df_copy[fii_col].cumsum()
    df_copy['DII_Cumulative'] = df_copy[dii_col].cumsum()
    
    fig = go.Figure()
    
    # Add FII cumulative
    fig.add_trace(go.Scatter(
        x=df_copy[date_col],
        y=df_copy['FII_Cumulative'],
        mode='lines',
        name='FII Cumulative',
        line=dict(color='#2ca02c', width=2),
        hovertemplate='<b>Date:</b> %{x}<br><b>FII Cumulative:</b> ₹%{y:,.0f} Cr<extra></extra>'
    ))
    
    # Add DII cumulative
    fig.add_trace(go.Scatter(
        x=df_copy[date_col],
        y=df_copy['DII_Cumulative'],
        mode='lines',
        name='DII Cumulative',
        line=dict(color='#ff7f0e', width=2),
        hovertemplate='<b>Date:</b> %{x}<br><b>DII Cumulative:</b> ₹%{y:,.0f} Cr<extra></extra>'
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Cumulative Flow (₹ Crores)',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def plot_return_distribution(
    df: pd.DataFrame,
    return_col: str = 'Daily_Return',
    title: str = 'Market Return Distribution'
) -> go.Figure:
    """
    Create a histogram showing the distribution of market returns.
    
    Args:
        df: DataFrame with return data
        return_col: Name of return column
        title: Chart title
        
    Returns:
        Plotly Figure object
    """
    # Remove NaN values
    returns = df[return_col].dropna()
    
    # Create histogram
    fig = go.Figure(data=[go.Histogram(
        x=returns,
        nbinsx=50,
        marker_color='#1f77b4',
        opacity=0.7,
        name='Returns',
        hovertemplate='<b>Return Range:</b> %{x:.2f}%<br><b>Count:</b> %{y}<extra></extra>'
    )])
    
    # Add mean line
    mean_return = returns.mean()
    fig.add_vline(
        x=mean_return,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Mean: {mean_return:.2f}%",
        annotation_position="top"
    )
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title='Daily Return (%)',
        yaxis_title='Frequency',
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    return fig


def plot_feature_importance(
    feature_names: List[str],
    importance_values: List[float],
    title: str = 'Feature Importance'
) -> go.Figure:
    """
    Create a horizontal bar chart showing feature importance.
    
    Args:
        feature_names: List of feature names
        importance_values: List of importance values
        title: Chart title
        
    Returns:
        Plotly Figure object
    """
    # Sort by importance
    sorted_indices = np.argsort(importance_values)
    sorted_features = [feature_names[i] for i in sorted_indices]
    sorted_importance = [importance_values[i] for i in sorted_indices]
    
    # Create horizontal bar chart
    fig = go.Figure(go.Bar(
        x=sorted_importance,
        y=sorted_features,
        orientation='h',
        marker_color='#1f77b4',
        hovertemplate='<b>%{y}</b><br>Importance: %{x:.4f}<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title='Importance',
        yaxis_title='Feature',
        template='plotly_white',
        height=max(400, len(feature_names) * 25),
        showlegend=False
    )
    
    return fig
