"""
Generate Sample Data for Demo

This script:
1. Downloads 5 years of NIFTY data from Yahoo Finance
2. Creates synthetic FII/DII data for demonstration
3. Runs the full pipeline to generate processed data and trained model
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.data_collection import download_nifty_data, save_data_to_database
from scripts.preprocessing import clean_market_data, clean_institutional_data, merge_datasets
from scripts.feature_engineering import (
    compute_returns, compute_rolling_averages, compute_volatility,
    compute_momentum, create_lag_features, create_target_variable
)
from scripts.model_training import MarketPredictor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_synthetic_fii_dii_data(nifty_df: pd.DataFrame, output_path: str = "data/raw/fii_dii_data.csv") -> pd.DataFrame:
    """
    Generate synthetic FII/DII data correlated with NIFTY movements.
    
    This creates realistic-looking institutional flow data for demonstration purposes.
    The data is generated to have some correlation with market movements.
    
    Args:
        nifty_df: DataFrame with NIFTY data (must have Date and Close columns)
        output_path: Path to save the synthetic FII/DII data
    
    Returns:
        DataFrame with synthetic FII/DII data
    """
    logger.info("Generating synthetic FII/DII data...")
    
    # Calculate daily returns for NIFTY
    nifty_df = nifty_df.copy()
    nifty_df['Return'] = nifty_df['Close'].pct_change() * 100
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Generate synthetic institutional flows
    dates = nifty_df['Date'].values
    returns = nifty_df['Return'].fillna(0).values
    
    fii_data = []
    dii_data = []
    
    # Base flow amounts (in crores)
    base_fii_buy = 2000
    base_fii_sell = 1800
    base_dii_buy = 1500
    base_dii_sell = 1600
    
    for i, (date, ret) in enumerate(zip(dates, returns)):
        # FII tends to follow momentum (buy when market up, sell when down)
        # Add correlation with returns + random noise
        fii_buy_factor = 1 + (ret / 100) * 0.5 + np.random.normal(0, 0.3)
        fii_sell_factor = 1 - (ret / 100) * 0.5 + np.random.normal(0, 0.3)
        
        # DII tends to be contrarian (buy when market down, sell when up)
        dii_buy_factor = 1 - (ret / 100) * 0.3 + np.random.normal(0, 0.25)
        dii_sell_factor = 1 + (ret / 100) * 0.3 + np.random.normal(0, 0.25)
        
        # Ensure factors are positive
        fii_buy_factor = max(0.1, fii_buy_factor)
        fii_sell_factor = max(0.1, fii_sell_factor)
        dii_buy_factor = max(0.1, dii_buy_factor)
        dii_sell_factor = max(0.1, dii_sell_factor)
        
        # Calculate flows
        fii_buy = base_fii_buy * fii_buy_factor
        fii_sell = base_fii_sell * fii_sell_factor
        dii_buy = base_dii_buy * dii_buy_factor
        dii_sell = base_dii_sell * dii_sell_factor
        
        # Add some trend (institutional flows tend to have persistence)
        if i > 0:
            fii_buy = 0.7 * fii_buy + 0.3 * fii_data[-1]['FII_Buy']
            fii_sell = 0.7 * fii_sell + 0.3 * fii_data[-1]['FII_Sell']
            dii_buy = 0.7 * dii_buy + 0.3 * dii_data[-1]['DII_Buy']
            dii_sell = 0.7 * dii_sell + 0.3 * dii_data[-1]['DII_Sell']
        
        fii_data.append({
            'Date': date,
            'FII_Buy': round(fii_buy, 2),
            'FII_Sell': round(fii_sell, 2)
        })
        
        dii_data.append({
            'Date': date,
            'DII_Buy': round(dii_buy, 2),
            'DII_Sell': round(dii_sell, 2)
        })
    
    # Combine FII and DII data
    fii_df = pd.DataFrame(fii_data)
    dii_df = pd.DataFrame(dii_data)
    
    institutional_df = pd.merge(fii_df, dii_df, on='Date')
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save to CSV
    institutional_df.to_csv(output_path, index=False)
    logger.info(f"Saved {len(institutional_df)} rows of synthetic FII/DII data to {output_path}")
    
    # Print summary statistics
    logger.info("\nSynthetic FII/DII Data Summary:")
    logger.info(f"  Date range: {institutional_df['Date'].min()} to {institutional_df['Date'].max()}")
    logger.info(f"  FII Buy range: {institutional_df['FII_Buy'].min():.2f} to {institutional_df['FII_Buy'].max():.2f} crores")
    logger.info(f"  FII Sell range: {institutional_df['FII_Sell'].min():.2f} to {institutional_df['FII_Sell'].max():.2f} crores")
    logger.info(f"  DII Buy range: {institutional_df['DII_Buy'].min():.2f} to {institutional_df['DII_Buy'].max():.2f} crores")
    logger.info(f"  DII Sell range: {institutional_df['DII_Sell'].min():.2f} to {institutional_df['DII_Sell'].max():.2f} crores")
    
    return institutional_df


def run_full_pipeline():
    """
    Run the complete data pipeline:
    1. Download NIFTY data (5 years)
    2. Generate synthetic FII/DII data
    3. Preprocess and merge data
    4. Engineer features
    5. Train and save model
    """
    logger.info("=" * 80)
    logger.info("SMART MONEY INTELLIGENCE - SAMPLE DATA GENERATION")
    logger.info("=" * 80)
    
    # Step 1: Download NIFTY data (5 years)
    logger.info("\n[Step 1/6] Downloading 5 years of NIFTY data...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5*365)  # Approximately 5 years
    
    try:
        nifty_df = download_nifty_data(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            output_path="data/raw/nifty_data.csv"
        )
        logger.info(f"✓ Downloaded {len(nifty_df)} rows of NIFTY data")
        logger.info(f"  Date range: {nifty_df['Date'].min()} to {nifty_df['Date'].max()}")
    except Exception as e:
        logger.error(f"✗ Failed to download NIFTY data: {e}")
        return False
    
    # Step 2: Generate synthetic FII/DII data
    logger.info("\n[Step 2/6] Generating synthetic FII/DII data...")
    try:
        institutional_df = generate_synthetic_fii_dii_data(nifty_df)
        logger.info(f"✓ Generated {len(institutional_df)} rows of synthetic institutional data")
    except Exception as e:
        logger.error(f"✗ Failed to generate FII/DII data: {e}")
        return False
    
    # Step 3: Preprocess and merge data
    logger.info("\n[Step 3/6] Preprocessing and merging datasets...")
    try:
        # Clean market data
        nifty_clean = clean_market_data(nifty_df)
        logger.info(f"  Cleaned market data: {len(nifty_clean)} rows")
        
        # Clean institutional data
        institutional_clean = clean_institutional_data(institutional_df)
        logger.info(f"  Cleaned institutional data: {len(institutional_clean)} rows")
        
        # Merge datasets
        merged_df = merge_datasets(nifty_clean, institutional_clean)
        logger.info(f"✓ Merged dataset: {len(merged_df)} rows")
    except Exception as e:
        logger.error(f"✗ Failed to preprocess data: {e}")
        return False
    
    # Step 4: Engineer features
    logger.info("\n[Step 4/6] Engineering features...")
    try:
        # Compute returns
        merged_df = compute_returns(merged_df)
        
        # Compute rolling averages
        merged_df = compute_rolling_averages(
            merged_df,
            columns=['FII_Net', 'DII_Net'],
            windows=[5, 10, 20]
        )
        
        # Compute volatility
        merged_df = compute_volatility(merged_df)
        
        # Compute momentum
        merged_df = compute_momentum(merged_df)
        
        # Create lag features
        merged_df = create_lag_features(
            merged_df,
            columns=['FII_Net', 'DII_Net', 'Daily_Return'],
            lags=[1, 2, 3]
        )
        
        # Create target variable
        merged_df = create_target_variable(merged_df)
        
        # Remove rows with NaN (from rolling windows and lags)
        merged_df = merged_df.dropna()
        
        logger.info(f"✓ Feature engineering complete: {len(merged_df)} rows with {len(merged_df.columns)} features")
        
        # Save processed data
        os.makedirs("data/processed", exist_ok=True)
        merged_df.to_csv("data/processed/merged_data.csv", index=False)
        logger.info(f"  Saved processed data to data/processed/merged_data.csv")
        
    except Exception as e:
        logger.error(f"✗ Failed to engineer features: {e}")
        return False
    
    # Step 5: Train model
    logger.info("\n[Step 5/6] Training machine learning models...")
    try:
        predictor = MarketPredictor()
        
        # Prepare features
        X, y = predictor.prepare_features(merged_df)
        logger.info(f"  Prepared {X.shape[0]} samples with {X.shape[1]} features")
        
        # Split data
        X_train, X_test, y_train, y_test = predictor.train_test_split(X, y)
        logger.info(f"  Train set: {len(X_train)} samples, Test set: {len(X_test)} samples")
        
        # Train models
        results = predictor.train_models(X_train, y_train)
        logger.info(f"  Trained {len(results)} models")
        
        # Evaluate models
        best_model_name = None
        best_accuracy = 0
        best_metrics = None
        
        for model_name, model in results.items():
            metrics = predictor.evaluate_model(model, X_test, y_test)
            logger.info(f"  {model_name}: Accuracy = {metrics['accuracy']:.4f}, F1 = {metrics['f1_score']:.4f}")
            
            if metrics['accuracy'] > best_accuracy:
                best_accuracy = metrics['accuracy']
                best_model_name = model_name
                best_metrics = metrics
                predictor.best_model = model
                predictor.best_model_name = model_name
        
        logger.info(f"✓ Best model: {best_model_name} (Accuracy: {best_accuracy:.4f})")
        
        # Prepare metadata
        metadata = {
            'model_type': best_model_name,
            'training_date': datetime.now().strftime('%Y-%m-%d'),
            'features': predictor.feature_names,
            'performance': {
                'accuracy': float(best_metrics['accuracy']),
                'precision': float(best_metrics['precision']),
                'recall': float(best_metrics['recall']),
                'f1_score': float(best_metrics['f1_score'])
            },
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'data_date_range': {
                'start': str(merged_df['Date'].min()),
                'end': str(merged_df['Date'].max())
            }
        }
        
        # Save best model with metadata
        os.makedirs("models", exist_ok=True)
        predictor.save_model(metadata=metadata)
        logger.info(f"  Saved model to models/market_prediction_model.pkl")
        logger.info(f"  Saved metadata to models/market_prediction_model_metadata.json")
        
    except Exception as e:
        logger.error(f"✗ Failed to train model: {e}")
        return False
    
    # Step 6: Summary
    logger.info("\n[Step 6/6] Pipeline Summary")
    logger.info("=" * 80)
    logger.info("✓ Sample data generation complete!")
    logger.info(f"\nGenerated files:")
    logger.info(f"  • data/raw/nifty_data.csv ({len(nifty_df)} rows)")
    logger.info(f"  • data/raw/fii_dii_data.csv ({len(institutional_df)} rows)")
    logger.info(f"  • data/processed/merged_data.csv ({len(merged_df)} rows)")
    logger.info(f"  • models/market_prediction_model.pkl")
    logger.info(f"  • models/model_metadata.json")
    logger.info(f"\nYou can now run the dashboard with: streamlit run dashboard/app.py")
    logger.info("=" * 80)
    
    return True


if __name__ == "__main__":
    success = run_full_pipeline()
    sys.exit(0 if success else 1)
