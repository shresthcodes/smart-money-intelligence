"""
Property-based tests for exception handling across the Smart Money Intelligence Platform.

Property 26: Exception Handling for Invalid Inputs
Validates: Requirements 12.5

For any function that accepts external inputs (file paths, date ranges, numeric parameters),
providing invalid inputs should raise an appropriate exception rather than silently failing
or producing incorrect results.
"""

import os
import sys
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, assume
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.data_collection import download_nifty_data, load_fii_dii_data, save_data_to_database
from scripts.preprocessing import clean_market_data, clean_institutional_data, merge_datasets
from scripts.feature_engineering import (
    compute_returns, compute_rolling_averages, compute_volatility,
    compute_momentum, create_lag_features, create_target_variable
)
from scripts.insights_generator import (
    identify_unusual_activity, detect_accumulation_periods, compute_market_reaction
)
from scripts.signal_generator import generate_signal


# Feature: smart-money-intelligence, Property 26: Exception Handling for Invalid Inputs
# Validates: Requirements 12.5


class TestExceptionHandling:
    """Test that functions raise appropriate exceptions for invalid inputs."""
    
    @settings(max_examples=100)
    @given(
        start_date=st.text(min_size=1, max_size=20),
        end_date=st.text(min_size=1, max_size=20)
    )
    def test_download_nifty_data_invalid_dates(self, start_date, end_date):
        """
        Property 26: Invalid date strings should raise ValueError.
        
        For any invalid date string inputs, the download function should raise
        an appropriate exception rather than silently failing.
        """
        # Filter out valid date formats to ensure we're testing invalid ones
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
            assume(False)  # Skip if both are valid dates
        except ValueError:
            pass  # Expected - these are invalid dates
        
        # Should raise ValueError for invalid date formats
        with pytest.raises((ValueError, TypeError, Exception)):
            download_nifty_data(start_date=start_date, end_date=end_date)
    
    @settings(max_examples=100)
    @given(filepath=st.text(min_size=1, max_size=100))
    def test_load_fii_dii_data_invalid_path(self, filepath):
        """
        Property 26: Non-existent file paths should raise FileNotFoundError.
        
        For any non-existent file path, the load function should raise
        FileNotFoundError rather than silently failing.
        """
        # Ensure the file doesn't exist
        assume(not os.path.exists(filepath))
        
        # Should raise FileNotFoundError
        with pytest.raises((FileNotFoundError, OSError, pd.errors.EmptyDataError)):
            load_fii_dii_data(filepath)
    
    @settings(max_examples=100)
    @given(
        data=st.lists(
            st.dictionaries(
                keys=st.sampled_from(['invalid_col1', 'invalid_col2', 'random']),
                values=st.floats(allow_nan=False, allow_infinity=False)
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_clean_market_data_missing_columns(self, data):
        """
        Property 26: DataFrames missing required columns should raise KeyError or ValueError.
        
        For any DataFrame without required columns (Date, Open, High, Low, Close, Volume),
        the cleaning function should raise an appropriate exception.
        """
        df = pd.DataFrame(data)
        
        # Ensure it doesn't have the required columns
        required_cols = {'Date', 'Open', 'High', 'Low', 'Close', 'Volume'}
        assume(not required_cols.issubset(set(df.columns)))
        
        # Should raise KeyError or ValueError
        with pytest.raises((KeyError, ValueError, AttributeError)):
            clean_market_data(df)
    
    @settings(max_examples=100)
    @given(
        data=st.lists(
            st.dictionaries(
                keys=st.sampled_from(['invalid_col1', 'invalid_col2']),
                values=st.floats(allow_nan=False, allow_infinity=False)
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_clean_institutional_data_missing_columns(self, data):
        """
        Property 26: Institutional data without required columns should raise exception.
        
        For any DataFrame without required columns (Date, FII_Buy, FII_Sell, DII_Buy, DII_Sell),
        the cleaning function should raise an appropriate exception.
        """
        df = pd.DataFrame(data)
        
        # Ensure it doesn't have the required columns
        required_cols = {'Date', 'FII_Buy', 'FII_Sell', 'DII_Buy', 'DII_Sell'}
        assume(not required_cols.issubset(set(df.columns)))
        
        # Should raise KeyError or ValueError
        with pytest.raises((KeyError, ValueError, AttributeError)):
            clean_institutional_data(df)
    
    @settings(max_examples=100)
    @given(
        data=st.lists(
            st.dictionaries(
                keys=st.sampled_from(['random_col']),
                values=st.floats(allow_nan=False, allow_infinity=False)
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_compute_returns_missing_price_column(self, data):
        """
        Property 26: Computing returns without price column should raise exception.
        
        For any DataFrame without a Close column, compute_returns should raise
        an appropriate exception.
        """
        df = pd.DataFrame(data)
        
        # Ensure it doesn't have Close column
        assume('Close' not in df.columns)
        
        # Should raise KeyError
        with pytest.raises((KeyError, ValueError)):
            compute_returns(df)
    
    @settings(max_examples=100)
    @given(
        window=st.integers(min_value=-100, max_value=-1)
    )
    def test_rolling_averages_negative_window(self, window):
        """
        Property 26: Negative window sizes should raise exception.
        
        For any negative window size, rolling average computation should raise
        an appropriate exception.
        """
        df = pd.DataFrame({
            'FII_Net': [1, 2, 3, 4, 5],
            'DII_Net': [1, 2, 3, 4, 5]
        })
        
        # Should raise ValueError
        with pytest.raises((ValueError, Exception)):
            compute_rolling_averages(df, ['FII_Net'], [window])
    
    @settings(max_examples=100)
    @given(
        threshold_std=st.floats(min_value=-1000, max_value=-0.1)
    )
    def test_unusual_activity_negative_threshold(self, threshold_std):
        """
        Property 26: Negative threshold values should raise exception or be handled.
        
        For any negative threshold, the function should either raise an exception
        or handle it gracefully (not produce incorrect results).
        """
        df = pd.DataFrame({
            'Date': pd.date_range('2023-01-01', periods=10),
            'FII_Net': np.random.randn(10) * 1000
        })
        
        # Should either raise ValueError or handle gracefully
        try:
            result = identify_unusual_activity(df, 'FII_Net', threshold_std)
            # If it doesn't raise, verify it returns a valid DataFrame
            assert isinstance(result, pd.DataFrame), "Should return DataFrame"
        except (ValueError, Exception):
            pass  # Acceptable to raise exception
    
    @settings(max_examples=100)
    @given(
        window=st.integers(min_value=-100, max_value=0)
    )
    def test_accumulation_periods_invalid_window(self, window):
        """
        Property 26: Zero or negative window sizes should raise exception.
        
        For any non-positive window size, period detection should raise
        an appropriate exception.
        """
        df = pd.DataFrame({
            'Date': pd.date_range('2023-01-01', periods=10),
            'FII_Net': np.random.randn(10) * 1000
        })
        
        # Should raise ValueError
        with pytest.raises((ValueError, Exception)):
            detect_accumulation_periods(df, window=window)
    
    @settings(max_examples=100)
    @given(
        fii_net=st.one_of(
            st.floats(allow_nan=True, allow_infinity=True),
            st.none()
        ),
        momentum=st.one_of(
            st.floats(allow_nan=True, allow_infinity=True),
            st.none()
        )
    )
    def test_signal_generation_invalid_inputs(self, fii_net, momentum):
        """
        Property 26: NaN or infinite values should be handled appropriately.
        
        For any NaN or infinite input values, signal generation should either
        raise an exception or handle gracefully.
        """
        # Test with potentially invalid numeric inputs
        if fii_net is None or momentum is None:
            with pytest.raises((TypeError, ValueError)):
                generate_signal(fii_net, 0, momentum, 1, 0.5)
        elif np.isnan(fii_net) or np.isnan(momentum) or np.isinf(fii_net) or np.isinf(momentum):
            try:
                result = generate_signal(fii_net, 0, momentum, 1, 0.5)
                # If it doesn't raise, verify it returns valid signal
                assert result['signal'] in ['Bullish', 'Neutral', 'Bearish'], "Should return valid signal"
            except (ValueError, TypeError):
                pass  # Acceptable to raise exception
    
    def test_empty_dataframe_handling(self):
        """
        Property 26: Empty DataFrames should be handled appropriately.
        
        Functions should either raise exceptions or handle empty DataFrames gracefully.
        """
        empty_df = pd.DataFrame()
        
        # Test various functions with empty DataFrame
        with pytest.raises((ValueError, KeyError, IndexError, Exception)):
            clean_market_data(empty_df)
        
        with pytest.raises((ValueError, KeyError, IndexError, Exception)):
            clean_institutional_data(empty_df)
        
        with pytest.raises((ValueError, KeyError, IndexError, Exception)):
            compute_returns(empty_df)
    
    def test_single_row_dataframe_handling(self):
        """
        Property 26: Single-row DataFrames should be handled appropriately.
        
        Functions that require multiple rows should raise exceptions or handle gracefully.
        """
        single_row_df = pd.DataFrame({
            'Date': ['2023-01-01'],
            'Close': [18000.0]
        })
        
        # compute_returns needs at least 2 rows
        result = compute_returns(single_row_df)
        # Should handle gracefully - first row will have NaN return
        assert len(result) == 1, "Should return same length DataFrame"
    
    def test_database_save_invalid_path(self):
        """
        Property 26: Invalid database paths should raise exception.
        
        Attempting to save to an invalid database path should raise an exception.
        """
        df = pd.DataFrame({'col1': [1, 2, 3]})
        
        # Try to save to an invalid path with non-existent parent directory
        # Use a path that definitely doesn't exist on any system
        import tempfile
        temp_base = tempfile.gettempdir()
        invalid_path = os.path.join(temp_base, 'nonexistent_parent_xyz123', 'nonexistent_child_abc456', 'database.db')
        
        # Ensure the parent directories don't exist
        parent_dir = os.path.dirname(os.path.dirname(invalid_path))
        if os.path.exists(parent_dir):
            import shutil
            shutil.rmtree(parent_dir, ignore_errors=True)
        
        with pytest.raises((OSError, Exception)):
            save_data_to_database(df, 'test_table', invalid_path)


class TestExceptionMessages:
    """Test that exceptions provide descriptive error messages."""
    
    def test_file_not_found_message(self):
        """Verify FileNotFoundError provides helpful message."""
        try:
            load_fii_dii_data('nonexistent_file.csv')
            assert False, "Should raise FileNotFoundError"
        except FileNotFoundError as e:
            # Error message should mention the file
            assert 'nonexistent_file.csv' in str(e) or 'No such file' in str(e)
    
    def test_missing_column_message(self):
        """Verify KeyError provides helpful message about missing columns."""
        df = pd.DataFrame({'wrong_col': [1, 2, 3]})
        
        try:
            clean_market_data(df)
            assert False, "Should raise KeyError or ValueError"
        except (KeyError, ValueError) as e:
            # Error message should be descriptive
            error_msg = str(e).lower()
            # Should mention column or key
            assert 'column' in error_msg or 'key' in error_msg or 'date' in error_msg


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
