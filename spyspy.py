import streamlit as st
import requests
import pandas as pd

st.title("Brazil GDP Growth 2023")

try:
    # IMF API base URL for WEO database
    base_url = "http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/WEO"
    
    # Specific indicator for Real GDP growth
    indicator = 'NGDP_RPCH'
    country = 'BRA'
    
    # Construct URL
    url = f"{base_url}/{indicator}.{country}"
    
    # Make request
    response = requests.get(url)
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

except Exception as e:
    st.error(f"Error fetching data: {str(e)}")
    st.write("URL attempted:", url)

