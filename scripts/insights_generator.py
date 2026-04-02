"""
Insights Generation Module

This module provides functions to generate actionable insights from market and
institutional data, including unusual activity detection, accumulation/selling
period identification, and market reaction analysis.
"""

import pandas as pd
import numpy as np
import logging
from typing import List, Tuple, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def identify_unusual_activity(
    df: pd.DataFrame,
    column: str,
    threshold_std: float = 2.0
) -> pd.DataFrame:
    """
    Identify days with unusual institutional activity.
    
    Args:
        df: DataFrame with institutional data
        column: Column to analyze (e.g., 'FII_Net')
        threshold_std: Number of standard deviations for threshold
    
    Returns:
        DataFrame with rows where activity exceeds threshold
        
    Raises:
        ValueError: If column is missing from DataFrame
    """
    logger.info(f"Identifying unusual activity in {column} column with threshold {threshold_std} std dev...")
    
    # Validate column exists
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame")
    
    # Calculate mean and standard deviation
    mean_value = df[column].mean()
    std_value = df[column].std()
    
    logger.info(f"Column statistics - Mean: {mean_value:.2f}, Std Dev: {std_value:.2f}")
    
    # Calculate thresholds
    upper_threshold = mean_value + (threshold_std * std_value)
    lower_threshold = mean_value - (threshold_std * std_value)
    
    logger.info(f"Thresholds - Upper: {upper_threshold:.2f}, Lower: {lower_threshold:.2f}")
    
    # Identify unusual activity days
    unusual_activity = df[
        (df[column] > upper_threshold) | (df[column] < lower_threshold)
    ].copy()
    
    # Add a column indicating the type of unusual activity
    unusual_activity['Activity_Type'] = unusual_activity[column].apply(
        lambda x: 'High_Buying' if x > upper_threshold else 'High_Selling'
    )
    
    # Add deviation magnitude
    unusual_activity['Deviation_Magnitude'] = unusual_activity[column].apply(
        lambda x: abs(x - mean_value) / std_value
    )
    
    logger.info(f"Found {len(unusual_activity)} days with unusual activity")
    
    return unusual_activity


def detect_accumulation_periods(
    df: pd.DataFrame,
    flow_col: str = "FII_Net",
    window: int = 5,
    threshold: float = 0
) -> List[Tuple[str, str]]:
    """
    Detect periods of sustained institutional accumulation.
    
    Accumulation = consecutive days with positive net flows
    
    Args:
        df: DataFrame with institutional data
        flow_col: Column representing net flows
        window: Minimum consecutive days
        threshold: Minimum average flow during period
    
    Returns:
        List of (start_date, end_date) tuples for accumulation periods
        
    Raises:
        ValueError: If flow column or Date column is missing, or if window is invalid
    """
    logger.info(f"Detecting accumulation periods in {flow_col} with window={window}, threshold={threshold}...")
    
    # Validate window parameter
    if window <= 0:
        raise ValueError(f"Window must be positive, got {window}")
    
    # Validate columns exist
    if flow_col not in df.columns:
        raise ValueError(f"Flow column '{flow_col}' not found in DataFrame")
    if 'Date' not in df.columns:
        raise ValueError("'Date' column not found in DataFrame")
    
    # Create a copy and ensure Date is datetime
    df_work = df.copy()
    df_work['Date'] = pd.to_datetime(df_work['Date'])
    
    # Identify positive flow days
    df_work['is_positive'] = df_work[flow_col] > 0
    
    # Find consecutive positive periods
    df_work['group'] = (df_work['is_positive'] != df_work['is_positive'].shift()).cumsum()
    
    accumulation_periods = []
    
    # Group by consecutive positive periods
    for group_id, group_df in df_work[df_work['is_positive']].groupby('group'):
        # Check if period meets minimum window size
        if len(group_df) >= window:
            # Check if average flow meets threshold
            avg_flow = group_df[flow_col].mean()
            if avg_flow >= threshold:
                start_date = group_df['Date'].iloc[0].strftime('%Y-%m-%d')
                end_date = group_df['Date'].iloc[-1].strftime('%Y-%m-%d')
                accumulation_periods.append((start_date, end_date))
                logger.info(f"Accumulation period: {start_date} to {end_date} (avg flow: {avg_flow:.2f})")
    
    logger.info(f"Found {len(accumulation_periods)} accumulation periods")
    return accumulation_periods


