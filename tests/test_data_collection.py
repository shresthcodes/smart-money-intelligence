"""
Property-Based Tests for Data Collection Module

Tests data loading consistency, persistence, and error handling using Hypothesis.
"""

import os
import tempfile
import sqlite3
import pytest
import pandas as pd
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, HealthCheck
import hypothesis.extra.pandas as pdst

# Import functions to test
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scripts.data_collection import (
    download_nifty_data,
    load_fii_dii_data,
    save_data_to_database
)


# Property 1: Data Loading Consistency
# Feature: smart-money-intelligence, Property 1: Data Loading Consistency
# Validates: Requirements 1.1, 1.2

@settings(max_examples=100, deadline=None)
@given(
    days_back=st.integers(min_value=30, max_value=365),
    days_duration=st.integers(min_value=7, max_value=90)
)
def test_data_loading_consistency_property(days_back, days_duration):
    """
    Property 1: Data Loading Consistency
    
    For any valid date range, the download function should return a DataFrame
    with expected columns and appropriate data types.
    
    Validates: Requirements 1.1, 1.2
    """
    # Generate valid date range
    end_date = datetime.now() - timedelta(days=days_back)
    start_date = end_date - timedelta(days=days_duration)
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    # Create temporary output path
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # Download data
        df = download_nifty_data(
            start_date=start_str,
            end_date=end_str,
            output_path=tmp_path
        )
        
        # Property assertions
        # 1. DataFrame should not be empty
        assert len(df) > 0, "DataFrame should contain data"
        
        # 2. Should have Date column
        assert 'Date' in df.columns, "DataFrame should have 'Date' column"
        
        # 3. Should have Close column (minimum required)
        assert 'Close' in df.columns, "DataFrame should have 'Close' column"
        
        # 4. Date column should be datetime-compatible
        # (yfinance returns datetime64, but after CSV save/load it might be string)
        assert df['Date'].dtype in ['datetime64[ns]', 'object'], \
            f"Date column should be datetime or object type, got {df['Date'].dtype}"
        
        # 5. Close prices should be numeric and positive
        # Handle both single-column and multi-index DataFrames from yfinance
        close_col = df['Close']
        if isinstance(close_col, pd.DataFrame):
            # Multi-index case: extract the first (and likely only) column
            close_values = close_col.iloc[:, 0]
        else:
            # Single column case
            close_values = close_col
            
        assert pd.api.types.is_numeric_dtype(close_values), \
            f"Close column should be numeric, got dtype: {close_values.dtype}"
        assert (close_values > 0).all(), \
            "All Close prices should be positive"
        
        # 6. File should be created
        assert os.path.exists(tmp_path), "CSV file should be created"
        
    finally:
        # Cleanup
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# Property 2: Data Persistence Round Trip
# Feature: smart-money-intelligence, Property 2: Data Persistence Round Trip
# Validates: Requirements 1.3

@settings(max_examples=100, deadline=None)
@given(
    df_data=pdst.data_frames(
        columns=[
            pdst.column('Date', dtype='datetime64[ns]', 
                       elements=st.datetimes(
                           min_value=datetime(2020, 1, 1),
                           max_value=datetime(2024, 12, 31)
                       )),
            pdst.column('Open', dtype=float, 
                       elements=st.floats(min_value=10000, max_value=25000, allow_nan=False)),
            pdst.column('High', dtype=float, 
                       elements=st.floats(min_value=10000, max_value=25000, allow_nan=False)),
            pdst.column('Low', dtype=float, 
                       elements=st.floats(min_value=10000, max_value=25000, allow_nan=False)),
            pdst.column('Close', dtype=float, 
                       elements=st.floats(min_value=10000, max_value=25000, allow_nan=False)),
            pdst.column('Volume', dtype=int, 
                       elements=st.integers(min_value=1000000, max_value=1000000000))
        ],
        index=pdst.range_indexes(min_size=5, max_size=50)
    )
)
def test_data_persistence_round_trip_property(df_data):
    """
    Property 2: Data Persistence Round Trip
    
    For any DataFrame, saving to database then loading should produce
    an equivalent DataFrame with same shape, columns, and values.
    
    Validates: Requirements 1.3
    """
    # Create temporary database
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as tmp:
        tmp_db_path = tmp.name
    
    try:
        # Save DataFrame to database
        table_name = "test_table"
        save_data_to_database(df_data, table_name, tmp_db_path)
        
        # Load DataFrame back from database
        conn = sqlite3.connect(tmp_db_path)
        df_loaded = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        conn.close()
        
        # Property assertions
        # 1. Same shape
        assert df_data.shape == df_loaded.shape, \
            f"Shape mismatch: original {df_data.shape}, loaded {df_loaded.shape}"
        
        # 2. Same columns
        assert list(df_data.columns) == list(df_loaded.columns), \
            "Column names should match"
        
        # 3. Same number of rows
        assert len(df_data) == len(df_loaded), \
            "Row count should match"
        
        # 4. Numeric columns should match within floating-point precision
        numeric_cols = df_data.select_dtypes(include=['float', 'int']).columns
        for col in numeric_cols:
            if col in df_loaded.columns:
                # Allow small floating-point differences
                assert pd.api.types.is_numeric_dtype(df_loaded[col]), \
                    f"Column {col} should remain numeric after round trip"
                
                # Check values are close (within 1e-6 for floats)
                if df_data[col].dtype == float:
                    max_diff = abs(df_data[col] - df_loaded[col]).max()
                    assert max_diff < 1e-6 or pd.isna(max_diff), \
                        f"Column {col} values differ by more than 1e-6"
        
    finally:
        # Cleanup
        if os.path.exists(tmp_db_path):
            os.remove(tmp_db_path)


