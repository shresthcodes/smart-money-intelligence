# Smart Money Intelligence

An end-to-end ML pipeline for detecting institutional trading patterns and pump-dump schemes in NSE/BSE stock market data, with an interactive 6-page Streamlit dashboard.

## Features

- **Data Collection** — Fetches NSE/BSE stock data using yfinance
- **Preprocessing** — Cleans and normalizes OHLCV data
- **Feature Engineering** — Technical indicators (RSI, MACD, Bollinger Bands, Volume spikes)
- **ML Models** — Random Forest & XGBoost for pattern detection
- **Signal Generator** — Buy/Sell/Hold signals based on institutional activity
- **Streamlit Dashboard** — 6-page interactive dashboard:
  - Market Overview
  - Institutional Activity
  - Sector Analysis
  - Predictions
- **18+ Unit & Integration Tests** — Ensuring pipeline reliability

## Tech Stack

- **Language:** Python 3.10+
- **ML:** Scikit-learn, XGBoost, Pandas, NumPy
- **Visualization:** Streamlit, Matplotlib, Plotly
- **Data:** yfinance, NSE/BSE APIs

## Getting Started

```bash
# Clone the repo
git clone https://github.com/shresthcodes/smart-money-intelligence.git
cd smart-money-intelligence

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run dashboard/app.py
```

## Project Structure

```
smart-money-intelligence/
├── scripts/          # Data collection, preprocessing, ML pipeline
├── dashboard/        # Streamlit app and pages
├── tests/            # Unit and integration tests
└── data/             # Sample data
```

## Author

**Shresth Pandey**  
B.Tech CSE @ GSFC University, Vadodara  
[LinkedIn](https://linkedin.com/in/shresth-pandey-1187ba372) • [GitHub](https://github.com/shresthcodes)
