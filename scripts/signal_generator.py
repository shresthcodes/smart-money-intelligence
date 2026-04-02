"""
Signal Generation Module

This module generates trading signals based on institutional flows, momentum,
and machine learning predictions. It combines rule-based logic with ML outputs
to provide actionable trading recommendations.

Author: Smart Money Intelligence Platform
"""

from typing import Dict, Any


def generate_signal(
    fii_net: float,
    dii_net: float,
    momentum: float,
    ml_prediction: int,
    ml_probability: float,
    fii_threshold: float = 1000,  # in crores
    momentum_threshold: float = 0
) -> Dict[str, Any]:
    """
    Generate trading signal based on multiple factors.
    
    This function implements a rule-based system that combines:
    1. FII (Foreign Institutional Investor) net flows
    2. Market momentum indicators
    3. Machine learning predictions
    
    Signal Rules:
    - Bullish: FII_Net > threshold AND momentum > 0 AND ML predicts Up (1)
    - Bearish: FII_Net < -threshold AND momentum < 0 AND ML predicts Down (0)
    - Neutral: All other conditions
    
    Args:
        fii_net: Net FII flow in crores (positive = buying, negative = selling)
        dii_net: Net DII flow in crores (positive = buying, negative = selling)
        momentum: Market momentum indicator (positive = upward, negative = downward)
        ml_prediction: ML model prediction (0 = Down, 1 = Up)
        ml_probability: ML prediction probability (0.0 to 1.0)
        fii_threshold: Threshold for significant FII activity (default: 1000 crores)
        momentum_threshold: Threshold for momentum (default: 0)
    
    Returns:
        Dictionary containing:
        {
            'signal': str ('Bullish', 'Neutral', 'Bearish'),
            'confidence': float (0.0 to 1.0),
            'factors': Dict with contributing factors and their values
        }
    
    Raises:
        TypeError: If any required numeric parameter is None
        ValueError: If ml_prediction is not 0 or 1, or ml_probability is not in [0, 1]
    
    Examples:
        >>> generate_signal(1500, 500, 50, 1, 0.75)
        {'signal': 'Bullish', 'confidence': 0.75, 'factors': {...}}
        
        >>> generate_signal(-1500, -200, -30, 0, 0.80)
        {'signal': 'Bearish', 'confidence': 0.80, 'factors': {...}}
        
        >>> generate_signal(500, 300, -10, 1, 0.55)
        {'signal': 'Neutral', 'confidence': 0.55, 'factors': {...}}
    """
    # Validate inputs
    if fii_net is None:
        raise TypeError("fii_net cannot be None")
    if dii_net is None:
        raise TypeError("dii_net cannot be None")
    if momentum is None:
        raise TypeError("momentum cannot be None")
    if ml_prediction is None:
        raise TypeError("ml_prediction cannot be None")
    if ml_probability is None:
        raise TypeError("ml_probability cannot be None")
    
    # Validate ml_prediction is binary
    if ml_prediction not in [0, 1]:
        raise ValueError(f"ml_prediction must be 0 or 1, got {ml_prediction}")
    
    # Validate ml_probability is in valid range
    if not (0 <= ml_probability <= 1):
        raise ValueError(f"ml_probability must be between 0 and 1, got {ml_probability}")
    
    # Initialize factors dictionary to track contributing factors
    factors = {
        'fii_net': fii_net,
        'dii_net': dii_net,
        'momentum': momentum,
        'ml_prediction': 'Up' if ml_prediction == 1 else 'Down',
        'ml_probability': ml_probability,
        'fii_threshold': fii_threshold,
        'momentum_threshold': momentum_threshold
    }
    
    # Determine signal based on rules
    signal = 'Neutral'  # Default signal
    confidence = ml_probability  # Base confidence on ML probability
    
    # Rule 1: Bullish Signal
    # Conditions: Strong FII buying AND positive momentum AND ML predicts Up
    if (fii_net > fii_threshold and 
        momentum > momentum_threshold and 
        ml_prediction == 1):
        signal = 'Bullish'
        
        # Calculate confidence based on strength of signals
        # Higher FII flows and momentum increase confidence
        fii_strength = min(fii_net / (fii_threshold * 2), 1.0)  # Normalize to 0-1
        momentum_strength = min(abs(momentum) / 100, 1.0)  # Normalize to 0-1
        
        # Weighted average: ML probability (50%), FII strength (30%), momentum (20%)
        confidence = (ml_probability * 0.5 + 
                     fii_strength * 0.3 + 
                     momentum_strength * 0.2)
        
        factors['signal_reason'] = 'Strong FII buying with positive momentum and ML confirmation'
        factors['fii_strength'] = fii_strength
        factors['momentum_strength'] = momentum_strength
    
    # Rule 2: Bearish Signal
    # Conditions: Strong FII selling AND negative momentum AND ML predicts Down
    elif (fii_net < -fii_threshold and 
          momentum < momentum_threshold and 
          ml_prediction == 0):
        signal = 'Bearish'
        
        # Calculate confidence based on strength of signals
        fii_strength = min(abs(fii_net) / (fii_threshold * 2), 1.0)  # Normalize to 0-1
        momentum_strength = min(abs(momentum) / 100, 1.0)  # Normalize to 0-1
        
        # Weighted average: ML probability (50%), FII strength (30%), momentum (20%)
        # For bearish, use (1 - ml_probability) since ml_probability is for "Up"
        confidence = ((1 - ml_probability) * 0.5 + 
                     fii_strength * 0.3 + 
                     momentum_strength * 0.2)
        
        factors['signal_reason'] = 'Strong FII selling with negative momentum and ML confirmation'
        factors['fii_strength'] = fii_strength
        factors['momentum_strength'] = momentum_strength
    
    # Rule 3: Neutral Signal (default)
    else:
        signal = 'Neutral'
        factors['signal_reason'] = 'Mixed signals or insufficient conviction'
        
        # For neutral, confidence represents uncertainty
        # Lower confidence when signals are conflicting
        if ml_prediction == 1:
            confidence = ml_probability
        else:
            confidence = 1 - ml_probability
    
    # Ensure confidence is bounded between 0 and 1
    confidence = max(0.0, min(1.0, confidence))
    
    return {
        'signal': signal,
        'confidence': round(confidence, 4),
        'factors': factors
    }


