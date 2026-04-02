"""
Tests for Feature Engineering Module

This module contains both unit tests and property-based tests for feature engineering functions.
"""

import pytest
import pandas as pd
import numpy as np
from hypothesis import given, strategies as st, settings
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from feature_engineering import (
    compute_returns,
    compute_rolling_averages,
    compute_volatility,
    compute_momentum,
    create_lag_features,
    create_target_variable
)


# ============================================================================
# Property-Based Tests
# ============================================================================

@settings(max_examples=100)
@given(st.lists(st.floats(min_value=1.0, max_value=100000.0, allow_nan=False, allow_infinity=False), min_size=2, max_size=100))
def test_return_calculation_property(prices):
    """
    Feature: smart-money-intelligence, Property 9: Return Calculation Correctness
    Validates: Requirements 3.1
    
    For any price series with at least two consecutive prices, the computed daily return
    should equal ((Price_today - Price_yesterday) / Price_yesterday) * 100 within
    floating-point precision.
    """
    # Create DataFrame from price list
    df = pd.DataFrame({'Close': prices})
    
    # Compute returns
    df_with_returns = compute_returns(df, 'Close')
    
    # Verify the formula for all rows except the first
    for i in range(1, len(df)):
        price_today = df.iloc[i]['Close']
        price_yesterday = df.iloc[i-1]['Close']
        
        expected_return = ((price_today - price_yesterday) / price_yesterday) * 100
        actual_return = df_with_returns.iloc[i]['Daily_Return']
        
        # Check within floating-point precision
        assert abs(expected_return - actual_return) < 1e-6, \
            f"Return mismatch at row {i}: expected {expected_return}, got {actual_return}"
    
    # First row should be NaN
    assert pd.isna(df_with_returns.iloc[0]['Daily_Return']), \
        "First row should have NaN return (no previous price)"


@settings(max_examples=100)
@given(
    st.lists(st.floats(min_value=-10000.0, max_value=10000.0, allow_nan=False, allow_infinity=False), min_size=5, max_size=100),
    st.integers(min_value=2, max_value=20)
)
def test_rolling_average_calculation_property(values, window):
    """
    Feature: smart-money-intelligence, Property 10: Rolling Average Calculation
    Validates: Requirements 3.2
    
    For any time series and window size N, the rolling average at position i should equal
    the mean of values from position (i-N+1) to i, for all positions where the window
    is fully defined.
    """
    # Create DataFrame from values list
    df = pd.DataFrame({'Value': values})
    
    # Skip if window is larger than data
    if window > len(df):
        return
    
    # Compute rolling average
    df_with_ma = compute_rolling_averages(df, ['Value'], [window])
    col_name = f'Value_MA{window}'
    
    # Verify rolling average for positions where window is fully defined
    for i in range(window - 1, len(df)):
        window_values = df.iloc[i - window + 1:i + 1]['Value']
        expected_mean = window_values.mean()
        actual_mean = df_with_ma.iloc[i][col_name]
        
        # Check within floating-point precision
        assert abs(expected_mean - actual_mean) < 1e-6, \
            f"Rolling average mismatch at row {i}: expected {expected_mean}, got {actual_mean}"


@settings(max_examples=100)
@given(
    st.lists(st.floats(min_value=-10.0, max_value=10.0, allow_nan=False, allow_infinity=False), min_size=20, max_size=100),
    st.integers(min_value=5, max_value=20)
)
def test_volatility_calculation_property(returns, window):
    """
    Feature: smart-money-intelligence, Property 12: Volatility Calculation
    Validates: Requirements 3.4
    
    For any return series and window size N, the computed volatility at position i should
    equal the standard deviation of returns from position (i-N+1) to i.
    """
    # Create DataFrame from returns list
    df = pd.DataFrame({'Daily_Return': returns})
    
    # Skip if window is larger than data
    if window > len(df):
        return
    
    # Compute volatility
    df_with_vol = compute_volatility(df, 'Daily_Return', window)
    
    # Verify volatility for positions where window is fully defined
    for i in range(window - 1, len(df)):
        window_values = df.iloc[i - window + 1:i + 1]['Daily_Return']
        expected_std = window_values.std()
        actual_vol = df_with_vol.iloc[i]['Volatility']
        
        # Check within floating-point precision
        assert abs(expected_std - actual_vol) < 1e-6, \
            f"Volatility mismatch at row {i}: expected {expected_std}, got {actual_vol}"


