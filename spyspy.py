import streamlit as st
import pandas as pd
import yfinance as yf
import requests

st.title("Russell 1000 Companies")

@st.cache_data
def fetch_russell1000():
    """Fetch Russell 1000 constituents"""
    # Using Wikipedia as a quick source for Russell 1000 constituents
    url = "https://en.wikipedia.org/wiki/Russell_1000_Index"
    
    try:
        # Read all tables from the Wikipedia page
        tables = pd.read_html(url)
        # The constituents table is typically the first table
        df = tables[0]
        
        # Clean up column names
        df.columns = ['ticker', 'company', 'sector', 'industry']
        
        return df
    except Exception as e:
        st.error(f"Error fetching Russell 1000 constituents: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def fetch_stock_info(ticker):
    """Fetch basic stock information"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            'Market Cap': info.get('marketCap', 'N/A'),
            'Sector': info.get('sector', 'N/A'),
            'Industry': info.get('industry', 'N/A'),
            'Description': info.get('longBusinessSummary', 'N/A')
        }
    except:
        return {
            'Market Cap': 'N/A',
            'Sector': 'N/A',
            'Industry': 'N/A',
            'Description': 'N/A'
        }

# Load Russell 1000 companies
companies_df = fetch_russell1000()

# Search interface
search_query = st.text_input("Search for companies (name or ticker):", "").lower()

if not companies_df.empty:
    if search_query:
        # Filter companies based on search query
        filtered_df = companies_df[
            companies_df['company'].str.lower().str.contains(search_query, na=False) |
            companies_df['ticker'].str.lower().str.contains(search_query, na=False)
        ]
        
        if not filtered_df.empty:
            st.write(f"Found {len(filtered_df)} companies matching your search.")
            
            # Option to fetch detailed info
            if st.button("Load detailed information"):
                with st.spinner('Fetching company details...'):
                    details = []
                    for _, row in filtered_df.iterrows():
                        info = fetch_stock_info(row['ticker'])
                        details.append({
                            'Ticker': row['ticker'],
                            'Company': row['company'],
                            'Market Cap': f"${info['Market Cap']/1e9:.2f}B" if isinstance(info['Market Cap'], (int, float)) else 'N/A',
                            'Sector': info['Sector'],
                            'Industry': info['Industry'],
                            'Description': info['Description'][:200] + '...' if len(info['Description']) > 200 else info['Description']
                        })
                    
                    details_df = pd.DataFrame(details)
                    st.dataframe(details_df, use_container_width=True)
            else:
                # Show basic info
                st.dataframe(filtered_df, use_container_width=True)
        else:
            st.write("No companies found matching your search criteria.")
    else:
        st.write(f"Showing all {len(companies_df)} Russell 1000 companies:")
        st.dataframe(companies_df, use_container_width=True)
else:
    st.write("Error loading Russell 1000 companies.")