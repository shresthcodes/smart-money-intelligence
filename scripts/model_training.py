"""
Machine Learning Module for Market Direction Prediction

This module implements the MarketPredictor class which trains and evaluates
multiple machine learning models to predict next-day market direction.
"""

import pandas as pd
import numpy as np
import os
from typing import Dict, Tuple, Any, List
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from xgboost import XGBClassifier
import joblib
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MarketPredictor:
    """
    Ensemble predictor for market direction.
    
    This class trains multiple machine learning models (Logistic Regression,
    Random Forest, XGBoost) to predict next-day market direction based on
    institutional flows, technical indicators, and historical patterns.
    """
    
    def __init__(self):
        """
        Initialize MarketPredictor with three models and a feature scaler.
        """
        self.models = {
            'logistic': LogisticRegression(max_iter=1000, random_state=42),
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'xgboost': XGBClassifier(n_estimators=100, random_state=42, use_label_encoder=False, eval_metric='logloss')
        }
        self.best_model = None
        self.best_model_name = None
        self.feature_names = None
        self.scaler = StandardScaler()
        logger.info("MarketPredictor initialized with 3 models: Logistic Regression, Random Forest, XGBoost")

    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare feature matrix and target vector from processed data.
        
        Features include:
        - FII_Net, DII_Net (institutional flows)
        - Daily_Return lags (1, 2, 3 days)
        - Volatility (20-day rolling std)
        - Momentum (10-day momentum)
        - Rolling averages (5, 10, 20 day for FII_Net and DII_Net)
        - Lag features (1, 2, 3 days for FII_Net, DII_Net)
        
        Args:
            df: DataFrame with processed market and institutional data
        
        Returns:
            X: Feature matrix (scaled)
            y: Target vector (binary: 0 or 1)
        
        Raises:
            ValueError: If required columns are missing or insufficient data
        """
        logger.info("Preparing features from DataFrame")
        
        # Define feature columns
        feature_cols = [
            'FII_Net', 'DII_Net',
            'Daily_Return_Lag1', 'Daily_Return_Lag2', 'Daily_Return_Lag3',
            'Volatility',
            'Momentum',
            'FII_Net_MA5', 'FII_Net_MA10', 'FII_Net_MA20',
            'DII_Net_MA5', 'DII_Net_MA10', 'DII_Net_MA20',
            'FII_Net_Lag1', 'FII_Net_Lag2', 'FII_Net_Lag3',
            'DII_Net_Lag1', 'DII_Net_Lag2', 'DII_Net_Lag3'
        ]
        
        # Check if all required columns exist
        missing_cols = [col for col in feature_cols + ['Target'] if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Select features and target
        X_df = df[feature_cols].copy()
        y_series = df['Target'].copy()
        
        # Handle missing values by dropping rows with NaN
        initial_rows = len(X_df)
        valid_mask = ~(X_df.isna().any(axis=1) | y_series.isna())
        X_df = X_df[valid_mask]
        y_series = y_series[valid_mask]
        
        dropped_rows = initial_rows - len(X_df)
        if dropped_rows > 0:
            logger.warning(f"Dropped {dropped_rows} rows with missing values")
        
        if len(X_df) < 100:
            raise ValueError(f"Insufficient data after cleaning: {len(X_df)} rows (minimum 100 required)")
        
        # Store feature names
        self.feature_names = feature_cols
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X_df)
        y = y_series.values
        
        logger.info(f"Features prepared: {X_scaled.shape[0]} samples, {X_scaled.shape[1]} features")
        
        return X_scaled, y

    
    def train_test_split(
        self,
        X: np.ndarray,
        y: np.ndarray,
        test_size: float = 0.2
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Split data chronologically for time series (no shuffle).
        
        For time series data, we must maintain temporal order to avoid
        look-ahead bias. The split is done chronologically with the last
        test_size portion used for testing.
        
        Args:
            X: Feature matrix
            y: Target vector
            test_size: Proportion of data for testing (default 0.2 = 80/20 split)
        
        Returns:
            X_train: Training features
            X_test: Testing features
            y_train: Training targets
            y_test: Testing targets
        
        Raises:
            ValueError: If test_size is not between 0 and 1
        """
        if not 0 < test_size < 1:
            raise ValueError(f"test_size must be between 0 and 1, got {test_size}")
        
        n_samples = len(X)
        split_idx = int(n_samples * (1 - test_size))
        
        X_train = X[:split_idx]
        X_test = X[split_idx:]
        y_train = y[:split_idx]
        y_test = y[split_idx:]
        
        logger.info(f"Data split: {len(X_train)} training samples, {len(X_test)} testing samples")
        
        return X_train, X_test, y_train, y_test

    
    def train_models(self, X_train: np.ndarray, y_train: np.ndarray) -> Dict[str, Any]:
        """
        Train all three models on training data.
        
        Trains Logistic Regression, Random Forest, and XGBoost models
        on the provided training data.
        
        Args:
            X_train: Training feature matrix
            y_train: Training target vector
        
        Returns:
            Dictionary with model names as keys and trained model objects as values
        
        Raises:
            ValueError: If training data is insufficient
        """
        if len(X_train) < 100:
            raise ValueError(f"Insufficient training data: {len(X_train)} samples (minimum 100 required)")
        
        logger.info(f"Training {len(self.models)} models on {len(X_train)} samples")
        
        trained_models = {}
        
        for model_name, model in self.models.items():
            logger.info(f"Training {model_name}...")
            try:
                model.fit(X_train, y_train)
                trained_models[model_name] = model
                logger.info(f"{model_name} training complete")
            except Exception as e:
                logger.error(f"Error training {model_name}: {str(e)}")
                raise
        
        logger.info("All models trained successfully")
        return trained_models

    
    def evaluate_model(
        self,
        model: Any,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict[str, Any]:
        """
        Evaluate model performance on test set.
        
        Computes accuracy, precision, recall, F1 score, confusion matrix,
        and classification report for the given model.
        
        Args:
            model: Trained model object
            X_test: Testing feature matrix
            y_test: Testing target vector
        
        Returns:
            Dictionary containing:
            - accuracy: float
            - precision: float
            - recall: float
            - f1_score: float
            - confusion_matrix: numpy array
            - classification_report: string
        """
        logger.info("Evaluating model on test set")
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Compute metrics
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1_score': f1_score(y_test, y_pred, zero_division=0),
            'confusion_matrix': confusion_matrix(y_test, y_pred),
            'classification_report': classification_report(y_test, y_pred, zero_division=0)
        }
        
        logger.info(f"Evaluation complete - Accuracy: {metrics['accuracy']:.4f}, F1: {metrics['f1_score']:.4f}")
        
        return metrics

    
    def save_model(
        self,
        filepath: str = "models/market_prediction_model.pkl",
        metadata: Dict[str, Any] = None
    ) -> None:
        """
        Save the best model and its metadata to disk.
        
        Saves the trained model using joblib and metadata (features,
        performance metrics, hyperparameters) as JSON.
        
        Args:
            filepath: Path to save the model file
            metadata: Optional dictionary with model metadata
        
        Raises:
            ValueError: If no model has been trained
            IOError: If file cannot be written
        """
        if self.best_model is None:
            raise ValueError("No model to save. Train a model first.")
        
        logger.info(f"Saving model to {filepath}")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save model
        try:
            joblib.dump({
                'model': self.best_model,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'model_name': self.best_model_name
            }, filepath)
            logger.info(f"Model saved successfully to {filepath}")
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            raise IOError(f"Failed to save model: {str(e)}")
        
        # Save metadata if provided
        if metadata:
            metadata_path = filepath.replace('.pkl', '_metadata.json')
            try:
                # Convert numpy arrays to lists for JSON serialization
                metadata_serializable = {}
                for key, value in metadata.items():
                    if isinstance(value, np.ndarray):
                        metadata_serializable[key] = value.tolist()
                    elif isinstance(value, (np.integer, np.floating)):
                        metadata_serializable[key] = float(value)
                    else:
                        metadata_serializable[key] = value
                
                with open(metadata_path, 'w') as f:
                    json.dump(metadata_serializable, f, indent=2)
                logger.info(f"Metadata saved to {metadata_path}")
            except Exception as e:
                logger.warning(f"Error saving metadata: {str(e)}")
    
    def load_model(self, filepath: str = "models/market_prediction_model.pkl") -> None:
        """
        Load a trained model from disk.
        
        Args:
            filepath: Path to the saved model file
        
        Raises:
            FileNotFoundError: If model file doesn't exist
            IOError: If file cannot be read
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        logger.info(f"Loading model from {filepath}")
        
        try:
            saved_data = joblib.load(filepath)
            self.best_model = saved_data['model']
            self.scaler = saved_data['scaler']
            self.feature_names = saved_data['feature_names']
            self.best_model_name = saved_data.get('model_name', 'unknown')
            logger.info(f"Model loaded successfully: {self.best_model_name}")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise IOError(f"Failed to load model: {str(e)}")

    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make predictions with probability scores.
        
        Uses the best trained model to make predictions on new data.
        
        Args:
            X: Feature matrix (unscaled)
        
        Returns:
            predictions: Binary predictions (0 or 1)
            probabilities: Probability scores for class 1 (Up direction)
        
        Raises:
            ValueError: If no model has been loaded or trained
        """
        if self.best_model is None:
            raise ValueError("No model available. Train or load a model first.")
        
        logger.info(f"Making predictions for {len(X)} samples")
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Make predictions
        predictions = self.best_model.predict(X_scaled)
        
        # Get probability scores
        if hasattr(self.best_model, 'predict_proba'):
            probabilities = self.best_model.predict_proba(X_scaled)[:, 1]
        else:
            # If model doesn't support predict_proba, use predictions as probabilities
            probabilities = predictions.astype(float)
        
        logger.info("Predictions complete")
        
        return predictions, probabilities



