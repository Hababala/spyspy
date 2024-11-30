import streamlit as st
import pandas as pd

st.title("Germany CPI 2023")

# Your EconDB API token
api_token = "95f02e5d4dcd471ad575cd2ef8298d92b6d4d318"

# Define the ticker for Germany's CPI
ticker = 'DECPI'

try:
    # Fetch the data using pandas
    df = pd.read_csv(
        f"https://www.econdb.com/api/series/{ticker}/?format=csv&token={api_token}", 
        index_col='Date', parse_dates=True
    )
    
    # Ensure the index is a DatetimeIndex
    df.index = pd.to_datetime(df.index)

    # Filter for 2023 data
    cpi_2023 = df[df.index.year == 2023]
    
    if not cpi_2023.empty:
        st.subheader("Germany CPI Data 2023")
        st.dataframe(cpi_2023)
        
        # Get the most recent value
        latest = cpi_2023.iloc[-1]
        st.metric(
            label=f"Latest CPI (Date: {latest.name.strftime('%Y-%m-%d')})", 
            value=f"{latest['Value']:.1f}"
        )
        
        # Plot the data
        st.line_chart(cpi_2023['Value'])
    else:
        st.warning("No 2023 CPI data available")

except Exception as e:
    st.error(f"Error fetching data from EconDB: {str(e)}")

