import streamlit as st
import pandas as pd
import requests
import yfinance as yf
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

st.title("US Listed Companies")

@st.cache_data
def fetch_us_companies():
    """Fetch all US listed companies using SEC API"""
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {
        'User-Agent': 'YourAppName/1.0 (Contact: your-email@example.com)',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'www.sec.gov'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            companies_dict = response.json()
            df = pd.DataFrame.from_dict(companies_dict, orient='index')
            df.columns = ['cik_str', 'ticker', 'title']
            return df
        else:
            st.error(f"Error: Status code {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching companies: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def fetch_company_details_batch(ticker):
    """Fetch company details with caching"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            'ticker': ticker,
            'description': info.get('longBusinessSummary', '').lower(),
            'sector': info.get('sector', 'N/A'),
            'market_cap': info.get('marketCap', 'N/A')
        }
    except Exception as e:
        return {
            'ticker': ticker,
            'description': '',
            'sector': 'N/A',
            'market_cap': 'N/A'
        }

def fetch_details_parallel(tickers, max_workers=10):
    """Fetch company details in parallel"""
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ticker = {executor.submit(fetch_company_details_batch, ticker): ticker 
                          for ticker in tickers}
        for future in as_completed(future_to_ticker):
            try:
                data = future.result()
                results.append(data)
            except Exception as e:
                st.error(f"Error fetching details: {str(e)}")
    return results

# Fetch companies
companies_df = fetch_us_companies()

if not companies_df.empty:
    search_query = st.text_input("Enter keywords to search in company descriptions:", "").lower()
    
    if search_query:
        st.info("Fetching and filtering companies... This may take a moment.")
        
        # Get all tickers
        tickers = companies_df['ticker'].tolist()
        
        # Fetch details in parallel
        with st.spinner('Loading company details...'):
            all_details = fetch_details_parallel(tickers)
        
        # Filter companies based on description
        filtered_companies = []
        for details in all_details:
            if search_query in details['description']:
                ticker = details['ticker']
                company = companies_df[companies_df['ticker'] == ticker].iloc[0]
                
                # Format market cap
                market_cap = details['market_cap']
                if isinstance(market_cap, (int, float)) and market_cap != 'N/A':
                    market_cap = f"${market_cap/1e9:.2f}B"
                
                # Truncate description
                description = details['description'][:200] + '...' if len(details['description']) > 200 else details['description']
                
                filtered_companies.append({
                    'Ticker': ticker,
                    'Name': company['title'],
                    'Description': description,
                    'Sector': details['sector'],
                    'Market Cap': market_cap
                })
        
        if filtered_companies:
            detailed_df = pd.DataFrame(filtered_companies)
            st.write(f"Found {len(filtered_companies)} companies matching your search:")
            st.dataframe(detailed_df, use_container_width=True)
        else:
            st.write("No companies found matching your search criteria.")
    else:
        st.write("Enter keywords to search through company descriptions.")
else:
    st.write("No company data available.")