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
    json_data = response.json()
    
    # Check if data is available
    if len(json_data) > 1 and json_data[1]:
        data = json_data[1]
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Check if 'date' and 'value' columns exist
        if 'date' in df.columns and 'value' in df.columns:
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
        else:
            st.error("The expected data fields are missing in the response.")
    else:
        st.error("No data available for the specified year.")

except Exception as e:
    st.error(f"Error fetching data from World Bank API: {str(e)}")
    st.write("URL attempted:", url)