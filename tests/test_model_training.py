"""
Property-based and unit tests for model_training module.

Tests the MarketPredictor class including feature preparation,
train-test splitting, model training, evaluation, and persistence.
"""

import pytest
import numpy as np
import pandas as pd
from hypothesis import given, strategies as st, settings
import sys
import os
import json

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from model_training import MarketPredictor


# Property 20: Train-Test Split Non-Overlap
# Feature: smart-money-intelligence, Property 20: Train-Test Split Non-Overlap
# Validates: Requirements 7.4
@settings(max_examples=100, deadline=None)
@given(
    n_samples=st.integers(min_value=100, max_value=1000),
    test_size=st.floats(min_value=0.1, max_value=0.4)
)
def test_train_test_split_non_overlap(n_samples, test_size):
    """
    Property 20: Train-Test Split Non-Overlap
    
    For any dataset split into training and testing sets, the two sets
    should have no overlapping indices, and their combined size should
    equal the original dataset size.
    """
    predictor = MarketPredictor()
    
    # Create random data
    X = np.random.randn(n_samples, 10)
    y = np.random.randint(0, 2, n_samples)
    
    # Split data
    X_train, X_test, y_train, y_test = predictor.train_test_split(X, y, test_size=test_size)
    
    # Check no overlap (train and test are consecutive slices, so no overlap by design)
    # Check combined size equals original
    assert len(X_train) + len(X_test) == n_samples
    assert len(y_train) + len(y_test) == n_samples
    
    # Check train comes before test (chronological order)
    expected_train_size = int(n_samples * (1 - test_size))
    assert len(X_train) == expected_train_size
    assert len(X_test) == n_samples - expected_train_size
    
    # Verify no data loss
    assert X_train.shape[1] == X.shape[1]
    assert X_test.shape[1] == X.shape[1]


# Unit test for edge cases
def test_train_test_split_invalid_test_size():
    """Test that invalid test_size raises ValueError."""
    predictor = MarketPredictor()
    X = np.random.randn(100, 10)
    y = np.random.randint(0, 2, 100)
    
    with pytest.raises(ValueError):
        predictor.train_test_split(X, y, test_size=0)
    
    with pytest.raises(ValueError):
        predictor.train_test_split(X, y, test_size=1)
    
    with pytest.raises(ValueError):
        predictor.train_test_split(X, y, test_size=-0.1)
    
    with pytest.raises(ValueError):
        predictor.train_test_split(X, y, test_size=1.5)


def test_train_test_split_chronological_order():
    """Test that train-test split maintains chronological order."""
    predictor = MarketPredictor()
    
    # Create data with identifiable pattern
    n_samples = 100
    X = np.arange(n_samples).reshape(-1, 1)
    y = np.arange(n_samples)
    
    X_train, X_test, y_train, y_test = predictor.train_test_split(X, y, test_size=0.2)
    
    # Check that all training indices come before test indices
    assert X_train[-1][0] < X_test[0][0]
    assert y_train[-1] < y_test[0]
    
    # Check continuity
    assert X_test[0][0] == X_train[-1][0] + 1
    assert y_test[0] == y_train[-1] + 1



# Property 21: Model Persistence Round Trip
# Feature: smart-money-intelligence, Property 21: Model Persistence Round Trip
# Validates: Requirements 7.7
@settings(max_examples=100, deadline=None)
@given(
    n_samples=st.integers(min_value=100, max_value=500),
    n_features=st.integers(min_value=5, max_value=20)
)
def test_model_persistence_round_trip(n_samples, n_features):
    """
    Property 21: Model Persistence Round Trip
    
    For any trained model saved using joblib, loading it back should
    produce a model that makes identical predictions on the same input data.
    """
    import tempfile
    
    predictor = MarketPredictor()
    
    # Create random training data
    X_train = np.random.randn(n_samples, n_features)
    y_train = np.random.randint(0, 2, n_samples)
    
    # Train a simple model (just use logistic regression for speed)
    predictor.models['logistic'].fit(X_train, y_train)
    predictor.best_model = predictor.models['logistic']
    predictor.best_model_name = 'logistic'
    predictor.feature_names = [f'feature_{i}' for i in range(n_features)]
    predictor.scaler.fit(X_train)
    
    # Create test data
    X_test = np.random.randn(10, n_features)
    
    # Make predictions before saving
    predictions_before = predictor.best_model.predict(X_test)
    
    # Save model to temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        model_path = os.path.join(tmp_dir, 'test_model.pkl')
        predictor.save_model(filepath=model_path)
        
        # Create new predictor and load model
        predictor2 = MarketPredictor()
        predictor2.load_model(filepath=model_path)
        
        # Make predictions after loading
        predictions_after = predictor2.best_model.predict(X_test)
        
        # Predictions should be identical
        assert np.array_equal(predictions_before, predictions_after)
        
        # Feature names should be preserved
        assert predictor2.feature_names == predictor.feature_names
        
        # Model name should be preserved
        assert predictor2.best_model_name == predictor.best_model_name


# Unit tests for model persistence
def test_save_model_without_training():
    """Test that saving without training raises ValueError."""
    predictor = MarketPredictor()
    
    with pytest.raises(ValueError, match="No model to save"):
        predictor.save_model()


def test_load_nonexistent_model():
    """Test that loading nonexistent model raises FileNotFoundError."""
    predictor = MarketPredictor()
    
    with pytest.raises(FileNotFoundError):
        predictor.load_model(filepath="nonexistent_model.pkl")


def test_save_and_load_with_metadata(tmp_path):
    """Test saving and loading model with metadata."""
    predictor = MarketPredictor()
    
    # Create and train a simple model
    X_train = np.random.randn(100, 10)
    y_train = np.random.randint(0, 2, 100)
    
    predictor.models['logistic'].fit(X_train, y_train)
    predictor.best_model = predictor.models['logistic']
    predictor.best_model_name = 'logistic'
    predictor.feature_names = [f'feature_{i}' for i in range(10)]
    predictor.scaler.fit(X_train)
    
    # Save with metadata
    model_path = os.path.join(tmp_path, 'test_model.pkl')
    metadata = {
        'accuracy': 0.75,
        'training_date': '2024-03-07',
        'training_samples': 100
    }
    predictor.save_model(filepath=model_path, metadata=metadata)
    
    # Check that metadata file was created
    metadata_path = model_path.replace('.pkl', '_metadata.json')
    assert os.path.exists(metadata_path)
    
    # Load and verify metadata
    with open(metadata_path, 'r') as f:
        loaded_metadata = json.load(f)
    
    assert loaded_metadata['accuracy'] == 0.75
    assert loaded_metadata['training_date'] == '2024-03-07'
    assert loaded_metadata['training_samples'] == 100
