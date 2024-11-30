import requests
import streamlit as st

st.title("Germany CPI 2023")

# Your EconDB API token
api_token = "95f02e5d4dcd471ad575cd2ef8298d92b6d4d318"

# Define the endpoint and parameters
url = "https://www.econdb.com/api/series/DECPI"  # DE for Germany, CPI for Consumer Price Index
params = {
    "api_token": api_token,
    "format": "json"
}

try:
    # Make the request to the EconDB API
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise an error for bad responses
    
    # Print response for debugging
    st.write("Response Status:", response.status_code)
    st.write("Response Headers:", dict(response.headers))

    # Parse the JSON response
    data = response.json()

    # Display raw data for debugging
    st.write("Raw Response:", data)

    # Check if data is available and filter for 2023
    if data and "data" in data:
        cpi_data = data["data"]
        cpi_2023 = [d for d in cpi_data if d.get("period", "").startswith("2023")]
        
        if cpi_2023:
            st.subheader("Germany CPI Data 2023")
            st.dataframe(cpi_2023)
            
            # Get the most recent value
            latest = cpi_2023[-1]
            st.metric(
                label=f"Latest CPI (Period: {latest['period']})", 
                value=f"{latest['value']:.1f}"
            )
        else:
            st.warning("No 2023 CPI data available")
    else:
        st.warning("No CPI data available")
        st.write("Full Response:", data)

except requests.exceptions.RequestException as e:
    st.error(f"Error fetching data from EconDB: {str(e)}")

