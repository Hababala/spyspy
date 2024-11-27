import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from io import StringIO

st.title("Currency Exchange Rates, Deposit Rates, and COT Positioning")

# Define currency pairs and their corresponding CFTC codes
currency_data = {
    "EUR": {
        "pair": "EURUSD=X",
        "cftc_code": "099741", # Euro FX
        "deposit_rate": -0.5
    },
    "JPY": {
        "pair": "JPY=X",
        "cftc_code": "097741", # Japanese Yen
        "deposit_rate": -0.1
    },
    "GBP": {
        "pair": "GBPUSD=X",
        "cftc_code": "096742", # British Pound
        "deposit_rate": 0.1
    },
    "AUD": {
        "pair": "AUDUSD=X",
        "cftc_code": "232741", # Australian Dollar
        "deposit_rate": 0.1
    },
    "CAD": {
        "pair": "CADUSD=X",
        "cftc_code": "090741", # Canadian Dollar
        "deposit_rate": 0.25
    },
    "CHF": {
        "pair": "CHFUSD=X",
        "cftc_code": "092741", # Swiss Franc
        "deposit_rate": -0.75
    },
    "MXN": {
        "pair": "MXN=X",
        "cftc_code": "095741", # Mexican Peso
        "deposit_rate": 4.0
    }
}

@st.cache_data
def fetch_cot_data():
    """Fetch latest COT data from CFTC"""
    try:
        # Get the most recent Friday's date
        today = datetime.now()
        friday = today - timedelta(days=(today.weekday() + 3) % 7)
        
        # CFTC report URL
        url = f"https://www.cftc.gov/dea/newcot/f_txt/{friday.strftime('%Y%m%d')}.txt"
        
        response = requests.get(url)
        if response.status_code == 200:
            # Parse the fixed-width file
            df = pd.read_csv(StringIO(response.text), sep=',')
            
            # Filter for currency futures and get non-commercial positions
            cot_data = {}
            for currency, info in currency_data.items():
                currency_df = df[df['Market_and_Exchange_Names'].str.contains(info['cftc_code'], na=False)]
                if not currency_df.empty:
                    cot_data[currency] = {
                        'Non-Commercial Long': currency_df['NonComm_Positions_Long_All'].iloc[0],
                        'Non-Commercial Short': currency_df['NonComm_Positions_Short_All'].iloc[0],
                        'Net Position': currency_df['NonComm_Positions_Long_All'].iloc[0] - 
                                      currency_df['NonComm_Positions_Short_All'].iloc[0]
                    }
            return cot_data
    except Exception as e:
        st.error(f"Error fetching COT data: {str(e)}")
        return {}

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

# Fetch all data
currency_prices = {curr: fetch_currency_data(info['pair']) 
                  for curr, info in currency_data.items()}
cot_positions = fetch_cot_data()

# Create combined DataFrame
results = []
for currency, info in currency_data.items():
    price_data = currency_prices[currency]
    cot_data = cot_positions.get(currency, {})
    
    result = {
        'Currency': currency,
        'Current Rate': price_data.iloc[-1] if not price_data.empty else np.nan,
        'Deposit Rate': info['deposit_rate'],
        'Deposit Rate Z-Score': calculate_z_score(pd.Series([info['deposit_rate']] * 252)),
        'Non-Comm Long': cot_data.get('Non-Commercial Long', np.nan),
        'Non-Comm Short': cot_data.get('Non-Commercial Short', np.nan),
        'Net Position': cot_data.get('Net Position', np.nan)
    }
    results.append(result)

df_results = pd.DataFrame(results)

# Display results
st.subheader("Currency Overview")
st.dataframe(df_results)

# Display currency charts
st.subheader("Currency Exchange Rates (Last 3 Years)")
for currency, price_data in currency_prices.items():
    if not price_data.empty:
        st.write(f"{currency}/USD Exchange Rate")
        st.line_chart(price_data)

# Display COT positioning charts
st.subheader("COT Non-Commercial Positioning")
if cot_positions:
    cot_df = pd.DataFrame([{
        'Currency': curr,
        'Net Position': data['Net Position']
    } for curr, data in cot_positions.items()])
    
    st.bar_chart(cot_df.set_index('Currency')['Net Position'])
