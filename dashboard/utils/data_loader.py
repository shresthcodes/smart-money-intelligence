"""
Data Loader Utility for Dashboard

This module provides functions to load processed data and trained models
for the Streamlit dashboard with caching for performance.
"""

import os
import pandas as pd
import joblib
import streamlit as st
from typing import Optional, Dict, Any
import json


@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_latest_data() -> Optional[pd.DataFrame]:
    """
    Load the most recent processed data from CSV.
    
    This function loads the merged and processed dataset that contains
    market data, institutional flows, and engineered features.
    
    Returns:
        DataFrame with processed data, or None if file not found
        
    Raises:
        FileNotFoundError: If the processed data file doesn't exist
        ValueError: If the CSV file is empty or malformed
    """
    # Define the path to processed data
    data_path = os.path.join("data", "processed", "merged_data.csv")
    
    # Check if file exists
    if not os.path.exists(data_path):
        st.error(f"❌ Data file not found at: {data_path}")
        st.info("💡 Please run the data pipeline first to generate processed data.")
        return None
    
    try:
        # Load the CSV file
        df = pd.read_csv(data_path)
        
        # Validate that DataFrame is not empty
        if df.empty:
            st.warning("⚠️ The data file is empty. Please regenerate the processed data.")
            return None
        
        # Convert Date column to datetime if it exists
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date')
        
        st.success(f"✅ Loaded {len(df)} rows of data from {data_path}")
        return df
        
    except pd.errors.EmptyDataError:
        st.error("❌ The data file is empty or malformed.")
        return None
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return None


@st.cache_resource  # Cache the model (use cache_resource for non-serializable objects)
def load_model() -> Optional[Dict[str, Any]]:
    """
    Load the trained machine learning model and its metadata.
    
    This function loads the saved model file (.pkl) and its associated
    metadata (JSON) which contains information about features, performance,
    and hyperparameters.
    
    Returns:
        Dictionary containing:
        - 'model': The trained model object
        - 'metadata': Model metadata (features, performance, etc.)
        Returns None if model files not found
        
    Raises:
        FileNotFoundError: If model files don't exist
        Exception: If model loading fails
    """
    # Define paths
    model_path = os.path.join("models", "market_prediction_model.pkl")
    metadata_path = os.path.join("models", "market_prediction_model_metadata.json")
    
    # Check if model file exists
    if not os.path.exists(model_path):
        st.error(f"❌ Model file not found at: {model_path}")
        st.info("💡 Please train the model first using scripts/model_training.py")
        return None
    
    try:
        # Load the model file (which is a dict with 'model', 'scaler', etc.)
        saved_data = joblib.load(model_path)
        
        # Extract the actual model object
        if isinstance(saved_data, dict) and 'model' in saved_data:
            actual_model = saved_data['model']
            model_name = saved_data.get('model_name', 'Unknown')
        else:
            # Fallback if it's just the model object
            actual_model = saved_data
            model_name = 'Unknown'
        
        # Load metadata if available
        metadata = {}
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        else:
            st.warning("⚠️ Model metadata file not found. Some information may be unavailable.")
        
        st.success(f"✅ Model loaded successfully from {model_path}")
        
        return {
            'model': actual_model,
            'metadata': metadata,
            'model_name': model_name
        }
        
    except Exception as e:
        st.error(f"❌ Error loading model: {str(e)}")
        return None


@st.cache_data(ttl=3600)
def load_raw_nifty_data() -> Optional[pd.DataFrame]:
    """
    Load raw NIFTY data from CSV.
    
    This is useful for displaying raw market data without features.
    
    Returns:
        DataFrame with raw NIFTY data, or None if not found
    """
    data_path = os.path.join("data", "raw", "nifty_data.csv")
    
    if not os.path.exists(data_path):
        st.warning(f"⚠️ Raw NIFTY data not found at: {data_path}")
        return None
    
    try:
        df = pd.read_csv(data_path)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date')
        return df
    except Exception as e:
        st.error(f"❌ Error loading raw NIFTY data: {str(e)}")
        return None


@st.cache_data(ttl=3600)
def load_raw_institutional_data() -> Optional[pd.DataFrame]:
    """
    Load raw FII/DII institutional data from CSV.
    
    Returns:
        DataFrame with raw institutional data, or None if not found
    """
    data_path = os.path.join("data", "raw", "fii_dii_data.csv")
    
    if not os.path.exists(data_path):
        st.warning(f"⚠️ Raw institutional data not found at: {data_path}")
        return None
    
    try:
        df = pd.read_csv(data_path)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date')
        return df
    except Exception as e:
        st.error(f"❌ Error loading raw institutional data: {str(e)}")
        return None


def get_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get summary statistics about the loaded data.
    
    Args:
        df: DataFrame to summarize
        
    Returns:
        Dictionary with summary statistics
    """
    if df is None or df.empty:
        return {}
    
    summary = {
        'total_rows': len(df),
        'date_range': {
            'start': df['Date'].min() if 'Date' in df.columns else None,
            'end': df['Date'].max() if 'Date' in df.columns else None
        },
        'columns': list(df.columns),
        'missing_values': df.isnull().sum().to_dict()
    }
    
    return summary


def clear_cache():
    """
    Clear all cached data and models.
    
    This is useful when data has been updated and needs to be reloaded.
    """
    st.cache_data.clear()
    st.cache_resource.clear()
    st.success("✅ Cache cleared successfully!")
