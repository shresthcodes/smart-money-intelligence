"""
Tests for Insights Generation Module

This module contains unit tests and property-based tests for the insights
generation functions.
"""

import pytest
import pandas as pd
import numpy as np
from hypothesis import given, strategies as st, settings
from datetime import datetime, timedelta
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from insights_generator import (
    identify_unusual_activity,
    detect_accumulation_periods,
    detect_selling_periods,
    compute_market_reaction
)


# ============================================================================
# Property-Based Tests
# ============================================================================

@settings(max_examples=100)
@given(
    data=st.lists(
        st.floats(min_value=-10000, max_value=10000, allow_nan=False, allow_infinity=False),
        min_size=10,
        max_size=100
    ),
    threshold_std=st.floats(min_value=0.5, max_value=5.0)
)
def test_threshold_detection_property(data, threshold_std):
    """
    Feature: smart-money-intelligence, Property 16: Threshold-Based Detection
    
    For any time series and statistical threshold T, all days identified as
    "unusual activity" should have values that exceed the threshold
    (mean + T * std_dev or mean - T * std_dev).
    
    Validates: Requirements 6.1
    """
    # Create DataFrame
    df = pd.DataFrame({
        'Date': pd.date_range(start='2020-01-01', periods=len(data)),
        'FII_Net': data
    })
    
    # Calculate expected thresholds
    mean_value = np.mean(data)
    std_value = np.std(data)
    upper_threshold = mean_value + (threshold_std * std_value)
    lower_threshold = mean_value - (threshold_std * std_value)
    
    # Identify unusual activity
    unusual = identify_unusual_activity(df, 'FII_Net', threshold_std)
    
    # Property: All identified days should exceed threshold
    for _, row in unusual.iterrows():
        value = row['FII_Net']
        assert value > upper_threshold or value < lower_threshold, \
            f"Value {value} does not exceed thresholds [{lower_threshold}, {upper_threshold}]"


@settings(max_examples=100)
@given(
    positive_runs=st.lists(
        st.integers(min_value=1, max_value=20),
        min_size=1,
        max_size=5
    ),
    negative_runs=st.lists(
        st.integers(min_value=1, max_value=20),
        min_size=1,
        max_size=5
    ),
    window=st.integers(min_value=2, max_value=10)
)
def test_period_detection_consistency_property(positive_runs, negative_runs, window):
    """
    Feature: smart-money-intelligence, Property 17: Period Detection Consistency
    
    For any detected accumulation or selling period, all days within that period
    should meet the specified criteria (consecutive positive/negative flows
    above/below threshold).
    
    Validates: Requirements 6.2, 6.3
    """
    # Create alternating positive and negative runs
    data = []
    dates = []
    current_date = datetime(2020, 1, 1)
    
    for i in range(min(len(positive_runs), len(negative_runs))):
        # Add positive run
        for _ in range(positive_runs[i]):
            data.append(np.random.uniform(100, 1000))
            dates.append(current_date)
            current_date += timedelta(days=1)
        
        # Add negative run
        for _ in range(negative_runs[i]):
            data.append(np.random.uniform(-1000, -100))
            dates.append(current_date)
            current_date += timedelta(days=1)
    
    df = pd.DataFrame({
        'Date': dates,
        'FII_Net': data
    })
    
    # Detect accumulation periods
    accumulation_periods = detect_accumulation_periods(df, 'FII_Net', window=window, threshold=0)
    
    # Property: All days in detected periods should have positive flows
    for start_date, end_date in accumulation_periods:
        period_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
        assert len(period_df) >= window, f"Period length {len(period_df)} < window {window}"
        assert all(period_df['FII_Net'] > 0), "Not all days in accumulation period have positive flows"
    
    # Detect selling periods
    selling_periods = detect_selling_periods(df, 'FII_Net', window=window, threshold=0)
    
    # Property: All days in detected periods should have negative flows
    for start_date, end_date in selling_periods:
        period_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
        assert len(period_df) >= window, f"Period length {len(period_df)} < window {window}"
        assert all(period_df['FII_Net'] < 0), "Not all days in selling period have negative flows"


