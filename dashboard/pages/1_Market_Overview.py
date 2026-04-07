"""
Market Overview Page

This page displays NIFTY index trends, key market statistics, and volatility analysis.
It provides a comprehensive view of the current market state and historical trends.
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to import utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import load_latest_data
from utils.visualizations import (
    plot_nifty_trend,
    plot_volatility_trend,
    plot_return_distribution
)

# Configure page
st.set_page_config(
    page_title="Market Overview - Smart Money Intelligence",
    page_icon=None,
    layout="wide"
)

# Page header
st.title("Market Overview")
st.markdown("---")

# Load data
with st.spinner("Loading market data..."):
    df = load_latest_data()

if df is None or df.empty:
    st.error("Unable to load market data. Please ensure the data pipeline has been run.")
    st.info("Run `python scripts/run_pipeline.py` to generate processed data.")
    st.stop()

# Ensure Date column is datetime
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')

# Date range selector in sidebar
st.sidebar.header("Date Range Filter")

# Get min and max dates
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()

# Default to last 1 year
default_start = max(min_date, (datetime.now() - timedelta(days=365)).date())

# Date range inputs
start_date = st.sidebar.date_input(
    "Start Date",
    value=default_start,
    min_value=min_date,
    max_value=max_date
)

end_date = st.sidebar.date_input(
    "End Date",
    value=max_date,
    min_value=min_date,
    max_value=max_date
)

# Validate date range
if start_date > end_date:
    st.sidebar.error("Start date must be before end date!")
    st.stop()

# Filter data by date range
df_filtered = df[
    (df['Date'].dt.date >= start_date) & 
    (df['Date'].dt.date <= end_date)
].copy()

if df_filtered.empty:
    st.warning("No data available for the selected date range. Please adjust the dates.")
    st.stop()

# Display date range info
st.sidebar.success(f"Showing data from {start_date} to {end_date}")
st.sidebar.info(f"Total trading days: {len(df_filtered)}")

# Key Statistics Section
st.header("Key Market Statistics")

# Calculate statistics
current_price = df_filtered['Close'].iloc[-1]
previous_price = df_filtered['Close'].iloc[0]
ytd_return = ((current_price - previous_price) / previous_price) * 100

# Get current volatility (most recent value)
current_volatility = df_filtered['Volatility'].iloc[-1] if 'Volatility' in df_filtered.columns else 0

# Calculate additional statistics
highest_price = df_filtered['Close'].max()
lowest_price = df_filtered['Close'].min()
avg_volume = df_filtered['Volume'].mean() if 'Volume' in df_filtered.columns else 0

# Display statistics in columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Current Price",
        value=f"₹{current_price:,.2f}",
        delta=f"{ytd_return:+.2f}%"
    )

with col2:
    st.metric(
        label="Period Return",
        value=f"{ytd_return:+.2f}%",
        delta=f"₹{current_price - previous_price:+,.2f}"
    )

with col3:
    st.metric(
        label="Current Volatility",
        value=f"{current_volatility:.2f}%",
        delta=None
    )

with col4:
    st.metric(
        label="Avg Daily Volume",
        value=f"{avg_volume/1e6:.1f}M",
        delta=None
    )

# Additional statistics in second row
col5, col6, col7, col8 = st.columns(4)

with col5:
    st.metric(
        label="Highest Price",
        value=f"₹{highest_price:,.2f}",
        delta=None
    )

with col6:
    st.metric(
        label="Lowest Price",
        value=f"₹{lowest_price:,.2f}",
        delta=None
    )

with col7:
    # Calculate average daily return
    avg_return = df_filtered['Daily_Return'].mean() if 'Daily_Return' in df_filtered.columns else 0
    st.metric(
        label="Avg Daily Return",
        value=f"{avg_return:.2f}%",
        delta=None
    )

with col8:
    # Calculate number of positive days
    positive_days = (df_filtered['Daily_Return'] > 0).sum() if 'Daily_Return' in df_filtered.columns else 0
    positive_pct = (positive_days / len(df_filtered)) * 100
    st.metric(
        label="Positive Days",
        value=f"{positive_pct:.1f}%",
        delta=f"{positive_days}/{len(df_filtered)} days"
    )

st.markdown("---")

# NIFTY Trend Chart
st.header("NIFTY Index Trend")

# Create the trend chart
fig_trend = plot_nifty_trend(
    df_filtered,
    date_col='Date',
    price_col='Close',
    title=f'NIFTY Index Trend ({start_date} to {end_date})'
)

st.plotly_chart(fig_trend, use_container_width=True)

# Add insights below the chart
with st.expander("Trend Analysis Insights"):
    # Calculate trend statistics
    price_change = current_price - previous_price
    price_change_pct = ytd_return
    
    # Determine trend
    if price_change_pct > 5:
        trend = "**Strong Uptrend**"
        trend_color = "green"
    elif price_change_pct > 0:
        trend = "**Mild Uptrend**"
        trend_color = "lightgreen"
    elif price_change_pct > -5:
        trend = "**Mild Downtrend**"
        trend_color = "orange"
    else:
        trend = "**Strong Downtrend**"
        trend_color = "red"
    
    st.markdown(f"**Overall Trend:** {trend}")
    st.markdown(f"- Price moved from **₹{previous_price:,.2f}** to **₹{current_price:,.2f}**")
    st.markdown(f"- Absolute change: **₹{price_change:+,.2f}**")
    st.markdown(f"- Percentage change: **{price_change_pct:+.2f}%**")
    st.markdown(f"- Trading range: **₹{lowest_price:,.2f}** to **₹{highest_price:,.2f}**")

st.markdown("---")

# Volatility Analysis
st.header("Volatility Analysis")

if 'Volatility' in df_filtered.columns:
    # Create volatility trend chart
    fig_volatility = plot_volatility_trend(
        df_filtered,
        date_col='Date',
        volatility_col='Volatility',
        title=f'Market Volatility Trend ({start_date} to {end_date})'
    )
    
    st.plotly_chart(fig_volatility, use_container_width=True)
    
    # Volatility statistics
    with st.expander("Volatility Insights"):
        avg_volatility = df_filtered['Volatility'].mean()
        max_volatility = df_filtered['Volatility'].max()
        min_volatility = df_filtered['Volatility'].min()
        
        # Find date of max volatility
        max_vol_date = df_filtered.loc[df_filtered['Volatility'].idxmax(), 'Date']
        
        st.markdown(f"**Current Volatility:** {current_volatility:.2f}%")
        st.markdown(f"**Average Volatility:** {avg_volatility:.2f}%")
        st.markdown(f"**Maximum Volatility:** {max_volatility:.2f}% (on {max_vol_date.strftime('%Y-%m-%d')})")
        st.markdown(f"**Minimum Volatility:** {min_volatility:.2f}%")
        
        # Volatility assessment
        if current_volatility > avg_volatility * 1.5:
            st.warning("High Volatility Alert: Current volatility is significantly above average. Market is experiencing increased uncertainty.")
        elif current_volatility < avg_volatility * 0.5:
            st.info("Low Volatility: Market is relatively calm with below-average volatility.")
        else:
            st.success("Normal Volatility: Current volatility is within normal range.")
else:
    st.warning("Volatility data not available in the dataset.")

st.markdown("---")

# Return Distribution
st.header("Return Distribution Analysis")

if 'Daily_Return' in df_filtered.columns:
    # Create return distribution chart
    fig_distribution = plot_return_distribution(
        df_filtered,
        return_col='Daily_Return',
        title=f'Daily Return Distribution ({start_date} to {end_date})'
    )
    
    st.plotly_chart(fig_distribution, use_container_width=True)
    
    # Return statistics
    with st.expander("Return Statistics"):
        returns = df_filtered['Daily_Return'].dropna()
        
        mean_return = returns.mean()
        median_return = returns.median()
        std_return = returns.std()
        max_return = returns.max()
        min_return = returns.min()
        
        # Find dates of max and min returns
        max_return_date = df_filtered.loc[df_filtered['Daily_Return'].idxmax(), 'Date']
        min_return_date = df_filtered.loc[df_filtered['Daily_Return'].idxmin(), 'Date']
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("**Central Tendency:**")
            st.markdown(f"- Mean Return: **{mean_return:.2f}%**")
            st.markdown(f"- Median Return: **{median_return:.2f}%**")
            st.markdown(f"- Std Deviation: **{std_return:.2f}%**")
        
        with col_b:
            st.markdown("**Extremes:**")
            st.markdown(f"- Best Day: **{max_return:.2f}%** ({max_return_date.strftime('%Y-%m-%d')})")
            st.markdown(f"- Worst Day: **{min_return:.2f}%** ({min_return_date.strftime('%Y-%m-%d')})")
        
        # Calculate percentiles
        st.markdown("**Percentiles:**")
        p25 = returns.quantile(0.25)
        p75 = returns.quantile(0.75)
        st.markdown(f"- 25th Percentile: **{p25:.2f}%**")
        st.markdown(f"- 75th Percentile: **{p75:.2f}%**")
else:
    st.warning("Daily return data not available in the dataset.")

st.markdown("---")

# Summary Section
st.header("Summary")

summary_col1, summary_col2 = st.columns(2)

with summary_col1:
    st.markdown("### Key Takeaways")
    st.markdown(f"""
    - **Market Direction:** {trend}
    - **Price Performance:** {price_change_pct:+.2f}% over the selected period
    - **Volatility Status:** {'High' if current_volatility > avg_volatility * 1.5 else 'Low' if current_volatility < avg_volatility * 0.5 else 'Normal'}
    - **Trading Activity:** {positive_pct:.1f}% positive days
    """)

with summary_col2:
    st.markdown("### Market Insights")
    
    # Generate dynamic insights
    insights = []
    
    if price_change_pct > 10:
        insights.append("Strong bullish momentum in the market")
    elif price_change_pct < -10:
        insights.append("Significant bearish pressure observed")
    
    if current_volatility > avg_volatility * 1.5:
        insights.append("Elevated volatility suggests increased risk")
    
    if positive_pct > 60:
        insights.append("Majority of trading days were positive")
    elif positive_pct < 40:
        insights.append("Majority of trading days were negative")
    
    if avg_return > 0.1:
        insights.append("Positive average daily returns indicate upward bias")
    elif avg_return < -0.1:
        insights.append("Negative average daily returns indicate downward bias")
    
    if insights:
        for insight in insights:
            st.markdown(f"- {insight}")
    else:
        st.markdown("- Market showing balanced behavior")
        st.markdown("- No extreme trends detected")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem 0;">
    <p><strong>Market Overview Dashboard</strong> | Data updated through {}</p>
    <p>Use the sidebar to adjust the date range for analysis</p>
</div>
""".format(max_date.strftime('%Y-%m-%d')), unsafe_allow_html=True)
