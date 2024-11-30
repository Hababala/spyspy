import streamlit as st
import requests
import pandas as pd

st.title("Brazil GDP Growth 2023")

try:
    # IMF API base URL for WEO database
    base_url = "http://dataservices.imf.org/REST/SDMX_JSON.svc"
    
    # Specific indicator for Real GDP growth
    indicator = 'NGDP_RPCH'
    country = 'BRA'
    
    # Construct URL with parameters
    url = f"{base_url}/CompactData/WEO/{indicator}/{country}?startPeriod=2023&endPeriod=2023"
    
    # Add headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': 'application/json',
        'Connection': 'keep-alive'
    }
    
    # Make request
    response = requests.get(url, headers=headers, verify=True)
    
    # Print response for debugging
    st.write("Response status:", response.status_code)
    st.write("Response content:", response.text[:200])  # First 200 chars
    
    if response.status_code == 200:
        json_data = response.json()
        
        # Extract data
        series = json_data['CompactData']['DataSet']['Series']
        obs = series['Obs'] if isinstance(series['Obs'], list) else [series['Obs']]
        
        # Convert to DataFrame
        df = pd.DataFrame(obs)
        df.columns = ['date', 'value']
        df['value'] = pd.to_numeric(df['value'])
        
        # Filter for 2023
        gdp_2023 = df[df['date'] == '2023']['value'].iloc[0]
        
        # Display result
        st.metric(
            label="Brazil Real GDP Growth 2023",
            value=f"{gdp_2023:.1f}%"
        )
    else:
        st.error(f"Failed to fetch data. Status code: {response.status_code}")

except Exception as e:
    st.error(f"Error fetching data: {str(e)}")
    st.write("URL attempted:", url)
    st.write("Headers used:", headers)

