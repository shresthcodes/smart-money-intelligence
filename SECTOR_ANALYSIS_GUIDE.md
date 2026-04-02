# Sector Analysis Page - User Guide

## 🎯 Overview

The Sector Analysis page is an intelligent dashboard component that adapts based on whether sector data is available in your dataset. It provides comprehensive guidance for adding sector analysis capabilities to the Smart Money Intelligence platform.

## 📊 Current State: Placeholder Mode

Since the current dataset doesn't include sector-specific data, the page displays helpful information to guide you through adding this functionality.

## 🖥️ What You'll See

### 1. **About Sector Analysis**
Learn what sector analysis provides:
- Sector rotation tracking
- Relative performance comparison
- Institutional preferences by sector
- Risk distribution across sectors

### 2. **Available Features Preview**
See what will be available once sector data is added:
- Sector Performance Heatmap
- Sector Rankings
- Sector Rotation Analysis
- Institutional Flow by Sector

### 3. **Implementation Guide**
Three options to add sector data:

#### Option 1: Manual Data Addition
- Obtain sector data from NSE or other sources
- Add columns: `Sector_Name`, `Sector_Return`, `Sector_FII_Flow`, `Sector_DII_Flow`
- Merge with existing dataset

#### Option 2: API Integration
- Integrate with NSE API
- Download sector indices programmatically
- Automate data collection

#### Option 3: Sector ETF Data
- Use sector ETF prices as proxy
- Download from Yahoo Finance
- Calculate sector returns from ETF prices

### 4. **Sample Code**
Ready-to-use Python code for downloading sector data:

```python
import pandas as pd
import yfinance as yf

def download_sector_data(start_date, end_date):
    sector_tickers = {
        'Banking': '^NSEBANK',
        'IT': '^CNXIT',
        'Auto': '^CNXAUTO',
        'Pharma': '^CNXPHARMA',
        'FMCG': '^CNXFMCG'
    }
    
    sector_data = {}
    for sector, ticker in sector_tickers.items():
        data = yf.download(ticker, start=start_date, end=end_date)
        data[f'{sector}_Return'] = data['Close'].pct_change() * 100
        sector_data[sector] = data[[f'{sector}_Return']]
    
    return pd.concat(sector_data.values(), axis=1)
```

### 5. **Expected Data Format**
Example of how your data should look:

| Date       | Close | Banking_Return | IT_Return | Auto_Return | Pharma_Return | FMCG_Return |
|------------|-------|----------------|-----------|-------------|---------------|-------------|
| 2024-01-01 | 21500 | 1.2            | 0.8       | -0.3        | 0.5           | 0.3         |
| 2024-01-02 | 21600 | -0.5           | 1.5       | 0.9         | 0.2           | -0.2        |
| 2024-01-03 | 21550 | 0.8            | -0.3      | 1.2         | -0.1          | 0.4         |

## 🚀 How to Enable Sector Analysis

### Step 1: Choose Your Data Source
Decide which option works best for you:
- **NSE Website**: Most accurate, requires manual download
- **Yahoo Finance**: Easy to automate, good coverage
- **API Services**: Professional, may require subscription

### Step 2: Modify Data Collection Script
Add sector data download to `scripts/data_collection.py`:

```python
def collect_all_data(start_date, end_date):
    # Existing code for NIFTY data
    nifty_df = download_nifty_data(start_date, end_date)
    
    # Add sector data collection
    sector_df = download_sector_data(start_date, end_date)
    
    # Merge datasets
    combined_df = nifty_df.merge(sector_df, on='Date', how='left')
    
    return combined_df
```

### Step 3: Update Preprocessing Pipeline
Modify `scripts/preprocessing.py` to handle sector columns:

```python
def preprocess_data(df):
    # Existing preprocessing
    df = clean_market_data(df)
    
    # Add sector-specific preprocessing
    sector_cols = [col for col in df.columns if 'Return' in col and col != 'Daily_Return']
    
    for col in sector_cols:
        # Handle missing values
        df[col] = df[col].fillna(0)
        
        # Calculate rolling averages
        df[f'{col}_MA5'] = df[col].rolling(window=5).mean()
    
    return df
```

### Step 4: Re-run the Pipeline
Execute the complete pipeline with sector data:

```bash
cd tracking game hand/smart-money-intelligence
python scripts/run_pipeline.py
```

### Step 5: Refresh Dashboard
Once the pipeline completes:
1. Restart the Streamlit dashboard
2. Navigate to "Sector Analysis" page
3. The page will automatically detect sector data
4. Full sector analysis features will be displayed

## 🎨 What You'll Get (After Adding Data)

### Sector Performance Heatmap
- Visual color-coded performance grid
- Compare all sectors at a glance
- Identify hot and cold sectors

### Sector Rankings
- Top performing sectors
- Worst performing sectors
- Momentum indicators by sector

### Sector Rotation Analysis
- Track which sectors are gaining favor
- Identify rotation patterns
- Detect leadership changes

### Institutional Flow by Sector
- See where FII/DII are investing
- Sector-wise accumulation/distribution
- Smart money sector preferences

## 📈 Benefits of Sector Analysis

### For Traders
- Identify sector rotation opportunities
- Find sectors with momentum
- Avoid sectors losing favor

### For Investors
- Diversification insights
- Long-term sector trends
- Risk management by sector

### For Analysts
- Comprehensive market view
- Institutional behavior patterns
- Sector correlation analysis

## 🔗 Helpful Resources

### Data Sources
- **NSE India**: https://www.nseindia.com/market-data/live-equity-market
- **Yahoo Finance**: https://finance.yahoo.com/
- **BSE India**: https://www.bseindia.com/indices/IndexArchiveData.html

### NSE Sector Indices
- Bank NIFTY: ^NSEBANK
- NIFTY IT: ^CNXIT
- NIFTY Auto: ^CNXAUTO
- NIFTY Pharma: ^CNXPHARMA
- NIFTY FMCG: ^CNXFMCG
- NIFTY Metal: ^CNXMETAL
- NIFTY Realty: ^CNXREALTY
- NIFTY Energy: ^CNXENERGY

## 💡 Tips & Best Practices

### Data Quality
- Ensure sector data covers the same date range as market data
- Handle missing values appropriately
- Validate data before merging

### Performance
- Cache sector data to avoid repeated downloads
- Use efficient data structures (pandas DataFrames)
- Consider data storage in database for large datasets

### Visualization
- Use consistent color schemes across charts
- Provide interactive filters for date ranges
- Include tooltips for detailed information

## 🐛 Troubleshooting

### "No sector data detected"
- Check column names contain 'sector' keyword
- Verify data was merged correctly
- Ensure preprocessing pipeline ran successfully

### "Data download failed"
- Check internet connection
- Verify ticker symbols are correct
- Try alternative data sources

### "Merge resulted in empty dataset"
- Ensure date formats match
- Check for date range overlap
- Validate date column names

## 📞 Support

If you encounter issues:
1. Check the error messages in the dashboard
2. Review the data format examples
3. Verify your data collection code
4. Ensure all dependencies are installed

## 🎉 Summary

The Sector Analysis page is designed to be:
- **User-friendly**: Clear guidance when data is missing
- **Educational**: Explains concepts and benefits
- **Practical**: Provides working code examples
- **Flexible**: Adapts to data availability
- **Professional**: Consistent with platform design

Once you add sector data, you'll unlock powerful sector analysis capabilities that complement the existing market and institutional analysis features!
