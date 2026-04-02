"""
Property-Based Tests for Signal Generation Module

This module contains property-based tests using Hypothesis to verify
the correctness of signal generation logic across many random inputs.

Author: Smart Money Intelligence Platform
"""

import pytest
from hypothesis import given, strategies as st, settings
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.signal_generator import generate_signal


# ============================================================================
# Property 22: Signal Classification Completeness
# Validates: Requirements 8.1, 8.2, 8.3, 8.4
# ============================================================================

@given(
    fii_net=st.floats(min_value=-10000, max_value=10000, allow_nan=False, allow_infinity=False),
    dii_net=st.floats(min_value=-10000, max_value=10000, allow_nan=False, allow_infinity=False),
    momentum=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
    ml_prediction=st.integers(min_value=0, max_value=1),
    ml_probability=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, deadline=None)
def test_property_22_signal_classification_completeness(
    fii_net, dii_net, momentum, ml_prediction, ml_probability
):
    """
    Feature: smart-money-intelligence, Property 22: Signal Classification Completeness
    
    For any combination of FII flows, momentum, and ML prediction inputs,
    the signal generation function should return exactly one of:
    "Bullish", "Neutral", or "Bearish".
    
    This property ensures that:
    1. The function always returns a valid signal
    2. The signal is one of the three expected values
    3. No edge cases produce invalid or missing signals
    """
    result = generate_signal(
        fii_net=fii_net,
        dii_net=dii_net,
        momentum=momentum,
        ml_prediction=ml_prediction,
        ml_probability=ml_probability
    )
    
    # Verify result structure
    assert isinstance(result, dict), "Result should be a dictionary"
    assert 'signal' in result, "Result should contain 'signal' key"
    assert 'confidence' in result, "Result should contain 'confidence' key"
    assert 'factors' in result, "Result should contain 'factors' key"
    
    # Property: Signal must be exactly one of the three valid values
    valid_signals = {'Bullish', 'Neutral', 'Bearish'}
    assert result['signal'] in valid_signals, \
        f"Signal must be one of {valid_signals}, got: {result['signal']}"
    
    # Additional checks
    assert isinstance(result['confidence'], (int, float)), \
        "Confidence should be numeric"
    assert 0.0 <= result['confidence'] <= 1.0, \
        f"Confidence should be between 0 and 1, got: {result['confidence']}"
    assert isinstance(result['factors'], dict), \
        "Factors should be a dictionary"


# ============================================================================
# Property 23: Bullish Signal Conditions
# Validates: Requirements 8.1
# ============================================================================

@given(
    fii_net=st.floats(min_value=1001, max_value=10000, allow_nan=False, allow_infinity=False),
    momentum=st.floats(min_value=0.01, max_value=1000, allow_nan=False, allow_infinity=False),
    dii_net=st.floats(min_value=-10000, max_value=10000, allow_nan=False, allow_infinity=False),
    ml_probability=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, deadline=None)
def test_property_23_bullish_signal_conditions(
    fii_net, momentum, dii_net, ml_probability
):
    """
    Feature: smart-money-intelligence, Property 23: Bullish Signal Conditions
    
    For any input where:
    - FII net buying exceeds the threshold (> 1000)
    - AND momentum is positive (> 0)
    - AND ML predicts Up (1)
    
    The generated signal should be "Bullish".
    
    This property validates the core bullish signal logic.
    """
    # Set up conditions for bullish signal
    ml_prediction = 1  # ML predicts Up
    fii_threshold = 1000
    momentum_threshold = 0
    
    result = generate_signal(
        fii_net=fii_net,
        dii_net=dii_net,
        momentum=momentum,
        ml_prediction=ml_prediction,
        ml_probability=ml_probability,
        fii_threshold=fii_threshold,
        momentum_threshold=momentum_threshold
    )
    
    # Property: When all bullish conditions are met, signal must be Bullish
    assert result['signal'] == 'Bullish', \
        f"Expected 'Bullish' signal when FII_Net={fii_net} > {fii_threshold}, " \
        f"momentum={momentum} > {momentum_threshold}, and ML predicts Up. " \
        f"Got: {result['signal']}"
    
    # Additional validation: confidence should be reasonable
    assert result['confidence'] > 0, \
        "Bullish signal should have positive confidence"
    
    # Verify factors are recorded
    assert result['factors']['fii_net'] == fii_net
    assert result['factors']['momentum'] == momentum
    assert result['factors']['ml_prediction'] == 'Up'


