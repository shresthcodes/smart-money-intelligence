"""
Smart Money Intelligence Platform - Main Dashboard Application

This is the main entry point for the Streamlit dashboard that provides
interactive visualizations and insights about institutional investment activity
and market predictions.
"""

import streamlit as st

# Configure the page
st.set_page_config(
    page_title="Smart Money Intelligence Platform",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 1rem 0;
        color: #262730;
    }
    .info-box h3 {
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .info-box p {
        color: #262730;
        margin: 0;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
st.sidebar.markdown("---")

# Navigation menu
st.sidebar.markdown("""
### Dashboard Pages

**Home - Welcome and Overview**
- Platform introduction and key features
- Quick start guide for new users
- Navigation instructions

**Market Overview - NIFTY Analysis**
- Historical price trends and patterns
- Daily, weekly, and monthly returns
- Volatility analysis and risk metrics
- Key statistical indicators
- Interactive time-series visualizations

**Institutional Activity - FII/DII Flows**
- Foreign Institutional Investor (FII) data
- Domestic Institutional Investor (DII) data
- Net buying/selling patterns
- Correlation with market movements
- Rolling averages and trend analysis
- Impact on NIFTY index performance

**Sector Analysis - Performance Metrics**
- Sector-wise market performance
- Comparative analysis across sectors
- Top gainers and losers
- Sectoral rotation patterns
- Industry-specific insights

**Predictions - Machine Learning Models**
- Next-day market direction forecasts
- Model confidence scores and probabilities
- Trading signal generation (Bullish/Bearish/Neutral)
- Feature importance analysis
- Historical prediction accuracy
- Model performance metrics

---

### Platform Information

**Purpose:**
This analytical platform tracks institutional investment activity and leverages
machine learning algorithms to predict market movements in the Indian equity market.

**Data Coverage:**
- NIFTY 50 Index (2021-2026)
- FII/DII Daily Flow Data
- Over 1200+ trading days analyzed

**Data Sources:**
- Yahoo Finance API (Market Data)
- National Stock Exchange (Institutional Data)

**Technology Stack:**
- Data Processing: Python, Pandas, NumPy
- Machine Learning: Scikit-learn, XGBoost
- Visualization: Streamlit, Plotly
- Statistical Analysis: SciPy, Statsmodels

**Models Implemented:**
- Logistic Regression (Baseline)
- Random Forest Classifier
- XGBoost Gradient Boosting
- Ensemble Model Selection

**Key Features:**
- Real-time data processing
- Interactive visualizations
- Multi-model predictions
- Rule-based trading signals
- Historical backtesting
""")

# Main content area
st.markdown('<div class="main-header">Smart Money Intelligence Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Track Institutional Investment Activity & Predict Market Movements</div>', unsafe_allow_html=True)

# Welcome section
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="info-box">
        <h3>Market Analysis</h3>
        <p>Comprehensive analysis of NIFTY index trends, volatility, and key market statistics.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-box">
        <h3>Institutional Flows</h3>
        <p>Track FII and DII buying/selling patterns and their correlation with market movements.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="info-box">
        <h3>ML Predictions</h3>
        <p>Machine learning models predict next-day market direction with confidence scores.</p>
    </div>
    """, unsafe_allow_html=True)

# Getting Started section
st.markdown("---")
st.header("Getting Started")

st.markdown("""
Welcome to the Smart Money Intelligence Platform! This dashboard helps you understand
how institutional investors (the "smart money") influence market movements.

### How to Use This Dashboard:

1. **Market Overview** - Start here to see current market trends and statistics
2. **Institutional Activity** - Analyze FII/DII flows and their impact on markets
3. **Sector Analysis** - Explore sector-wise performance (if data available)
4. **Predictions** - View ML predictions and trading signals for next-day market direction

### Key Features:

- **Interactive Charts** - All visualizations are interactive using Plotly
- **Real-time Analysis** - Data is processed and analyzed in real-time
- **ML Predictions** - Multiple models (Logistic Regression, Random Forest, XGBoost)
- **Trading Signals** - Rule-based signals combining ML predictions with technical indicators
- **Historical Analysis** - Analyze patterns over multiple years of data

### Navigation:

Use the **sidebar menu** on the left to navigate between different pages. Each page
provides specific insights and visualizations.

---

**Note:** This is a demonstration platform built for educational and portfolio purposes.
Always conduct your own research before making investment decisions.
""")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>Smart Money Intelligence Platform | Built with Streamlit & Python</p>
    <p>Data Sources: Yahoo Finance, NSE | Technology: Pandas, Scikit-learn, XGBoost, Plotly</p>
</div>
""", unsafe_allow_html=True)
