import os
import streamlit as st
import plotly.graph_objects as go
import yfinance as yf  
import numpy as np
from scipy import stats
import pandas as pd

# Set OpenBB user directory to a writable location BEFORE importing OpenBB
os.environ["OPENBB_USER_PATH"] = "/tmp/openbb_user"
os.makedirs("/tmp/openbb_user", exist_ok=True)

# Now import OpenBB
from openbb import obb

st.title("US Budget Balance Forecast")

# Initialize OpenBB authentication
if 'openbb_authenticated' not in st.session_state:
    st.session_state.openbb_authenticated = False

def init_openbb():
    try:
        if 'OPENBB_API_KEY' in st.secrets:
            api_key = st.secrets['OPENBB_API_KEY']
        else:
            # Use the hardcoded key as fallback
            api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdXRoX3Rva2VuIjoiTUJFNDhxaEtHYWlmdHJKVlN0eWZoVktxNmZlMGE5am41aGVnWkxDbiIsImV4cCI6MTc2Mjg5MzIyMH0.48URoFcEJ2dWF2SpWyj0B8MR-mBY8nc5lliHBuNR8bo"
        
        obb.account.login(pat=api_key)
        st.session_state.openbb_authenticated = True
        return True
    except Exception as e:
        st.error(f"Failed to authenticate with OpenBB: {str(e)}")
        return False

# Try to authenticate
if not st.session_state.openbb_authenticated:
    if not init_openbb():
        st.stop()

try:
    # Fetch US budget balance forecast
    budget_data = obb.economy.fiscal.balance(country="united states", forecast=True)
    
    if not budget_data.empty:
        st.dataframe(budget_data)
        
        # Extract 2025 forecast if available
        if 2025 in budget_data.index:
            forecast_2025 = budget_data.loc[2025]['Budget Balance (% of GDP)']
            st.metric("2025 Budget Balance Forecast (% of GDP)", f"{forecast_2025:.1f}%")
        else:
            st.warning("2025 forecast not available in the data")
    else:
        st.warning("No budget balance data available")

except Exception as e:
    st.error(f"Error fetching budget balance data: {str(e)}")

