import streamlit as st
import requests
import pandas as pd

st.title("Brazil GDP Growth 2023")

try:
    # IMF API base URL and endpoint
    url = "http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/IFS/Q.BR.NGDP_R_PC_CP_A_PT.?startPeriod=2023&endPeriod=2023"
    
    # Add headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': 'application/json'
    }
    
    # Make request
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        json_data = response.json()
        
        # Extract data
        series = json_data['CompactData']['DataSet']['Series']
        obs = series['Obs'] if isinstance(series['Obs'], list) else [series['Obs']]
        
        # Convert to DataFrame
        df = pd.DataFrame(obs)
        df.columns = ['date', 'value']
        df['value'] = pd.to_numeric(df['value'])
        
        # Get the latest value
        gdp_growth = df['value'].iloc[0]
        
        # Display result
        st.metric(
            label="Brazil Real GDP Growth 2023",
            value=f"{gdp_growth:.1f}%"
        )
    else:
        st.error(f"Failed to fetch data. Status code: {response.status_code}")
        st.write("Response content:", response.text[:200])

except Exception as e:
    st.error(f"Error fetching data: {str(e)}")
    st.write("URL attempted:", url)

