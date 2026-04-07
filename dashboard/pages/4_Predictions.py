"""
Predictions Page

This page displays machine learning predictions for next-day market direction,
trading signals, feature importance, and historical prediction accuracy.
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

# Add parent directory to path to import utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import load_latest_data, load_model
from utils.visualizations import (
    plot_prediction_gauge,
    plot_feature_importance
)

# Import signal generator
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'scripts'))
from signal_generator import generate_signal

# Configure page
st.set_page_config(
    page_title="Predictions - Smart Money Intelligence",
    page_icon=None,
    layout="wide"
)

# Page header
st.title("Market Predictions & Trading Signals")
st.markdown("---")

# Load data and model
with st.spinner("Loading data and model..."):
    df = load_latest_data()
    model_data = load_model()

# Check if data and model are loaded
if df is None or df.empty:
    st.error("Unable to load market data. Please ensure the data pipeline has been run.")
    st.info("Run `python scripts/run_pipeline.py` to generate processed data.")
    st.stop()

if model_data is None:
    st.error("Unable to load trained model. Please ensure the model has been trained.")
    st.info("Run `python scripts/model_training.py` to train the model.")
    st.stop()

# Extract model and metadata
model = model_data['model']
metadata = model_data.get('metadata', {})

# Ensure Date column is datetime
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')

# Get the latest data point for prediction
latest_data = df.iloc[-1]
latest_date = latest_data['Date']

st.info(f"📅 Making prediction for next trading day after: **{latest_date.strftime('%Y-%m-%d')}**")

# Define feature columns (must match training)
feature_cols = [
    'FII_Net', 'DII_Net',
    'Daily_Return_Lag1', 'Daily_Return_Lag2', 'Daily_Return_Lag3',
    'Volatility',
    'Momentum',
    'FII_Net_MA5', 'FII_Net_MA10', 'FII_Net_MA20',
    'DII_Net_MA5', 'DII_Net_MA10', 'DII_Net_MA20',
    'FII_Net_Lag1', 'FII_Net_Lag2', 'FII_Net_Lag3',
    'DII_Net_Lag1', 'DII_Net_Lag2', 'DII_Net_Lag3'
]

# Check if all features are available
missing_features = [col for col in feature_cols if col not in df.columns]
if missing_features:
    st.error(f"❌ Missing required features: {missing_features}")
    st.info("💡 Please ensure the feature engineering pipeline has been run completely.")
    st.stop()

# Extract features for prediction
try:
    X_latest = latest_data[feature_cols].values.reshape(1, -1)
    
    # Convert to float and check for NaN values
    X_latest = X_latest.astype(float)
    
    # Check for NaN values using pandas
    if pd.isna(X_latest).any():
        st.warning("⚠️ Some features contain missing values. Prediction may be unreliable.")
        # Fill NaN with 0 for prediction
        X_latest = np.nan_to_num(X_latest, nan=0.0)
    
    # Make prediction
    ml_prediction = model.predict(X_latest)[0]
    ml_probabilities = model.predict_proba(X_latest)[0]
    ml_probability = ml_probabilities[1]  # Probability of class 1 (Up)
    
except Exception as e:
    st.error(f"❌ Error making prediction: {str(e)}")
    st.stop()

# Generate trading signal
try:
    signal_result = generate_signal(
        fii_net=float(latest_data.get('FII_Net', 0)),
        dii_net=float(latest_data.get('DII_Net', 0)),
        momentum=float(latest_data.get('Momentum', 0)),
        ml_prediction=int(ml_prediction),
        ml_probability=float(ml_probability)
    )
except Exception as e:
    st.error(f"❌ Error generating signal: {str(e)}")
    signal_result = {
        'signal': 'Unknown',
        'confidence': 0.0,
        'factors': {}
    }

st.markdown("---")

# Main Prediction Section
st.header("Next-Day Market Direction Prediction")

# Create two columns for prediction display
pred_col1, pred_col2 = st.columns([1, 1])

with pred_col1:
    # Display prediction gauge
    fig_gauge = plot_prediction_gauge(
        probability=ml_probability,
        title='ML Model Prediction Probability'
    )
    st.plotly_chart(fig_gauge, use_container_width=True)
    
    # Prediction interpretation
    if ml_prediction == 1:
        pred_text = "**UP** (Bullish)"
        pred_color = "green"
    else:
        pred_text = "**DOWN** (Bearish)"
        pred_color = "red"
    
    st.markdown(f"### Predicted Direction: {pred_text}")
    st.markdown(f"**Confidence:** {ml_probability * 100:.1f}%")

with pred_col2:
    # Display trading signal
    st.markdown("### 🎯 Trading Signal")
    
    signal = signal_result['signal']
    confidence = signal_result['confidence']
    
    # Signal display with color coding
    if signal == 'Bullish':
        signal_emoji = ""
        signal_color = "green"
    elif signal == 'Bearish':
        signal_emoji = ""
        signal_color = "red"
    else:
        signal_emoji = ""
        signal_color = "orange"
    
    st.markdown(f"## **{signal}**")
    st.markdown(f"**Signal Confidence:** {confidence * 100:.1f}%")
    
    # Display signal reasoning
    if 'signal_reason' in signal_result['factors']:
        st.info(f"💡 {signal_result['factors']['signal_reason']}")
    
    # Signal strength indicator
    st.progress(confidence)

st.markdown("---")

# Contributing Factors Section
st.header("Contributing Factors")

factors_col1, factors_col2, factors_col3 = st.columns(3)

with factors_col1:
    st.markdown("### Institutional Flows")
    fii_net = latest_data.get('FII_Net', 0)
    dii_net = latest_data.get('DII_Net', 0)
    
    # FII Net
    fii_delta_color = "normal" if fii_net >= 0 else "inverse"
    st.metric(
        label="FII Net Flow",
        value=f"₹{fii_net:,.0f} Cr",
        delta=f"{'Buying' if fii_net >= 0 else 'Selling'}",
        delta_color=fii_delta_color
    )
    
    # DII Net
    dii_delta_color = "normal" if dii_net >= 0 else "inverse"
    st.metric(
        label="DII Net Flow",
        value=f"₹{dii_net:,.0f} Cr",
        delta=f"{'Buying' if dii_net >= 0 else 'Selling'}",
        delta_color=dii_delta_color
    )

with factors_col2:
    st.markdown("### Technical Indicators")
    momentum = latest_data.get('Momentum', 0)
    volatility = latest_data.get('Volatility', 0)
    
    # Momentum
    momentum_delta_color = "normal" if momentum >= 0 else "inverse"
    st.metric(
        label="Momentum (10-day)",
        value=f"{momentum:,.2f}",
        delta=f"{'Positive' if momentum >= 0 else 'Negative'}",
        delta_color=momentum_delta_color
    )
    
    # Volatility
    st.metric(
        label="Volatility (20-day)",
        value=f"{volatility:.2f}%",
        delta=None
    )

with factors_col3:
    st.markdown("### Recent Performance")
    daily_return_lag1 = latest_data.get('Daily_Return_Lag1', 0)
    
    # Recent return
    return_delta_color = "normal" if daily_return_lag1 >= 0 else "inverse"
    st.metric(
        label="Previous Day Return",
        value=f"{daily_return_lag1:.2f}%",
        delta=None,
        delta_color=return_delta_color
    )
    
    # Moving averages
    fii_ma5 = latest_data.get('FII_Net_MA5', 0)
    st.metric(
        label="FII 5-Day Avg",
        value=f"₹{fii_ma5:,.0f} Cr",
        delta=None
    )

st.markdown("---")

# Feature Importance Section
st.header("Feature Importance Analysis")

# Check if model has feature_importances_ attribute
if hasattr(model, 'feature_importances_'):
    feature_importance = model.feature_importances_
    
    # Create feature importance chart
    fig_importance = plot_feature_importance(
        feature_names=feature_cols,
        importance_values=feature_importance.tolist(),
        title='Top Features Influencing Predictions'
    )
    
    st.plotly_chart(fig_importance, use_container_width=True)
    
    # Display top features
    with st.expander("Top 5 Most Important Features"):
        # Sort features by importance
        importance_df = pd.DataFrame({
            'Feature': feature_cols,
            'Importance': feature_importance
        }).sort_values('Importance', ascending=False)
        
        st.dataframe(
            importance_df.head(5).reset_index(drop=True),
            use_container_width=True
        )
        
        st.markdown("""
        **Feature Importance Interpretation:**
        - Higher values indicate features that have more influence on the model's predictions
        - These features are most critical for determining market direction
        - Focus on monitoring these key indicators for better market insights
        """)
else:
    st.info("ℹ️ Feature importance is not available for this model type (Logistic Regression).")
    st.markdown("""
    **Note:** Feature importance is available for tree-based models like Random Forest and XGBoost.
    If you want to see feature importance, ensure the best model is one of these types.
    """)

st.markdown("---")

# Model Performance Section
st.header("Model Performance Metrics")

if metadata:
    perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
    
    performance = metadata.get('performance', {})
    
    with perf_col1:
        accuracy = performance.get('accuracy', 0)
        st.metric(
            label="Accuracy",
            value=f"{accuracy * 100:.1f}%",
            delta=None
        )
    
    with perf_col2:
        precision = performance.get('precision', 0)
        st.metric(
            label="Precision",
            value=f"{precision * 100:.1f}%",
            delta=None
        )
    
    with perf_col3:
        recall = performance.get('recall', 0)
        st.metric(
            label="Recall",
            value=f"{recall * 100:.1f}%",
            delta=None
        )
    
    with perf_col4:
        f1_score = performance.get('f1_score', 0)
        st.metric(
            label="F1 Score",
            value=f"{f1_score * 100:.1f}%",
            delta=None
        )
    
    # Model details
    with st.expander("Model Details"):
        model_type = metadata.get('model_type', 'Unknown')
        training_date = metadata.get('training_date', 'Unknown')
        training_samples = metadata.get('training_samples', 0)
        test_samples = metadata.get('test_samples', 0)
        
        st.markdown(f"**Model Type:** {model_type}")
        st.markdown(f"**Training Date:** {training_date}")
        st.markdown(f"**Training Samples:** {training_samples:,}")
        st.markdown(f"**Test Samples:** {test_samples:,}")
        
        # Hyperparameters
        hyperparameters = metadata.get('hyperparameters', {})
        if hyperparameters:
            st.markdown("**Hyperparameters:**")
            for param, value in hyperparameters.items():
                st.markdown(f"- {param}: {value}")
else:
    st.info("ℹ️ Model performance metrics not available. Metadata file may be missing.")

st.markdown("---")

# Historical Accuracy Section (if available)
st.header("Historical Prediction Accuracy")

# Check if we have Target column to calculate historical accuracy
if 'Target' in df.columns:
    # Get last N predictions for accuracy calculation
    n_recent = min(30, len(df) - 1)  # Last 30 days or available data
    
    if n_recent > 0:
        # Get recent data (excluding the latest point since we don't have actual outcome yet)
        recent_df = df.iloc[-(n_recent+1):-1].copy()
        
        # Extract features and make predictions
        X_recent = recent_df[feature_cols].values
        
        # Handle NaN values
        X_recent = np.nan_to_num(X_recent, nan=0.0)
        
        # Make predictions
        predictions = model.predict(X_recent)
        actuals = recent_df['Target'].values
        
        # Calculate accuracy
        correct_predictions = (predictions == actuals).sum()
        accuracy = (correct_predictions / len(predictions)) * 100
        
        # Display accuracy metrics
        acc_col1, acc_col2, acc_col3 = st.columns(3)
        
        with acc_col1:
            st.metric(
                label=f"Recent Accuracy ({n_recent} days)",
                value=f"{accuracy:.1f}%",
                delta=f"{correct_predictions}/{len(predictions)} correct"
            )
        
        with acc_col2:
            # Calculate bullish accuracy
            bullish_mask = predictions == 1
            if bullish_mask.sum() > 0:
                bullish_accuracy = ((predictions[bullish_mask] == actuals[bullish_mask]).sum() / bullish_mask.sum()) * 100
                st.metric(
                    label="Bullish Prediction Accuracy",
                    value=f"{bullish_accuracy:.1f}%",
                    delta=f"{bullish_mask.sum()} predictions"
                )
            else:
                st.metric(
                    label="Bullish Prediction Accuracy",
                    value="N/A",
                    delta="No bullish predictions"
                )
        
        with acc_col3:
            # Calculate bearish accuracy
            bearish_mask = predictions == 0
            if bearish_mask.sum() > 0:
                bearish_accuracy = ((predictions[bearish_mask] == actuals[bearish_mask]).sum() / bearish_mask.sum()) * 100
                st.metric(
                    label="Bearish Prediction Accuracy",
                    value=f"{bearish_accuracy:.1f}%",
                    delta=f"{bearish_mask.sum()} predictions"
                )
            else:
                st.metric(
                    label="Bearish Prediction Accuracy",
                    value="N/A",
                    delta="No bearish predictions"
                )
        
        # Show recent predictions table
        with st.expander("Recent Predictions vs Actuals"):
            # Create comparison dataframe
            comparison_df = pd.DataFrame({
                'Date': recent_df['Date'].dt.strftime('%Y-%m-%d'),
                'Predicted': ['Up' if p == 1 else 'Down' for p in predictions],
                'Actual': ['Up' if a == 1 else 'Down' for a in actuals],
                'Correct': ['✅' if p == a else '❌' for p, a in zip(predictions, actuals)]
            })
            
            # Show last 10 predictions
            st.dataframe(
                comparison_df.tail(10).reset_index(drop=True),
                use_container_width=True
            )
else:
    st.info("ℹ️ Historical accuracy data not available. Target column missing from dataset.")

st.markdown("---")

# Disclaimer and Recommendations
st.header("Important Notes")

col_note1, col_note2 = st.columns(2)

with col_note1:
    st.markdown("### Disclaimer")
    st.markdown("""
    - These predictions are generated by machine learning models for educational purposes
    - Past performance does not guarantee future results
    - Always conduct your own research before making investment decisions
    - Consider multiple factors beyond ML predictions
    - Consult with financial advisors for investment advice
    """)

with col_note2:
    st.markdown("### How to Use These Predictions")
    st.markdown("""
    - Use predictions as one input among many for decision-making
    - Pay attention to signal confidence levels
    - Monitor contributing factors (FII/DII flows, momentum, volatility)
    - Consider the overall market context and news
    - Track historical accuracy to gauge model reliability
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem 0;">
    <p><strong>Predictions Dashboard</strong> | Powered by Machine Learning</p>
    <p>Model: {} | Last Updated: {}</p>
</div>
""".format(
    metadata.get('model_type', 'Unknown'),
    metadata.get('training_date', 'Unknown')
), unsafe_allow_html=True)
