"""
Property-Based Tests for Data Preprocessing Module

This module contains property-based tests using Hypothesis to verify
preprocessing functions work correctly across a wide range of inputs.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings
from hypothesis.extra.pandas import column, data_frames, range_indexes
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from preprocessing import clean_market_data, clean_institutional_data, merge_datasets


# Custom strategies for generating test data
@st.composite
def market_dataframe(draw):
    """Generate a random market DataFrame with valid structure."""
    n_rows = draw(st.integers(min_value=1, max_value=100))
    
    # Generate dates
    start_date = datetime(2020, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(n_rows)]
    
    # Possibly add duplicates
    if draw(st.booleans()):
        dup_idx = draw(st.integers(min_value=0, max_value=n_rows-1))
        dates.append(dates[dup_idx])
    
    # Generate price data
    prices = draw(st.lists(
        st.floats(min_value=10000, max_value=20000, allow_nan=False, allow_infinity=False),
        min_size=len(dates),
        max_size=len(dates)
    ))
    
    df = pd.DataFrame({
        'Date': dates,
        'Open': prices,
        'High': [p * 1.01 for p in prices],
        'Low': [p * 0.99 for p in prices],
        'Close': [p * 1.005 for p in prices],
        'Volume': draw(st.lists(
            st.integers(min_value=0, max_value=1000000000),
            min_size=len(dates),
            max_size=len(dates)
        ))
    })
    
    return df


@st.composite
def institutional_dataframe(draw):
    """Generate a random institutional DataFrame with valid structure."""
    n_rows = draw(st.integers(min_value=1, max_value=100))
    
    # Generate dates
    start_date = datetime(2020, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(n_rows)]
    
    # Possibly add duplicates
    if draw(st.booleans()):
        dup_idx = draw(st.integers(min_value=0, max_value=n_rows-1))
        dates.append(dates[dup_idx])
    
    # Generate flow data
    df = pd.DataFrame({
        'Date': dates,
        'FII_Buy': draw(st.lists(
            st.floats(min_value=0, max_value=10000, allow_nan=False, allow_infinity=False),
            min_size=len(dates),
            max_size=len(dates)
        )),
        'FII_Sell': draw(st.lists(
            st.floats(min_value=0, max_value=10000, allow_nan=False, allow_infinity=False),
            min_size=len(dates),
            max_size=len(dates)
        )),
        'DII_Buy': draw(st.lists(
            st.floats(min_value=0, max_value=10000, allow_nan=False, allow_infinity=False),
            min_size=len(dates),
            max_size=len(dates)
        )),
        'DII_Sell': draw(st.lists(
            st.floats(min_value=0, max_value=10000, allow_nan=False, allow_infinity=False),
            min_size=len(dates),
            max_size=len(dates)
        ))
    })
    
    return df


# Property 4: Date Column Type Conversion
@pytest.mark.property
@settings(max_examples=100)
@given(df=market_dataframe())
def test_date_column_type_conversion(df):
    """
    Feature: smart-money-intelligence, Property 4: Date Column Type Conversion
    Validates: Requirements 2.1
    
    For any DataFrame with string date columns, after applying the cleaning function,
    all date columns should have datetime64 dtype.
    """
    # Convert dates to strings to test conversion
    df['Date'] = df['Date'].astype(str)
    
    # Clean the data
    cleaned_df = clean_market_data(df)
    
    # Verify Date column is datetime64
    assert pd.api.types.is_datetime64_any_dtype(cleaned_df['Date']), \
        f"Date column should be datetime64, but got {cleaned_df['Date'].dtype}"


# Property 6: Duplicate Removal
@pytest.mark.property
@settings(max_examples=100)
@given(df=market_dataframe())
def test_duplicate_removal(df):
    """
    Feature: smart-money-intelligence, Property 6: Duplicate Removal
    Validates: Requirements 2.3
    
    For any DataFrame with duplicate rows, after applying the deduplication function,
    the output should contain no duplicate rows based on the date column.
    """
    # Clean the data
    cleaned_df = clean_market_data(df)
    
    # Verify no duplicates based on Date
    duplicates = cleaned_df.duplicated(subset=['Date']).sum()
    assert duplicates == 0, f"Found {duplicates} duplicate dates after cleaning"


# Property 7: Date Sorting Order
@pytest.mark.property
@settings(max_examples=100)
@given(df=market_dataframe())
def test_date_sorting_order(df):
    """
    Feature: smart-money-intelligence, Property 7: Date Sorting Order
    Validates: Requirements 2.4
    
    For any DataFrame with a date column, after applying the sorting function,
    the dates should be in strictly ascending order (each date >= previous date).
    """
    # Clean the data
    cleaned_df = clean_market_data(df)
    
    # Verify dates are in ascending order
    if len(cleaned_df) > 1:
        dates = cleaned_df['Date'].values
        for i in range(1, len(dates)):
            assert dates[i] >= dates[i-1], \
                f"Dates not in ascending order at index {i}: {dates[i-1]} > {dates[i]}"


# Unit tests for specific edge cases
def test_clean_market_data_empty_dataframe():
    """Test cleaning an empty DataFrame."""
    df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    cleaned_df = clean_market_data(df)
    assert len(cleaned_df) == 0
    assert list(cleaned_df.columns) == ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']


def test_clean_market_data_missing_columns():
    """Test that missing required columns raises ValueError."""
    df = pd.DataFrame({'Date': ['2024-01-01'], 'Close': [15000]})
    with pytest.raises(ValueError, match="Missing required columns"):
        clean_market_data(df)


def test_clean_market_data_with_missing_values():
    """Test handling of missing values in price columns."""
    df = pd.DataFrame({
        'Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'Open': [15000, np.nan, 15200],
        'High': [15100, 15150, np.nan],
        'Low': [14900, 14950, 15000],
        'Close': [15050, 15100, 15150],
        'Volume': [1000000, 1100000, 1200000]
    })
    
    cleaned_df = clean_market_data(df)
    
    # Check that missing values are filled
    assert not cleaned_df['Open'].isna().any()
    assert not cleaned_df['High'].isna().any()


def test_clean_institutional_data_basic():
    """Test basic institutional data cleaning."""
    df = pd.DataFrame({
        'Date': ['2024-01-03', '2024-01-01', '2024-01-02'],
        'FII_Buy': [1000, 1500, 1200],
        'FII_Sell': [800, 900, 1000],
        'DII_Buy': [500, 600, 550],
        'DII_Sell': [400, 500, 450]
    })
    
    cleaned_df = clean_institutional_data(df)
    
    # Check sorting
    assert cleaned_df['Date'].iloc[0] == pd.Timestamp('2024-01-01')
    assert cleaned_df['Date'].iloc[1] == pd.Timestamp('2024-01-02')
    assert cleaned_df['Date'].iloc[2] == pd.Timestamp('2024-01-03')
    
    # Check net flows are computed
    assert 'FII_Net' in cleaned_df.columns
    assert 'DII_Net' in cleaned_df.columns


def test_clean_institutional_data_missing_columns():
    """Test that missing required columns raises ValueError."""
    df = pd.DataFrame({'Date': ['2024-01-01'], 'FII_Buy': [1000]})
    with pytest.raises(ValueError, match="Missing required columns"):
        clean_institutional_data(df)


# Property 11: Net Flow Calculation
@pytest.mark.property
@settings(max_examples=100)
@given(df=institutional_dataframe())
def test_net_flow_calculation(df):
    """
    Feature: smart-money-intelligence, Property 11: Net Flow Calculation
    Validates: Requirements 3.3
    
    For any institutional data with Buy and Sell columns, the computed Net flow
    should equal (Buy - Sell) for every row.
    """
    # Clean the data
    cleaned_df = clean_institutional_data(df)
    
    # Verify FII_Net = FII_Buy - FII_Sell for all rows
    for idx in range(len(cleaned_df)):
        expected_fii_net = cleaned_df.iloc[idx]['FII_Buy'] - cleaned_df.iloc[idx]['FII_Sell']
        actual_fii_net = cleaned_df.iloc[idx]['FII_Net']
        assert abs(expected_fii_net - actual_fii_net) < 1e-6, \
            f"FII_Net calculation incorrect at row {idx}: expected {expected_fii_net}, got {actual_fii_net}"
    
    # Verify DII_Net = DII_Buy - DII_Sell for all rows
    for idx in range(len(cleaned_df)):
        expected_dii_net = cleaned_df.iloc[idx]['DII_Buy'] - cleaned_df.iloc[idx]['DII_Sell']
        actual_dii_net = cleaned_df.iloc[idx]['DII_Net']
        assert abs(expected_dii_net - actual_dii_net) < 1e-6, \
            f"DII_Net calculation incorrect at row {idx}: expected {expected_dii_net}, got {actual_dii_net}"


# Property 8: Dataset Merge Completeness
@pytest.mark.property
@settings(max_examples=100)
@given(
    market_df=market_dataframe(),
    institutional_df=institutional_dataframe()
)
def test_dataset_merge_completeness(market_df, institutional_df):
    """
    Feature: smart-money-intelligence, Property 8: Dataset Merge Completeness
    Validates: Requirements 2.5
    
    For any two DataFrames with date columns, after merging by date, the result
    should contain all dates present in both input DataFrames and include columns
    from both sources.
    """
    # Clean both datasets first
    market_clean = clean_market_data(market_df)
    institutional_clean = clean_institutional_data(institutional_df)
    
    # Merge the datasets
    merged_df = merge_datasets(market_clean, institutional_clean)
    
    # Find common dates
    market_dates = set(market_clean['Date'].dt.date)
    institutional_dates = set(institutional_clean['Date'].dt.date)
    common_dates = market_dates.intersection(institutional_dates)
    
    # Verify merged data contains only common dates
    merged_dates = set(merged_df['Date'].dt.date)
    assert merged_dates == common_dates, \
        f"Merged dates {merged_dates} should equal common dates {common_dates}"
    
    # Verify columns from both sources are present
    market_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    institutional_columns = ['FII_Buy', 'FII_Sell', 'FII_Net', 'DII_Buy', 'DII_Sell', 'DII_Net']
    
    for col in market_columns:
        assert col in merged_df.columns, f"Market column '{col}' missing from merged data"
    
    for col in institutional_columns:
        assert col in merged_df.columns, f"Institutional column '{col}' missing from merged data"
    
    # Verify Date column is present
    assert 'Date' in merged_df.columns, "Date column missing from merged data"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'property'])
