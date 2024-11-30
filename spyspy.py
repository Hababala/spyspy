import streamlit as st
from openbb import obb

st.title("US Real GDP Growth 2023")

try:
    # Initialize OpenBB with API key
    if 'OPENBB_API_KEY' in st.secrets:
        api_key = st.secrets['OPENBB_API_KEY']
    else:
        api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdXRoX3Rva2VuIjoiTUJFNDhxaEtHYWlmdHJKVlN0eWZoVktxNmZlMGE5am41aGVnWkxDbiIsImV4cCI6MTc2Mjg5MzIyMH0.48URoFcEJ2dWF2SpWyj0B8MR-mBY8nc5lliHBuNR8bo"
    
    obb.account.login(pat=api_key)
    
    # Get GDP data for 2023
    gdp_data = obb.economy.gdp(
        country="united-states", 
        start_date="2023-01-01", 
        end_date="2023-12-31"
    ).to_df()
    
    # Display the data
    if not gdp_data.empty:
        gdp_2023 = gdp_data['value'].iloc[-1]
        st.metric(
            label="US Real GDP Growth (2023)",
            value=f"{gdp_2023:.1f}%"
        )
        st.write("GDP Data:")
        st.dataframe(gdp_data)
    else:
        st.error("No GDP data available for 2023")

except Exception as e:
    st.error(f"Error: {str(e)}")