@settings(max_examples=100)
@given(
    st.lists(st.floats(min_value=1.0, max_value=100000.0, allow_nan=False, allow_infinity=False), min_size=11, max_size=100),
    st.integers(min_value=1, max_value=10)
)
def test_momentum_calculation_property(prices, period):
    """
    Feature: smart-money-intelligence, Property 13: Momentum Calculation
    Validates: Requirements 3.5
    
    For any price series and period N, the momentum at position i should equal
    (Price_i - Price_(i-N)) for all positions where the lookback is defined.
    """
    # Create DataFrame from prices list
    df = pd.DataFrame({'Close': prices})
    
    # Skip if period is larger than data
    if period >= len(df):
        return
    
    # Compute momentum
    df_with_momentum = compute_momentum(df, 'Close', period)
    
    # Verify momentum for positions where lookback is defined
    for i in range(period, len(df)):
        price_today = df.iloc[i]['Close']
        price_n_days_ago = df.iloc[i - period]['Close']
        
        expected_momentum = price_today - price_n_days_ago
        actual_momentum = df_with_momentum.iloc[i]['Momentum']
        
        # Check within floating-point precision
        assert abs(expected_momentum - actual_momentum) < 1e-6, \
            f"Momentum mismatch at row {i}: expected {expected_momentum}, got {actual_momentum}"


@settings(max_examples=100)
@given(
    st.lists(st.floats(min_value=-10000.0, max_value=10000.0, allow_nan=False, allow_infinity=False), min_size=5, max_size=100),
    st.integers(min_value=1, max_value=3)
)
def test_lag_feature_correctness_property(values, lag):
    """
    Feature: smart-money-intelligence, Property 14: Lag Feature Correctness
    Validates: Requirements 3.6
    
    For any time series and lag value L, the lag feature at position i should equal
    the original value at position (i-L) for all positions where the lag is defined.
    """
    # Create DataFrame from values list
    df = pd.DataFrame({'Value': values})
    
    # Skip if lag is larger than or equal to data length
    if lag >= len(df):
        return
    
    # Create lag features
    df_with_lags = create_lag_features(df, ['Value'], [lag])
    lag_col_name = f'Value_Lag{lag}'
    
    # Verify lag feature for positions where lag is defined
    for i in range(lag, len(df)):
        expected_value = df.iloc[i - lag]['Value']
        actual_value = df_with_lags.iloc[i][lag_col_name]
        
        # Check within floating-point precision
        assert abs(expected_value - actual_value) < 1e-6, \
            f"Lag feature mismatch at row {i}: expected {expected_value}, got {actual_value}"


@settings(max_examples=100)
@given(st.lists(st.floats(min_value=-10.0, max_value=10.0, allow_nan=False, allow_infinity=False), min_size=2, max_size=100))
def test_binary_target_encoding_property(returns):
    """
    Feature: smart-money-intelligence, Property 19: Binary Target Encoding
    Validates: Requirements 7.2
    
    For any return series, the generated target variable should contain only values 0 and 1,
    where 1 represents positive next-day returns and 0 represents non-positive returns.
    """
    # Create DataFrame from returns list
    df = pd.DataFrame({'Daily_Return': returns})
    
    # Create target variable
    df_with_target = create_target_variable(df, 'Daily_Return')
    
    # Check all non-NaN target values are binary (0 or 1)
    target_values = df_with_target['Target'].dropna()
    assert target_values.isin([0, 1]).all(), \
        "Target variable should only contain 0 and 1"
    
    # Verify target encoding for all rows except the last
    for i in range(len(df) - 1):
        next_day_return = df.iloc[i + 1]['Daily_Return']
        target = df_with_target.iloc[i]['Target']
        
        if next_day_return > 0:
            assert target == 1, \
                f"Target should be 1 when next day return ({next_day_return}) is positive"
        else:
            assert target == 0, \
                f"Target should be 0 when next day return ({next_day_return}) is non-positive"
    
    # Last row should have NaN target (no next day data)
    assert pd.isna(df_with_target.iloc[-1]['Target']), \
        "Last row should have NaN target (no next day data)"


# ============================================================================
# Unit Tests
# ============================================================================

