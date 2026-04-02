"""
Feature Engineering Module

This module provides functions to create derived features for machine learning
from market and institutional data.
"""

import pandas as pd
import numpy as np
import logging
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def compute_returns(df: pd.DataFrame, price_col: str = "Close") -> pd.DataFrame:
    """
    Compute daily returns.
    
    Formula: Return = (Price_today - Price_yesterday) / Price_yesterday * 100
    
    Args:
        df: DataFrame with price data
        price_col: Name of price column
    
    Returns:
        DataFrame with 'Daily_Return' column added
        
    Raises:
        ValueError: If price column is missing
    """
    logger.info(f"Computing daily returns from {price_col} column...")
    
    # Validate price column exists
    if price_col not in df.columns:
        raise ValueError(f"Price column '{price_col}' not found in DataFrame")
    
    # Create a copy to avoid modifying original
    df_result = df.copy()
    
    # Calculate daily returns
    # First row will be NaN since there's no previous price
    df_result['Daily_Return'] = (
        (df_result[price_col] - df_result[price_col].shift(1)) / 
        df_result[price_col].shift(1) * 100
    )
    
    logger.info(f"Daily returns computed. First row is NaN (no previous price)")
    return df_result


def compute_rolling_averages(
    df: pd.DataFrame,
    columns: List[str],
    windows: List[int] = [5, 10, 20]
) -> pd.DataFrame:
    """
    Compute rolling averages for specified columns.
    
    Args:
        df: Input DataFrame
        columns: List of column names to compute rolling averages for
        windows: List of window sizes (days)
    
    Returns:
        DataFrame with rolling average columns added
        (e.g., 'FII_Net_MA5', 'FII_Net_MA10', 'FII_Net_MA20')
        
    Raises:
        ValueError: If any specified column is missing
    """
    logger.info(f"Computing rolling averages for columns: {columns} with windows: {windows}")
    
    # Validate columns exist
    missing_columns = [col for col in columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")
    
    # Create a copy to avoid modifying original
    df_result = df.copy()
    
    # Compute rolling averages for each column and window
    for col in columns:
        for window in windows:
            new_col_name = f"{col}_MA{window}"
            logger.info(f"Computing {window}-day rolling average for {col}")
            df_result[new_col_name] = df_result[col].rolling(window=window, min_periods=1).mean()
    
    logger.info(f"Rolling averages computed for {len(columns)} columns with {len(windows)} windows")
    return df_result


def compute_volatility(
    df: pd.DataFrame,
    return_col: str = "Daily_Return",
    window: int = 20
) -> pd.DataFrame:
    """
    Compute rolling volatility (standard deviation of returns).
    
    Args:
        df: DataFrame with return data
        return_col: Name of return column
        window: Rolling window size
    
    Returns:
        DataFrame with 'Volatility' column added
        
    Raises:
        ValueError: If return column is missing
    """
    logger.info(f"Computing {window}-day rolling volatility from {return_col} column...")
    
    # Validate return column exists
    if return_col not in df.columns:
        raise ValueError(f"Return column '{return_col}' not found in DataFrame")
    
    # Create a copy to avoid modifying original
    df_result = df.copy()
    
    # Calculate rolling standard deviation
    df_result['Volatility'] = df_result[return_col].rolling(window=window, min_periods=1).std()
    
    logger.info(f"Volatility computed with {window}-day rolling window")
    return df_result


def compute_momentum(
    df: pd.DataFrame,
    price_col: str = "Close",
    period: int = 10
) -> pd.DataFrame:
    """
    Compute momentum indicator.
    
    Formula: Momentum = Price_today - Price_N_days_ago
    
    Args:
        df: DataFrame with price data
        price_col: Name of price column
        period: Lookback period in days
    
    Returns:
        DataFrame with 'Momentum' column added
        
    Raises:
        ValueError: If price column is missing
    """
    logger.info(f"Computing {period}-day momentum from {price_col} column...")
    
    # Validate price column exists
    if price_col not in df.columns:
        raise ValueError(f"Price column '{price_col}' not found in DataFrame")
    
    # Create a copy to avoid modifying original
    df_result = df.copy()
    
    # Calculate momentum
    df_result['Momentum'] = df_result[price_col] - df_result[price_col].shift(period)
    
    logger.info(f"Momentum computed with {period}-day lookback period")
    return df_result


def create_lag_features(
    df: pd.DataFrame,
    columns: List[str],
    lags: List[int] = [1, 2, 3]
) -> pd.DataFrame:
    """
    Create lagged features for time series.
    
    Args:
        df: Input DataFrame
        columns: Columns to create lags for
        lags: List of lag periods
    
    Returns:
        DataFrame with lag columns added
        (e.g., 'FII_Net_Lag1', 'FII_Net_Lag2')
        
    Raises:
        ValueError: If any specified column is missing
    """
    logger.info(f"Creating lag features for columns: {columns} with lags: {lags}")
    
    # Validate columns exist
    missing_columns = [col for col in columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")
    
    # Create a copy to avoid modifying original
    df_result = df.copy()
    
    # Create lag features for each column and lag period
    for col in columns:
        for lag in lags:
            new_col_name = f"{col}_Lag{lag}"
            logger.info(f"Creating lag-{lag} feature for {col}")
            df_result[new_col_name] = df_result[col].shift(lag)
    
    logger.info(f"Lag features created for {len(columns)} columns with {len(lags)} lag periods")
    return df_result


def create_target_variable(
    df: pd.DataFrame,
    return_col: str = "Daily_Return"
) -> pd.DataFrame:
    """
    Create binary target variable for next-day market direction.
    
    Target = 1 if next day return > 0, else 0
    
    Args:
        df: DataFrame with return data
        return_col: Name of return column
    
    Returns:
        DataFrame with 'Target' column added
        
    Raises:
        ValueError: If return column is missing
    """
    logger.info(f"Creating binary target variable from {return_col} column...")
    
    # Validate return column exists
    if return_col not in df.columns:
        raise ValueError(f"Return column '{return_col}' not found in DataFrame")
    
    # Create a copy to avoid modifying original
    df_result = df.copy()
    
    # Shift returns to get next day's return
    next_day_return = df_result[return_col].shift(-1)
    
    # Create binary target: 1 if next day return > 0, else 0
    # Keep NaN as NaN (don't convert to 0)
    df_result['Target'] = next_day_return.apply(lambda x: 1 if x > 0 else (0 if x <= 0 else np.nan))
    
    # Last row will have NaN target (no next day data)
    logger.info(f"Binary target variable created. Last row has NaN (no next day data)")
    return df_result
