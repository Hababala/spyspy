import streamlit as st
import pandas as pd

st.title("US GDP 2022-2023")

# Your EconDB API token
api_token = "95f02e5d4dcd471ad575cd2ef8298d92b6d4d318"

# Define the ticker for US GDP
ticker = 'USGDP'

try:
    # Fetch the data using pandas
    df = pd.read_csv(
        f"https://www.econdb.com/api/series/{ticker}/?format=csv&token={api_token}", 
        index_col='Date', parse_dates=True
    )
    
    # Ensure the index is a DatetimeIndex
    df.index = pd.to_datetime(df.index)

    # Display the entire DataFrame for debugging
    st.subheader("Full GDP Data")
    st.dataframe(df)

    # Filter for 2022-2023 data
    gdp_recent = df[df.index.year.isin([2022, 2023])]
    
    if not gdp_recent.empty:
        st.subheader("US GDP Data 2022-2023")
        st.dataframe(gdp_recent)
        
        # Get the most recent value
        latest = gdp_recent.iloc[-1]
        st.metric(
            label=f"Latest GDP (Date: {latest.name.strftime('%Y-%m-%d')})", 
            value=f"${latest['Value']:,.2f} Billion"
        )
        
        # Plot the data
        st.line_chart(gdp_recent['Value'])
        
        # Calculate year-over-year growth
        if len(gdp_recent) > 4:  # Ensure we have enough data for YoY calculation
            yoy_growth = ((latest['Value'] / gdp_recent.iloc[-5]['Value']) - 1) * 100
            st.metric(
                label="Year-over-Year Growth",
                value=f"{yoy_growth:.1f}%"
            )
    else:
        st.warning("No GDP data available for 2022-2023")

except Exception as e:
    st.error(f"Error fetching data from EconDB: {str(e)}")
    # Print the URL for debugging
    st.write(f"URL attempted: https://www.econdb.com/api/series/{ticker}/?format=csv&token={api_token}")