def main():
    """
    Main function to train and evaluate market prediction models.
    
    This script:
    1. Loads processed data
    2. Initializes MarketPredictor
    3. Prepares features and splits data
    4. Trains all models
    5. Evaluates and compares models
    6. Saves the best model
    7. Prints performance metrics
    """
    logger.info("=" * 60)
    logger.info("Starting Market Prediction Model Training")
    logger.info("=" * 60)
    
    # Load processed data
    data_path = "data/processed/merged_data.csv"
    logger.info(f"Loading data from {data_path}")
    
    try:
        df = pd.read_csv(data_path)
        logger.info(f"Data loaded: {len(df)} rows, {len(df.columns)} columns")
    except FileNotFoundError:
        logger.error(f"Data file not found: {data_path}")
        logger.error("Please run the data pipeline first (scripts/run_pipeline.py)")
        return
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        return
    
    # Initialize MarketPredictor
    predictor = MarketPredictor()
    
    # Prepare features
    try:
        X, y = predictor.prepare_features(df)
        logger.info(f"Features prepared: {X.shape}")
        logger.info(f"Target distribution: {np.bincount(y.astype(int))}")
    except Exception as e:
        logger.error(f"Error preparing features: {str(e)}")
        return
    
    # Split data
    X_train, X_test, y_train, y_test = predictor.train_test_split(X, y, test_size=0.2)
    
    # Train all models
    try:
        trained_models = predictor.train_models(X_train, y_train)
    except Exception as e:
        logger.error(f"Error training models: {str(e)}")
        return
    
    # Evaluate and compare models
    logger.info("\n" + "=" * 60)
    logger.info("Model Evaluation Results")
    logger.info("=" * 60)
    
    best_f1 = 0
    best_model_name = None
    all_metrics = {}
    
    for model_name, model in trained_models.items():
        logger.info(f"\nEvaluating {model_name}...")
        metrics = predictor.evaluate_model(model, X_test, y_test)
        all_metrics[model_name] = metrics
        
        logger.info(f"\n{model_name.upper()} Results:")
        logger.info(f"  Accuracy:  {metrics['accuracy']:.4f}")
        logger.info(f"  Precision: {metrics['precision']:.4f}")
        logger.info(f"  Recall:    {metrics['recall']:.4f}")
        logger.info(f"  F1 Score:  {metrics['f1_score']:.4f}")
        logger.info(f"\nConfusion Matrix:")
        logger.info(f"{metrics['confusion_matrix']}")
        
        # Track best model by F1 score
        if metrics['f1_score'] > best_f1:
            best_f1 = metrics['f1_score']
            best_model_name = model_name
    
    # Set best model
    predictor.best_model = trained_models[best_model_name]
    predictor.best_model_name = best_model_name
    
    logger.info("\n" + "=" * 60)
    logger.info(f"Best Model: {best_model_name.upper()} (F1 Score: {best_f1:.4f})")
    logger.info("=" * 60)
    
    # Save best model
    model_path = "models/market_prediction_model.pkl"
    metadata = {
        'model_type': best_model_name,
        'training_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'features': predictor.feature_names,
        'performance': {
            'accuracy': float(all_metrics[best_model_name]['accuracy']),
            'precision': float(all_metrics[best_model_name]['precision']),
            'recall': float(all_metrics[best_model_name]['recall']),
            'f1_score': float(all_metrics[best_model_name]['f1_score'])
        },
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'target_distribution': {
            'class_0': int(np.sum(y == 0)),
            'class_1': int(np.sum(y == 1))
        }
    }
    
    try:
        predictor.save_model(filepath=model_path, metadata=metadata)
        logger.info(f"\nModel saved successfully to {model_path}")
    except Exception as e:
        logger.error(f"Error saving model: {str(e)}")
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("Training Complete!")
    logger.info("=" * 60)
    logger.info(f"Best Model: {best_model_name}")
    logger.info(f"Accuracy: {all_metrics[best_model_name]['accuracy']:.4f}")
    logger.info(f"F1 Score: {all_metrics[best_model_name]['f1_score']:.4f}")
    logger.info(f"Model saved to: {model_path}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
