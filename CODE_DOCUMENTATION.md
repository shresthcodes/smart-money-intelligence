# Code Documentation Guide

This document provides an overview of the codebase structure, key functions, and financial logic used in the Smart Money Intelligence Platform.

## Table of Contents

1. [Module Overview](#module-overview)
2. [Data Collection](#data-collection)
3. [Data Preprocessing](#data-preprocessing)
4. [Feature Engineering](#feature-engineering)
5. [Machine Learning](#machine-learning)
6. [Signal Generation](#signal-generation)
7. [Insights Engine](#insights-engine)
8. [Dashboard](#dashboard)
9. [Financial Logic Explained](#financial-logic-explained)
10. [Testing](#testing)

## Module Overview

The codebase is organized into several modules, each with a specific responsibility:

```
scripts/
├── data_collection.py      # Download and load market data
├── preprocessing.py         # Clean and merge datasets
├── feature_engineering.py   # Create derived features
├── model_training.py        # Train ML models
├── insights_generator.py    # Generate insights from data
├── signal_generator.py      # Generate trading signals
└── run_pipeline.py          # Orchestrate the full pipeline

dashboard/
├── app.py                   # Main dashboard entry point
├── pages/                   # Individual dashboard pages
│   ├── 1_Market_Overview.py
│   ├── 2_Institutional_Activity.py
│   ├── 3_Sector_Analysis.py
│   └── 4_Predictions.py
└── utils/                   # Dashboard utilities
    ├── data_loader.py       # Load data for dashboard
    └── visualizations.py    # Create charts and plots

tests/
├── test_data_collection.py
├── test_preprocessing.py
├── test_feature_engineering.py
├── test_model_training.py
├── test_insights_generator.py
└── test_signal_generator.py
```

## Data Collection

### Module: `scripts/data_collection.py`

**Purpose**: Download NIFTY data from Yahoo Finance and load FII/DII data from CSV files.

**Key Functions**:

#### `download_nifty_data()`
Downloads historical NIFTY index data with retry logic and error handling.

**Financial Context**: 
- NIFTY 50 is India's benchmark stock market index
- Represents the weighted average of 50 largest Indian companies
- Used as a proxy for overall market performance

**Implementation Details**:
- Uses yfinance library to access Yahoo Finance API
- Implements exponential backoff (1s, 2s, 4s) for network failures
- Validates date ranges to prevent invalid queries
- Handles MultiIndex columns from yfinance

#### `load_fii_dii_data()`
Loads institutional investor flow data from CSV files.

**Financial Context**:
- FII (Foreign Institutional Investors): Overseas entities investing in Indian markets
- DII (Domestic Institutional Investors): Indian institutional entities
- Their buying/selling activity often moves markets due to large transaction sizes

#### `save_data_to_database()`
Persists data to SQLite database for efficient querying.

## Data Preprocessing

### Module: `scripts/preprocessing.py`

**Purpose**: Clean raw data and merge datasets for analysis.

**Key Functions**:

#### `clean_market_data()`
Cleans NIFTY market data by:
- Converting dates to datetime format
- Removing duplicate rows
- Sorting chronologically
- Forward-filling missing prices (assumes last known price)

**Financial Rationale**: Forward fill is appropriate for prices because markets don't have gaps - the last traded price remains valid until a new trade occurs.

#### `clean_institutional_data()`
Cleans FII/DII data and computes net flows:
```python
FII_Net = FII_Buy - FII_Sell
DII_Net = DII_Buy - DII_Sell
```

**Financial Interpretation**:
- Positive Net Flow: Net buying (bullish sentiment)
- Negative Net Flow: Net selling (bearish sentiment)
- Magnitude indicates strength of conviction

#### `merge_datasets()`
Merges market and institutional data by date using inner join.

**Why Inner Join**: Only keeps dates where both datasets have data, ensuring complete information for analysis.

## Feature Engineering

### Module: `scripts/feature_engineering.py`

**Purpose**: Create derived features that capture market dynamics.

**Key Functions**:

#### `compute_returns()`
Calculates daily percentage returns:
```python
Return = (Price_today - Price_yesterday) / Price_yesterday * 100
```

**Financial Significance**: Returns normalize price changes, making them comparable across different price levels and time periods.

#### `compute_rolling_averages()`
Calculates moving averages (5, 10, 20 days) for smoothing noisy data.

**Financial Application**:
- **5-day MA**: Short-term trend
- **10-day MA**: Medium-term trend
- **20-day MA**: Long-term trend
- Crossovers between MAs signal trend changes

#### `compute_volatility()`
Calculates 20-day rolling standard deviation of returns.

**Financial Interpretation**:
- High volatility: Uncertain, risky market conditions
- Low volatility: Stable, predictable market
- Volatility clustering: High volatility periods tend to persist

#### `compute_momentum()`
Calculates 10-day momentum:
```python
Momentum = Price_today - Price_10_days_ago
```

**Financial Significance**: Momentum captures the rate of price change, indicating trend strength.

#### `create_lag_features()`
Creates lagged versions of features (1, 2, 3 days back).

**ML Rationale**: Time series models need historical context. Lags provide the model with "memory" of recent patterns.

#### `create_target_variable()`
Creates binary target for next-day prediction:
```python
Target = 1 if next_day_return > 0 else 0
```

**ML Design Choice**: Binary classification is simpler and more robust than regression for market direction prediction.

## Machine Learning

### Module: `scripts/model_training.py`

**Purpose**: Train ensemble models to predict market direction.

**Key Class**: `MarketPredictor`

#### Model Selection

**Three Models Used**:

1. **Logistic Regression**
   - Simple, interpretable baseline
   - Fast training and prediction
   - Linear decision boundary

2. **Random Forest**
   - Handles non-linear relationships
   - Robust to outliers
   - Provides feature importance

3. **XGBoost**
   - State-of-the-art gradient boosting
   - Often best performance
   - Handles complex interactions

**Ensemble Approach**: Train all three, select best performer on validation set.

#### Feature Selection

**Features Used**:
- FII_Net, DII_Net (institutional flows)
- Daily_Return lags (recent price action)
- Volatility (market uncertainty)
- Momentum (trend strength)
- Rolling averages (trend direction)
- Lag features (temporal patterns)

**Financial Rationale**: These features capture different aspects of market behavior:
- Flows: Smart money activity
- Returns: Price momentum
- Volatility: Risk environment
- MAs: Trend context

#### Train-Test Split

**Critical Design Choice**: Chronological split (no shuffle)

**Why**: Time series data has temporal dependencies. Shuffling would leak future information into training, causing overfitting.

```python
# Correct for time series
train = data[:80%]
test = data[80%:]

# WRONG for time series (would shuffle)
train, test = train_test_split(data, shuffle=True)  # DON'T DO THIS!
```

#### Model Evaluation

**Metrics Used**:
- **Accuracy**: Overall correctness
- **Precision**: Of predicted ups, how many were actually up
- **Recall**: Of actual ups, how many did we predict
- **F1 Score**: Harmonic mean of precision and recall

**Expected Performance**: 60-65% accuracy is good for market prediction (better than random 50%).

## Signal Generation

### Module: `scripts/signal_generator.py`

**Purpose**: Generate actionable trading signals by combining rules and ML.

**Key Function**: `generate_signal()`

### Signal Rules

#### Bullish Signal
```
IF FII_Net > threshold (e.g., 1000 crores)
AND Momentum > 0
AND ML predicts Up (1)
THEN Signal = Bullish
```

**Financial Logic**: 
- Strong institutional buying (FII_Net > threshold)
- Positive price momentum (uptrend)
- ML confirmation
- All three factors align → High conviction bullish signal

#### Bearish Signal
```
IF FII_Net < -threshold (e.g., -1000 crores)
AND Momentum < 0
AND ML predicts Down (0)
THEN Signal = Bearish
```

**Financial Logic**:
- Strong institutional selling (FII_Net < -threshold)
- Negative price momentum (downtrend)
- ML confirmation
- All three factors align → High conviction bearish signal

#### Neutral Signal
```
ELSE Signal = Neutral
```

**Financial Logic**: Mixed or weak signals → Stay on sidelines, wait for clarity.

### Confidence Calculation

**For Bullish/Bearish Signals**:
```python
confidence = (ml_probability * 0.5 + 
             fii_strength * 0.3 + 
             momentum_strength * 0.2)
```

**Weighting Rationale**:
- ML probability (50%): Primary signal source
- FII strength (30%): Smart money conviction
- Momentum strength (20%): Trend confirmation

**For Neutral Signals**:
```python
confidence = ml_probability  # or (1 - ml_probability) for Down prediction
```

Lower confidence indicates uncertainty, appropriate for neutral stance.

## Insights Engine

### Module: `scripts/insights_generator.py`

**Purpose**: Identify patterns and anomalies in institutional behavior.

**Key Functions**:

#### `identify_unusual_activity()`
Detects days with institutional activity exceeding statistical thresholds.

**Statistical Method**:
```python
threshold = mean + (2 * std_dev)  # or mean - (2 * std_dev)
```

**Financial Interpretation**: Activity beyond 2 standard deviations is statistically unusual, potentially signaling important events.

#### `detect_accumulation_periods()`
Finds consecutive days of positive net flows.

**Financial Significance**: 
- Sustained buying (5+ days) suggests institutional conviction
- Often precedes price rallies
- Indicates smart money positioning for upside

#### `detect_selling_periods()`
Finds consecutive days of negative net flows.

**Financial Significance**:
- Sustained selling suggests institutional concern
- Often precedes price declines
- Indicates smart money reducing exposure

#### `compute_market_reaction()`
Calculates average market returns following specific events.

**Use Case**: "What happens to NIFTY after heavy FII buying?"

**Statistical Approach**:
1. Identify events (e.g., FII_Net > threshold)
2. Measure forward returns (1, 5, 10 days)
3. Compute average, median, success rate

## Dashboard

### Module: `dashboard/`

**Purpose**: Interactive web interface for exploring data and predictions.

### Page Structure

#### 1. Market Overview (`pages/1_Market_Overview.py`)
- NIFTY price trends
- Key statistics (current price, YTD return)
- Volatility indicators

#### 2. Institutional Activity (`pages/2_Institutional_Activity.py`)
- FII vs DII flows comparison
- Cumulative flows
- Accumulation/distribution periods
- Correlation heatmaps

#### 3. Sector Analysis (`pages/3_Sector_Analysis.py`)
- Sector performance (if data available)
- Sector rotation analysis

#### 4. Predictions (`pages/4_Predictions.py`)
- Next-day market direction prediction
- Trading signal (Bullish/Neutral/Bearish)
- Confidence scores
- Feature importance

### Visualization Utilities (`utils/visualizations.py`)

**Key Functions**:
- `plot_nifty_trend()`: Interactive line chart with Plotly
- `plot_institutional_flows()`: Dual-axis chart for FII/DII
- `plot_correlation_heatmap()`: Correlation matrix visualization
- `plot_prediction_gauge()`: Gauge chart for confidence

**Why Plotly**: Interactive charts allow users to zoom, pan, and hover for details.

## Financial Logic Explained

### Why Track Institutional Flows?

**Smart Money Hypothesis**: Institutional investors have:
- Better research capabilities
- Access to company management
- Sophisticated analysis tools
- Long-term perspective

Their actions often predict market movements, making them valuable to track.

### FII vs DII Behavior

**Typical Patterns**:
- **FIIs**: More volatile, react to global factors, often trend-followers
- **DIIs**: More stable, provide market support, often contrarian

**Divergence Signals**:
- FII selling + DII buying: Potential bottom (DIIs catching falling knife)
- FII buying + DII selling: Potential top (DIIs taking profits)

### Momentum Indicators

**Why Momentum Matters**:
- Markets trend: "The trend is your friend"
- Momentum persists in short-term (1-3 months)
- Combining momentum with flows improves signals

### Volatility Considerations

**High Volatility Periods**:
- Reduce position sizes
- Widen stop losses
- Expect larger swings

**Low Volatility Periods**:
- Potential for volatility expansion
- Complacency risk
- Often precedes major moves

## Testing

### Unit Tests

**Purpose**: Verify specific functionality with known inputs/outputs.

**Example**:
```python
def test_return_calculation():
    df = pd.DataFrame({'Close': [100, 105, 103]})
    result = compute_returns(df)
    assert result.iloc[1]['Daily_Return'] == 5.0  # (105-100)/100 * 100
    assert result.iloc[2]['Daily_Return'] == -1.9047...  # (103-105)/105 * 100
```

### Property-Based Tests

**Purpose**: Verify universal properties across many random inputs.

**Example**:
```python
@given(pdst.data_frames([
    pdst.column('Price', dtype=float, elements=st.floats(min_value=1, max_value=100000))
]))
def test_return_calculation_property(df):
    """For any price series, returns should match the formula."""
    if len(df) < 2:
        return
    
    df_with_returns = compute_returns(df, 'Price')
    
    for i in range(1, len(df)):
        expected = ((df.iloc[i]['Price'] - df.iloc[i-1]['Price']) / 
                   df.iloc[i-1]['Price']) * 100
        actual = df_with_returns.iloc[i]['Daily_Return']
        assert abs(expected - actual) < 1e-6
```

**Why Property-Based Testing**: 
- Tests with 100+ random inputs per property
- Finds edge cases humans miss
- Provides stronger correctness guarantees

## Code Quality Standards

### Docstring Format

All functions follow this format:
```python
def function_name(arg1: type, arg2: type) -> return_type:
    """
    Brief description.
    
    Longer description with context and financial rationale.
    
    Args:
        arg1: Description
        arg2: Description
    
    Returns:
        Description of return value
    
    Raises:
        ExceptionType: When and why
    
    Examples:
        >>> function_name(value1, value2)
        expected_output
    """
```

### Error Handling

**Principles**:
1. Validate inputs early
2. Provide descriptive error messages
3. Log errors for debugging
4. Fail gracefully when possible

**Example**:
```python
if price_col not in df.columns:
    error_msg = f"Price column '{price_col}' not found. Available columns: {df.columns.tolist()}"
    logger.error(error_msg)
    raise ValueError(error_msg)
```

### Logging

**Levels Used**:
- `INFO`: Normal operations (data loaded, model trained)
- `WARNING`: Potential issues (missing values filled)
- `ERROR`: Failures (file not found, invalid data)

**Example**:
```python
logger.info(f"Loading data from {filepath}")
logger.warning(f"Found {missing_count} missing values, filling with forward fill")
logger.error(f"Failed to load file: {e}")
```

## Best Practices

### For Contributors

1. **Add docstrings** to all public functions
2. **Comment complex logic**, especially financial calculations
3. **Write tests** for new features (both unit and property tests)
4. **Log important operations** for debugging
5. **Handle errors gracefully** with descriptive messages
6. **Follow naming conventions**: snake_case for functions, PascalCase for classes
7. **Keep functions focused**: Single responsibility principle
8. **Document financial rationale**: Explain why, not just what

### For Users

1. **Read docstrings** to understand function behavior
2. **Check logs** when debugging issues
3. **Review tests** for usage examples
4. **Understand financial context** before modifying logic
5. **Test changes** thoroughly before deploying

## Further Reading

### Financial Concepts
- "Technical Analysis of the Financial Markets" by John Murphy
- "Quantitative Trading" by Ernest Chan
- NSE India website for institutional flow data

### Machine Learning
- "Hands-On Machine Learning" by Aurélien Géron
- scikit-learn documentation
- XGBoost documentation

### Python Best Practices
- PEP 8 Style Guide
- "Clean Code" by Robert Martin
- Python logging documentation

---

**Last Updated**: 2024
**Version**: 1.0
