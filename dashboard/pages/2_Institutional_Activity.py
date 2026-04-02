"""
Institutional Activity Page

This page displays FII and DII institutional flow analysis, including:
- FII vs DII flows comparison (dual-axis line chart)
- Cumulative flows chart
- Detected accumulation/distribution periods
- Correlation heatmap between flows and returns
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
    plot_institutional_flows,
    plot_cumulative_flows,
    plot_correlation_heatmap
)

# Import insights generator for period detection
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'scripts'))
from insights_generator import detect_accumulation_periods, detect_selling_periods

# Configure page
st.set_page_config(
    page_title="Institutional Activity - Smart Money Intelligence",
    page_icon="🏢",
    layout="wide"
)

# Page header
st.title("🏢 Institutional Activity Analysis")
st.markdown("Track FII and DII investment flows and their impact on market movements")
st.markdown("---")

# Load data
with st.spinner("Loading institutional activity data..."):
    df = load_latest_data()

if df is None or df.empty:
    st.error("❌ Unable to load institutional data. Please ensure the data pipeline has been run.")
    st.info("💡 Run `python scripts/run_pipeline.py` to generate processed data.")
    st.stop()

# Ensure Date column is datetime
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')

# Check for required columns
required_cols = ['FII_Net', 'DII_Net']
missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
    st.info("💡 Please ensure the preprocessing pipeline has computed net flows.")
    st.stop()

# Date range selector in sidebar
st.sidebar.header("📅 Date Range Filter")

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
    st.sidebar.error("❌ Start date must be before end date!")
    st.stop()

# Filter data by date range
df_filtered = df[
    (df['Date'].dt.date >= start_date) & 
    (df['Date'].dt.date <= end_date)
].copy()

if df_filtered.empty:
    st.warning("⚠️ No data available for the selected date range. Please adjust the dates.")
    st.stop()

# Display date range info
st.sidebar.success(f"✅ Showing data from {start_date} to {end_date}")
st.sidebar.info(f"📊 Total trading days: {len(df_filtered)}")

# Key Statistics Section
st.header("📊 Institutional Flow Statistics")

# Calculate statistics
total_fii_net = df_filtered['FII_Net'].sum()
total_dii_net = df_filtered['DII_Net'].sum()
avg_fii_net = df_filtered['FII_Net'].mean()
avg_dii_net = df_filtered['DII_Net'].mean()

# Count positive and negative days
fii_positive_days = (df_filtered['FII_Net'] > 0).sum()
dii_positive_days = (df_filtered['DII_Net'] > 0).sum()
fii_positive_pct = (fii_positive_days / len(df_filtered)) * 100
dii_positive_pct = (dii_positive_days / len(df_filtered)) * 100

# Display statistics in columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total FII Net Flow",
        value=f"₹{total_fii_net:,.0f} Cr",
        delta=f"{fii_positive_pct:.1f}% positive days"
    )

with col2:
    st.metric(
        label="Total DII Net Flow",
        value=f"₹{total_dii_net:,.0f} Cr",
        delta=f"{dii_positive_pct:.1f}% positive days"
    )

with col3:
    st.metric(
        label="Avg Daily FII Flow",
        value=f"₹{avg_fii_net:,.0f} Cr",
        delta=None
    )

with col4:
    st.metric(
        label="Avg Daily DII Flow",
        value=f"₹{avg_dii_net:,.0f} Cr",
        delta=None
    )

# Additional statistics
col5, col6, col7, col8 = st.columns(4)

with col5:
    max_fii_buying = df_filtered['FII_Net'].max()
    st.metric(
        label="Max FII Buying Day",
        value=f"₹{max_fii_buying:,.0f} Cr",
        delta=None
    )

with col6:
    max_fii_selling = df_filtered['FII_Net'].min()
    st.metric(
        label="Max FII Selling Day",
        value=f"₹{max_fii_selling:,.0f} Cr",
        delta=None
    )

with col7:
    max_dii_buying = df_filtered['DII_Net'].max()
    st.metric(
        label="Max DII Buying Day",
        value=f"₹{max_dii_buying:,.0f} Cr",
        delta=None
    )

with col8:
    max_dii_selling = df_filtered['DII_Net'].min()
    st.metric(
        label="Max DII Selling Day",
        value=f"₹{max_dii_selling:,.0f} Cr",
        delta=None
    )

st.markdown("---")

# FII vs DII Flows Comparison
st.header("📈 FII vs DII Net Flows Comparison")

# Create the flows comparison chart
fig_flows = plot_institutional_flows(
    df_filtered,
    date_col='Date',
    fii_col='FII_Net',
    dii_col='DII_Net',
    title=f'FII vs DII Net Flows ({start_date} to {end_date})'
)

st.plotly_chart(fig_flows, use_container_width=True)

# Add insights below the chart
with st.expander("📊 Flow Analysis Insights"):
    # Determine FII behavior
    if total_fii_net > 1000:
        fii_behavior = "📈 **Strong Net Buyers** - FII showed significant buying interest"
    elif total_fii_net > 0:
        fii_behavior = "📊 **Mild Net Buyers** - FII showed moderate buying interest"
    elif total_fii_net > -1000:
        fii_behavior = "📉 **Mild Net Sellers** - FII showed moderate selling pressure"
    else:
        fii_behavior = "📉 **Strong Net Sellers** - FII showed significant selling pressure"
    
    # Determine DII behavior
    if total_dii_net > 1000:
        dii_behavior = "📈 **Strong Net Buyers** - DII showed significant buying interest"
    elif total_dii_net > 0:
        dii_behavior = "📊 **Mild Net Buyers** - DII showed moderate buying interest"
    elif total_dii_net > -1000:
        dii_behavior = "📉 **Mild Net Sellers** - DII showed moderate selling pressure"
    else:
        dii_behavior = "📉 **Strong Net Sellers** - DII showed significant selling pressure"
    
    st.markdown(f"**FII Behavior:** {fii_behavior}")
    st.markdown(f"**DII Behavior:** {dii_behavior}")
    
    # Analyze relationship
    if (total_fii_net > 0 and total_dii_net < 0) or (total_fii_net < 0 and total_dii_net > 0):
        st.markdown("**Relationship:** 🔄 **Divergent** - FII and DII showed opposite behavior (one buying, one selling)")
    elif abs(total_fii_net) > abs(total_dii_net) * 2:
        st.markdown("**Relationship:** ⚖️ **FII Dominated** - FII flows significantly outweighed DII flows")
    elif abs(total_dii_net) > abs(total_fii_net) * 2:
        st.markdown("**Relationship:** ⚖️ **DII Dominated** - DII flows significantly outweighed FII flows")
    else:
        st.markdown("**Relationship:** 🤝 **Balanced** - FII and DII showed similar magnitude of flows")

st.markdown("---")

# Cumulative Flows Chart
st.header("📊 Cumulative Institutional Flows")

# Create cumulative flows chart
fig_cumulative = plot_cumulative_flows(
    df_filtered,
    date_col='Date',
    fii_col='FII_Net',
    dii_col='DII_Net',
    title=f'Cumulative Institutional Flows ({start_date} to {end_date})'
)

st.plotly_chart(fig_cumulative, use_container_width=True)

with st.expander("📈 Cumulative Flow Insights"):
    st.markdown("""
    **Understanding Cumulative Flows:**
    
    Cumulative flows show the running total of institutional investments over time:
    - **Rising trend** indicates sustained buying (accumulation)
    - **Falling trend** indicates sustained selling (distribution)
    - **Flat trend** indicates balanced buying and selling
    
    **Key Observations:**
    """)
    
    # Calculate cumulative at start and end
    df_filtered_copy = df_filtered.copy()
    df_filtered_copy['FII_Cumulative'] = df_filtered_copy['FII_Net'].cumsum()
    df_filtered_copy['DII_Cumulative'] = df_filtered_copy['DII_Net'].cumsum()
    
    fii_cum_start = df_filtered_copy['FII_Cumulative'].iloc[0]
    fii_cum_end = df_filtered_copy['FII_Cumulative'].iloc[-1]
    dii_cum_start = df_filtered_copy['DII_Cumulative'].iloc[0]
    dii_cum_end = df_filtered_copy['DII_Cumulative'].iloc[-1]
    
    st.markdown(f"- FII cumulative flow: **₹{fii_cum_start:,.0f} Cr** → **₹{fii_cum_end:,.0f} Cr**")
    st.markdown(f"- DII cumulative flow: **₹{dii_cum_start:,.0f} Cr** → **₹{dii_cum_end:,.0f} Cr**")
    st.markdown(f"- Net change in FII position: **₹{fii_cum_end - fii_cum_start:+,.0f} Cr**")
    st.markdown(f"- Net change in DII position: **₹{dii_cum_end - dii_cum_start:+,.0f} Cr**")

st.markdown("---")

# Accumulation and Distribution Periods
st.header("🎯 Accumulation & Distribution Periods")

# Sidebar controls for period detection
st.sidebar.header("⚙️ Period Detection Settings")
window_size = st.sidebar.slider(
    "Minimum Consecutive Days",
    min_value=3,
    max_value=10,
    value=5,
    help="Minimum number of consecutive days to identify a period"
)

threshold = st.sidebar.number_input(
    "Minimum Average Flow (₹ Cr)",
    min_value=0.0,
    max_value=1000.0,
    value=0.0,
    step=50.0,
    help="Minimum average flow during the period"
)

# Detect periods
with st.spinner("Detecting accumulation and distribution periods..."):
    try:
        # FII Accumulation
        fii_accumulation = detect_accumulation_periods(
            df_filtered,
            flow_col='FII_Net',
            window=window_size,
            threshold=threshold
        )
        
        # FII Selling
        fii_selling = detect_selling_periods(
            df_filtered,
            flow_col='FII_Net',
            window=window_size,
            threshold=-threshold
        )
        
        # DII Accumulation
        dii_accumulation = detect_accumulation_periods(
            df_filtered,
            flow_col='DII_Net',
            window=window_size,
            threshold=threshold
        )
        
        # DII Selling
        dii_selling = detect_selling_periods(
            df_filtered,
            flow_col='DII_Net',
            window=window_size,
            threshold=-threshold
        )
        
    except Exception as e:
        st.error(f"❌ Error detecting periods: {str(e)}")
        fii_accumulation = []
        fii_selling = []
        dii_accumulation = []
        dii_selling = []

# Display periods in tabs
tab1, tab2, tab3, tab4 = st.tabs([
    f"🟢 FII Accumulation ({len(fii_accumulation)})",
    f"🔴 FII Distribution ({len(fii_selling)})",
    f"🟢 DII Accumulation ({len(dii_accumulation)})",
    f"🔴 DII Distribution ({len(dii_selling)})"
])

with tab1:
    st.subheader("FII Accumulation Periods")
    if fii_accumulation:
        # Create DataFrame for display
        periods_df = pd.DataFrame(fii_accumulation, columns=['Start Date', 'End Date'])
        
        # Calculate duration and average flow for each period
        durations = []
        avg_flows = []
        
        for start, end in fii_accumulation:
            period_data = df_filtered[
                (df_filtered['Date'].dt.strftime('%Y-%m-%d') >= start) &
                (df_filtered['Date'].dt.strftime('%Y-%m-%d') <= end)
            ]
            duration = len(period_data)
            avg_flow = period_data['FII_Net'].mean()
            durations.append(duration)
            avg_flows.append(avg_flow)
        
        periods_df['Duration (days)'] = durations
        periods_df['Avg Flow (₹ Cr)'] = [f"₹{flow:,.0f}" for flow in avg_flows]
        
        st.dataframe(periods_df, use_container_width=True)
        st.success(f"✅ Found {len(fii_accumulation)} FII accumulation periods")
    else:
        st.info("ℹ️ No FII accumulation periods detected with current settings. Try adjusting the parameters in the sidebar.")

with tab2:
    st.subheader("FII Distribution (Selling) Periods")
    if fii_selling:
        # Create DataFrame for display
        periods_df = pd.DataFrame(fii_selling, columns=['Start Date', 'End Date'])
        
        # Calculate duration and average flow for each period
        durations = []
        avg_flows = []
        
        for start, end in fii_selling:
            period_data = df_filtered[
                (df_filtered['Date'].dt.strftime('%Y-%m-%d') >= start) &
                (df_filtered['Date'].dt.strftime('%Y-%m-%d') <= end)
            ]
            duration = len(period_data)
            avg_flow = period_data['FII_Net'].mean()
            durations.append(duration)
            avg_flows.append(avg_flow)
        
        periods_df['Duration (days)'] = durations
        periods_df['Avg Flow (₹ Cr)'] = [f"₹{flow:,.0f}" for flow in avg_flows]
        
        st.dataframe(periods_df, use_container_width=True)
        st.warning(f"⚠️ Found {len(fii_selling)} FII distribution periods")
    else:
        st.info("ℹ️ No FII distribution periods detected with current settings. Try adjusting the parameters in the sidebar.")

with tab3:
    st.subheader("DII Accumulation Periods")
    if dii_accumulation:
        # Create DataFrame for display
        periods_df = pd.DataFrame(dii_accumulation, columns=['Start Date', 'End Date'])
        
        # Calculate duration and average flow for each period
        durations = []
        avg_flows = []
        
        for start, end in dii_accumulation:
            period_data = df_filtered[
                (df_filtered['Date'].dt.strftime('%Y-%m-%d') >= start) &
                (df_filtered['Date'].dt.strftime('%Y-%m-%d') <= end)
            ]
            duration = len(period_data)
            avg_flow = period_data['DII_Net'].mean()
            durations.append(duration)
            avg_flows.append(avg_flow)
        
        periods_df['Duration (days)'] = durations
        periods_df['Avg Flow (₹ Cr)'] = [f"₹{flow:,.0f}" for flow in avg_flows]
        
        st.dataframe(periods_df, use_container_width=True)
        st.success(f"✅ Found {len(dii_accumulation)} DII accumulation periods")
    else:
        st.info("ℹ️ No DII accumulation periods detected with current settings. Try adjusting the parameters in the sidebar.")

with tab4:
    st.subheader("DII Distribution (Selling) Periods")
    if dii_selling:
        # Create DataFrame for display
        periods_df = pd.DataFrame(dii_selling, columns=['Start Date', 'End Date'])
        
        # Calculate duration and average flow for each period
        durations = []
        avg_flows = []
        
        for start, end in dii_selling:
            period_data = df_filtered[
                (df_filtered['Date'].dt.strftime('%Y-%m-%d') >= start) &
                (df_filtered['Date'].dt.strftime('%Y-%m-%d') <= end)
            ]
            duration = len(period_data)
            avg_flow = period_data['DII_Net'].mean()
            durations.append(duration)
            avg_flows.append(avg_flow)
        
        periods_df['Duration (days)'] = durations
        periods_df['Avg Flow (₹ Cr)'] = [f"₹{flow:,.0f}" for flow in avg_flows]
        
        st.dataframe(periods_df, use_container_width=True)
        st.warning(f"⚠️ Found {len(dii_selling)} DII distribution periods")
    else:
        st.info("ℹ️ No DII distribution periods detected with current settings. Try adjusting the parameters in the sidebar.")

st.markdown("---")

# Correlation Analysis
st.header("🔗 Correlation Analysis")

# Select columns for correlation
correlation_columns = ['FII_Net', 'DII_Net']

# Add Daily_Return if available
if 'Daily_Return' in df_filtered.columns:
    correlation_columns.append('Daily_Return')

# Add other relevant columns if available
optional_cols = ['Volatility', 'Momentum', 'FII_Net_MA5', 'DII_Net_MA5']
for col in optional_cols:
    if col in df_filtered.columns:
        correlation_columns.append(col)

# Create correlation heatmap
fig_corr = plot_correlation_heatmap(
    df_filtered,
    columns=correlation_columns,
    title='Correlation Heatmap: Institutional Flows & Market Metrics'
)

st.plotly_chart(fig_corr, use_container_width=True)

with st.expander("📊 Correlation Insights"):
    st.markdown("""
    **Understanding Correlations:**
    
    - **Positive correlation (green)**: Variables move in the same direction
    - **Negative correlation (red)**: Variables move in opposite directions
    - **Near zero (white)**: Little to no linear relationship
    
    **Key Relationships to Watch:**
    """)
    
    # Calculate specific correlations if Daily_Return is available
    if 'Daily_Return' in df_filtered.columns:
        fii_return_corr = df_filtered['FII_Net'].corr(df_filtered['Daily_Return'])
        dii_return_corr = df_filtered['DII_Net'].corr(df_filtered['Daily_Return'])
        fii_dii_corr = df_filtered['FII_Net'].corr(df_filtered['DII_Net'])
        
        st.markdown(f"- **FII vs Market Returns:** {fii_return_corr:.3f}")
        st.markdown(f"- **DII vs Market Returns:** {dii_return_corr:.3f}")
        st.markdown(f"- **FII vs DII:** {fii_dii_corr:.3f}")
        
        # Interpret correlations
        st.markdown("\n**Interpretation:**")
        
        if abs(fii_return_corr) > 0.3:
            direction = "positive" if fii_return_corr > 0 else "negative"
            st.markdown(f"- FII flows show **moderate to strong {direction} correlation** with market returns")
        else:
            st.markdown("- FII flows show **weak correlation** with market returns")
        
        if abs(dii_return_corr) > 0.3:
            direction = "positive" if dii_return_corr > 0 else "negative"
            st.markdown(f"- DII flows show **moderate to strong {direction} correlation** with market returns")
        else:
            st.markdown("- DII flows show **weak correlation** with market returns")
        
        if abs(fii_dii_corr) > 0.3:
            if fii_dii_corr > 0:
                st.markdown("- FII and DII tend to **move together** (both buying or both selling)")
            else:
                st.markdown("- FII and DII tend to **move in opposite directions** (one buying when other selling)")
        else:
            st.markdown("- FII and DII show **independent behavior**")
    else:
        st.warning("⚠️ Daily return data not available for correlation analysis.")

st.markdown("---")

# Summary Section
st.header("📋 Summary & Key Insights")

summary_col1, summary_col2 = st.columns(2)

with summary_col1:
    st.markdown("### 🎯 Institutional Behavior")
    st.markdown(f"""
    **FII (Foreign Institutional Investors):**
    - Total Net Flow: **₹{total_fii_net:,.0f} Cr**
    - Average Daily Flow: **₹{avg_fii_net:,.0f} Cr**
    - Positive Days: **{fii_positive_pct:.1f}%**
    - Accumulation Periods: **{len(fii_accumulation)}**
    - Distribution Periods: **{len(fii_selling)}**
    
    **DII (Domestic Institutional Investors):**
    - Total Net Flow: **₹{total_dii_net:,.0f} Cr**
    - Average Daily Flow: **₹{avg_dii_net:,.0f} Cr**
    - Positive Days: **{dii_positive_pct:.1f}%**
    - Accumulation Periods: **{len(dii_accumulation)}**
    - Distribution Periods: **{len(dii_selling)}**
    """)

with summary_col2:
    st.markdown("### 💡 Key Takeaways")
    
    # Generate dynamic insights
    insights = []
    
    # Net flow insights
    if total_fii_net > 1000 and total_dii_net > 1000:
        insights.append("🚀 Both FII and DII were strong net buyers - bullish signal")
    elif total_fii_net < -1000 and total_dii_net < -1000:
        insights.append("📉 Both FII and DII were strong net sellers - bearish signal")
    elif total_fii_net > 1000 and total_dii_net < -1000:
        insights.append("🔄 FII buying while DII selling - mixed signals")
    elif total_fii_net < -1000 and total_dii_net > 1000:
        insights.append("🔄 DII buying while FII selling - mixed signals")
    
    # Consistency insights
    if fii_positive_pct > 70:
        insights.append("✅ FII showed consistent buying behavior")
    elif fii_positive_pct < 30:
        insights.append("⚠️ FII showed consistent selling behavior")
    
    if dii_positive_pct > 70:
        insights.append("✅ DII showed consistent buying behavior")
    elif dii_positive_pct < 30:
        insights.append("⚠️ DII showed consistent selling behavior")
    
    # Period insights
    if len(fii_accumulation) > len(fii_selling):
        insights.append("📈 More FII accumulation than distribution periods")
    elif len(fii_selling) > len(fii_accumulation):
        insights.append("📉 More FII distribution than accumulation periods")
    
    # Correlation insights
    if 'Daily_Return' in df_filtered.columns:
        fii_return_corr = df_filtered['FII_Net'].corr(df_filtered['Daily_Return'])
        if abs(fii_return_corr) > 0.3:
            insights.append(f"🔗 FII flows {'positively' if fii_return_corr > 0 else 'negatively'} correlated with returns")
    
    if insights:
        for insight in insights:
            st.markdown(f"- {insight}")
    else:
        st.markdown("- 📊 Institutional activity showing balanced behavior")
        st.markdown("- 📈 No extreme patterns detected")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem 0;">
    <p><strong>Institutional Activity Dashboard</strong> | Data updated through {}</p>
    <p>Use the sidebar to adjust date range and period detection settings</p>
</div>
""".format(max_date.strftime('%Y-%m-%d')), unsafe_allow_html=True)