def detect_selling_periods(
    df: pd.DataFrame,
    flow_col: str = "FII_Net",
    window: int = 5,
    threshold: float = 0
) -> List[Tuple[str, str]]:
    """
    Detect periods of sustained institutional selling.
    
    Selling = consecutive days with negative net flows
    
    Args:
        df: DataFrame with institutional data
        flow_col: Column representing net flows
        window: Minimum consecutive days
        threshold: Maximum average flow during period (should be negative)
    
    Returns:
        List of (start_date, end_date) tuples for selling periods
        
    Raises:
        ValueError: If flow column or Date column is missing, or if window is invalid
    """
    logger.info(f"Detecting selling periods in {flow_col} with window={window}, threshold={threshold}...")
    
    # Validate window parameter
    if window <= 0:
        raise ValueError(f"Window must be positive, got {window}")
    
    # Validate columns exist
    if flow_col not in df.columns:
        raise ValueError(f"Flow column '{flow_col}' not found in DataFrame")
    if 'Date' not in df.columns:
        raise ValueError("'Date' column not found in DataFrame")
    
    # Create a copy and ensure Date is datetime
    df_work = df.copy()
    df_work['Date'] = pd.to_datetime(df_work['Date'])
    
    # Identify negative flow days
    df_work['is_negative'] = df_work[flow_col] < 0
    
    # Find consecutive negative periods
    df_work['group'] = (df_work['is_negative'] != df_work['is_negative'].shift()).cumsum()
    
    selling_periods = []
    
    # Group by consecutive negative periods
    for group_id, group_df in df_work[df_work['is_negative']].groupby('group'):
        # Check if period meets minimum window size
        if len(group_df) >= window:
            # Check if average flow meets threshold (more negative than threshold)
            avg_flow = group_df[flow_col].mean()
            if avg_flow <= threshold:
                start_date = group_df['Date'].iloc[0].strftime('%Y-%m-%d')
                end_date = group_df['Date'].iloc[-1].strftime('%Y-%m-%d')
                selling_periods.append((start_date, end_date))
                logger.info(f"Selling period: {start_date} to {end_date} (avg flow: {avg_flow:.2f})")
    
    logger.info(f"Found {len(selling_periods)} selling periods")
    return selling_periods


def compute_market_reaction(
    df: pd.DataFrame,
    event_col: str,
    event_threshold: float,
    return_col: str = "Daily_Return",
    forward_days: int = 1
) -> Dict[str, float]:
    """
    Compute average market reaction after specific events.
    
    Args:
        df: DataFrame with event and return data
        event_col: Column representing event (e.g., 'FII_Net')
        event_threshold: Threshold for event occurrence
        return_col: Column with market returns
        forward_days: Days forward to measure reaction
    
    Returns:
        Dictionary with statistics:
        {
            'avg_return': float,
            'median_return': float,
            'count': int,
            'positive_pct': float
        }
        
    Raises:
        ValueError: If required columns are missing
    """
    logger.info(f"Computing market reaction after {event_col} exceeds {event_threshold}...")
    
    # Validate columns exist
    if event_col not in df.columns:
        raise ValueError(f"Event column '{event_col}' not found in DataFrame")
    if return_col not in df.columns:
        raise ValueError(f"Return column '{return_col}' not found in DataFrame")
    
    # Create a copy
    df_work = df.copy()
    
    # Identify events based on threshold
    # For positive threshold, look for values above it
    # For negative threshold, look for values below it
    if event_threshold >= 0:
        event_mask = df_work[event_col] > event_threshold
    else:
        event_mask = df_work[event_col] < event_threshold
    
    # Get forward returns for event days
    df_work['forward_return'] = df_work[return_col].shift(-forward_days)
    
    # Filter to event days and get forward returns
    event_returns = df_work[event_mask]['forward_return'].dropna()
    
    if len(event_returns) == 0:
        logger.warning("No events found matching the threshold")
        return {
            'avg_return': 0.0,
            'median_return': 0.0,
            'count': 0,
            'positive_pct': 0.0
        }
    
    # Compute statistics
    avg_return = event_returns.mean()
    median_return = event_returns.median()
    count = len(event_returns)
    positive_count = (event_returns > 0).sum()
    positive_pct = (positive_count / count) * 100 if count > 0 else 0.0
    
    logger.info(f"Market reaction statistics:")
    logger.info(f"  Events found: {count}")
    logger.info(f"  Average return: {avg_return:.2f}%")
    logger.info(f"  Median return: {median_return:.2f}%")
    logger.info(f"  Positive outcomes: {positive_pct:.1f}%")
    
    return {
        'avg_return': avg_return,
        'median_return': median_return,
        'count': count,
        'positive_pct': positive_pct
    }