# ============================================================================
# Property 24: Bearish Signal Conditions
# Validates: Requirements 8.2
# ============================================================================

@given(
    fii_net=st.floats(min_value=-10000, max_value=-1001, allow_nan=False, allow_infinity=False),
    momentum=st.floats(min_value=-1000, max_value=-0.01, allow_nan=False, allow_infinity=False),
    dii_net=st.floats(min_value=-10000, max_value=10000, allow_nan=False, allow_infinity=False),
    ml_probability=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, deadline=None)
def test_property_24_bearish_signal_conditions(
    fii_net, momentum, dii_net, ml_probability
):
    """
    Feature: smart-money-intelligence, Property 24: Bearish Signal Conditions
    
    For any input where:
    - FII net selling exceeds the threshold (< -1000)
    - AND momentum is negative (< 0)
    - AND ML predicts Down (0)
    
    The generated signal should be "Bearish".
    
    This property validates the core bearish signal logic.
    """
    # Set up conditions for bearish signal
    ml_prediction = 0  # ML predicts Down
    fii_threshold = 1000
    momentum_threshold = 0
    
    result = generate_signal(
        fii_net=fii_net,
        dii_net=dii_net,
        momentum=momentum,
        ml_prediction=ml_prediction,
        ml_probability=ml_probability,
        fii_threshold=fii_threshold,
        momentum_threshold=momentum_threshold
    )
    
    # Property: When all bearish conditions are met, signal must be Bearish
    assert result['signal'] == 'Bearish', \
        f"Expected 'Bearish' signal when FII_Net={fii_net} < -{fii_threshold}, " \
        f"momentum={momentum} < {momentum_threshold}, and ML predicts Down. " \
        f"Got: {result['signal']}"
    
    # Additional validation: confidence should be reasonable
    assert result['confidence'] > 0, \
        "Bearish signal should have positive confidence"
    
    # Verify factors are recorded
    assert result['factors']['fii_net'] == fii_net
    assert result['factors']['momentum'] == momentum
    assert result['factors']['ml_prediction'] == 'Down'


# ============================================================================
# Additional Property Tests for Edge Cases and Robustness
# ============================================================================

@given(
    fii_net=st.floats(min_value=-10000, max_value=10000, allow_nan=False, allow_infinity=False),
    dii_net=st.floats(min_value=-10000, max_value=10000, allow_nan=False, allow_infinity=False),
    momentum=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
    ml_prediction=st.integers(min_value=0, max_value=1),
    ml_probability=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, deadline=None)
def test_confidence_bounds(fii_net, dii_net, momentum, ml_prediction, ml_probability):
    """
    Property: Confidence Score Bounds
    
    For any valid inputs, the confidence score should always be between 0 and 1.
    """
    result = generate_signal(
        fii_net=fii_net,
        dii_net=dii_net,
        momentum=momentum,
        ml_prediction=ml_prediction,
        ml_probability=ml_probability
    )
    
    assert 0.0 <= result['confidence'] <= 1.0, \
        f"Confidence must be between 0 and 1, got: {result['confidence']}"


@given(
    fii_net=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
    momentum=st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
    ml_prediction=st.integers(min_value=0, max_value=1),
    ml_probability=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, deadline=None)
def test_neutral_signal_for_weak_conditions(
    fii_net, momentum, ml_prediction, ml_probability
):
    """
    Property: Neutral Signal for Weak Conditions
    
    When FII flows are below threshold (between -1000 and 1000),
    the signal should be Neutral regardless of other factors,
    since the conditions for Bullish or Bearish are not met.
    """
    result = generate_signal(
        fii_net=fii_net,
        dii_net=0,
        momentum=momentum,
        ml_prediction=ml_prediction,
        ml_probability=ml_probability,
        fii_threshold=1000
    )
    
    # When FII is weak, signal should be Neutral
    assert result['signal'] == 'Neutral', \
        f"Expected 'Neutral' signal when FII_Net={fii_net} is below threshold. " \
        f"Got: {result['signal']}"


