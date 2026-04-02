"""
Test script for Institutional Activity page

This script verifies that the Institutional Activity page can load data
and perform basic operations without errors.
"""

import sys
import os
import pandas as pd

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from data_loader import load_latest_data
from insights_generator import detect_accumulation_periods, detect_selling_periods

def test_institutional_activity_page():
    """Test the Institutional Activity page functionality"""
    
    print("=" * 60)
    print("Testing Institutional Activity Page")
    print("=" * 60)
    
    # Test 1: Load data
    print("\n1. Testing data loading...")
    df = load_latest_data()
    
    if df is None or df.empty:
        print("❌ FAILED: Unable to load data")
        return False
    
    print(f"✅ PASSED: Loaded {len(df)} rows of data")
    
    # Test 2: Check required columns
    print("\n2. Testing required columns...")
    required_cols = ['Date', 'FII_Net', 'DII_Net']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        print(f"❌ FAILED: Missing columns: {missing_cols}")
        return False
    
    print(f"✅ PASSED: All required columns present")
    
    # Test 3: Ensure Date is datetime
    print("\n3. Testing date conversion...")
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    print(f"✅ PASSED: Date column converted to datetime")
    
    # Test 4: Calculate statistics
    print("\n4. Testing statistics calculation...")
    try:
        total_fii_net = df['FII_Net'].sum()
        total_dii_net = df['DII_Net'].sum()
        avg_fii_net = df['FII_Net'].mean()
        avg_dii_net = df['DII_Net'].mean()
        
        print(f"   Total FII Net: ₹{total_fii_net:,.0f} Cr")
        print(f"   Total DII Net: ₹{total_dii_net:,.0f} Cr")
        print(f"   Avg FII Net: ₹{avg_fii_net:,.0f} Cr")
        print(f"   Avg DII Net: ₹{avg_dii_net:,.0f} Cr")
        print("✅ PASSED: Statistics calculated successfully")
    except Exception as e:
        print(f"❌ FAILED: Error calculating statistics: {e}")
        return False
    
    # Test 5: Detect accumulation periods
    print("\n5. Testing accumulation period detection...")
    try:
        fii_accumulation = detect_accumulation_periods(
            df,
            flow_col='FII_Net',
            window=5,
            threshold=0
        )
        print(f"   Found {len(fii_accumulation)} FII accumulation periods")
        
        dii_accumulation = detect_accumulation_periods(
            df,
            flow_col='DII_Net',
            window=5,
            threshold=0
        )
        print(f"   Found {len(dii_accumulation)} DII accumulation periods")
        print("✅ PASSED: Accumulation periods detected successfully")
    except Exception as e:
        print(f"❌ FAILED: Error detecting accumulation periods: {e}")
        return False
    
    # Test 6: Detect selling periods
    print("\n6. Testing selling period detection...")
    try:
        fii_selling = detect_selling_periods(
            df,
            flow_col='FII_Net',
            window=5,
            threshold=0
        )
        print(f"   Found {len(fii_selling)} FII selling periods")
        
        dii_selling = detect_selling_periods(
            df,
            flow_col='DII_Net',
            window=5,
            threshold=0
        )
        print(f"   Found {len(dii_selling)} DII selling periods")
        print("✅ PASSED: Selling periods detected successfully")
    except Exception as e:
        print(f"❌ FAILED: Error detecting selling periods: {e}")
        return False
    
    # Test 7: Test correlation calculation
    print("\n7. Testing correlation calculation...")
    try:
        if 'Daily_Return' in df.columns:
            fii_return_corr = df['FII_Net'].corr(df['Daily_Return'])
            dii_return_corr = df['DII_Net'].corr(df['Daily_Return'])
            fii_dii_corr = df['FII_Net'].corr(df['DII_Net'])
            
            print(f"   FII vs Returns correlation: {fii_return_corr:.3f}")
            print(f"   DII vs Returns correlation: {dii_return_corr:.3f}")
            print(f"   FII vs DII correlation: {fii_dii_corr:.3f}")
            print("✅ PASSED: Correlations calculated successfully")
        else:
            print("⚠️  WARNING: Daily_Return column not available")
    except Exception as e:
        print(f"❌ FAILED: Error calculating correlations: {e}")
        return False
    
    # Test 8: Test cumulative flows
    print("\n8. Testing cumulative flows calculation...")
    try:
        df_copy = df.copy()
        df_copy['FII_Cumulative'] = df_copy['FII_Net'].cumsum()
        df_copy['DII_Cumulative'] = df_copy['DII_Net'].cumsum()
        
        fii_cum_end = df_copy['FII_Cumulative'].iloc[-1]
        dii_cum_end = df_copy['DII_Cumulative'].iloc[-1]
        
        print(f"   FII Cumulative: ₹{fii_cum_end:,.0f} Cr")
        print(f"   DII Cumulative: ₹{dii_cum_end:,.0f} Cr")
        print("✅ PASSED: Cumulative flows calculated successfully")
    except Exception as e:
        print(f"❌ FAILED: Error calculating cumulative flows: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nThe Institutional Activity page is ready to use.")
    print("Run the dashboard with: streamlit run dashboard/app.py")
    print("Then navigate to the 'Institutional Activity' page.")
    
    return True

if __name__ == "__main__":
    success = test_institutional_activity_page()
    sys.exit(0 if success else 1)
