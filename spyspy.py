import streamlit as st
import pandas as pd
import requests
import yfinance as yf
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

st.title("US Listed Companies")

# File paths
DATA_DIR = "data"
COMPANIES_FILE = os.path.join(DATA_DIR, "company_details.json")
LAST_UPDATE_FILE = os.path.join(DATA_DIR, "last_update.txt")

def should_update_data():
    """Check if data should be updated (older than 7 days)"""
    if not os.path.exists(LAST_UPDATE_FILE):
        return True
    
    with open(LAST_UPDATE_FILE, 'r') as f:
        last_update = datetime.strptime(f.read().strip(), '%Y-%m-%d')
    
    return datetime.now() - last_update > timedelta(days=7)

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

@st.cache_data
def fetch_and_store_company_details():
    """Fetch all company details and store them"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # First get the list of companies
    companies_df = fetch_us_companies()
    tickers = companies_df['ticker'].tolist()
    
    # Fetch details in parallel
    with st.spinner('Updating company database... This may take a few minutes.'):
        all_details = fetch_details_parallel(tickers)
    
    # Store the data
    data = {
        'companies': companies_df.to_dict(orient='records'),
        'details': all_details
    }
    
    with open(COMPANIES_FILE, 'w') as f:
        json.dump(data, f)
    
    # Update last update time
    with open(LAST_UPDATE_FILE, 'w') as f:
        f.write(datetime.now().strftime('%Y-%m-%d'))
    
    return data

def load_company_data():
    """Load company data from file or fetch if needed"""
    if not os.path.exists(COMPANIES_FILE) or should_update_data():
        return fetch_and_store_company_details()
    
    with open(COMPANIES_FILE, 'r') as f:
        return json.load(f)

# Load data
data = load_company_data()
companies_df = pd.DataFrame(data['companies'])
company_details = {detail['ticker']: detail for detail in data['details']}

# Search interface
search_query = st.text_input("Enter keywords to search in company descriptions:", "").lower()

if search_query:
    # Filter companies based on description
    filtered_companies = []
    for ticker, details in company_details.items():
        if search_query in details['description']:
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