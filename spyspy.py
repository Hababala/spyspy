import requests
import streamlit as st

st.title("US Budget Balance Forecast")

# Your EconDB API token
api_token = "95f02e5d4dcd471ad575cd2ef8298d92b6d4d318"

# Define the endpoint and parameters
url = "https://www.econdb.com/api/series/USGBAL"
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

    # Check if data is available
    if data and "data" in data:
        budget_data = data["data"]
        st.dataframe(budget_data)

        # Try to find the most recent forecast
        if isinstance(budget_data, list):
            # Sort by date/period if available
            recent_data = sorted(budget_data, key=lambda x: x.get("period", ""), reverse=True)
            if recent_data:
                st.metric("Most Recent Budget Balance", f"{recent_data[0]['value']:.1f}%")
        
    else:
        st.warning("No budget balance data available")
        st.write("Full Response:", data)  # Debug information

except requests.exceptions.RequestException as e:
    st.error(f"Error fetching data from EconDB: {str(e)}")

