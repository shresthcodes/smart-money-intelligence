"""
Integration tests for Feature Engineering Module

Tests the feature engineering functions working together with realistic data.
"""

import pytest
import pandas as pd
import numpy as np
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


def test_complete_feature_engineering_pipeline():
    """
    Test the complete feature engineering pipeline with realistic market data.
    
    This simulates processing merged market and institutional data through
    all feature engineering steps.
    """
    # Create sample merged data (market + institutional)
    dates = pd.date_range('2023-01-01', periods=50, freq='D')
    
    df = pd.DataFrame({
        'Date': dates,
        'Close': np.random.uniform(18000, 19000, 50),  # NIFTY prices
        'FII_Net': np.random.uniform(-1000, 1000, 50),  # FII net flows
        'DII_Net': np.random.uniform(-500, 500, 50),    # DII net flows
    })
    
    # Step 1: Compute returns
    df = compute_returns(df, 'Close')
    assert 'Daily_Return' in df.columns
    assert pd.isna(df.iloc[0]['Daily_Return'])  # First row should be NaN
    assert not df.iloc[1:]['Daily_Return'].isna().all()  # Rest should have values
    
    # Step 2: Compute rolling averages for institutional flows
    df = compute_rolling_averages(df, ['FII_Net', 'DII_Net'], [5, 10, 20])
    assert 'FII_Net_MA5' in df.columns
    assert 'FII_Net_MA10' in df.columns
    assert 'FII_Net_MA20' in df.columns
    assert 'DII_Net_MA5' in df.columns
    
    # Step 3: Compute volatility
    df = compute_volatility(df, 'Daily_Return', 20)
    assert 'Volatility' in df.columns
    assert not df['Volatility'].isna().all()
    
    # Step 4: Compute momentum
    df = compute_momentum(df, 'Close', 10)
    assert 'Momentum' in df.columns
    
    # Step 5: Create lag features
    df = create_lag_features(df, ['FII_Net', 'DII_Net', 'Daily_Return'], [1, 2, 3])
    assert 'FII_Net_Lag1' in df.columns
    assert 'FII_Net_Lag2' in df.columns
    assert 'FII_Net_Lag3' in df.columns
    assert 'DII_Net_Lag1' in df.columns
    assert 'Daily_Return_Lag1' in df.columns
    
    # Step 6: Create target variable
    df = create_target_variable(df, 'Daily_Return')
    assert 'Target' in df.columns
    assert df['Target'].dropna().isin([0, 1]).all()
    assert pd.isna(df.iloc[-1]['Target'])  # Last row should be NaN
    
    # Verify we have all expected columns
    expected_columns = [
        'Date', 'Close', 'FII_Net', 'DII_Net',
        'Daily_Return', 'Volatility', 'Momentum',
        'FII_Net_MA5', 'FII_Net_MA10', 'FII_Net_MA20',
        'DII_Net_MA5', 'DII_Net_MA10', 'DII_Net_MA20',
        'FII_Net_Lag1', 'FII_Net_Lag2', 'FII_Net_Lag3',
        'DII_Net_Lag1', 'DII_Net_Lag2', 'DII_Net_Lag3',
        'Daily_Return_Lag1', 'Daily_Return_Lag2', 'Daily_Return_Lag3',
        'Target'
    ]
    
    for col in expected_columns:
        assert col in df.columns, f"Missing expected column: {col}"
    
    print(f"\n✅ Complete feature engineering pipeline successful!")
    print(f"   Input: {len(df)} rows with 4 columns")
    print(f"   Output: {len(df)} rows with {len(df.columns)} columns")
    print(f"   Features created: {len(df.columns) - 4}")


def test_feature_engineering_with_minimal_data():
    """
    Test feature engineering with minimal data (edge case).
    """
    # Create minimal data (just enough for calculations)
    df = pd.DataFrame({
        'Close': [100, 105, 110, 115, 120],
        'FII_Net': [100, -50, 200, -100, 150],
    })
    
    # Apply all transformations
    df = compute_returns(df, 'Close')
    df = compute_rolling_averages(df, ['FII_Net'], [3])
    df = compute_volatility(df, 'Daily_Return', 3)
    df = compute_momentum(df, 'Close', 2)
    df = create_lag_features(df, ['FII_Net'], [1])
    df = create_target_variable(df, 'Daily_Return')
    
    # Verify all operations completed without errors
    assert len(df) == 5
    assert 'Daily_Return' in df.columns
    assert 'FII_Net_MA3' in df.columns
    assert 'Volatility' in df.columns
    assert 'Momentum' in df.columns
    assert 'FII_Net_Lag1' in df.columns
    assert 'Target' in df.columns


def test_feature_engineering_preserves_data_integrity():
    """
    Test that feature engineering doesn't corrupt original data.
    """
    # Create original data
    original_df = pd.DataFrame({
        'Date': pd.date_range('2023-01-01', periods=20, freq='D'),
        'Close': np.random.uniform(18000, 19000, 20),
        'FII_Net': np.random.uniform(-1000, 1000, 20),
    })
    
    # Store original values
    original_close = original_df['Close'].copy()
    original_fii = original_df['FII_Net'].copy()
    
    # Apply feature engineering
    result_df = compute_returns(original_df, 'Close')
    result_df = compute_rolling_averages(result_df, ['FII_Net'], [5])
    result_df = compute_volatility(result_df, 'Daily_Return', 5)
    
    # Verify original columns are unchanged
    assert (result_df['Close'] == original_close).all()
    assert (result_df['FII_Net'] == original_fii).all()
    
    # Verify original DataFrame is unchanged (functions create copies)
    assert 'Daily_Return' not in original_df.columns
    assert 'FII_Net_MA5' not in original_df.columns
    assert 'Volatility' not in original_df.columns


if __name__ == '__main__':
    # Run integration tests
    test_complete_feature_engineering_pipeline()
    test_feature_engineering_with_minimal_data()
    test_feature_engineering_preserves_data_integrity()
    print("\n✅ All integration tests passed!")
