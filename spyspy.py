import streamlit as st
import pandas as pd
import yfinance as yf

st.title("Top 1000 US Companies by Market Cap")

@st.cache_data
def fetch_top_1000():
    """Fetch top 1000 US companies by market cap"""
    try:
        # Use S&P 500 as a starting point to get major tickers
        sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
        nasdaq = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')[4]
        
        # Combine and get unique tickers
        tickers = pd.concat([
            sp500['Symbol'],
            nasdaq['Ticker']
        ]).unique()
        
        # Fetch market cap and other info for each company
        companies = []
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                companies.append({
                    'ticker': ticker,
                    'name': info.get('longName', 'N/A'),
                    'market_cap': info.get('marketCap', 0),
                    'sector': info.get('sector', 'N/A'),
                    'industry': info.get('industry', 'N/A')
                })
            except:
                continue
        
        # Convert to DataFrame and sort by market cap
        df = pd.DataFrame(companies)
        df = df.sort_values('market_cap', ascending=False).head(1000)
        
        # Format market cap
        df['market_cap'] = df['market_cap'].apply(lambda x: f"${x/1e9:.2f}B" if x > 0 else 'N/A')
        
        return df
    
    except Exception as e:
        st.error(f"Error fetching companies: {str(e)}")
        return pd.DataFrame()

# Load companies
companies_df = fetch_top_1000()

if not companies_df.empty:
    # Add search functionality
    search_query = st.text_input("Search companies by name or ticker:", "").lower()
    
    if search_query:
        filtered_df = companies_df[
            companies_df['name'].str.lower().str.contains(search_query, na=False) |
            companies_df['ticker'].str.lower().str.contains(search_query, na=False)
        ]
        st.write(f"Found {len(filtered_df)} matching companies:")
        st.dataframe(filtered_df)
    else:
        st.write(f"Showing all {len(companies_df)} companies:")
        st.dataframe(companies_df)
else:
    st.write("Error loading companies.")