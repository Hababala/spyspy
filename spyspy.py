import requests
import streamlit as st

st.title("US Budget Balance Forecast")

# Your EconDB API token
api_token = "95f02e5d4dcd471ad575cd2ef8298d92b6d4d318"

# Define the endpoint and parameters
url = "https://api.econdb.com/v1/forecast/budget_balance"
params = {
    "country": "united states",
    "forecast": True,
    "api_token": api_token
}

try:
    # Make the request to the EconDB API
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise an error for bad responses

    # Parse the JSON response
    data = response.json()

    # Check if data is available
    if data and "data" in data:
        budget_data = data["data"]
        st.dataframe(budget_data)

        # Extract 2025 forecast if available
        forecast_2025 = next((item for item in budget_data if item["year"] == 2025), None)
        if forecast_2025:
            st.metric("2025 Budget Balance Forecast (% of GDP)", f"{forecast_2025['value']:.1f}%")
        else:
            st.warning("2025 forecast not available in the data")
    else:
        st.warning("No budget balance data available")

except requests.exceptions.RequestException as e:
    st.error(f"Error fetching data from EconDB: {str(e)}")

