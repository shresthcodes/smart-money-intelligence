"""
Integration test to verify preprocessing module works with data collection module.
"""

import pytest
import pandas as pd
import sys
import os
from datetime import datetime, timedelta

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from preprocessing import clean_market_data, clean_institutional_data, merge_datasets


def test_preprocessing_integration():
    """Test that preprocessing functions work together in a realistic scenario."""
    
    # Create sample market data (simulating data from yfinance)
    dates = [datetime(2024, 1, i) for i in range(1, 11)]
    market_data = pd.DataFrame({
        'Date': dates,
        'Open': [15000 + i*10 for i in range(10)],
        'High': [15100 + i*10 for i in range(10)],
        'Low': [14900 + i*10 for i in range(10)],
        'Close': [15050 + i*10 for i in range(10)],
        'Volume': [1000000 + i*10000 for i in range(10)]
    })
    
    # Create sample institutional data
    institutional_data = pd.DataFrame({
        'Date': dates,
        'FII_Buy': [1000 + i*50 for i in range(10)],
        'FII_Sell': [800 + i*40 for i in range(10)],
        'DII_Buy': [500 + i*20 for i in range(10)],
        'DII_Sell': [400 + i*15 for i in range(10)]
    })
    
    # Clean market data
    market_clean = clean_market_data(market_data)
    assert len(market_clean) == 10
    assert pd.api.types.is_datetime64_any_dtype(market_clean['Date'])
    
    # Clean institutional data
    institutional_clean = clean_institutional_data(institutional_data)
    assert len(institutional_clean) == 10
    assert 'FII_Net' in institutional_clean.columns
    assert 'DII_Net' in institutional_clean.columns
    
    # Merge datasets
    merged = merge_datasets(market_clean, institutional_clean)
    assert len(merged) == 10
    
    # Verify all expected columns are present
    expected_columns = [
        'Date', 'Open', 'High', 'Low', 'Close', 'Volume',
        'FII_Buy', 'FII_Sell', 'FII_Net', 'DII_Buy', 'DII_Sell', 'DII_Net'
    ]
    for col in expected_columns:
        assert col in merged.columns, f"Column {col} missing from merged data"
    
    # Verify net flows are calculated correctly
    assert merged['FII_Net'].iloc[0] == merged['FII_Buy'].iloc[0] - merged['FII_Sell'].iloc[0]
    assert merged['DII_Net'].iloc[0] == merged['DII_Buy'].iloc[0] - merged['DII_Sell'].iloc[0]
    
    print("✅ Integration test passed! Preprocessing module works correctly.")


if __name__ == '__main__':
    test_preprocessing_integration()
