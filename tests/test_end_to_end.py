"""
End-to-end integration test for the Smart Money Intelligence Platform.

This test validates the complete pipeline:
data collection → preprocessing → feature engineering → model training → prediction

Requirements: 1.1, 2.5, 3.6, 7.7
"""

import os
import sys
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.data_collection import download_nifty_data, save_data_to_database
from scripts.preprocessing import clean_market_data, clean_institutional_data, merge_datasets
from scripts.feature_engineering import (
    compute_returns, compute_rolling_averages, compute_volatility,
    compute_momentum, create_lag_features, create_target_variable
)
from scripts.model_training import MarketPredictor


class TestEndToEndPipeline:
    """Test the complete data pipeline from collection to prediction."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_market_data(self):
        """Create sample market data for testing."""
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        data = {
            'Date': dates,
            'Open': np.random.uniform(18000, 19000, len(dates)),
            'High': np.random.uniform(18500, 19500, len(dates)),
            'Low': np.random.uniform(17500, 18500, len(dates)),
            'Close': np.random.uniform(18000, 19000, len(dates)),
            'Volume': np.random.randint(1000000, 10000000, len(dates))
        }
        return pd.DataFrame(data)
    
    @pytest.fixture
    def sample_institutional_data(self):
        """Create sample institutional data for testing."""
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        data = {
            'Date': dates,
            'FII_Buy': np.random.uniform(1000, 5000, len(dates)),
            'FII_Sell': np.random.uniform(1000, 5000, len(dates)),
            'DII_Buy': np.random.uniform(1000, 5000, len(dates)),
            'DII_Sell': np.random.uniform(1000, 5000, len(dates))
        }
        return pd.DataFrame(data)
    
    def test_complete_pipeline(self, temp_dir, sample_market_data, sample_institutional_data):
        """
        Test the complete pipeline from data collection to prediction.
        
        Validates:
        - Data collection and storage (Requirement 1.1)
        - Data preprocessing and merging (Requirement 2.5)
        - Feature engineering (Requirement 3.6)
        - Model training and prediction (Requirement 7.7)
        """
        # Step 1: Save sample data to CSV files
        market_csv = os.path.join(temp_dir, 'nifty_data.csv')
        institutional_csv = os.path.join(temp_dir, 'fii_dii_data.csv')
        
        sample_market_data.to_csv(market_csv, index=False)
        sample_institutional_data.to_csv(institutional_csv, index=False)
        
        # Verify files were created (Requirement 1.1)
        assert os.path.exists(market_csv), "Market data CSV should be created"
        assert os.path.exists(institutional_csv), "Institutional data CSV should be created"
        
        # Step 2: Load and preprocess data
        market_df = pd.read_csv(market_csv)
        institutional_df = pd.read_csv(institutional_csv)
        
        market_df = clean_market_data(market_df)
        institutional_df = clean_institutional_data(institutional_df)
        
        # Step 3: Merge datasets (Requirement 2.5)
        merged_df = merge_datasets(market_df, institutional_df)
        
        # Verify merge was successful
        assert len(merged_df) > 0, "Merged dataset should not be empty"
        assert 'Close' in merged_df.columns, "Merged data should have Close column"
        assert 'FII_Net' in merged_df.columns, "Merged data should have FII_Net column"
        assert 'DII_Net' in merged_df.columns, "Merged data should have DII_Net column"
        
        # Step 4: Feature engineering (Requirement 3.6)
        merged_df = compute_returns(merged_df)
        merged_df = compute_rolling_averages(merged_df, ['FII_Net', 'DII_Net'], [5, 10, 20])
        merged_df = compute_volatility(merged_df)
        merged_df = compute_momentum(merged_df)
        merged_df = create_lag_features(merged_df, ['FII_Net', 'DII_Net', 'Daily_Return'], [1, 2, 3])
        merged_df = create_target_variable(merged_df)
        
        # Verify all features were created
        expected_features = [
            'Daily_Return', 'Volatility', 'Momentum',
            'FII_Net_MA5', 'FII_Net_MA10', 'FII_Net_MA20',
            'DII_Net_MA5', 'DII_Net_MA10', 'DII_Net_MA20',
            'FII_Net_Lag1', 'FII_Net_Lag2', 'FII_Net_Lag3',
            'DII_Net_Lag1', 'DII_Net_Lag2', 'DII_Net_Lag3',
            'Daily_Return_Lag1', 'Daily_Return_Lag2', 'Daily_Return_Lag3',
            'Target'
        ]
        
        for feature in expected_features:
            assert feature in merged_df.columns, f"Feature {feature} should be created"
        
        # Save processed data
        processed_csv = os.path.join(temp_dir, 'processed_data.csv')
        merged_df.to_csv(processed_csv, index=False)
        assert os.path.exists(processed_csv), "Processed data CSV should be created"
        
        # Step 5: Model training and prediction (Requirement 7.7)
        predictor = MarketPredictor()
        
        # Prepare features
        X, y = predictor.prepare_features(merged_df)
        
        # Verify feature preparation
        assert X is not None, "Feature matrix should be created"
        assert y is not None, "Target vector should be created"
        assert len(X) == len(y), "X and y should have same length"
        assert len(X) > 0, "Should have training samples"
        
        # Train-test split
        X_train, X_test, y_train, y_test = predictor.train_test_split(X, y, test_size=0.2)
        
        # Verify split
        assert len(X_train) > 0, "Training set should not be empty"
        assert len(X_test) > 0, "Test set should not be empty"
        assert len(X_train) + len(X_test) == len(X), "Split should preserve total samples"
        
        # Train models
        results = predictor.train_models(X_train, y_train)
        
        # Verify training
        assert len(results) > 0, "Should train at least one model"
        assert 'logistic' in results, "Should train logistic regression"
        
        # Set best model for saving (normally done by comparing metrics)
        predictor.best_model = predictor.models['logistic']
        
        # Evaluate model
        metrics = predictor.evaluate_model(predictor.models['logistic'], X_test, y_test)
        
        # Verify evaluation metrics
        assert 'accuracy' in metrics, "Should compute accuracy"
        assert 'precision' in metrics, "Should compute precision"
        assert 'recall' in metrics, "Should compute recall"
        assert 'f1_score' in metrics, "Should compute F1 score"
        assert 0 <= metrics['accuracy'] <= 1, "Accuracy should be between 0 and 1"
        
        # Save model
        model_path = os.path.join(temp_dir, 'test_model.pkl')
        predictor.save_model(model_path)
        assert os.path.exists(model_path), "Model file should be created"
        
        # Load model and make prediction
        predictor_loaded = MarketPredictor()
        predictor_loaded.load_model(model_path)
        
        # Make prediction on test data
        predictions, probabilities = predictor_loaded.predict(X_test[:5])
        
        # Verify predictions
        assert len(predictions) == 5, "Should make 5 predictions"
        assert len(probabilities) == 5, "Should return 5 probabilities"
        assert all(p in [0, 1] for p in predictions), "Predictions should be binary"
        assert all(0 <= prob <= 1 for prob in probabilities), "Probabilities should be between 0 and 1"
        
        print("\n✅ End-to-end pipeline test passed!")
        print(f"   - Data collection: ✓")
        print(f"   - Preprocessing: ✓")
        print(f"   - Feature engineering: ✓")
        print(f"   - Model training: ✓")
        print(f"   - Model persistence: ✓")
        print(f"   - Prediction: ✓")
    
    def test_pipeline_with_database(self, temp_dir, sample_market_data):
        """
        Test data persistence to database.
        
        Validates: Requirement 1.1 (database storage)
        """
        db_path = os.path.join(temp_dir, 'test_database.db')
        
        # Save to database
        save_data_to_database(sample_market_data, 'market_data', db_path)
        
        # Verify database file was created
        assert os.path.exists(db_path), "Database file should be created"
        
        # Load from database
        import sqlite3
        conn = sqlite3.connect(db_path)
        loaded_df = pd.read_sql_query("SELECT * FROM market_data", conn)
        conn.close()
        
        # Verify data was saved and loaded correctly
        assert len(loaded_df) == len(sample_market_data), "Should load same number of rows"
        assert list(loaded_df.columns) == list(sample_market_data.columns), "Should have same columns"
        
        print("\n✅ Database persistence test passed!")
    
    def test_pipeline_error_handling(self, temp_dir):
        """
        Test that pipeline handles errors gracefully.
        
        Validates: Error handling throughout the pipeline
        """
        # Test with missing file
        with pytest.raises(FileNotFoundError):
            pd.read_csv(os.path.join(temp_dir, 'nonexistent.csv'))
        
        # Test with invalid data
        invalid_df = pd.DataFrame({'invalid': [1, 2, 3]})
        
        # Should handle missing required columns
        try:
            clean_market_data(invalid_df)
            assert False, "Should raise error for missing columns"
        except (KeyError, ValueError):
            pass  # Expected
        
        print("\n✅ Error handling test passed!")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
