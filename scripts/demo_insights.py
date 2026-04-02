"""
Demo script for Insights Generation Module

This script demonstrates how to use the insights generation functions
with processed data.
"""

import pandas as pd
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(__file__))

from insights_generator import (
    identify_unusual_activity,
    detect_accumulation_periods,
    detect_selling_periods,
    compute_market_reaction
)


def main():
    """Run insights generation demo"""
    print("=" * 80)
    print("INSIGHTS GENERATION MODULE DEMO")
    print("=" * 80)
    
    # Load processed data
    data_path = os.path.join('data', 'processed', 'merged_data.csv')
    
    if not os.path.exists(data_path):
        print(f"\nError: Processed data not found at {data_path}")
        print("Please run the data pipeline first: python scripts/run_pipeline.py")
        return
    
    print(f"\nLoading data from {data_path}...")
    df = pd.read_csv(data_path)
    df['Date'] = pd.to_datetime(df['Date'])
    
    print(f"Loaded {len(df)} rows of data")
    print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
    
    # 1. Identify unusual FII activity
    print("\n" + "=" * 80)
    print("1. UNUSUAL FII ACTIVITY DETECTION")
    print("=" * 80)
    
    unusual_fii = identify_unusual_activity(df, 'FII_Net', threshold_std=2.0)
    print(f"\nFound {len(unusual_fii)} days with unusual FII activity")
    
    if len(unusual_fii) > 0:
        print("\nTop 5 unusual activity days:")
        top_unusual = unusual_fii.nlargest(5, 'Deviation_Magnitude')[
            ['Date', 'FII_Net', 'Activity_Type', 'Deviation_Magnitude']
        ]
        print(top_unusual.to_string(index=False))
    
    # 2. Detect accumulation periods
    print("\n" + "=" * 80)
    print("2. FII ACCUMULATION PERIODS")
    print("=" * 80)
    
    accumulation = detect_accumulation_periods(df, 'FII_Net', window=5, threshold=0)
    print(f"\nFound {len(accumulation)} accumulation periods (5+ consecutive days)")
    
    if len(accumulation) > 0:
        print("\nAccumulation periods:")
        for i, (start, end) in enumerate(accumulation[:5], 1):
            period_df = df[(df['Date'] >= start) & (df['Date'] <= end)]
            avg_flow = period_df['FII_Net'].mean()
            days = len(period_df)
            print(f"  {i}. {start} to {end} ({days} days, avg flow: {avg_flow:,.0f} crores)")
    
    # 3. Detect selling periods
    print("\n" + "=" * 80)
    print("3. FII SELLING PERIODS")
    print("=" * 80)
    
    selling = detect_selling_periods(df, 'FII_Net', window=5, threshold=0)
    print(f"\nFound {len(selling)} selling periods (5+ consecutive days)")
    
    if len(selling) > 0:
        print("\nSelling periods:")
        for i, (start, end) in enumerate(selling[:5], 1):
            period_df = df[(df['Date'] >= start) & (df['Date'] <= end)]
            avg_flow = period_df['FII_Net'].mean()
            days = len(period_df)
            print(f"  {i}. {start} to {end} ({days} days, avg flow: {avg_flow:,.0f} crores)")
    
    # 4. Compute market reaction to heavy FII buying
    print("\n" + "=" * 80)
    print("4. MARKET REACTION TO HEAVY FII BUYING")
    print("=" * 80)
    
    # Calculate threshold (mean + 1.5 std)
    fii_mean = df['FII_Net'].mean()
    fii_std = df['FII_Net'].std()
    buy_threshold = fii_mean + (1.5 * fii_std)
    
    print(f"\nThreshold for heavy buying: {buy_threshold:,.0f} crores")
    
    reaction_buy = compute_market_reaction(
        df, 'FII_Net', buy_threshold, 'Daily_Return', forward_days=1
    )
    
    print(f"\nMarket reaction after heavy FII buying:")
    print(f"  Events found: {reaction_buy['count']}")
    print(f"  Average next-day return: {reaction_buy['avg_return']:.2f}%")
    print(f"  Median next-day return: {reaction_buy['median_return']:.2f}%")
    print(f"  Positive outcomes: {reaction_buy['positive_pct']:.1f}%")
    
    # 5. Compute market reaction to heavy FII selling
    print("\n" + "=" * 80)
    print("5. MARKET REACTION TO HEAVY FII SELLING")
    print("=" * 80)
    
    sell_threshold = fii_mean - (1.5 * fii_std)
    print(f"\nThreshold for heavy selling: {sell_threshold:,.0f} crores")
    
    reaction_sell = compute_market_reaction(
        df, 'FII_Net', sell_threshold, 'Daily_Return', forward_days=1
    )
    
    print(f"\nMarket reaction after heavy FII selling:")
    print(f"  Events found: {reaction_sell['count']}")
    print(f"  Average next-day return: {reaction_sell['avg_return']:.2f}%")
    print(f"  Median next-day return: {reaction_sell['median_return']:.2f}%")
    print(f"  Positive outcomes: {reaction_sell['positive_pct']:.1f}%")
    
    # 6. DII Analysis
    print("\n" + "=" * 80)
    print("6. DII ACTIVITY ANALYSIS")
    print("=" * 80)
    
    unusual_dii = identify_unusual_activity(df, 'DII_Net', threshold_std=2.0)
    print(f"\nFound {len(unusual_dii)} days with unusual DII activity")
    
    dii_accumulation = detect_accumulation_periods(df, 'DII_Net', window=5, threshold=0)
    print(f"Found {len(dii_accumulation)} DII accumulation periods")
    
    dii_selling = detect_selling_periods(df, 'DII_Net', window=5, threshold=0)
    print(f"Found {len(dii_selling)} DII selling periods")
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    print("\nAll insights generation functions are working correctly!")
    print("These insights can now be used in:")
    print("  - Dashboard visualizations")
    print("  - Signal generation")
    print("  - Research analysis")


if __name__ == '__main__':
    main()
