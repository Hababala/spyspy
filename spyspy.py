import streamlit as st
from openbb import obb
import pandas as pd
import os

# Set up OpenBB credentials
api_key = st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdXRoX3Rva2VuIjoiQWpIZ2hsazVtcXk0VEV5V1FEUFRlakpqS3NYQjcxOXd5NzhyRjI2MiIsImV4cCI6MTc2Mjg4OTc4N30.4cKXMKxmZxc9CgWPIyAjF7T8nCyH0gThySmeACR-I1o"]
obb.account.login(pat=api_key)

#obb.user.credentials.fmp_api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdXRoX3Rva2VuIjoiQWpIZ2hsazVtcXk0VEV5V1FEUFRlakpqS3NYQjcxOXd5NzhyRjI2MiIsImV4cCI6MTc2Mjg4OTc4N30.4cKXMKxmZxc9CgWPIyAjF7T8nCyH0gThySmeACR-I1o"



st.title("Apple Stock Price - Last Year")

@st.cache_data
def get_apple_data():
    """Fetch Apple stock data for the last year"""
    try:
        # Get AAPL data from OpenBB
        aapl_data = obb.stocks.price.historical("AAPL", interval="1d", start="1 year ago")
        return aapl_data
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return pd.DataFrame()

# Get the data
df = get_apple_data()

if not df.empty:
    # Display the stock chart
    st.line_chart(df['Close'])
    
    # Display the data table
    st.write("Historical Data:")
    st.dataframe(df)
else:
    st.write("Error loading Apple stock data.")