"""
Sector Analysis Page

This page displays sector-wise performance analysis when sector data is available.
If sector data is not available, it shows a placeholder message with information
about how to add sector data to the platform.

Features (when data available):
- Sector performance heatmap
- Sector rankings by returns
- Sector rotation analysis
- Sector-wise institutional flows
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to import utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import load_latest_data

# Configure page
st.set_page_config(
    page_title="Sector Analysis - Smart Money Intelligence",
    page_icon="🏭",
    layout="wide"
)

# Page header
st.title("🏭 Sector Analysis")
st.markdown("Analyze sector-wise performance and institutional flows")
st.markdown("---")

# Load data
with st.spinner("Loading data..."):
    df = load_latest_data()

if df is None or df.empty:
    st.error("❌ Unable to load data. Please ensure the data pipeline has been run.")
    st.info("💡 Run `python scripts/run_pipeline.py` to generate processed data.")
    st.stop()

# Check if sector data is available
# Sector data would typically have columns like 'Sector', 'Sector_Return', etc.
sector_columns = [col for col in df.columns if 'sector' in col.lower()]
has_sector_data = len(sector_columns) > 0

if not has_sector_data:
    # Display placeholder message when sector data is not available
    st.info("📊 **Sector Analysis Feature**")
    
    st.markdown("""
    ### 🔍 About Sector Analysis
    
    Sector analysis provides insights into how different market sectors are performing
    and where institutional investors are allocating their capital. This helps identify:
    
    - **Sector Rotation**: Which sectors are gaining or losing favor
    - **Relative Performance**: How sectors compare to the overall market
    - **Institutional Preferences**: Where FII/DII are investing
    - **Risk Distribution**: Sector-wise volatility and risk metrics
    """)
    
    st.markdown("---")
    
    # Show what would be available with sector data
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Available Features (with sector data)")
        st.markdown("""
        When sector data is available, this page will display:
        
        1. **Sector Performance Heatmap**
           - Visual representation of sector returns
           - Color-coded performance indicators
           - Time-based performance comparison
        
        2. **Sector Rankings**
           - Top performing sectors
           - Worst performing sectors
           - Sector momentum indicators
        
        3. **Sector Rotation Analysis**
           - Identify sectors gaining momentum
           - Track sector leadership changes
           - Detect rotation patterns
        
        4. **Institutional Flow by Sector**
           - FII/DII preferences by sector
           - Sector-wise accumulation/distribution
           - Smart money sector allocation
        """)
    
    with col2:
        st.markdown("### 🔧 How to Add Sector Data")
        st.markdown("""
        To enable sector analysis, you need to:
        
        **Option 1: Manual Data Addition**
        1. Obtain sector-wise data from NSE or other sources
        2. Add sector columns to your dataset:
           - `Sector_Name`: Name of the sector
           - `Sector_Return`: Daily sector return
           - `Sector_FII_Flow`: FII flows to the sector
           - `Sector_DII_Flow`: DII flows to the sector
        
        **Option 2: API Integration**
        1. Integrate with NSE API for sector indices
        2. Download sector-wise data programmatically
        3. Merge with existing market data
        
        **Option 3: Use Sector ETF Data**
        1. Download sector ETF prices (e.g., Bank NIFTY, IT NIFTY)
        2. Calculate sector returns from ETF prices
        3. Add to the processed dataset
        """)
    
    st.markdown("---")
    
    # Example of what sector data structure should look like
    st.markdown("### 📋 Expected Sector Data Format")
    
    st.markdown("""
    Your processed data should include columns like:
    """)
    
    # Create example DataFrame
    example_data = {
        'Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'Close': [21500, 21600, 21550],
        'Banking_Return': [1.2, -0.5, 0.8],
        'IT_Return': [0.8, 1.5, -0.3],
        'Auto_Return': [-0.3, 0.9, 1.2],
        'Pharma_Return': [0.5, 0.2, -0.1],
        'FMCG_Return': [0.3, -0.2, 0.4]
    }
    
    example_df = pd.DataFrame(example_data)
    st.dataframe(example_df, use_container_width=True)
    
    st.markdown("---")
    
    # Provide sample code for adding sector data
    st.markdown("### 💻 Sample Code: Adding Sector Data")
    
    with st.expander("📝 Click to view sample code"):
        st.code("""
# Example: Adding sector data to your pipeline

import pandas as pd
import yfinance as yf

