import streamlit as st
import pandas as pd
import yfinance as yf

st.title("Russell 1000 Companies")

@st.cache_data
def fetch_russell1000():
    """Fetch Russell 1000 constituents from iShares Russell 1000 ETF (IWB)"""
    try:
        # Get IWB holdings
        iwb = yf.Ticker("IWB")
        holdings = iwb.holdings
        
        # Convert to DataFrame and clean up
        df = pd.DataFrame(holdings)
        
        # Sort by weight descending
        df = df.sort_values('weight', ascending=False)
        
        # Convert weight to percentage
        df['weight'] = df['weight'].apply(lambda x: f"{x:.2f}%")
        
        return df
    except Exception as e:
        st.error(f"Error fetching Russell 1000 constituents: {str(e)}")
        return pd.DataFrame()

# Load Russell 1000 companies
companies_df = fetch_russell1000()

if not companies_df.empty:
    st.write(f"Loaded {len(companies_df)} companies from Russell 1000")
    st.dataframe(companies_df)
else:
    st.write("Error loading Russell 1000 companies.")
    