@settings(max_examples=100)
@given(
    returns=st.lists(
        st.floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False),
        min_size=10,
        max_size=100
    )
)
def test_average_reaction_calculation_property(returns):
    """
    Feature: smart-money-intelligence, Property 18: Average Reaction Calculation
    
    For any set of events and corresponding outcomes, the computed average market
    reaction should equal the arithmetic mean of all outcome values associated
    with those events.
    
    Validates: Requirements 6.4
    """
    # Create DataFrame with events and returns
    df = pd.DataFrame({
        'Date': pd.date_range(start='2020-01-01', periods=len(returns)),
        'FII_Net': np.random.uniform(-1000, 1000, len(returns)),
        'Daily_Return': returns
    })
    
    # Set a threshold that will capture some events
    threshold = 500
    
    # Compute market reaction
    reaction = compute_market_reaction(df, 'FII_Net', threshold, 'Daily_Return', forward_days=1)
    
    # Manually calculate expected average
    event_mask = df['FII_Net'] > threshold
    forward_returns = df['Daily_Return'].shift(-1)
    event_returns = forward_returns[event_mask].dropna()
    
    if len(event_returns) > 0:
        expected_avg = event_returns.mean()
        # Property: Computed average should equal arithmetic mean
        assert abs(reaction['avg_return'] - expected_avg) < 1e-6, \
            f"Computed average {reaction['avg_return']} != expected {expected_avg}"
        
        # Also verify count
        assert reaction['count'] == len(event_returns), \
            f"Count mismatch: {reaction['count']} != {len(event_returns)}"


# ============================================================================
# Unit Tests
# ============================================================================

def test_identify_unusual_activity_basic():
    """Test basic unusual activity identification"""
    # Create test data with clear outliers
    data = [100] * 10 + [1000, -1000] + [100] * 10
    df = pd.DataFrame({
        'Date': pd.date_range(start='2020-01-01', periods=len(data)),
        'FII_Net': data
    })
    
    unusual = identify_unusual_activity(df, 'FII_Net', threshold_std=2.0)
    
    # Should identify the two outliers
    assert len(unusual) >= 2
    assert 1000 in unusual['FII_Net'].values
    assert -1000 in unusual['FII_Net'].values


def test_identify_unusual_activity_missing_column():
    """Test error handling for missing column"""
    df = pd.DataFrame({
        'Date': pd.date_range(start='2020-01-01', periods=10),
        'FII_Net': [100] * 10
    })
    
    with pytest.raises(ValueError, match="Column 'NonExistent' not found"):
        identify_unusual_activity(df, 'NonExistent', threshold_std=2.0)


def test_detect_accumulation_periods_basic():
    """Test basic accumulation period detection"""
    # Create data with clear accumulation period
    data = [-100] * 5 + [200] * 7 + [-100] * 5
    df = pd.DataFrame({
        'Date': pd.date_range(start='2020-01-01', periods=len(data)),
        'FII_Net': data
    })
    
    periods = detect_accumulation_periods(df, 'FII_Net', window=5, threshold=0)
    
    # Should detect one accumulation period
    assert len(periods) >= 1


def test_detect_selling_periods_basic():
    """Test basic selling period detection"""
    # Create data with clear selling period
    data = [100] * 5 + [-200] * 7 + [100] * 5
    df = pd.DataFrame({
        'Date': pd.date_range(start='2020-01-01', periods=len(data)),
        'FII_Net': data
    })
    
    periods = detect_selling_periods(df, 'FII_Net', window=5, threshold=0)
    
    # Should detect one selling period
    assert len(periods) >= 1


def test_compute_market_reaction_basic():
    """Test basic market reaction computation"""
    # Create test data
    df = pd.DataFrame({
        'Date': pd.date_range(start='2020-01-01', periods=20),
        'FII_Net': [100, 200, 1500, 100, 200, 1600, 100] + [100] * 13,
        'Daily_Return': [1.0, -0.5, 2.0, 1.5, -1.0, 2.5, 0.5] + [0.5] * 13
    })
    
    # Compute reaction after high FII buying (threshold = 1000)
    reaction = compute_market_reaction(df, 'FII_Net', 1000, 'Daily_Return', forward_days=1)
    
    # Should find events and compute statistics
    assert reaction['count'] >= 2
    assert 'avg_return' in reaction
    assert 'median_return' in reaction
    assert 'positive_pct' in reaction


def test_compute_market_reaction_no_events():
    """Test market reaction when no events match threshold"""
    df = pd.DataFrame({
        'Date': pd.date_range(start='2020-01-01', periods=10),
        'FII_Net': [100] * 10,
        'Daily_Return': [1.0] * 10
    })
    
    # Use very high threshold that won't match any events
    reaction = compute_market_reaction(df, 'FII_Net', 10000, 'Daily_Return', forward_days=1)
    
    # Should return zero statistics
    assert reaction['count'] == 0
    assert reaction['avg_return'] == 0.0


def test_period_detection_missing_date_column():
    """Test error handling for missing Date column"""
    df = pd.DataFrame({
        'FII_Net': [100] * 10
    })
    
    with pytest.raises(ValueError, match="'Date' column not found"):
        detect_accumulation_periods(df, 'FII_Net', window=5, threshold=0)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
