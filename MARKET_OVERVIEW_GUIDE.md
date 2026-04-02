# Market Overview Page - User Guide

## 🎯 Overview

The Market Overview page is your starting point for understanding the current state of the NIFTY index and overall market conditions. It provides comprehensive statistics, trend analysis, and volatility insights.

## 📍 Accessing the Page

1. Start the dashboard: `streamlit run dashboard/app.py`
2. Look for **"1 Market Overview"** in the sidebar navigation
3. Click to open the page

## 🎨 Page Layout

### Top Section: Key Statistics (8 Metrics)

```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│  Current Price  │  Period Return  │ Current Volatil │ Avg Daily Volume│
│   ₹22,474.05    │    +84.48%      │     0.65%       │    150.2M       │
│   +84.48% ▲     │  +₹10,300.50    │                 │                 │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘

┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ Highest Price   │  Lowest Price   │ Avg Daily Return│  Positive Days  │
│   ₹23,110.80    │   ₹12,180.35    │     0.10%       │     52.4%       │
│                 │                 │                 │  129/246 days   │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

### Middle Section: Interactive Charts

#### 1. NIFTY Index Trend
- **Type**: Line chart
- **Shows**: Daily closing prices over selected period
- **Features**:
  - Hover to see exact price and date
  - Zoom in/out by dragging
  - Pan by clicking and dragging
  - Reset view with home button
  - Download as PNG

#### 2. Volatility Trend
- **Type**: Area chart
- **Shows**: Market volatility over time
- **Features**:
  - Filled area for visual impact
  - Same interactive features as trend chart
  - Identifies periods of high/low volatility

#### 3. Return Distribution
- **Type**: Histogram
- **Shows**: Frequency of different return levels
- **Features**:
  - Red dashed line shows mean return
  - Helps identify return patterns
  - Shows if returns are normally distributed

### Bottom Section: Summary & Insights

```
┌─────────────────────────────────────────────────────────────┐
│  🎯 Key Takeaways              │  💡 Market Insights          │
│                                │                              │
│  • Market Direction: 📈 Strong │  • Strong bullish momentum   │
│    Uptrend                     │  • Positive average returns  │
│  • Price Performance: +84.48%  │  • Majority positive days    │
│  • Volatility Status: Normal   │                              │
│  • Trading Activity: 52.4%     │                              │
│    positive days               │                              │
└─────────────────────────────────────────────────────────────┘
```

## 🎛️ Using the Date Range Selector

### Location
- **Sidebar** (left side of screen)

### Controls
1. **Start Date**: Select the beginning of your analysis period
2. **End Date**: Select the end of your analysis period

### Default Behavior
- Automatically shows **last 1 year** of data
- Can extend to full dataset (2020-01-01 to present)

### Tips
- Use shorter periods (1-3 months) for detailed analysis
- Use longer periods (1-3 years) for trend identification
- Compare different periods to spot patterns

## 📊 Understanding the Metrics

### Current Price
- Latest closing price of NIFTY
- Green ▲ = increase from period start
- Red ▼ = decrease from period start

### Period Return
- Percentage change from start to end date
- Shows absolute change in rupees
- Positive = market went up
- Negative = market went down

### Current Volatility
- Measure of price fluctuation
- Higher = more risky/uncertain
- Lower = more stable/calm
- Calculated as 20-day rolling standard deviation

### Avg Daily Volume
- Average number of shares traded per day
- Shown in millions (M)
- Higher volume = more liquidity

### Positive Days
- Percentage of days with positive returns
- Above 50% = bullish bias
- Below 50% = bearish bias

## 🔍 Expandable Insights

### Trend Analysis Insights
Click to expand and see:
- Overall trend classification
- Price movement details
- Absolute and percentage changes
- Trading range (high to low)

### Volatility Insights
Click to expand and see:
- Current vs average volatility
- Maximum volatility and date
- Minimum volatility
- Volatility assessment (High/Normal/Low)

### Return Statistics
Click to expand and see:
- Mean and median returns
- Standard deviation
- Best and worst days with dates
- Percentile analysis

## 🎯 Use Cases

### 1. Daily Market Check
**Goal**: Quick overview of current market state

**Steps**:
1. Open Market Overview page
2. Check current price and period return
3. Look at volatility status
4. Review key takeaways

**Time**: 30 seconds

### 2. Trend Analysis
**Goal**: Understand market direction over time

**Steps**:
1. Set date range to desired period (e.g., 6 months)
2. Examine NIFTY trend chart
3. Expand trend analysis insights
4. Note support/resistance levels

**Time**: 2-3 minutes

### 3. Volatility Assessment
**Goal**: Evaluate market risk level

**Steps**:
1. Check current volatility metric
2. View volatility trend chart
3. Expand volatility insights
4. Compare current to average

**Time**: 1-2 minutes

### 4. Return Pattern Analysis
**Goal**: Understand return distribution

**Steps**:
1. View return distribution histogram
2. Expand return statistics
3. Note mean, median, and extremes
4. Assess if returns are skewed

**Time**: 2-3 minutes

### 5. Period Comparison
**Goal**: Compare different time periods

**Steps**:
1. Set date range to Period 1
2. Note key statistics
3. Change date range to Period 2
4. Compare metrics and trends

**Time**: 3-5 minutes

## 💡 Tips for Effective Use

### 1. Start with the Big Picture
- Use default 1-year view first
- Get overall trend direction
- Then zoom into specific periods

### 2. Watch for Volatility Spikes
- High volatility = increased risk
- Often precedes major moves
- Check news for causes

### 3. Use Return Distribution
- Normal distribution = healthy market
- Skewed distribution = unusual behavior
- Fat tails = more extreme events

### 4. Compare Metrics
- High returns + high volatility = risky gains
- Low returns + low volatility = stable market
- High returns + low volatility = ideal scenario

### 5. Look for Patterns
- Seasonal trends
- Recurring volatility patterns
- Support/resistance levels

## ⚠️ Important Notes

### Data Freshness
- Data is updated when pipeline runs
- Check date range to see latest data
- Run pipeline regularly for current data

### Interpretation
- Past performance ≠ future results
- Use as one input among many
- Combine with other analysis

### Limitations
- Shows NIFTY index only (not individual stocks)
- Historical data (not real-time)
- Technical analysis only (no fundamentals)

## 🔧 Troubleshooting

### "Unable to load market data"
**Solution**: Run the data pipeline
```bash
python scripts/run_pipeline.py
```

### Charts not displaying
**Solution**: 
1. Check internet connection (Plotly needs it)
2. Refresh the page
3. Clear browser cache

### Date range shows no data
**Solution**:
1. Adjust date range to available data
2. Check data/processed/merged_data.csv exists
3. Verify data covers selected period

### Metrics showing NaN or errors
**Solution**:
1. Ensure data pipeline completed successfully
2. Check for missing columns in data
3. Re-run preprocessing if needed

## 📚 Related Pages

After reviewing Market Overview, explore:

1. **Institutional Activity** - See FII/DII flows
2. **Predictions** - View ML predictions
3. **Sector Analysis** - Sector-wise performance (if available)

## 🎓 Learning Resources

### Understanding Volatility
- Low (< 0.5%): Calm market
- Normal (0.5-1.0%): Typical conditions
- High (> 1.0%): Uncertain/risky market

### Return Interpretation
- Mean return: Average daily change
- Median return: Middle value (less affected by outliers)
- Std deviation: Measure of variability

### Trend Classification
- Strong Uptrend: > +5%
- Mild Uptrend: 0% to +5%
- Mild Downtrend: 0% to -5%
- Strong Downtrend: < -5%

## 🎉 Quick Start Checklist

- [ ] Open dashboard with `streamlit run dashboard/app.py`
- [ ] Navigate to "1 Market Overview"
- [ ] Review 8 key statistics at top
- [ ] Examine NIFTY trend chart
- [ ] Check volatility status
- [ ] Review return distribution
- [ ] Read summary insights
- [ ] Adjust date range as needed
- [ ] Expand detailed insights
- [ ] Compare different time periods

## 📞 Support

If you encounter issues:
1. Check TASK_12_COMPLETE.md for technical details
2. Run test_market_overview.py to verify setup
3. Review error messages in terminal
4. Ensure all dependencies are installed

---

**Happy Analyzing! 📊📈**
