import streamlit as st
import os
import sys

st.title("US Real GDP Growth 2023")

try:
    from openbb import obb
    
    # Initialize OpenBB authentication
    if 'openbb_authenticated' not in st.session_state:
        st.session_state.openbb_authenticated = False

    def init_openbb():
        try:
            if 'OPENBB_API_KEY' in st.secrets:
                api_key = st.secrets['OPENBB_API_KEY']
            else:
                api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdXRoX3Rva2VuIjoiTUJFNDhxaEtHYWlmdHJKVlN0eWZoVktxNmZlMGE5am41aGVnWkxDbiIsImV4cCI6MTc2Mjg5MzIyMH0.48URoFcEJ2dWF2SpWyj0B8MR-mBY8nc5lliHBuNR8bo"
            
            # Debug info
            st.write("Python path:", sys.executable)
            st.write("OpenBB path:", os.path.dirname(obb.__file__))
            
            obb.account.login(pat=api_key)
            st.session_state.openbb_authenticated = True
            return True
        except Exception as e:
            st.error(f"Failed to authenticate with OpenBB: {str(e)}")
            return False

    if not st.session_state.openbb_authenticated:
        if not init_openbb():
            st.stop()

    # Get GDP data
    gdp_data = obb.economy.gdp(country="united-states", start_date="2023-01-01", end_date="2023-12-31").to_df()
    
    if not gdp_data.empty:
        gdp_2023 = gdp_data['value'].iloc[-1]
        st.metric(label="US Real GDP Growth (2023)", value=f"{gdp_2023:.1f}%")
        st.write("GDP Data:")
        st.dataframe(gdp_data)
    else:
        st.error("No GDP data available for 2023")

except ImportError:
    st.error("Failed to import OpenBB. Please check installation.")
except Exception as e:
    st.error(f"Error: {str(e)}")
    st.write("Python version:", sys.version)