def generate_signal_with_context(
    latest_data: Dict[str, float],
    ml_model,
    feature_columns: list
) -> Dict[str, Any]:
    """
    Generate signal using latest market data and trained ML model.
    
    This is a convenience function that extracts necessary features from
    a data dictionary and calls generate_signal().
    
    Args:
        latest_data: Dictionary with latest market data including:
                    - FII_Net, DII_Net, Momentum, and other features
        ml_model: Trained ML model with predict() and predict_proba() methods
        feature_columns: List of feature column names expected by the model
    
    Returns:
        Dictionary with signal, confidence, and factors
    
    Raises:
        KeyError: If required features are missing from latest_data
        ValueError: If model prediction fails
    """
    import numpy as np
    
    # Extract features for ML prediction
    try:
        features = np.array([[latest_data[col] for col in feature_columns]])
    except KeyError as e:
        raise KeyError(f"Missing required feature in latest_data: {e}")
    
    # Get ML prediction and probability
    try:
        ml_prediction = ml_model.predict(features)[0]
        ml_probabilities = ml_model.predict_proba(features)[0]
        ml_probability = ml_probabilities[1]  # Probability of class 1 (Up)
    except Exception as e:
        raise ValueError(f"Model prediction failed: {e}")
    
    # Extract required values for signal generation
    fii_net = latest_data.get('FII_Net', 0)
    dii_net = latest_data.get('DII_Net', 0)
    momentum = latest_data.get('Momentum', 0)
    
    # Generate signal
    return generate_signal(
        fii_net=fii_net,
        dii_net=dii_net,
        momentum=momentum,
        ml_prediction=int(ml_prediction),
        ml_probability=float(ml_probability)
    )


if __name__ == "__main__":
    # Example usage and testing
    print("Signal Generator Module - Example Usage\n")
    print("=" * 60)
    
    # Example 1: Bullish scenario
    print("\nExample 1: Bullish Scenario")
    print("-" * 60)
    result = generate_signal(
        fii_net=1500,      # Strong buying
        dii_net=500,       # Supporting buying
        momentum=75,       # Positive momentum
        ml_prediction=1,   # ML predicts Up
        ml_probability=0.78
    )
    print(f"Signal: {result['signal']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Reason: {result['factors']['signal_reason']}")
    
    # Example 2: Bearish scenario
    print("\nExample 2: Bearish Scenario")
    print("-" * 60)
    result = generate_signal(
        fii_net=-1800,     # Strong selling
        dii_net=-300,      # Supporting selling
        momentum=-60,      # Negative momentum
        ml_prediction=0,   # ML predicts Down
        ml_probability=0.25  # Low probability of Up = High probability of Down
    )
    print(f"Signal: {result['signal']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Reason: {result['factors']['signal_reason']}")
    
    # Example 3: Neutral scenario (mixed signals)
    print("\nExample 3: Neutral Scenario (Mixed Signals)")
    print("-" * 60)
    result = generate_signal(
        fii_net=500,       # Moderate buying (below threshold)
        dii_net=-200,      # DII selling
        momentum=-10,      # Slight negative momentum
        ml_prediction=1,   # ML predicts Up
        ml_probability=0.55
    )
    print(f"Signal: {result['signal']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Reason: {result['factors']['signal_reason']}")
    
    # Example 4: Neutral scenario (conflicting signals)
    print("\nExample 4: Neutral Scenario (Conflicting Signals)")
    print("-" * 60)
    result = generate_signal(
        fii_net=1200,      # Strong buying
        dii_net=400,       # Supporting buying
        momentum=50,       # Positive momentum
        ml_prediction=0,   # But ML predicts Down (conflict!)
        ml_probability=0.35
    )
    print(f"Signal: {result['signal']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Reason: {result['factors']['signal_reason']}")
    
    print("\n" + "=" * 60)
    print("Signal generation examples complete!")