@given(
    ml_probability=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100, deadline=None)
def test_factors_dictionary_completeness(ml_probability):
    """
    Property: Factors Dictionary Completeness
    
    For any inputs, the factors dictionary should contain all expected keys.
    """
    result = generate_signal(
        fii_net=1500,
        dii_net=500,
        momentum=50,
        ml_prediction=1,
        ml_probability=ml_probability
    )
    
    expected_keys = {
        'fii_net', 'dii_net', 'momentum', 'ml_prediction',
        'ml_probability', 'fii_threshold', 'momentum_threshold',
        'signal_reason'
    }
    
    actual_keys = set(result['factors'].keys())
    
    # Check that all expected keys are present
    assert expected_keys.issubset(actual_keys), \
        f"Missing keys in factors: {expected_keys - actual_keys}"


# ============================================================================
# Unit Tests for Specific Examples
# ============================================================================

def test_example_bullish_signal():
    """
    Unit test: Specific example of bullish signal
    """
    result = generate_signal(
        fii_net=1500,
        dii_net=500,
        momentum=75,
        ml_prediction=1,
        ml_probability=0.78
    )
    
    assert result['signal'] == 'Bullish'
    assert result['confidence'] > 0.5
    assert 'Bullish' in result['factors']['signal_reason'] or \
           'buying' in result['factors']['signal_reason'].lower()


def test_example_bearish_signal():
    """
    Unit test: Specific example of bearish signal
    """
    result = generate_signal(
        fii_net=-1800,
        dii_net=-300,
        momentum=-60,
        ml_prediction=0,
        ml_probability=0.25
    )
    
    assert result['signal'] == 'Bearish'
    assert result['confidence'] > 0.5
    assert 'Bearish' in result['factors']['signal_reason'] or \
           'selling' in result['factors']['signal_reason'].lower()


def test_example_neutral_signal_mixed():
    """
    Unit test: Specific example of neutral signal with mixed conditions
    """
    result = generate_signal(
        fii_net=500,
        dii_net=-200,
        momentum=-10,
        ml_prediction=1,
        ml_probability=0.55
    )
    
    assert result['signal'] == 'Neutral'
    assert 'Mixed' in result['factors']['signal_reason'] or \
           'Neutral' in result['signal']


def test_example_neutral_signal_conflicting():
    """
    Unit test: Specific example of neutral signal with conflicting signals
    """
    result = generate_signal(
        fii_net=1200,
        dii_net=400,
        momentum=50,
        ml_prediction=0,  # ML predicts Down despite positive indicators
        ml_probability=0.35
    )
    
    assert result['signal'] == 'Neutral'


def test_custom_thresholds():
    """
    Unit test: Verify custom thresholds work correctly
    """
    # With default threshold (1000), this should be Neutral
    result1 = generate_signal(
        fii_net=800,
        dii_net=200,
        momentum=50,
        ml_prediction=1,
        ml_probability=0.75,
        fii_threshold=1000
    )
    assert result1['signal'] == 'Neutral'
    
    # With lower threshold (500), this should be Bullish
    result2 = generate_signal(
        fii_net=800,
        dii_net=200,
        momentum=50,
        ml_prediction=1,
        ml_probability=0.75,
        fii_threshold=500
    )
    assert result2['signal'] == 'Bullish'


def test_zero_values():
    """
    Unit test: Handle zero values correctly
    """
    result = generate_signal(
        fii_net=0,
        dii_net=0,
        momentum=0,
        ml_prediction=1,
        ml_probability=0.5
    )
    
    assert result['signal'] == 'Neutral'
    assert 0.0 <= result['confidence'] <= 1.0


def test_extreme_values():
    """
    Unit test: Handle extreme values correctly
    """
    result = generate_signal(
        fii_net=10000,
        dii_net=5000,
        momentum=1000,
        ml_prediction=1,
        ml_probability=0.99
    )
    
    assert result['signal'] == 'Bullish'
    assert result['confidence'] > 0.8  # Should have high confidence


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