# Property 3: Error Logging on Failure
# Feature: smart-money-intelligence, Property 3: Error Logging on Failure
# Validates: Requirements 1.5

@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    invalid_start=st.text(min_size=1, max_size=20, 
                         alphabet=st.characters(blacklist_categories=('Cs',))),
    invalid_end=st.text(min_size=1, max_size=20,
                       alphabet=st.characters(blacklist_categories=('Cs',)))
)
def test_error_logging_on_invalid_dates_property(invalid_start, invalid_end, caplog):
    """
    Property 3: Error Logging on Failure
    
    For any invalid date inputs, the system should log an error message
    containing descriptive information about the failure.
    
    Validates: Requirements 1.5
    """
    # Skip if by chance we generated valid dates
    try:
        datetime.strptime(invalid_start, '%Y-%m-%d')
        datetime.strptime(invalid_end, '%Y-%m-%d')
        return  # Skip this test case if dates are accidentally valid
    except ValueError:
        pass  # Good, dates are invalid as intended
    
    # Create temporary output path
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # Clear any previous log records
        caplog.clear()
        
        # Attempt to download with invalid dates
        with pytest.raises((ValueError, ConnectionError)):
            download_nifty_data(
                start_date=invalid_start,
                end_date=invalid_end,
                output_path=tmp_path
            )
        
        # Property assertion: Error should be logged
        # Check that logging occurred (caplog captures log messages)
        assert len(caplog.records) > 0, \
            "Error should be logged when invalid inputs are provided"
        
        # Check that error message contains descriptive information
        error_messages = [record.message for record in caplog.records 
                         if record.levelname in ['ERROR', 'WARNING']]
        assert len(error_messages) > 0, \
            "At least one error or warning message should be logged"
        
        # Error message should mention the problem
        combined_message = ' '.join(error_messages).lower()
        assert any(keyword in combined_message for keyword in 
                  ['invalid', 'error', 'format', 'date', 'failed']), \
            "Error message should contain descriptive keywords"
        
    finally:
        # Cleanup
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# Additional unit tests for specific edge cases

def test_download_with_invalid_date_order():
    """Test that start_date after end_date raises ValueError"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        with pytest.raises(ValueError, match="start_date.*must be before.*end_date"):
            download_nifty_data(
                start_date="2024-01-01",
                end_date="2023-01-01",
                output_path=tmp_path
            )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_load_fii_dii_missing_file():
    """Test that loading non-existent file raises FileNotFoundError"""
    with pytest.raises(FileNotFoundError, match="not found"):
        load_fii_dii_data("nonexistent_file.csv")


def test_load_fii_dii_missing_columns():
    """Test that CSV with missing columns raises ValueError"""
    # Create temporary CSV with wrong columns
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
        tmp.write("Date,Wrong_Column\n")
        tmp.write("2024-01-01,100\n")
        tmp_path = tmp.name
    
    try:
        with pytest.raises(ValueError, match="Missing columns"):
            load_fii_dii_data(tmp_path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_save_to_database_creates_directory():
    """Test that save_data_to_database creates directory if needed"""
    # Create a DataFrame
    df = pd.DataFrame({
        'Date': ['2024-01-01', '2024-01-02'],
        'Value': [100, 200]
    })
    
    # Use a path in a non-existent directory
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, 'subdir', 'test.db')
        
        # Should create the directory
        save_data_to_database(df, 'test_table', db_path)
        
        # Verify database was created
        assert os.path.exists(db_path)
        
        # Verify data was saved
        conn = sqlite3.connect(db_path)
        result = pd.read_sql("SELECT * FROM test_table", conn)
        conn.close()
        
        assert len(result) == 2


if __name__ == "__main__":
    print("Running property-based tests for data collection module...")
    print("=" * 60)
    pytest.main([__file__, "-v", "--tb=short"])
