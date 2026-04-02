# Smart Money Intelligence Dashboard - User Guide

## 🚀 Quick Start

### Starting the Dashboard

```bash
cd "tracking game hand/smart-money-intelligence"
python -m streamlit run dashboard/app.py
```

The dashboard will open automatically in your browser at: **http://localhost:8501**

---

## 📊 Dashboard Pages Overview

### 1. Home Page (Landing)

**What you'll see:**
- Welcome message and platform overview
- Three feature cards:
  - 📈 Market Analysis
  - 🏢 Institutional Flows
  - 🔮 ML Predictions
- Getting started guide
- Navigation instructions

**Purpose:** Introduction to the platform and its capabilities

---

### 2. 📈 Market Overview

**What you'll see:**
- **NIFTY Trend Chart**: Interactive line chart showing NIFTY index movement over the last year
- **Key Statistics Cards**:
  - Current NIFTY price
  - Year-to-date (YTD) return percentage
  - Current volatility level
- **Volatility Trend Chart**: Shows how market volatility has changed over time
- **Date Range Selector**: Filter data by custom date ranges

**Interactive Features:**
- Hover over charts to see exact values
- Zoom in/out on specific time periods
- Pan across the timeline
- Toggle data series on/off

**Purpose:** Understand overall market trends and current market conditions

---

### 3. 🏢 Institutional Activity

**What you'll see:**
- **FII vs DII Flows Chart**: Dual-axis line chart comparing Foreign and Domestic institutional flows
- **Cumulative Flows Chart**: Shows accumulated buying/selling over time
- **Accumulation/Distribution Periods Table**: Lists periods of sustained institutional buying or selling
- **Correlation Heatmap**: Visual representation of correlations between:
  - FII flows and NIFTY returns
  - DII flows and NIFTY returns
  - FII and DII flows

**Interactive Features:**
- Hover to see exact flow amounts
- Compare FII and DII patterns visually
- Identify accumulation and distribution phases
- Understand correlation strengths

**Purpose:** Track "smart money" behavior and its impact on markets

---

### 4. 🎯 Sector Analysis

**What you'll see:**
- If sector data is available:
  - Sector performance heatmap
  - Sector rankings by returns
  - Sector rotation analysis
- If sector data is NOT available:
  - Placeholder message
  - Instructions for adding sector data

**Purpose:** Analyze sector-wise market performance (optional feature)

---

### 5. 🔮 Predictions

**What you'll see:**
- **Next-Day Prediction**: Up or Down prediction for tomorrow's market
- **Probability Gauge**: Visual gauge showing prediction confidence (0-100%)
- **Trading Signal**: 
  - 🟢 **Bullish** - Strong buy signal
  - 🟡 **Neutral** - Hold/wait signal
  - 🔴 **Bearish** - Strong sell signal
- **Confidence Score**: Numerical confidence level
- **Feature Importance Chart**: Shows which factors influenced the prediction most
- **Model Information**: Details about the ML model used

**Interactive Features:**
- View probability distribution
- Understand prediction reasoning
- See which features matter most
- Check model performance metrics

**Purpose:** Get data-driven predictions and trading signals

---

## 🎨 Navigation

### Sidebar Menu
Located on the left side of every page:
- **Navigation Links**: Click to switch between pages
- **About Section**: Information about the platform
- **Data Sources**: Where the data comes from
- **Technology Stack**: Tools and libraries used

### Page Layout
- **Wide Layout**: Maximizes screen space for charts
- **Responsive Design**: Works on different screen sizes
- **Clean Interface**: Professional, easy-to-read design

---

## 💡 Tips for Best Experience

### 1. Data Exploration
- Start with **Market Overview** to understand current conditions
- Move to **Institutional Activity** to see smart money behavior
- Check **Predictions** for actionable insights

### 2. Chart Interaction
- **Hover**: See exact values and dates
- **Zoom**: Click and drag to zoom into specific periods
- **Pan**: Hold and drag to move across time
- **Reset**: Double-click to reset zoom
- **Legend**: Click legend items to show/hide data series

### 3. Understanding Signals

**Bullish Signal** 🟢
- Heavy FII buying detected
- Positive momentum
- ML model predicts upward movement
- **Action**: Consider buying opportunities

**Neutral Signal** 🟡
- Mixed or unclear signals
- No strong directional bias
- **Action**: Wait for clearer signals

