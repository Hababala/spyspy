import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import numpy as np
from scipy import stats
import pandas as pd
import requests
import time

st.title("Stock Market Analysis")

@st.cache_data
def get_sec_companies():
    """Get all companies from SEC API"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'www.sec.gov',
        'Accept': 'application/json',
        'Connection': 'keep-alive'
    }
    
    try:
        # Add delay to comply with SEC rate limits
        time.sleep(0.1)
        url = "https://www.sec.gov/files/company_tickers.json"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            st.error(f"Error: Status code {response.status_code}")
            st.write("Response content:", response.text)  # Debug info
            return pd.DataFrame()
            
        companies_dict = response.json()
        
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(companies_dict, orient='index')
        st.write("Debug - DataFrame columns:", df.columns.tolist())
        st.write("Debug - First few rows:", df.head())  # Debug info
        
        return df
    except Exception as e:
        st.error(f"Error fetching companies: {str(e)}")
        st.write("Full error:", str(e))  # Debug info
        return pd.DataFrame()

# Get companies list
companies_df = get_sec_companies()

if not companies_df.empty:
    # Use correct column name based on debug output
    symbols_list = companies_df['ticker'].tolist()  # Will adjust based on actual column name
    
    # Add search box
    search_query = st.text_input("Search for a symbol:", "")

    if search_query:
        # Filter symbols (show max 10 results)
        filtered_symbols = [s for s in symbols_list if search_query.upper() in s.upper()][:10]
        
        if filtered_symbols:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                selected_symbol = st.radio("Select a symbol:", filtered_symbols)
                st.session_state.selected_symbol = selected_symbol
        
        if selected_symbol:
            # Show detailed data in tabs
            tab1, tab2 = st.tabs(["Price Data", "Chart"])
            
            with tab1:
                st.write("Recent Price Data:")
                st.write(ticker.history(period="5d"))
            
            with tab2:
                hist_data = ticker.history(period="ytd")
                fig = go.Figure(data=go.Scatter(x=hist_data.index, y=hist_data['Close']))
                fig.update_layout(
                    title=f"{selected_symbol} YTD Performance",
                    yaxis_title="Price",
                    xaxis_title="Date"
                )
                st.plotly_chart(fig)
    else:
        st.write("No matching symbols found.")

# Add company info if a symbol is selected
if 'selected_symbol' in st.session_state:
    st.markdown("---")
    st.subheader("Company Information")
    
    try:
        ticker = yf.Ticker(st.session_state.selected_symbol)
        info = ticker.info
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Sector:**", info.get('sector', 'N/A'))
            st.write("**Industry:**", info.get('industry', 'N/A'))
            st.write("**Market Cap:**", f"${info.get('marketCap', 0):,}")
        
        with col2:
            st.write("**52 Week High:**", f"${info.get('fiftyTwoWeekHigh', 0):.2f}")
            st.write("**52 Week Low:**", f"${info.get('fiftyTwoWeekLow', 0):.2f}")
            st.write("**Beta:**", f"{info.get('beta', 0):.2f}")
        
        st.write("**Business Summary:**")
        st.write(info.get('longBusinessSummary', 'No description available.'))
        
    except Exception as e:
        st.error(f"Error loading company information: {str(e)}")