def test_compute_returns_basic():
    """Test basic return calculation with known values."""
    df = pd.DataFrame({
        'Close': [100, 110, 105, 115]
    })
    
    result = compute_returns(df, 'Close')
    
    # First row should be NaN
    assert pd.isna(result.iloc[0]['Daily_Return'])
    
    # Check specific calculations
    assert abs(result.iloc[1]['Daily_Return'] - 10.0) < 1e-6  # (110-100)/100 * 100 = 10%
    assert abs(result.iloc[2]['Daily_Return'] - (-4.545454545)) < 1e-6  # (105-110)/110 * 100
    assert abs(result.iloc[3]['Daily_Return'] - 9.523809524) < 1e-6  # (115-105)/105 * 100


def test_compute_returns_missing_column():
    """Test that missing price column raises ValueError."""
    df = pd.DataFrame({'Open': [100, 110]})
    
    with pytest.raises(ValueError, match="Price column 'Close' not found"):
        compute_returns(df, 'Close')


def test_compute_rolling_averages_basic():
    """Test basic rolling average calculation."""
    df = pd.DataFrame({
        'Value': [10, 20, 30, 40, 50]
    })
    
    result = compute_rolling_averages(df, ['Value'], [3])
    
    # Check 3-day rolling average
    assert abs(result.iloc[2]['Value_MA3'] - 20.0) < 1e-6  # (10+20+30)/3
    assert abs(result.iloc[3]['Value_MA3'] - 30.0) < 1e-6  # (20+30+40)/3
    assert abs(result.iloc[4]['Value_MA3'] - 40.0) < 1e-6  # (30+40+50)/3


def test_compute_volatility_basic():
    """Test basic volatility calculation."""
    df = pd.DataFrame({
        'Daily_Return': [1.0, 2.0, 3.0, 4.0, 5.0]
    })
    
    result = compute_volatility(df, 'Daily_Return', 3)
    
    # Volatility should be standard deviation of rolling window
    assert 'Volatility' in result.columns
    assert not result['Volatility'].isna().all()


def test_compute_momentum_basic():
    """Test basic momentum calculation."""
    df = pd.DataFrame({
        'Close': [100, 105, 110, 115, 120]
    })
    
    result = compute_momentum(df, 'Close', 2)
    
    # Check momentum calculations
    assert pd.isna(result.iloc[0]['Momentum'])  # No lookback
    assert pd.isna(result.iloc[1]['Momentum'])  # No lookback
    assert abs(result.iloc[2]['Momentum'] - 10.0) < 1e-6  # 110 - 100
    assert abs(result.iloc[3]['Momentum'] - 10.0) < 1e-6  # 115 - 105
    assert abs(result.iloc[4]['Momentum'] - 10.0) < 1e-6  # 120 - 110


def test_create_lag_features_basic():
    """Test basic lag feature creation."""
    df = pd.DataFrame({
        'Value': [10, 20, 30, 40, 50]
    })
    
    result = create_lag_features(df, ['Value'], [1, 2])
    
    # Check lag-1 feature
    assert pd.isna(result.iloc[0]['Value_Lag1'])
    assert result.iloc[1]['Value_Lag1'] == 10
    assert result.iloc[2]['Value_Lag1'] == 20
    
    # Check lag-2 feature
    assert pd.isna(result.iloc[0]['Value_Lag2'])
    assert pd.isna(result.iloc[1]['Value_Lag2'])
    assert result.iloc[2]['Value_Lag2'] == 10


def test_create_target_variable_basic():
    """Test basic target variable creation."""
    df = pd.DataFrame({
        'Daily_Return': [1.0, -2.0, 3.0, -1.0, 2.0]
    })
    
    result = create_target_variable(df, 'Daily_Return')
    
    # Check target encoding
    assert result.iloc[0]['Target'] == 0  # Next day is -2.0 (negative)
    assert result.iloc[1]['Target'] == 1  # Next day is 3.0 (positive)
    assert result.iloc[2]['Target'] == 0  # Next day is -1.0 (negative)
    assert result.iloc[3]['Target'] == 1  # Next day is 2.0 (positive)
    assert pd.isna(result.iloc[4]['Target'])  # No next day


def test_create_target_variable_zero_return():
    """Test target encoding when next day return is exactly zero."""
    df = pd.DataFrame({
        'Daily_Return': [1.0, 0.0, 2.0]
    })
    
    result = create_target_variable(df, 'Daily_Return')
    
    # Zero return should be encoded as 0 (not positive)
    assert result.iloc[0]['Target'] == 0