def download_sector_data(start_date, end_date):
    \"\"\"
    Download sector ETF data as proxy for sector performance.
    \"\"\"
    # NSE Sector Indices (example tickers)
    sector_tickers = {
        'Banking': '^NSEBANK',      # Bank NIFTY
        'IT': '^CNXIT',             # NIFTY IT
        'Auto': '^CNXAUTO',         # NIFTY Auto
        'Pharma': '^CNXPHARMA',     # NIFTY Pharma
        'FMCG': '^CNXFMCG'          # NIFTY FMCG
    }
    
    sector_data = {}
    
    for sector, ticker in sector_tickers.items():
        try:
            data = yf.download(ticker, start=start_date, end=end_date)
            # Calculate daily returns
            data[f'{sector}_Return'] = data['Close'].pct_change() * 100
            sector_data[sector] = data[[f'{sector}_Return']]
        except Exception as e:
            print(f"Error downloading {sector}: {e}")
    
    # Merge all sector data
    merged_data = pd.concat(sector_data.values(), axis=1)
    return merged_data

# Add to your preprocessing pipeline
def add_sector_data_to_pipeline(market_df, start_date, end_date):
    \"\"\"
    Integrate sector data with market data.
    \"\"\"
    sector_df = download_sector_data(start_date, end_date)
    
    # Merge with market data on date
    merged_df = market_df.merge(
        sector_df,
        left_on='Date',
        right_index=True,
        how='left'
    )
    
    return merged_df

# Usage in your pipeline
# df = add_sector_data_to_pipeline(df, '2020-01-01', '2024-12-31')
        """, language='python')
    
    st.markdown("---")
    
    # Current data summary
    st.markdown("### 📊 Current Data Summary")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.metric(
            label="Total Records",
            value=f"{len(df):,}",
            delta=None
        )
    
    with col_b:
        st.metric(
            label="Available Columns",
            value=f"{len(df.columns)}",
            delta=None
        )
    
    with col_c:
        st.metric(
            label="Sector Columns",
            value="0",
            delta="Add sector data to enable"
        )
    
    # Show current columns
    with st.expander("📋 View Current Data Columns"):
        st.write("**Available columns in your dataset:**")
        cols_display = pd.DataFrame({
            'Column Name': df.columns,
            'Data Type': [str(dtype) for dtype in df.dtypes],
            'Non-Null Count': [df[col].notna().sum() for col in df.columns]
        })
        st.dataframe(cols_display, use_container_width=True)
    
    st.markdown("---")
    
    # Next steps
    st.markdown("### 🚀 Next Steps")
    
    st.markdown("""
    To enable sector analysis on this platform:
    
    1. **Choose a data source** for sector information
    2. **Modify the data collection script** (`scripts/data_collection.py`) to include sector data
    3. **Update the preprocessing pipeline** (`scripts/preprocessing.py`) to handle sector columns
    4. **Re-run the pipeline** to generate updated processed data
    5. **Refresh this page** to see sector analysis features
    
    Once sector data is available, this page will automatically detect it and display
    comprehensive sector analysis visualizations and insights.
    """)
    
    # Helpful resources
    st.markdown("### 📚 Helpful Resources")
    
    st.markdown("""
    - [NSE India - Sectoral Indices](https://www.nseindia.com/market-data/live-equity-market)
    - [Yahoo Finance - Indian Sector ETFs](https://finance.yahoo.com/)
    - [BSE India - Sector Indices](https://www.bseindia.com/indices/IndexArchiveData.html)
    """)

else:
    # If sector data is available, display sector analysis
    st.success("✅ Sector data detected! Displaying sector analysis...")
    
    # Ensure Date column is datetime
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')
    
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
    
    # TODO: Implement sector analysis visualizations
    # This section would include:
    # - Sector performance heatmap
    # - Sector rankings table
    # - Sector rotation analysis
    # - Sector-wise institutional flows
    
    st.info("🚧 Sector analysis visualizations will be implemented here once sector data structure is finalized.")
    
    # Display available sector columns
    st.markdown("### 📊 Available Sector Data")
    st.write(f"Detected {len(sector_columns)} sector-related columns:")
    st.write(sector_columns)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem 0;">
    <p><strong>Sector Analysis Dashboard</strong> | Smart Money Intelligence Platform</p>
    <p>Add sector data to unlock comprehensive sector analysis features</p>
</div>
""", unsafe_allow_html=True)
