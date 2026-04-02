"""
Test script to verify all required packages can be imported.
This ensures the requirements.txt file is complete and correct.
"""

import sys

def test_imports():
    """Test that all required packages can be imported."""
    
    print("Testing package imports...")
    print("=" * 60)
    
    packages = [
        ("pandas", "Data processing"),
        ("numpy", "Numerical computing"),
        ("yfinance", "Market data collection"),
        ("sklearn", "Machine learning"),
        ("xgboost", "XGBoost models"),
        ("joblib", "Model persistence"),
        ("matplotlib", "Plotting"),
        ("seaborn", "Statistical visualization"),
        ("plotly", "Interactive charts"),
        ("streamlit", "Dashboard framework"),
        ("hypothesis", "Property-based testing"),
        ("pytest", "Testing framework"),
        ("sqlalchemy", "Database ORM"),
    ]
    
    failed = []
    
    for package, description in packages:
        try:
            __import__(package)
            print(f"✓ {package:20s} - {description}")
        except ImportError as e:
            print(f"✗ {package:20s} - FAILED: {e}")
            failed.append(package)
    
    print("=" * 60)
    
    if failed:
        print(f"\n❌ {len(failed)} package(s) failed to import: {', '.join(failed)}")
        print("Please install missing packages with: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All required packages imported successfully!")
        print("The environment is ready to run the Smart Money Intelligence Platform.")
        return True


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
