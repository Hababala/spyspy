import streamlit as st
from openbb import obb

# Initialize OpenBB authentication
if 'openbb_authenticated' not in st.session_state:
    st.session_state.openbb_authenticated = False

def init_openbb():
    try:
        # Use the same API key as in world.py
        api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdXRoX3Rva2VuIjoiTUJFNDhxaEtHYWlmdHJKVlN0eWZoVktxNmZlMGE5am41aGVnWkxDbiIsImV4cCI6MTc2Mjg5MzIyMH0.48URoFcEJ2dWF2SpWyj0B8MR-mBY8nc5lliHBuNR8bo"
        
        obb.account.login(pat=api_key)
        st.session_state.openbb_authenticated = True
        return True
    except Exception as e:
        st.error(f"Failed to authenticate with OpenBB: {str(e)}")
        return False

# Try to authenticate
if not st.session_state.openbb_authenticated:
    if not init_openbb():
        st.stop()

try:
    # Fetch US budget balance forecast
    budget_data = obb.economy.fiscal.balance(country="united states", forecast=True)
    
    # Convert to DataFrame and display
    if not budget_data.empty:
        st.title("US Budget Balance Forecast")
        st.dataframe(budget_data)
        
        # Extract 2025 forecast if available
        if 2025 in budget_data.index:
            forecast_2025 = budget_data.loc[2025]['Budget Balance (% of GDP)']
            st.metric("2025 Budget Balance Forecast (% of GDP)", f"{forecast_2025:.1f}%")
        else:
            st.warning("2025 forecast not available in the data")
    else:
        st.warning("No budget balance data available")

except Exception as e:
    st.error(f"Error fetching budget balance data: {str(e)}")