**Bearish Signal** 🔴
- Heavy institutional selling
- Negative momentum
- ML model predicts downward movement
- **Action**: Consider defensive positions

### 4. Data Freshness
- Data is loaded from processed CSV files
- To update data, run the data collection pipeline:
  ```bash
  python scripts/run_pipeline.py
  ```
- Dashboard uses caching for fast performance

---

## 🔧 Troubleshooting

### Dashboard Won't Start
```bash
# Install required packages
pip install streamlit plotly pandas numpy scikit-learn xgboost

# Try running again
python -m streamlit run dashboard/app.py
```

### Charts Not Loading
- Check that `data/processed/merged_data.csv` exists
- Verify the file is not empty
- Run the data pipeline if needed

### Predictions Page Error
- Ensure `models/market_prediction_model.pkl` exists
- Check that model training completed successfully
- Re-run model training if needed:
  ```bash
  python scripts/model_training.py
  ```

### Port Already in Use
```bash
# Use a different port
python -m streamlit run dashboard/app.py --server.port 8502
```

---

## 📈 Understanding the Data

### NIFTY Index
- India's benchmark stock market index
- Represents top 50 companies on NSE
- Indicator of overall market health

### FII (Foreign Institutional Investors)
- Overseas entities investing in Indian markets
- Large buying = bullish signal
- Large selling = bearish signal

### DII (Domestic Institutional Investors)
- Indian institutional entities (mutual funds, insurance companies)
- Often counter-balance FII flows
- Provide market stability

### Volatility
- Measure of market uncertainty
- High volatility = risky conditions
- Low volatility = stable conditions

### Momentum
- Rate of price change
- Positive momentum = upward trend
- Negative momentum = downward trend

---

## 🎯 Use Cases

### For Traders
1. Check daily predictions before market open
2. Monitor institutional flows for trend confirmation
3. Use signals to time entry/exit points
4. Track volatility for risk management

### For Analysts
1. Study historical correlations
2. Analyze institutional behavior patterns
3. Identify accumulation/distribution phases
4. Understand feature importance in predictions

### For Students/Learners
1. Understand market dynamics
2. Learn about institutional investing
3. See machine learning in action
4. Explore data visualization techniques

### For Portfolio Managers
1. Monitor smart money activity
2. Assess market sentiment
3. Make data-driven allocation decisions
4. Track sector performance

---

## 📊 Data Sources

### Market Data
- **Source**: Yahoo Finance (yfinance library)
- **Ticker**: ^NSEI (NIFTY 50)
- **Frequency**: Daily
- **History**: Multiple years

### Institutional Data
- **Source**: NSE (National Stock Exchange of India)
- **Data**: FII/DII buy/sell amounts
- **Frequency**: Daily
- **Format**: CSV files

---

## 🛠️ Technology Stack

### Backend
- **Python 3.8+**: Core programming language
- **Pandas**: Data manipulation
- **NumPy**: Numerical computations
- **Scikit-learn**: Machine learning models
- **XGBoost**: Gradient boosting model
- **Joblib**: Model persistence

### Frontend
- **Streamlit**: Web dashboard framework
- **Plotly**: Interactive visualizations
- **Matplotlib/Seaborn**: Additional charts

### Data Storage
- **CSV Files**: Raw and processed data
- **SQLite**: Optional database storage
- **Pickle**: Model serialization

---

## 📝 Important Notes

### Disclaimer
⚠️ **This is a demonstration platform for educational purposes.**
- Not financial advice
- Always do your own research
- Past performance doesn't guarantee future results
- Consult a financial advisor before investing

### Data Accuracy
- Data is sourced from public APIs
- Subject to availability and accuracy of sources
- May have delays or gaps
- Verify critical data independently

### Model Limitations
- ML models are probabilistic, not deterministic
- Accuracy varies with market conditions
- Should be one of many decision factors
- Regular retraining recommended

---

## 🚀 Next Steps

After exploring the dashboard:

1. **Customize**: Modify charts and layouts to your needs
2. **Extend**: Add new features or data sources
3. **Deploy**: Host on cloud platforms (Streamlit Cloud, Heroku, AWS)
4. **Share**: Use for portfolio demonstrations or presentations
5. **Learn**: Study the code to understand implementation

---

## 📞 Support

For issues or questions:
- Check the README.md file
- Review the code documentation
- Examine the design and requirements documents
- Run the test suite to verify functionality

---

**Happy Analyzing! 📊📈🚀**
