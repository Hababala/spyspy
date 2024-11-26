import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

st.title("Russell 1000 Companies by Market Cap")

@st.cache_data(show_spinner=False)
def fetch_russell1000_tickers():
    """Fetch Russell 1000 tickers from a reliable GitHub source."""
    url = "https://raw.githubusercontent.com/datasets/russell-1000-companies/main/data/russell-1000.csv"
    try:
        response = requests.get(url)
        response.raise_for_status()
        df = pd.read_csv(pd.compat.StringIO(response.text))
        tickers = df['Ticker'].tolist()
        return tickers
    except Exception as e:
        st.error(f"Error fetching Russell 1000 tickers: {e}")
        return []

@st.cache_data(show_spinner=False)
def fetch_company_info(ticker):
    """Fetch company information using yfinance."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        description = info.get('longBusinessSummary', 'No description available.').lower()
        market_cap = info.get('marketCap', 'N/A')
        sector = info.get('sector', 'N/A')
        industry = info.get('industry', 'N/A')
        return {
            'Ticker': ticker,
            'Name': info.get('longName', 'N/A'),
            'Market Cap': f"${market_cap/1e9:.2f}B" if isinstance(market_cap, (int, float)) else 'N/A',
            'Sector': sector,
            'Industry': industry,
            'Description': description[:200] + '...' if len(description) > 200 else description
        }
    except Exception as e:
        return {
            'Ticker': ticker,
            'Name': 'N/A',
            'Market Cap': 'N/A',
            'Sector': 'N/A',
            'Industry': 'N/A',
            'Description': 'N/A'
        }

@st.cache_data(show_spinner=False)
def fetch_all_company_data(tickers):
    """Fetch data for all tickers using multithreading."""
    company_data = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_ticker = {executor.submit(fetch_company_info, ticker): ticker for ticker in tickers}
        for future in as_completed(future_to_ticker):
            data = future.result()
            company_data.append(data)
    df = pd.DataFrame(company_data)
    df = df.sort_values('Market Cap', ascending=False)
    return df

# Fetch Russell 1000 tickers
tickers = fetch_russell1000_tickers()

if tickers:
    st.info("Fetching company data. Please wait...")
    # Fetch all company data
    companies_df = fetch_all_company_data(tickers)
    
    if not companies_df.empty:
        st.success("Data loaded successfully!")
        
        # Search functionality
        search_query = st.text_input("Search companies by keyword in description:", "").lower()
        
        if search_query:
            filtered_df = companies_df[companies_df['Description'].str.contains(search_query, na=False)]
            st.write(f"Found {len(filtered_df)} companies matching your search:")
            st.dataframe(filtered_df[['Ticker', 'Name', 'Market Cap', 'Sector', 'Industry']])
        else:
            st.write(f"Showing all {len(companies_df)} Russell 1000 companies:")
            st.dataframe(companies_df[['Ticker', 'Name', 'Market Cap', 'Sector', 'Industry']])
    else:
        st.write("No company data available.")
else:
    st.write("Failed to retrieve Russell 1000 tickers.")