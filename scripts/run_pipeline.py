"""
Data Pipeline Runner for Smart Money Intelligence Platform

This script runs the complete data pipeline:
1. Data Collection (NIFTY data + FII/DII data)
2. Data Preprocessing (cleaning and merging)
3. Feature Engineering (creating derived features)

It verifies that all expected columns are present in the final output.
"""

import os
import sys
import logging
from datetime import datetime
import pandas as pd

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from data_collection import download_nifty_data, load_fii_dii_data, save_data_to_database
from preprocessing import clean_market_data, clean_institutional_data, merge_datasets
from feature_engineering import (
    compute_returns,
    compute_rolling_averages,
    compute_volatility,
    compute_momentum,
    create_lag_features,
    create_target_variable
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_sample_fii_dii_data():
    """
    Create sample FII/DII data for demonstration purposes.
    In production, this would come from NSE or other data sources.
    """
    logger.info("Creating sample FII/DII data...")
    
    # Generate sample data from 2020-01-01 to 2024-03-07
    date_range = pd.date_range(start='2020-01-01', end='2024-03-07', freq='D')
    
    # Create sample institutional flows (in crores)
    # Using random but realistic values
    import numpy as np
    np.random.seed(42)  # For reproducibility
    
    df = pd.DataFrame({
        'Date': date_range,
        'FII_Buy': np.random.uniform(1000, 5000, len(date_range)),
        'FII_Sell': np.random.uniform(1000, 5000, len(date_range)),
        'DII_Buy': np.random.uniform(800, 4000, len(date_range)),
        'DII_Sell': np.random.uniform(800, 4000, len(date_range))
    })
    
    # Save to CSV
    output_path = "data/raw/fii_dii_data.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    
    logger.info(f"Created sample FII/DII data with {len(df)} rows at {output_path}")
    return df


def verify_processed_data(df: pd.DataFrame) -> bool:
    """
    Verify that the processed data has all expected columns.
    
    Args:
        df: Processed DataFrame
    
    Returns:
        True if all expected columns are present, False otherwise
    """
    expected_columns = [
        # Market data
        'Date', 'Open', 'High', 'Low', 'Close', 'Volume',
        # Institutional data
        'FII_Buy', 'FII_Sell', 'FII_Net',
        'DII_Buy', 'DII_Sell', 'DII_Net',
        # Derived features
        'Daily_Return', 'Volatility', 'Momentum',
        # Rolling averages
        'FII_Net_MA5', 'FII_Net_MA10', 'FII_Net_MA20',
        'DII_Net_MA5', 'DII_Net_MA10', 'DII_Net_MA20',
        # Lag features
        'FII_Net_Lag1', 'FII_Net_Lag2', 'FII_Net_Lag3',
        'DII_Net_Lag1', 'DII_Net_Lag2', 'DII_Net_Lag3',
        'Daily_Return_Lag1', 'Daily_Return_Lag2', 'Daily_Return_Lag3',
        # Target variable
        'Target'
    ]
    
    missing_columns = [col for col in expected_columns if col not in df.columns]
    
    if missing_columns:
        logger.error(f"Missing columns in processed data: {missing_columns}")
        return False
    
    logger.info(f"✓ All {len(expected_columns)} expected columns are present")
    return True


def run_pipeline():
    """
    Run the complete data pipeline.
    """
    print("\n" + "=" * 80)
    print("SMART MONEY INTELLIGENCE PLATFORM - DATA PIPELINE")
    print("=" * 80)
    
    try:
        # Step 1: Data Collection
        print("\n[STEP 1] DATA COLLECTION")
        print("-" * 80)
        
        # Download NIFTY data
        logger.info("Downloading NIFTY data from Yahoo Finance...")
        nifty_df = download_nifty_data(
            start_date="2020-01-01",
            end_date="2024-03-07"
        )
        print(f"✓ Downloaded NIFTY data: {len(nifty_df)} rows")
        print(f"  Date range: {nifty_df['Date'].min()} to {nifty_df['Date'].max()}")
        
        # Create or load FII/DII data
        fii_dii_path = "data/raw/fii_dii_data.csv"
        if not os.path.exists(fii_dii_path):
            logger.info("FII/DII data not found, creating sample data...")
            fii_dii_df = create_sample_fii_dii_data()
        else:
            logger.info("Loading existing FII/DII data...")
            fii_dii_df = load_fii_dii_data(fii_dii_path)
        
        print(f"✓ Loaded FII/DII data: {len(fii_dii_df)} rows")
        
        # Step 2: Data Preprocessing
        print("\n[STEP 2] DATA PREPROCESSING")
        print("-" * 80)
        
        # Clean market data
        logger.info("Cleaning market data...")
        nifty_clean = clean_market_data(nifty_df)
        print(f"✓ Cleaned market data: {len(nifty_clean)} rows")
        
        # Clean institutional data
        logger.info("Cleaning institutional data...")
        fii_dii_clean = clean_institutional_data(fii_dii_df)
        print(f"✓ Cleaned institutional data: {len(fii_dii_clean)} rows")
        
        # Merge datasets
        logger.info("Merging datasets...")
        merged_df = merge_datasets(nifty_clean, fii_dii_clean)
        print(f"✓ Merged data: {len(merged_df)} rows")
        
        # Step 3: Feature Engineering
        print("\n[STEP 3] FEATURE ENGINEERING")
        print("-" * 80)
        
        # Compute returns
        logger.info("Computing daily returns...")
        merged_df = compute_returns(merged_df)
        print(f"✓ Computed daily returns")
        
        # Compute rolling averages
        logger.info("Computing rolling averages...")
        merged_df = compute_rolling_averages(
            merged_df,
            columns=['FII_Net', 'DII_Net'],
            windows=[5, 10, 20]
        )
        print(f"✓ Computed rolling averages (5, 10, 20 day windows)")
        
        # Compute volatility
        logger.info("Computing volatility...")
        merged_df = compute_volatility(merged_df)
        print(f"✓ Computed volatility (20-day rolling)")
        
        # Compute momentum
        logger.info("Computing momentum...")
        merged_df = compute_momentum(merged_df)
        print(f"✓ Computed momentum (10-day)")
        
        # Create lag features
        logger.info("Creating lag features...")
        merged_df = create_lag_features(
            merged_df,
            columns=['FII_Net', 'DII_Net', 'Daily_Return'],
            lags=[1, 2, 3]
        )
        print(f"✓ Created lag features (1, 2, 3 day lags)")
        
        # Create target variable
        logger.info("Creating target variable...")
        merged_df = create_target_variable(merged_df)
        print(f"✓ Created target variable (next-day direction)")
        
        # Step 4: Save Processed Data
        print("\n[STEP 4] SAVING PROCESSED DATA")
        print("-" * 80)
        
        output_path = "data/processed/merged_data.csv"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        merged_df.to_csv(output_path, index=False)
        print(f"✓ Saved processed data to: {output_path}")
        print(f"  Total rows: {len(merged_df)}")
        print(f"  Total columns: {len(merged_df.columns)}")
        
        # Also save to database
        logger.info("Saving to database...")
        save_data_to_database(merged_df, "processed_data")
        print(f"✓ Saved to database: data/database.db")
        
        # Step 5: Verification
        print("\n[STEP 5] VERIFICATION")
        print("-" * 80)
        
        # Verify all expected columns are present
        if verify_processed_data(merged_df):
            print("✓ All expected columns are present")
        else:
            print("✗ Some expected columns are missing")
            return False
        
        # Display sample of processed data
        print("\nSample of processed data (first 5 rows):")
        print(merged_df.head().to_string())
        
        # Display data info
        print("\nData Info:")
        print(f"  Shape: {merged_df.shape}")
        print(f"  Columns: {len(merged_df.columns)}")
        print(f"  Non-null counts:")
        non_null_counts = merged_df.count()
        for col in merged_df.columns[:10]:  # Show first 10 columns
            print(f"    {col}: {non_null_counts[col]}/{len(merged_df)}")
        if len(merged_df.columns) > 10:
            print(f"    ... and {len(merged_df.columns) - 10} more columns")
        
        # Summary statistics
        print("\nSummary Statistics (key columns):")
        key_cols = ['Close', 'Daily_Return', 'FII_Net', 'DII_Net', 'Volatility', 'Momentum']
        available_key_cols = [col for col in key_cols if col in merged_df.columns]
        print(merged_df[available_key_cols].describe().to_string())
        
        print("\n" + "=" * 80)
        print("✓ DATA PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"\nProcessed data saved to: {output_path}")
        print(f"Database saved to: data/database.db")
        print("\nNext steps:")
        print("  1. Run exploratory data analysis (notebooks/)")
        print("  2. Train machine learning models (scripts/model_training.py)")
        print("  3. Launch dashboard (streamlit run dashboard/app.py)")
        
        return True
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        print(f"\n✗ PIPELINE FAILED: {str(e)}")
        return False


if __name__ == "__main__":
    success = run_pipeline()
    sys.exit(0 if success else 1)
