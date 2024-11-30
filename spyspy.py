import streamlit as st
import requests
import pandas as pd

st.title("South Africa 2025 GDP Growth Forecast")

try:
    # Base URL for IMF WEO database
    base_url = "http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/WEO"
    
    # Indicator for Real GDP Growth
    indicator_code = 'NGDP_RPCH'
    country_code = 'ZAF'  # South Africa's country code
    
    # Construct URL
    url = f"{base_url}/{indicator_code}/{country_code}?startPeriod=2025&endPeriod=2025"
    
    # Make request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': 'application/json'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        json_data = response.json()
        value = float(json_data['CompactData']['DataSet']['Series']['Obs']['@value'])
        
        # Display metric
        st.metric(
            label="South Africa Real GDP Growth (2025)",
            value=f"{value:.1f}%"
        )
    else:
        st.error("Failed to fetch GDP growth forecast")

except Exception as e:
    st.error(f"Error: {str(e)}")
    st.write("URL attempted:", url)
