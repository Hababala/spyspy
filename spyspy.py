import streamlit as st
import pandas as pd

st.title("US Budget Balance Time Series")

# Your EconDB API token
api_token = "95f02e5d4dcd471ad575cd2ef8298d92b6d4d318"

# Define the ticker for US Budget Balance
ticker = 'USBB'  # Budget Balance ticker

try:
    # Fetch the data using pandas
    df = pd.read_csv(
        f"https://www.econdb.com/api/series/{ticker}/?format=csv&token={api_token}", 
        index_col='Date', parse_dates=True
    )
    
    # Ensure the index is a DatetimeIndex
    df.index = pd.to_datetime(df.index)

    # Display the entire DataFrame
    st.subheader("Full Budget Balance Data")
    st.dataframe(df)

    # Get the last 24 months of data
    recent_data = df.last('24M')
    
    if not recent_data.empty:
        st.subheader("Recent Budget Balance Data (Last 24 Months)")
        st.dataframe(recent_data)
        
        # Get the most recent value
        latest = recent_data.iloc[-1]
        st.metric(
            label=f"Latest Budget Balance (Date: {latest.name.strftime('%Y-%m-%d')})", 
            value=f"${latest['Value']:,.2f} Billion",
            delta=f"{latest['Value'] - recent_data.iloc[-2]['Value']:,.2f}B vs Previous"
        )
        
        # Plot the time series
        st.subheader("Budget Balance Trend")
        fig_data = recent_data.copy()
        st.line_chart(fig_data['Value'])
        
        # Calculate year-over-year change
        if len(recent_data) > 12:  # Ensure we have enough data for YoY calculation
            yoy_change = latest['Value'] - recent_data.iloc[-13]['Value']
            st.metric(
                label="Year-over-Year Change",
                value=f"${yoy_change:,.2f}B",
                delta=f"{(yoy_change/abs(recent_data.iloc[-13]['Value'])*100):,.1f}%"
            )
    else:
        st.warning("No recent Budget Balance data available")

except Exception as e:
    st.error(f"Error fetching data from EconDB: {str(e)}")
    # Print the URL for debugging
    st.write(f"URL attempted: https://www.econdb.com/api/series/{ticker}/?format=csv&token={api_token}")

