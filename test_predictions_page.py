"""
Test script to verify the Predictions page can be imported and basic functionality works.
"""

import sys
import os

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

print("Testing Predictions Page Implementation...")
print("=" * 60)

# Test 1: Import the signal generator
print("\n1. Testing signal_generator import...")
try:
    from signal_generator import generate_signal
    print("   ✅ signal_generator imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import signal_generator: {e}")
    sys.exit(1)

# Test 2: Test signal generation with sample data
print("\n2. Testing signal generation...")
try:
    # Test bullish scenario
    result = generate_signal(
        fii_net=1500,
        dii_net=500,
        momentum=75,
        ml_prediction=1,
        ml_probability=0.78
    )
    assert result['signal'] == 'Bullish', f"Expected Bullish, got {result['signal']}"
    assert 0 <= result['confidence'] <= 1, f"Confidence out of range: {result['confidence']}"
    print(f"   ✅ Bullish signal test passed: {result['signal']} with {result['confidence']:.2%} confidence")
    
    # Test bearish scenario
    result = generate_signal(
        fii_net=-1800,
        dii_net=-300,
        momentum=-60,
        ml_prediction=0,
        ml_probability=0.25
    )
    assert result['signal'] == 'Bearish', f"Expected Bearish, got {result['signal']}"
    print(f"   ✅ Bearish signal test passed: {result['signal']} with {result['confidence']:.2%} confidence")
    
    # Test neutral scenario
    result = generate_signal(
        fii_net=500,
        dii_net=-200,
        momentum=-10,
        ml_prediction=1,
        ml_probability=0.55
    )
    assert result['signal'] == 'Neutral', f"Expected Neutral, got {result['signal']}"
    print(f"   ✅ Neutral signal test passed: {result['signal']} with {result['confidence']:.2%} confidence")
    
except Exception as e:
    print(f"   ❌ Signal generation test failed: {e}")
    sys.exit(1)

# Test 3: Check if visualization utilities exist
print("\n3. Testing visualization utilities...")
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard', 'utils'))
    from visualizations import plot_prediction_gauge, plot_feature_importance
    print("   ✅ Visualization utilities imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import visualization utilities: {e}")
    sys.exit(1)

# Test 4: Test prediction gauge creation
print("\n4. Testing prediction gauge creation...")
try:
    fig = plot_prediction_gauge(probability=0.75)
    assert fig is not None, "Figure is None"
    print("   ✅ Prediction gauge created successfully")
except Exception as e:
    print(f"   ❌ Prediction gauge creation failed: {e}")
    sys.exit(1)

# Test 5: Test feature importance chart creation
print("\n5. Testing feature importance chart...")
try:
    feature_names = ['FII_Net', 'DII_Net', 'Momentum', 'Volatility']
    importance_values = [0.3, 0.25, 0.25, 0.2]
    fig = plot_feature_importance(feature_names, importance_values)
    assert fig is not None, "Figure is None"
    print("   ✅ Feature importance chart created successfully")
except Exception as e:
    print(f"   ❌ Feature importance chart creation failed: {e}")
    sys.exit(1)

# Test 6: Check if data loader utilities exist
print("\n6. Testing data loader utilities...")
try:
    from data_loader import load_latest_data, load_model
    print("   ✅ Data loader utilities imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import data loader utilities: {e}")
    sys.exit(1)

# Test 7: Verify the Predictions page file exists
print("\n7. Verifying Predictions page file...")
predictions_page_path = os.path.join(os.path.dirname(__file__), 'dashboard', 'pages', '4_Predictions.py')
if os.path.exists(predictions_page_path):
    print(f"   ✅ Predictions page exists at: {predictions_page_path}")
    
    # Check file size
    file_size = os.path.getsize(predictions_page_path)
    print(f"   ℹ️  File size: {file_size:,} bytes")
    
    # Count lines
    with open(predictions_page_path, 'r', encoding='utf-8') as f:
        line_count = len(f.readlines())
    print(f"   ℹ️  Line count: {line_count:,} lines")
else:
    print(f"   ❌ Predictions page not found at: {predictions_page_path}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All tests passed! Predictions page is ready.")
print("\nTo run the dashboard:")
print("  cd smart-money-intelligence")
print("  streamlit run dashboard/app.py")
print("\nThen navigate to the 'Predictions' page from the sidebar.")
print("=" * 60)
