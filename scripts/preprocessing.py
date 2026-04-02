"""
Data Preprocessing Module

This module provides functions to clean and prepare raw market and institutional data
for analysis and modeling.
"""

import pandas as pd
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def clean_market_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean NIFTY market data.
    
    Operations:
    - Convert Date column to datetime
    - Remove duplicates based on Date
    - Sort by Date ascending
    - Handle missing values (forward fill for prices)
    - Validate data types
    
    Args:
        df: Raw market data DataFrame
    
    Returns:
        Cleaned DataFrame
        
    Raises:
        ValueError: If required columns are missing
    """
    logger.info("Starting market data cleaning...")
    
    # Validate required columns
    required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # Create a copy to avoid modifying original
    df_clean = df.copy()
    
    # Convert Date column to datetime
    logger.info("Converting Date column to datetime format...")
    df_clean['Date'] = pd.to_datetime(df_clean['Date'], errors='coerce')
    
    # Remove rows with invalid dates
    invalid_dates = df_clean['Date'].isna().sum()
    if invalid_dates > 0:
        logger.warning(f"Removing {invalid_dates} rows with invalid dates")
        df_clean = df_clean.dropna(subset=['Date'])
    
    # Remove duplicate rows based on Date
    duplicates = df_clean.duplicated(subset=['Date']).sum()
    if duplicates > 0:
        logger.info(f"Removing {duplicates} duplicate rows based on Date")
        df_clean = df_clean.drop_duplicates(subset=['Date'], keep='first')
    
    # Sort by Date ascending
    logger.info("Sorting data by Date in ascending order...")
    df_clean = df_clean.sort_values('Date').reset_index(drop=True)
    
    # Handle missing values with forward fill for prices
    price_columns = ['Open', 'High', 'Low', 'Close']
    missing_before = df_clean[price_columns].isna().sum().sum()
    if missing_before > 0:
        logger.info(f"Handling {missing_before} missing values in price columns using forward fill")
        df_clean[price_columns] = df_clean[price_columns].ffill()
        
        # If still missing (at the beginning), use backward fill
        remaining_missing = df_clean[price_columns].isna().sum().sum()
        if remaining_missing > 0:
            logger.info(f"Using backward fill for {remaining_missing} remaining missing values")
            df_clean[price_columns] = df_clean[price_columns].bfill()
    
    # Handle missing Volume (fill with 0)
    if df_clean['Volume'].isna().any():
        logger.info("Filling missing Volume values with 0")
        df_clean['Volume'] = df_clean['Volume'].fillna(0)
    
    logger.info(f"Market data cleaning complete. Final shape: {df_clean.shape}")
    return df_clean


def clean_institutional_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean FII/DII institutional data.
    
    Operations:
    - Convert Date column to datetime
    - Remove duplicates
    - Sort by Date
    - Handle missing values (fill with 0 for flows)
    - Compute net flows: FII_Net = FII_Buy - FII_Sell
    
    Args:
        df: Raw institutional data DataFrame
    
    Returns:
        Cleaned DataFrame with net flow columns
        
    Raises:
        ValueError: If required columns are missing
    """
    logger.info("Starting institutional data cleaning...")
    
    # Validate required columns
    required_columns = ['Date', 'FII_Buy', 'FII_Sell', 'DII_Buy', 'DII_Sell']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # Create a copy to avoid modifying original
    df_clean = df.copy()
    
    # Convert Date column to datetime
    logger.info("Converting Date column to datetime format...")
    df_clean['Date'] = pd.to_datetime(df_clean['Date'], errors='coerce')
    
    # Remove rows with invalid dates
    invalid_dates = df_clean['Date'].isna().sum()
    if invalid_dates > 0:
        logger.warning(f"Removing {invalid_dates} rows with invalid dates")
        df_clean = df_clean.dropna(subset=['Date'])
    
    # Remove duplicate rows based on Date
    duplicates = df_clean.duplicated(subset=['Date']).sum()
    if duplicates > 0:
        logger.info(f"Removing {duplicates} duplicate rows based on Date")
        df_clean = df_clean.drop_duplicates(subset=['Date'], keep='first')
    
    # Sort by Date ascending
    logger.info("Sorting data by Date in ascending order...")
    df_clean = df_clean.sort_values('Date').reset_index(drop=True)
    
    # Handle missing values (fill with 0 for flows)
    flow_columns = ['FII_Buy', 'FII_Sell', 'DII_Buy', 'DII_Sell']
    missing_flows = df_clean[flow_columns].isna().sum().sum()
    if missing_flows > 0:
        logger.info(f"Filling {missing_flows} missing values in flow columns with 0")
        df_clean[flow_columns] = df_clean[flow_columns].fillna(0)
    
    # Compute net flows
    logger.info("Computing net institutional flows...")
    df_clean['FII_Net'] = df_clean['FII_Buy'] - df_clean['FII_Sell']
    df_clean['DII_Net'] = df_clean['DII_Buy'] - df_clean['DII_Sell']
    
    logger.info(f"Institutional data cleaning complete. Final shape: {df_clean.shape}")
    return df_clean


def merge_datasets(
    market_df: pd.DataFrame,
    institutional_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge market and institutional data by date.
    
    Args:
        market_df: Cleaned market data
        institutional_df: Cleaned institutional data
    
    Returns:
        Merged DataFrame with both market and institutional data
        
    Raises:
        ValueError: If Date column is missing in either DataFrame
    """
    logger.info("Starting dataset merge...")
    
    # Validate Date column exists
    if 'Date' not in market_df.columns:
        raise ValueError("Market DataFrame missing 'Date' column")
    if 'Date' not in institutional_df.columns:
        raise ValueError("Institutional DataFrame missing 'Date' column")
    
    # Ensure Date columns are datetime
    market_df = market_df.copy()
    institutional_df = institutional_df.copy()
    market_df['Date'] = pd.to_datetime(market_df['Date'])
    institutional_df['Date'] = pd.to_datetime(institutional_df['Date'])
    
    # Perform inner join on Date
    logger.info(f"Merging datasets - Market: {len(market_df)} rows, Institutional: {len(institutional_df)} rows")
    merged_df = pd.merge(
        market_df,
        institutional_df,
        on='Date',
        how='inner'
    )
    
    # Sort by date
    merged_df = merged_df.sort_values('Date').reset_index(drop=True)
    
    logger.info(f"Merge complete. Merged dataset has {len(merged_df)} rows")
    
    # Log merge statistics
    market_only = len(market_df) - len(merged_df)
    institutional_only = len(institutional_df) - len(merged_df)
    if market_only > 0:
        logger.info(f"{market_only} dates in market data not found in institutional data")
    if institutional_only > 0:
        logger.info(f"{institutional_only} dates in institutional data not found in market data")
    
    return merged_df
