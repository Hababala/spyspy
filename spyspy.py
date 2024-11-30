import streamlit as st
from openbb import obb

st.title("US Real GDP Growth 2023")

try:
    # Get GDP data from OpenBB
    gdp_data = obb.economy.gdp(country="united-states", start_date="2023-01-01", end_date="2023-12-31").to_df()
    
    # Display the data
    if not gdp_data.empty:
        # Get the most recent value for 2023
        gdp_2023 = gdp_data['value'].iloc[-1]
        
        # Display the metric
        st.metric(
            label="US Real GDP Growth (2023)",
            value=f"{gdp_2023:.1f}%"
        )
        
        # Show the full data table
        st.write("GDP Data:")
        st.dataframe(gdp_data)
    else:
        st.error("No GDP data available for 2023")

except Exception as e:
    st.error(f"Error fetching GDP data: {str(e)}")