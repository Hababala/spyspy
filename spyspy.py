import streamlit as st
import requests
import pandas as pd

st.title("Brazil 2025 Forecasts")

try:
    # Base URL for IMF WEO database
    base_url = "http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/WEO"
    
    # Indicators we want
    indicators = {
        'NGDP_RPCH': 'Real GDP Growth',
        'PCPIPCH': 'CPI Inflation'
    }
    
    data = {}
    
    for indicator_code, indicator_name in indicators.items():
        # Construct URL for each indicator
        url = f"{base_url}/{indicator_code}/BRA?startPeriod=2025&endPeriod=2025"
        
        # Make request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            json_data = response.json()
            value = float(json_data['CompactData']['DataSet']['Series']['Obs']['@value'])
            data[indicator_name] = value
            
            # Display metric
            st.metric(
                label=f"Brazil {indicator_name} (2025)",
                value=f"{value:.1f}%"
            )
        else:
            st.error(f"Failed to fetch {indicator_name}")

except Exception as e:
    st.error(f"Error: {str(e)}")
    st.write("URL attempted:", url)

