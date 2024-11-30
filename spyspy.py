import streamlit as st
import requests
import pandas as pd


st.title("South Africa 2025 GDP Growth Forecast")

try:
    # World Bank API endpoint for GDP growth
    url = "http://api.worldbank.org/v2/country/ZAF/indicator/NY.GDP.MKTP.KD.ZG"
    
    # Parameters for the API request
    params = {
        "format": "json",
        "per_page": "100",  # Get more data than needed to ensure we have our date range
        "date": "2025"  # Specific year
    }
    
    # Make the API request
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise an error for bad responses
    
    # Parse the JSON response
    data = response.json()[1]  # World Bank returns metadata in [0] and data in [1]
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'], format='%Y')
    df['value'] = pd.to_numeric(df['value'])
    df = df.sort_values('date')
    
    # Get the 2025 value
    gdp_2025 = df[df['date'].dt.year == 2025]['value'].iloc[0]
    
    # Display result
    st.metric(
        label="South Africa Real GDP Growth (2025)",
        value=f"{gdp_2025:.1f}%"
    )

except Exception as e:
    st.error(f"Error fetching data from World Bank API: {str(e)}")
    st.write("URL attempted:", url)