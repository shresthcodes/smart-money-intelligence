"""
Smart Money Intelligence - Exploratory Data Analysis

This script performs exploratory data analysis on the merged market and institutional data.

Objectives:
1. Load processed data
2. Compute correlations between FII/DII flows and NIFTY returns
3. Calculate rolling correlations over time
4. Generate distribution statistics for returns
5. Create visualizations

Requirements: 4.1, 4.2, 4.5, 4.6, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('husl')

# ============================================================================
# 1. LOAD PROCESSED DATA
# ============================================================================

def load_processed_data(filepath=None):
    """
    Load the processed merged dataset.
    
    Args:
        filepath: Path to the merged data CSV (optional)
    
    Returns:
        DataFrame with processed data
    """
    if filepath is None:
        # Determine path relative to this script
        script_dir = Path(__file__).parent
        filepath = script_dir.parent / 'data' / 'processed' / 'merged_data.csv'
    
    print("Loading processed data...")
    df = pd.read_csv(filepath)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    print(f"Loaded {len(df)} rows of data")
    print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
    return df


# ============================================================================
# 2. CORRELATION ANALYSIS
# ============================================================================

def compute_correlations(df):
    """
    Compute correlations between institutional flows and market returns.
    
    Requirements: 4.1, 4.2
    
    Args:
        df: DataFrame with FII_Net, DII_Net, and Daily_Return columns
    
    Returns:
        Dictionary with correlation results
    """
    print("\n" + "="*60)
    print("CORRELATION ANALYSIS")
    print("="*60)
    
    # Compute Pearson correlations
    fii_nifty_corr = df['FII_Net'].corr(df['Daily_Return'])
    dii_nifty_corr = df['DII_Net'].corr(df['Daily_Return'])
    
    print(f"\nFII Net Flow vs NIFTY Returns: {fii_nifty_corr:.4f}")
    print(f"DII Net Flow vs NIFTY Returns: {dii_nifty_corr:.4f}")
    
    # Compute correlation matrix for key variables
    corr_vars = ['FII_Net', 'DII_Net', 'Daily_Return', 'Volatility', 'Momentum']
    available_vars = [v for v in corr_vars if v in df.columns]
    
    if len(available_vars) > 0:
        corr_matrix = df[available_vars].corr()
        print("\nCorrelation Matrix:")
        print(corr_matrix)
    
    return {
        'fii_nifty_corr': fii_nifty_corr,
        'dii_nifty_corr': dii_nifty_corr,
        'corr_matrix': corr_matrix if len(available_vars) > 0 else None
    }


def compute_rolling_correlations(df, window=60):
    """
    Calculate rolling correlations over time.
    
    Requirements: 4.6
    
    Args:
        df: DataFrame with institutional and market data
        window: Rolling window size in days (default 60 = ~3 months)
    
    Returns:
        DataFrame with rolling correlation columns
    """
    print(f"\nComputing {window}-day rolling correlations...")
    
    df_copy = df.copy()
    
    # Rolling correlation between FII and returns
    df_copy['FII_Return_RollingCorr'] = df_copy['FII_Net'].rolling(window).corr(df_copy['Daily_Return'])
    
    # Rolling correlation between DII and returns
    df_copy['DII_Return_RollingCorr'] = df_copy['DII_Net'].rolling(window).corr(df_copy['Daily_Return'])
    
    print(f"Rolling correlations computed for {window}-day window")
    
    return df_copy


# ============================================================================
# 3. DISTRIBUTION STATISTICS
# ============================================================================

def generate_distribution_statistics(df):
    """
    Generate distribution statistics for market returns.
    
    Requirements: 4.5
    
    Args:
        df: DataFrame with Daily_Return column
    
    Returns:
        Dictionary with distribution statistics
    """
    print("\n" + "="*60)
    print("RETURN DISTRIBUTION STATISTICS")
    print("="*60)
    
    returns = df['Daily_Return'].dropna()
    
    stats = {
        'mean': returns.mean(),
        'median': returns.median(),
        'std': returns.std(),
        'min': returns.min(),
        'max': returns.max(),
        'skewness': returns.skew(),
        'kurtosis': returns.kurtosis(),
        'percentile_5': returns.quantile(0.05),
        'percentile_25': returns.quantile(0.25),
        'percentile_75': returns.quantile(0.75),
        'percentile_95': returns.quantile(0.95)
    }
    
    print(f"\nMean Return: {stats['mean']:.4f}%")
    print(f"Median Return: {stats['median']:.4f}%")
    print(f"Std Deviation: {stats['std']:.4f}%")
    print(f"Min Return: {stats['min']:.4f}%")
    print(f"Max Return: {stats['max']:.4f}%")
    print(f"Skewness: {stats['skewness']:.4f}")
    print(f"Kurtosis: {stats['kurtosis']:.4f}")
    print(f"\nPercentiles:")
    print(f"  5th: {stats['percentile_5']:.4f}%")
    print(f"  25th: {stats['percentile_25']:.4f}%")
    print(f"  75th: {stats['percentile_75']:.4f}%")
    print(f"  95th: {stats['percentile_95']:.4f}%")
    
    # Count positive vs negative days
    positive_days = (returns > 0).sum()
    negative_days = (returns < 0).sum()
    neutral_days = (returns == 0).sum()
    
    print(f"\nMarket Direction:")
    print(f"  Positive days: {positive_days} ({positive_days/len(returns)*100:.2f}%)")
    print(f"  Negative days: {negative_days} ({negative_days/len(returns)*100:.2f}%)")
    print(f"  Neutral days: {neutral_days} ({neutral_days/len(returns)*100:.2f}%)")
    
    return stats


# ============================================================================
# 4. VISUALIZATIONS
# ============================================================================

def create_visualizations(df, df_with_rolling, output_dir=None):
    """
    Create all required visualizations.
    
    Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
    
    Args:
        df: Original DataFrame
        df_with_rolling: DataFrame with rolling correlations
        output_dir: Directory to save figures (optional)
    """
    if output_dir is None:
        # Determine path relative to this script
        script_dir = Path(__file__).parent
        output_dir = script_dir / 'figures'
    
    print("\n" + "="*60)
    print("CREATING VISUALIZATIONS")
    print("="*60)
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 1. FII flows vs NIFTY line chart (Requirement 5.1)
    print("\n1. Creating FII flows vs NIFTY chart...")
    fig, ax1 = plt.subplots(figsize=(14, 6))
    
    ax1.set_xlabel('Date')
    ax1.set_ylabel('NIFTY Close Price', color='tab:blue')
    ax1.plot(df['Date'], df['Close'], color='tab:blue', label='NIFTY Close', linewidth=1.5)
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.legend(loc='upper left')
    
    ax2 = ax1.twinx()
    ax2.set_ylabel('FII Net Flow (Crores)', color='tab:red')
    ax2.plot(df['Date'], df['FII_Net'], color='tab:red', label='FII Net Flow', linewidth=1, alpha=0.7)
    ax2.tick_params(axis='y', labelcolor='tab:red')
    ax2.legend(loc='upper right')
    
    plt.title('FII Flows vs NIFTY Index', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/fii_vs_nifty.png', dpi=300, bbox_inches='tight')
    print(f"   Saved: {output_dir}/fii_vs_nifty.png")
    plt.close()
    
    # 2. DII flows vs NIFTY line chart (Requirement 5.2)
    print("2. Creating DII flows vs NIFTY chart...")
    fig, ax1 = plt.subplots(figsize=(14, 6))
    
    ax1.set_xlabel('Date')
    ax1.set_ylabel('NIFTY Close Price', color='tab:blue')
    ax1.plot(df['Date'], df['Close'], color='tab:blue', label='NIFTY Close', linewidth=1.5)
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.legend(loc='upper left')
    
    ax2 = ax1.twinx()
    ax2.set_ylabel('DII Net Flow (Crores)', color='tab:green')
    ax2.plot(df['Date'], df['DII_Net'], color='tab:green', label='DII Net Flow', linewidth=1, alpha=0.7)
    ax2.tick_params(axis='y', labelcolor='tab:green')
    ax2.legend(loc='upper right')
    
    plt.title('DII Flows vs NIFTY Index', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/dii_vs_nifty.png', dpi=300, bbox_inches='tight')
    print(f"   Saved: {output_dir}/dii_vs_nifty.png")
    plt.close()

    
    # 3. Correlation heatmap (Requirement 5.3)
    print("3. Creating correlation heatmap...")
    corr_vars = ['FII_Net', 'DII_Net', 'Daily_Return', 'Volatility', 'Momentum']
    available_vars = [v for v in corr_vars if v in df.columns]
    
    if len(available_vars) > 2:
        plt.figure(figsize=(10, 8))
        corr_matrix = df[available_vars].corr()
        sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='coolwarm', center=0,
                    square=True, linewidths=1, cbar_kws={"shrink": 0.8})
        plt.title('Correlation Heatmap - Key Variables', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/correlation_heatmap.png', dpi=300, bbox_inches='tight')
        print(f"   Saved: {output_dir}/correlation_heatmap.png")
        plt.close()
    
    # 4. Rolling average flows chart (Requirement 5.4)
    print("4. Creating rolling average flows chart...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # FII rolling averages
    ax1.plot(df['Date'], df['FII_Net'], label='FII Net Flow', alpha=0.3, linewidth=0.5)
    if 'FII_Net_MA5' in df.columns:
        ax1.plot(df['Date'], df['FII_Net_MA5'], label='5-Day MA', linewidth=1.5)
    if 'FII_Net_MA10' in df.columns:
        ax1.plot(df['Date'], df['FII_Net_MA10'], label='10-Day MA', linewidth=1.5)
    if 'FII_Net_MA20' in df.columns:
        ax1.plot(df['Date'], df['FII_Net_MA20'], label='20-Day MA', linewidth=1.5)
    ax1.set_ylabel('FII Net Flow (Crores)')
    ax1.set_title('FII Net Flow - Rolling Averages', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=0, color='black', linestyle='--', linewidth=0.8)
    
    # DII rolling averages
    ax2.plot(df['Date'], df['DII_Net'], label='DII Net Flow', alpha=0.3, linewidth=0.5)
    if 'DII_Net_MA5' in df.columns:
        ax2.plot(df['Date'], df['DII_Net_MA5'], label='5-Day MA', linewidth=1.5)
    if 'DII_Net_MA10' in df.columns:
        ax2.plot(df['Date'], df['DII_Net_MA10'], label='10-Day MA', linewidth=1.5)
    if 'DII_Net_MA20' in df.columns:
        ax2.plot(df['Date'], df['DII_Net_MA20'], label='20-Day MA', linewidth=1.5)
    ax2.set_xlabel('Date')
    ax2.set_ylabel('DII Net Flow (Crores)')
    ax2.set_title('DII Net Flow - Rolling Averages', fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=0, color='black', linestyle='--', linewidth=0.8)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/rolling_average_flows.png', dpi=300, bbox_inches='tight')
    print(f"   Saved: {output_dir}/rolling_average_flows.png")
    plt.close()

    
    # 5. Market return distribution histogram (Requirement 5.5)
    print("5. Creating market return distribution histogram...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    returns = df['Daily_Return'].dropna()
    
    # Histogram
    ax1.hist(returns, bins=50, edgecolor='black', alpha=0.7, color='steelblue')
    ax1.axvline(returns.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {returns.mean():.2f}%')
    ax1.axvline(returns.median(), color='green', linestyle='--', linewidth=2, label=f'Median: {returns.median():.2f}%')
    ax1.set_xlabel('Daily Return (%)')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Distribution of Daily Returns', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Box plot
    ax2.boxplot(returns, vert=True)
    ax2.set_ylabel('Daily Return (%)')
    ax2.set_title('Daily Returns - Box Plot', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/return_distribution.png', dpi=300, bbox_inches='tight')
    print(f"   Saved: {output_dir}/return_distribution.png")
    plt.close()
    
    # 6. Volatility trend chart (Requirement 5.6)
    print("6. Creating volatility trend chart...")
    if 'Volatility' in df.columns:
        fig, ax = plt.subplots(figsize=(14, 6))
        
        ax.plot(df['Date'], df['Volatility'], color='purple', linewidth=1.5)
        ax.fill_between(df['Date'], df['Volatility'], alpha=0.3, color='purple')
        ax.set_xlabel('Date')
        ax.set_ylabel('Volatility (20-day Rolling Std Dev)')
        ax.set_title('Market Volatility Trend', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Add horizontal line for mean volatility
        mean_vol = df['Volatility'].mean()
        ax.axhline(y=mean_vol, color='red', linestyle='--', linewidth=1.5, 
                   label=f'Mean Volatility: {mean_vol:.2f}')
        ax.legend()
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/volatility_trend.png', dpi=300, bbox_inches='tight')
        print(f"   Saved: {output_dir}/volatility_trend.png")
        plt.close()
    
    # 7. Rolling correlations chart (bonus visualization)
    print("7. Creating rolling correlations chart...")
    if 'FII_Return_RollingCorr' in df_with_rolling.columns:
        fig, ax = plt.subplots(figsize=(14, 6))
        
        ax.plot(df_with_rolling['Date'], df_with_rolling['FII_Return_RollingCorr'], 
                label='FII-Return Correlation', linewidth=1.5, color='red')
        ax.plot(df_with_rolling['Date'], df_with_rolling['DII_Return_RollingCorr'], 
                label='DII-Return Correlation', linewidth=1.5, color='green')
        ax.axhline(y=0, color='black', linestyle='--', linewidth=0.8)
        ax.set_xlabel('Date')
        ax.set_ylabel('Rolling Correlation (60-day)')
        ax.set_title('Rolling Correlations: Institutional Flows vs Market Returns', 
                     fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/rolling_correlations.png', dpi=300, bbox_inches='tight')
        print(f"   Saved: {output_dir}/rolling_correlations.png")
        plt.close()
    
    print("\nAll visualizations created successfully!")



# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution function for exploratory data analysis.
    """
    print("="*60)
    print("SMART MONEY INTELLIGENCE - EXPLORATORY DATA ANALYSIS")
    print("="*60)
    
    # Load data
    df = load_processed_data()
    
    # Perform correlation analysis
    corr_results = compute_correlations(df)
    
    # Compute rolling correlations
    df_with_rolling = compute_rolling_correlations(df, window=60)
    
    # Generate distribution statistics
    dist_stats = generate_distribution_statistics(df)
    
    # Create visualizations
    create_visualizations(df, df_with_rolling)
    
    print("\n" + "="*60)
    print("EXPLORATORY DATA ANALYSIS COMPLETE!")
    print("="*60)
    print("\nKey Findings:")
    print(f"1. FII-NIFTY Correlation: {corr_results['fii_nifty_corr']:.4f}")
    print(f"2. DII-NIFTY Correlation: {corr_results['dii_nifty_corr']:.4f}")
    print(f"3. Mean Daily Return: {dist_stats['mean']:.4f}%")
    print(f"4. Return Volatility (Std): {dist_stats['std']:.4f}%")
    print(f"\nAll visualizations saved to: notebooks/figures/")


if __name__ == "__main__":
    main()
