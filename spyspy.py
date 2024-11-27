import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.title("Currency Exchange Rates and Deposit Rates")

# Define currency pairs for DM and EM
currency_pairs = {
    "USD/EUR": "EURUSD=X",
    "USD/JPY": "JPY=X",
    "USD/GBP": "GBPUSD=X",
    "USD/AUD": "AUDUSD=X",
    "USD/CAD": "CADUSD=X",
    "USD/CHF": "CHFUSD=X",
    "USD/CNY": "CNY=X",
    "USD/INR": "INR=X",
    "USD/BRL": "BRL=X",
    "USD/RUB": "RUB=X",
    "USD/ZAR": "ZAR=X",
    "USD/MXN": "MXN=X",
    "USD/KRW": "KRW=X",
    "USD/IDR": "IDR=X",
    "USD/TRY": "TRY=X"
}

# Placeholder for deposit rates (mock data)
deposit_rates = {
    "USD": 0.25,
    "EUR": -0.5,
    "JPY": -0.1,
    "GBP": 0.1,
    "AUD": 0.1,
    "CAD": 0.25,
    "CHF": -0.75,
    "CNY": 2.2,
    "INR": 4.0,
    "BRL": 2.0,
    "RUB": 4.5,
    "ZAR": 3.5,
    "MXN": 4.0,
    "KRW": 1.5,
    "IDR": 3.5,
    "TRY": 5.0
}

@st.cache_data
def fetch_currency_data(symbol):
    """Fetch historical data for a currency pair"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="3y")
        return data['Close']
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return pd.Series()

@st.cache_data
def calculate_z_score(series):
    """Calculate the 1-year Z-score for a series"""
    if len(series) < 252:
        return np.nan
    mean = series[-252:].mean()
    std = series[-252:].std()
    return (series.iloc[-1] - mean) / std

# Fetch data for all currency pairs
currency_data = {pair: fetch_currency_data(symbol) for pair, symbol in currency_pairs.items()}

# Create a DataFrame for deposit rates and Z-scores
deposit_rate_df = pd.DataFrame({
    "Currency": list(deposit_rates.keys()),
    "Deposit Rate": list(deposit_rates.values())
})

# Calculate Z-scores for deposit rates
deposit_rate_df['1Y Z-Score'] = deposit_rate_df['Deposit Rate'].apply(lambda x: calculate_z_score(pd.Series([x] * 252)))

# Display currency data
st.subheader("Currency Exchange Rates (Last 3 Years)")
for pair, data in currency_data.items():
    if not data.empty:
        st.line_chart(data, height=200, use_container_width=True)
        st.write(f"{pair} - Last Price: {data.iloc[-1]:.4f}")

# Display deposit rates and Z-scores
st.subheader("Deposit Rates and 1-Year Z-Scores")
st.dataframe(deposit_rate_df)
