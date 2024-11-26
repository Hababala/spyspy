import streamlit as st
import pandas as pd
import yfinance as yf

st.title("Russell 1000 Companies")

@st.cache_data
def fetch_russell1000():
    """Fetch Russell 1000 constituents from iShares Russell 1000 ETF (IWB)"""
    try:
        # Get IWB info
        iwb = yf.Ticker("IWB")
        
        # Get holdings from download method
        holdings = iwb.get_holdings()
        
        # Convert to DataFrame and clean up
        df = pd.DataFrame(holdings)
        
        # Sort by weight descending
        df = df.sort_values('% of ETF', ascending=False)
        
        # Rename columns for clarity
        df = df.rename(columns={
            'Symbol': 'ticker',
            'Name': 'company',
            '% of ETF': 'weight'
        })
        
        return df
    except Exception as e:
        st.error(f"Error fetching Russell 1000 constituents: {str(e)}")
        st.write("Error details:", str(e))  # Add this line for debugging
        return pd.DataFrame()

# Load Russell 1000 companies
companies_df = fetch_russell1000()

if not companies_df.empty:
    st.write(f"Loaded {len(companies_df)} companies from Russell 1000")
    st.dataframe(companies_df)
else:
    st.write("Error loading Russell 1000 companies.")
    