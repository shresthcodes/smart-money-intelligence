"""
Test script to verify Market Overview page functionality
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# Add dashboard to path
sys.path.append('dashboard')

from utils.data_loader import load_latest_data
from utils.visualizations import (
    plot_nifty_trend,
    plot_volatility_trend,
    plot_return_distribution
)

def test_market_overview_page():
    """Test that all components of the Market Overview page work correctly."""
    
    print("Testing Market Overview Page Components...")
    print("=" * 60)
    
    # Test 1: Load data
    print("\n1. Testing data loading...")
    df = load_latest_data()
    
    if df is None or df.empty:
        print("❌ FAILED: Unable to load data")
        return False
    
    print(f"✅ PASSED: Loaded {len(df)} rows of data")
    print(f"   Date range: {df['Date'].min()} to {df['Date'].max()}")
    
    # Test 2: Check required columns
    print("\n2. Testing required columns...")
    required_columns = ['Date', 'Close', 'Volume', 'Daily_Return', 'Volatility']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"❌ FAILED: Missing columns: {missing_columns}")
        return False
    
    print(f"✅ PASSED: All required columns present")
    
    # Test 3: Calculate key statistics
    print("\n3. Testing key statistics calculation...")
    try:
        current_price = df['Close'].iloc[-1]
        previous_price = df['Close'].iloc[0]
        ytd_return = ((current_price - previous_price) / previous_price) * 100
        current_volatility = df['Volatility'].iloc[-1]
        
        print(f"✅ PASSED: Statistics calculated successfully")
        print(f"   Current Price: ₹{current_price:,.2f}")
        print(f"   Period Return: {ytd_return:+.2f}%")
        print(f"   Current Volatility: {current_volatility:.2f}%")
    except Exception as e:
        print(f"❌ FAILED: Error calculating statistics: {e}")
        return False
    
    # Test 4: Test date filtering
    print("\n4. Testing date range filtering...")
    try:
        max_date = df['Date'].max()
        start_date = max_date - timedelta(days=365)
        df_filtered = df[df['Date'] >= start_date].copy()
        
        print(f"✅ PASSED: Date filtering works")
        print(f"   Filtered to {len(df_filtered)} rows (last 1 year)")
    except Exception as e:
        print(f"❌ FAILED: Error filtering dates: {e}")
        return False
    
    # Test 5: Test visualizations
    print("\n5. Testing visualization functions...")
    try:
        # Test NIFTY trend chart
        fig_trend = plot_nifty_trend(df_filtered, 'Date', 'Close', 'Test NIFTY Trend')
        print(f"✅ PASSED: NIFTY trend chart created")
        
        # Test volatility chart
        fig_volatility = plot_volatility_trend(df_filtered, 'Date', 'Volatility', 'Test Volatility')
        print(f"✅ PASSED: Volatility chart created")
        
        # Test return distribution
        fig_distribution = plot_return_distribution(df_filtered, 'Daily_Return', 'Test Distribution')
        print(f"✅ PASSED: Return distribution chart created")
        
    except Exception as e:
        print(f"❌ FAILED: Error creating visualizations: {e}")
        return False
    
    # Test 6: Test return statistics
    print("\n6. Testing return statistics...")
    try:
        returns = df_filtered['Daily_Return'].dropna()
        mean_return = returns.mean()
        median_return = returns.median()
        std_return = returns.std()
        max_return = returns.max()
        min_return = returns.min()
        
        print(f"✅ PASSED: Return statistics calculated")
        print(f"   Mean Return: {mean_return:.2f}%")
        print(f"   Median Return: {median_return:.2f}%")
        print(f"   Std Deviation: {std_return:.2f}%")
        print(f"   Max Return: {max_return:.2f}%")
        print(f"   Min Return: {min_return:.2f}%")
    except Exception as e:
        print(f"❌ FAILED: Error calculating return statistics: {e}")
        return False
    
    # Test 7: Test volatility statistics
    print("\n7. Testing volatility statistics...")
    try:
        avg_volatility = df_filtered['Volatility'].mean()
        max_volatility = df_filtered['Volatility'].max()
        min_volatility = df_filtered['Volatility'].min()
        
        print(f"✅ PASSED: Volatility statistics calculated")
        print(f"   Average Volatility: {avg_volatility:.2f}%")
        print(f"   Max Volatility: {max_volatility:.2f}%")
        print(f"   Min Volatility: {min_volatility:.2f}%")
    except Exception as e:
        print(f"❌ FAILED: Error calculating volatility statistics: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nMarket Overview page is ready to use!")
    print("Run the dashboard with: streamlit run dashboard/app.py")
    
    return True

if __name__ == "__main__":
    success = test_market_overview_page()
    sys.exit(0 if success else 1)
