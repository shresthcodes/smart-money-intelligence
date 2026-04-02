"""
Data Collection Module for Smart Money Intelligence Platform

This module handles downloading market data from Yahoo Finance and loading
institutional investor (FII/DII) data from CSV files.
"""

import os
import time
import logging
from typing import Optional
from datetime import datetime
import pandas as pd
import yfinance as yf
import sqlite3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def download_nifty_data(
    ticker: str = "^NSEI",
    start_date: str = None,
    end_date: str = None,
    output_path: str = "data/raw/nifty_data.csv"
) -> pd.DataFrame:
    """
    Download NIFTY index historical data from Yahoo Finance.
    
    Implements retry logic with exponential backoff for network failures.
    Validates date ranges and handles errors gracefully.
    
    Args:
        ticker: Yahoo Finance ticker symbol for NIFTY (default: ^NSEI)
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
        output_path: Path to save CSV file
    
    Returns:
        DataFrame with columns: Date, Open, High, Low, Close, Volume
    
    Raises:
        ValueError: If date range is invalid
        ConnectionError: If Yahoo Finance is unreachable after retries
    """
    # Validate dates
    if start_date and end_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            if start_dt >= end_dt:
                error_msg = f"Invalid date range: start_date ({start_date}) must be before end_date ({end_date})"
                logger.error(error_msg)
                raise ValueError(error_msg)
        except ValueError as e:
            if "does not match format" in str(e):
                error_msg = f"Invalid date format. Expected 'YYYY-MM-DD', got start_date='{start_date}', end_date='{end_date}'"
                logger.error(error_msg)
                raise ValueError(error_msg)
            raise
    
    # Retry logic with exponential backoff
    max_retries = 3
    retry_delays = [1, 2, 4]  # seconds
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to download {ticker} data (attempt {attempt + 1}/{max_retries})")
            
            # Download data from Yahoo Finance
            df = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                progress=False
            )
            
            if df.empty:
                error_msg = f"No data returned for ticker {ticker} between {start_date} and {end_date}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Reset index to make Date a column
            df = df.reset_index()
            
            # Handle MultiIndex columns (yfinance returns MultiIndex for single ticker)
            if isinstance(df.columns, pd.MultiIndex):
                # Flatten the MultiIndex by taking the first level
                df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
            
            # Ensure we have the expected columns
            expected_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            
            # yfinance might return 'Adj Close' as well, we'll keep only what we need
            available_columns = [col for col in expected_columns if col in df.columns]
            df = df[available_columns]
            
            # Validate we have the minimum required columns
            required_columns = ['Date', 'Close']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                error_msg = f"Missing required columns: {missing_columns}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save to CSV
            df.to_csv(output_path, index=False)
            logger.info(f"Successfully downloaded {len(df)} rows of data and saved to {output_path}")
            
            return df
            
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            
            if attempt < max_retries - 1:
                delay = retry_delays[attempt]
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                error_msg = f"Failed to download data after {max_retries} attempts: {str(e)}"
                logger.error(error_msg)
                raise ConnectionError(error_msg)


def load_fii_dii_data(
    input_path: str = "data/raw/fii_dii_data.csv"
) -> pd.DataFrame:
    """
    Load FII/DII institutional investment data from CSV.
    
    Expected CSV format:
    Date, FII_Buy, FII_Sell, DII_Buy, DII_Sell
    
    Args:
        input_path: Path to FII/DII CSV file
    
    Returns:
        DataFrame with institutional flow data
    
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If CSV format is invalid
    """
    # Check if file exists
    if not os.path.exists(input_path):
        error_msg = f"FII/DII data file not found at: {input_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    try:
        # Load CSV
        df = pd.read_csv(input_path)
        logger.info(f"Loaded {len(df)} rows from {input_path}")
        
        # Validate expected columns
        expected_columns = ['Date', 'FII_Buy', 'FII_Sell', 'DII_Buy', 'DII_Sell']
        missing_columns = [col for col in expected_columns if col not in df.columns]
        
        if missing_columns:
            error_msg = f"Invalid CSV format. Missing columns: {missing_columns}. Expected columns: {expected_columns}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"Successfully loaded FII/DII data with columns: {list(df.columns)}")
        return df
        
    except pd.errors.EmptyDataError:
        error_msg = f"CSV file is empty: {input_path}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    except pd.errors.ParserError as e:
        error_msg = f"Failed to parse CSV file: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg)


def save_data_to_database(
    df: pd.DataFrame,
    table_name: str,
    db_path: str = "data/database.db"
) -> None:
    """
    Save DataFrame to SQLite database.
    
    Creates table if it doesn't exist. Replaces existing data.
    
    Args:
        df: DataFrame to save
        table_name: Name of database table
        db_path: Path to SQLite database file
    
    Raises:
        OSError: If database directory cannot be created
        sqlite3.Error: If database operation fails
    """
    try:
        # Validate database path
        db_dir = os.path.dirname(db_path)
        
        # Check if the parent directory exists or can be created
        if db_dir:
            # Check if parent of db_dir exists (to prevent creating deep non-existent paths)
            parent_dir = os.path.dirname(db_dir)
            if parent_dir and not os.path.exists(parent_dir):
                error_msg = f"Parent directory '{parent_dir}' does not exist. Cannot create database at '{db_path}'"
                logger.error(error_msg)
                raise OSError(error_msg)
            
            # Try to create the immediate directory
            if not os.path.exists(db_dir):
                try:
                    os.makedirs(db_dir, exist_ok=True)
                except OSError as e:
                    error_msg = f"Cannot create database directory '{db_dir}': {str(e)}"
                    logger.error(error_msg)
                    raise OSError(error_msg)
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        logger.info(f"Connected to database: {db_path}")
        
        # Save DataFrame to database (replace if exists)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        # Verify the save
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        
        conn.close()
        
        logger.info(f"Successfully saved {row_count} rows to table '{table_name}' in {db_path}")
        
    except sqlite3.Error as e:
        error_msg = f"Database error while saving to table '{table_name}': {str(e)}"
        logger.error(error_msg)
        raise sqlite3.Error(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error while saving to database: {str(e)}"
        logger.error(error_msg)
        raise


if __name__ == "__main__":
    # Example usage
    print("Smart Money Intelligence - Data Collection Module")
    print("=" * 60)
    
    # Example 1: Download NIFTY data
    print("\n1. Downloading NIFTY data...")
    try:
        nifty_df = download_nifty_data(
            start_date="2020-01-01",
            end_date="2024-03-07"
        )
        print(f"   Downloaded {len(nifty_df)} rows")
        print(f"   Columns: {list(nifty_df.columns)}")
        print(f"   Date range: {nifty_df['Date'].min()} to {nifty_df['Date'].max()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example 2: Load FII/DII data (if file exists)
    print("\n2. Loading FII/DII data...")
    try:
        fii_dii_df = load_fii_dii_data()
        print(f"   Loaded {len(fii_dii_df)} rows")
        print(f"   Columns: {list(fii_dii_df.columns)}")
    except FileNotFoundError:
        print("   FII/DII data file not found (this is expected if not yet created)")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example 3: Save to database
    print("\n3. Saving NIFTY data to database...")
    try:
        if 'nifty_df' in locals():
            save_data_to_database(nifty_df, "nifty_data")
            print("   Successfully saved to database")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 60)
    print("Data collection module ready!")
