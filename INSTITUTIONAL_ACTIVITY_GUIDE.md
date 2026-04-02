# Institutional Activity Page - User Guide

## 📊 Overview

The Institutional Activity page provides comprehensive analysis of Foreign Institutional Investors (FII) and Domestic Institutional Investors (DII) flows and their impact on the Indian stock market (NIFTY index).

## 🎯 What You'll Find

### 1. Key Statistics Dashboard

At the top of the page, you'll see 8 key metrics:

**Row 1:**
- **Total FII Net Flow** - Cumulative FII buying/selling over the period
- **Total DII Net Flow** - Cumulative DII buying/selling over the period
- **Avg Daily FII Flow** - Average daily FII activity
- **Avg Daily DII Flow** - Average daily DII activity

**Row 2:**
- **Max FII Buying Day** - Largest single-day FII purchase
- **Max FII Selling Day** - Largest single-day FII sale
- **Max DII Buying Day** - Largest single-day DII purchase
- **Max DII Selling Day** - Largest single-day DII sale

### 2. FII vs DII Flows Comparison

**Interactive line chart** showing daily net flows for both FII and DII:

- **Green line** = FII Net Flow
- **Orange line** = DII Net Flow
- **Gray dashed line** = Zero reference (above = buying, below = selling)

**How to use:**
- Hover over the chart to see exact values for any date
- Look for periods where both lines are above/below zero (coordinated behavior)
- Identify divergences where FII and DII move in opposite directions

**Insights section:**
- Click "📊 Flow Analysis Insights" to see:
  - FII behavior classification (Strong/Mild Buyers/Sellers)
  - DII behavior classification
  - Relationship analysis (Divergent/Balanced/Dominated)

### 3. Cumulative Flows Chart

**Running total** of institutional investments over time:

- **Rising trend** = Sustained buying (accumulation)
- **Falling trend** = Sustained selling (distribution)
- **Flat trend** = Balanced buying and selling

**How to interpret:**
- Steep upward slopes indicate aggressive accumulation
- Steep downward slopes indicate aggressive distribution
- The final value shows the net position change over the entire period

### 4. Accumulation & Distribution Periods

**Four tabs** showing detected periods of sustained institutional activity:

#### 🟢 FII Accumulation
Periods where FII showed consecutive days of buying

#### 🔴 FII Distribution
Periods where FII showed consecutive days of selling

#### 🟢 DII Accumulation
Periods where DII showed consecutive days of buying

#### 🔴 DII Distribution
Periods where DII showed consecutive days of selling

**Each period shows:**
- Start Date and End Date
- Duration (number of consecutive days)
- Average Flow during the period

**Configuring detection:**
Use the sidebar controls to adjust:
- **Minimum Consecutive Days** (3-10): How many days in a row to qualify as a "period"
- **Minimum Average Flow**: Minimum flow threshold to filter out small periods

### 5. Correlation Heatmap

**Color-coded matrix** showing relationships between variables:

- **Green** = Positive correlation (move together)
- **Red** = Negative correlation (move opposite)
- **White** = No correlation

**Variables analyzed:**
- FII Net flows
- DII Net flows
- Daily Returns
- Volatility (if available)
- Momentum (if available)
- Moving averages (if available)

**Key relationships to watch:**
- **FII vs Returns**: Do FII flows predict market movements?
- **DII vs Returns**: Do DII flows predict market movements?
- **FII vs DII**: Do they move together or opposite?

**Insights section:**
- Click "📊 Correlation Insights" to see:
  - Specific correlation values
  - Interpretation of relationships
  - Analysis of institutional behavior patterns

### 6. Summary & Key Insights

**Left column:** Institutional Behavior
- Complete statistics for FII and DII
- Number of accumulation and distribution periods

**Right column:** Key Takeaways
- Automatically generated insights based on the data
- Highlights important patterns and trends
- Identifies bullish, bearish, or mixed signals

## ⚙️ Sidebar Controls

### Date Range Filter
- **Start Date**: Beginning of analysis period
- **End Date**: End of analysis period
- Default: Last 1 year of data

### Period Detection Settings
- **Minimum Consecutive Days**: 3-10 days (default: 5)
- **Minimum Average Flow**: 0-1000 Cr (default: 0)

## 💡 How to Use This Page

### For Quick Analysis:
1. Look at the key statistics at the top
2. Check the FII vs DII flows chart for recent trends
3. Review the summary insights at the bottom

### For Deep Analysis:
1. Adjust the date range to focus on specific periods
2. Study the cumulative flows to identify long-term trends
3. Configure period detection to find accumulation/distribution phases
4. Analyze the correlation heatmap to understand relationships
5. Read the detailed insights in each expandable section

### For Trading Decisions:
1. Identify current FII/DII behavior (buying or selling)
2. Check if behavior is consistent (high % of positive days)
3. Look for accumulation periods (potential bullish signal)
4. Look for distribution periods (potential bearish signal)
5. Check correlation with returns to gauge predictive power

## 📈 Understanding the Metrics

### Net Flow
- **Positive** = Net buying (Buy > Sell)
- **Negative** = Net selling (Sell > Buy)
- Measured in ₹ Crores

### Accumulation Period
- Consecutive days of positive net flows
- Indicates sustained buying interest
- Generally considered bullish

### Distribution Period
- Consecutive days of negative net flows
- Indicates sustained selling pressure
- Generally considered bearish

### Correlation
- **+1.0** = Perfect positive correlation
- **0.0** = No correlation
- **-1.0** = Perfect negative correlation
- **> 0.3** = Moderate to strong relationship
- **< 0.3** = Weak relationship

## 🎨 Chart Interactions

All charts are interactive:
- **Hover** to see detailed values
- **Zoom** by clicking and dragging
- **Pan** by holding shift and dragging
- **Reset** by double-clicking
- **Toggle series** by clicking legend items

## ⚠️ Important Notes

1. **Data Availability**: The page requires processed data from the pipeline
2. **Date Range**: Ensure your selected date range has available data
3. **Period Detection**: Adjust parameters if no periods are detected
4. **Correlation**: Correlation does not imply causation
5. **Investment Decisions**: This is for analysis only, not investment advice

## 🔍 Common Patterns to Look For

### Bullish Signals:
- ✅ Both FII and DII showing strong net buying
- ✅ Multiple accumulation periods detected
- ✅ Positive correlation between flows and returns
- ✅ Rising cumulative flows trend

### Bearish Signals:
- ⚠️ Both FII and DII showing strong net selling
- ⚠️ Multiple distribution periods detected
- ⚠️ Negative correlation between flows and returns
- ⚠️ Falling cumulative flows trend

### Mixed Signals:
- 🔄 FII and DII moving in opposite directions
- 🔄 Equal number of accumulation and distribution periods
- 🔄 Weak or no correlation with returns
- 🔄 Flat cumulative flows trend

## 🚀 Tips for Best Results

1. **Start with a longer time period** (1 year) to see overall trends
2. **Zoom in on specific periods** of interest for detailed analysis
3. **Compare FII and DII behavior** to identify divergences
4. **Use period detection** to find sustained trends
5. **Check correlations** to understand predictive relationships
6. **Read the insights** for automated pattern detection

## 📞 Need Help?

If you encounter any issues:
1. Check that the data pipeline has been run
2. Verify the date range has available data
3. Try adjusting the period detection parameters
4. Review the error messages for guidance

---

**Happy Analyzing! 📊**

*Smart Money Intelligence Platform*
*Track institutional flows and predict market movements*
