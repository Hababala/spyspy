import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.title("Germany GDP Growth Rate (2020-2024)")

try:
    # World Bank API endpoint for GDP growth
    # NY.GDP.MKTP.KD.ZG is the indicator code for real GDP growth
    url = "http://api.worldbank.org/v2/country/DEU/indicator/NY.GDP.MKTP.KD.ZG"
    
    # Parameters for the API request
    params = {
        "format": "json",
        "per_page": "100",  # Get more data than needed to ensure we have our date range
        "date": "2020:2024"  # Date range
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
    
    # Display the data
    st.subheader("GDP Growth Rate Data")
    display_df = df[['date', 'value']].copy()
    display_df.columns = ['Year', 'Growth Rate (%)']
    st.dataframe(display_df)
    
    # Get the most recent actual value (not null)
    latest = df[df['value'].notna()].iloc[-1]
    st.metric(
        label=f"Latest GDP Growth Rate ({latest['date'].year})",
        value=f"{latest['value']:.1f}%"
    )
    
    # Plot the time series
    st.subheader("GDP Growth Rate Trend")
    st.line_chart(df.set_index('date')['value'])
    
    # Add some context
    st.markdown("""
    **Note:**
    - Values after 2023 are projections
    - Negative values indicate economic contraction
    - Data source: World Bank
    """)

except Exception as e:
    st.error(f"Error fetching data from World Bank API: {str(e)}")
    st.write("URL attempted:", url)

