"""
Verification script to ensure the Smart Money Intelligence Platform is ready to run.

This script checks:
1. All required data files exist
2. Model files exist
3. Data can be loaded
4. Model can be loaded
5. Dashboard utilities work
"""

import os
import sys
import pandas as pd
import joblib
import json

def check_file_exists(filepath, description):
    """Check if a file exists and print status."""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description} NOT FOUND: {filepath}")
        return False

def main():
    print("=" * 80)
    print("SMART MONEY INTELLIGENCE PLATFORM - SETUP VERIFICATION")
    print("=" * 80)
    
    all_checks_passed = True
    
    # Check 1: Data files
    print("\n[1/5] Checking data files...")
    data_files = [
        ("data/raw/nifty_data.csv", "Raw NIFTY data"),
        ("data/raw/fii_dii_data.csv", "Raw FII/DII data"),
        ("data/processed/merged_data.csv", "Processed merged data")
    ]
    
    for filepath, description in data_files:
        if not check_file_exists(filepath, description):
            all_checks_passed = False
    
    # Check 2: Model files
    print("\n[2/5] Checking model files...")
    model_files = [
        ("models/market_prediction_model.pkl", "Trained model"),
        ("models/market_prediction_model_metadata.json", "Model metadata")
    ]
    
    for filepath, description in model_files:
        if not check_file_exists(filepath, description):
            all_checks_passed = False
    
    # Check 3: Load and validate data
    print("\n[3/5] Loading and validating data...")
    try:
        df = pd.read_csv("data/processed/merged_data.csv")
        print(f"✓ Loaded {len(df)} rows of processed data")
        print(f"  Date range: {df['Date'].min()} to {df['Date'].max()}")
        print(f"  Features: {len(df.columns)} columns")
        
        # Check for required columns
        required_cols = ['Date', 'Close', 'FII_Net', 'DII_Net', 'Target']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"✗ Missing required columns: {missing_cols}")
            all_checks_passed = False
        else:
            print(f"✓ All required columns present")
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        all_checks_passed = False
    
    # Check 4: Load and validate model
    print("\n[4/5] Loading and validating model...")
    try:
        model_data = joblib.load("models/market_prediction_model.pkl")
        print(f"✓ Model loaded successfully")
        print(f"  Model type: {model_data.get('model_name', 'Unknown')}")
        print(f"  Features: {len(model_data.get('feature_names', []))} features")
        
        # Load metadata
        with open("models/market_prediction_model_metadata.json", 'r') as f:
            metadata = json.load(f)
        print(f"✓ Metadata loaded successfully")
        print(f"  Training date: {metadata.get('training_date', 'Unknown')}")
        print(f"  Accuracy: {metadata.get('performance', {}).get('accuracy', 0):.4f}")
        print(f"  F1 Score: {metadata.get('performance', {}).get('f1_score', 0):.4f}")
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        all_checks_passed = False
    
    # Check 5: Test dashboard utilities
    print("\n[5/5] Testing dashboard utilities...")
    try:
        sys.path.insert(0, 'dashboard')
        # Just import to verify no syntax errors
        from utils import data_loader, visualizations
        print("✓ Dashboard utilities can be imported")
    except Exception as e:
        print(f"✗ Error importing dashboard utilities: {e}")
        all_checks_passed = False
    
    # Final summary
    print("\n" + "=" * 80)
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED!")
        print("\nThe Smart Money Intelligence Platform is ready to use.")
        print("\nNext steps:")
        print("  1. Run the dashboard: streamlit run dashboard/app.py")
        print("  2. Run tests: pytest tests/ -v")
        print("  3. Explore notebooks: jupyter notebook notebooks/")
    else:
        print("❌ SOME CHECKS FAILED!")
        print("\nPlease fix the issues above before running the platform.")
        print("\nTo regenerate all data and models, run:")
        print("  python scripts/generate_sample_data.py")
    print("=" * 80)
    
    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    sys.exit(main())
