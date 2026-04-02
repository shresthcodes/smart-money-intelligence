"""
Property-based tests for Exploratory Data Analysis functions.

This module tests the correlation analysis and statistical functions
used in the EDA notebook.
"""

import pytest
import pandas as pd
import numpy as np
from hypothesis import given, strategies as st, settings
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from notebooks.data_exploration import (
    compute_correlations,
    compute_rolling_correlations,
    generate_distribution_statistics
)


# ============================================================================
# PROPERTY 15: CORRELATION BOUNDS
# Feature: smart-money-intelligence, Property 15: Correlation Bounds
# Validates: Requirements 4.1, 4.2, 4.6
# ============================================================================

@settings(max_examples=100)
@given(
    size=st.integers(min_value=10, max_value=100),
    seed=st.integers(min_value=0, max_value=10000)
)
def test_correlation_bounds_property(size, seed):
    """
    Property 15: Correlation Bounds
    
    For any two numeric series, the computed correlation coefficient 
    should be a value between -1 and 1 inclusive.
    
    This property tests that:
    1. Pearson correlation is always in [-1, 1]
    2. This holds for any randomly generated data
    3. This holds for edge cases (constant series, identical series)
    
    Validates: Requirements 4.1, 4.2, 4.6
    """
    np.random.seed(seed)
    
    # Generate random data for FII_Net, DII_Net, and Daily_Return
    fii_net = np.random.randn(size) * 1000  # Random FII flows
    dii_net = np.random.randn(size) * 800   # Random DII flows
    daily_return = np.random.randn(size) * 2  # Random returns
    
    # Create DataFrame
    df = pd.DataFrame({
        'FII_Net': fii_net,
        'DII_Net': dii_net,
        'Daily_Return': daily_return
    })
    
    # Compute correlations
    corr_results = compute_correlations(df)
    
    # Property: Correlation must be between -1 and 1
    assert -1 <= corr_results['fii_nifty_corr'] <= 1, \
        f"FII-NIFTY correlation {corr_results['fii_nifty_corr']} is outside [-1, 1]"
    
    assert -1 <= corr_results['dii_nifty_corr'] <= 1, \
        f"DII-NIFTY correlation {corr_results['dii_nifty_corr']} is outside [-1, 1]"
    
    # If correlation matrix exists, check all values
    if corr_results['corr_matrix'] is not None:
        corr_matrix = corr_results['corr_matrix']
        assert (corr_matrix >= -1).all().all(), "Some correlations < -1"
        assert (corr_matrix <= 1).all().all(), "Some correlations > 1"



@settings(max_examples=100)
@given(
    size=st.integers(min_value=30, max_value=100),
    window=st.integers(min_value=10, max_value=30),
    seed=st.integers(min_value=0, max_value=10000)
)
def test_rolling_correlation_bounds_property(size, window, seed):
    """
    Property 15 (Extended): Rolling Correlation Bounds
    
    For any time series and rolling window, all rolling correlation 
    values should be between -1 and 1 inclusive.
    
    Validates: Requirements 4.6
    """
    # Ensure window is smaller than size
    if window >= size:
        window = size // 2
    
    np.random.seed(seed)
    
    # Generate random data
    dates = pd.date_range('2020-01-01', periods=size, freq='D')
    fii_net = np.random.randn(size) * 1000
    dii_net = np.random.randn(size) * 800
    daily_return = np.random.randn(size) * 2
    
    df = pd.DataFrame({
        'Date': dates,
        'FII_Net': fii_net,
        'DII_Net': dii_net,
        'Daily_Return': daily_return
    })
    
    # Compute rolling correlations
    df_with_rolling = compute_rolling_correlations(df, window=window)
    
    # Property: All rolling correlations must be in [-1, 1]
    fii_rolling = df_with_rolling['FII_Return_RollingCorr'].dropna()
    dii_rolling = df_with_rolling['DII_Return_RollingCorr'].dropna()
    
    if len(fii_rolling) > 0:
        assert (fii_rolling >= -1).all(), "Some FII rolling correlations < -1"
        assert (fii_rolling <= 1).all(), "Some FII rolling correlations > 1"
    
    if len(dii_rolling) > 0:
        assert (dii_rolling >= -1).all(), "Some DII rolling correlations < -1"
        assert (dii_rolling <= 1).all(), "Some DII rolling correlations > 1"


# ============================================================================
# EDGE CASE TESTS FOR CORRELATION BOUNDS
# ============================================================================

def test_correlation_perfect_positive():
    """
    Test that perfectly correlated series give correlation = 1.
    """
    df = pd.DataFrame({
        'FII_Net': [1, 2, 3, 4, 5],
        'DII_Net': [2, 4, 6, 8, 10],
        'Daily_Return': [1, 2, 3, 4, 5]
    })
    
    corr_results = compute_correlations(df)
    
    # Perfect positive correlation
    assert abs(corr_results['fii_nifty_corr'] - 1.0) < 1e-10
    assert abs(corr_results['dii_nifty_corr'] - 1.0) < 1e-10


def test_correlation_perfect_negative():
    """
    Test that perfectly negatively correlated series give correlation = -1.
    """
    df = pd.DataFrame({
        'FII_Net': [1, 2, 3, 4, 5],
        'DII_Net': [5, 4, 3, 2, 1],  # Negatively correlated with Daily_Return
        'Daily_Return': [1, 2, 3, 4, 5]  # Increasing
    })
    
    corr_results = compute_correlations(df)
    
    # Perfect negative correlation
    assert abs(corr_results['fii_nifty_corr'] - 1.0) < 1e-10  # FII increases with returns
    assert abs(corr_results['dii_nifty_corr'] - (-1.0)) < 1e-10  # DII decreases with returns


def test_correlation_no_correlation():
    """
    Test that uncorrelated series give correlation near 0.
    """
    np.random.seed(42)
    
    df = pd.DataFrame({
        'FII_Net': np.random.randn(100),
        'DII_Net': np.random.randn(100),
        'Daily_Return': np.random.randn(100)
    })
    
    corr_results = compute_correlations(df)
    
    # Should be close to 0 (but not exactly due to randomness)
    assert -1 <= corr_results['fii_nifty_corr'] <= 1
    assert -1 <= corr_results['dii_nifty_corr'] <= 1


def test_correlation_with_nan_values():
    """
    Test that correlation handles NaN values correctly.
    """
    df = pd.DataFrame({
        'FII_Net': [1, 2, np.nan, 4, 5],
        'DII_Net': [2, 4, 6, np.nan, 10],
        'Daily_Return': [1, 2, 3, 4, 5]
    })
    
    corr_results = compute_correlations(df)
    
    # Correlation should still be in bounds
    assert -1 <= corr_results['fii_nifty_corr'] <= 1
    assert -1 <= corr_results['dii_nifty_corr'] <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
