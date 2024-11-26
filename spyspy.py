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
def fetch_company_description(cik):
    """Fetch company description from SEC filings"""
    url = "https://api.sec-api.io/full-text-search"
    api_key = "your_api_key_here"  # You'll need to sign up for an API key
    
    # Query for the most recent 10-K filing's business description
    query = {
        "query": {
            "query_string": {
                "query": "\"Item 1. Business\"",
                "fields": ["text"]
            }
        },
        "from": "0",
        "size": "1",
        "sort": [{"filedAt": {"order": "desc"}}]
    }
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            f"{url}?cik={cik}",
            headers=headers,
            json=query
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['filings']:
                # Extract the business description section
                text = data['filings'][0]['text']
                # Find the section between "Item 1. Business" and "Item 1A. Risk Factors"
                start = text.find("Item 1. Business")
                end = text.find("Item 1A. Risk Factors")
                if start != -1 and end != -1:
                    description = text[start:end].strip()
                    # Truncate and clean up the description
                    return description[:1000] + "..."
        return "No description available"
    except Exception as e:
        return f"Error fetching description: {str(e)}"

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
            
            # Add company descriptions
            df['description'] = df['cik_str'].apply(lambda x: fetch_company_description(x))
            
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
    filtered_df = companies_df[
        companies_df['description'].str.lower().str.contains(search_query, na=False)
    ]
    
    if not filtered_df.empty:
        st.write(f"Found {len(filtered_df)} companies matching your search:")
        st.dataframe(
            filtered_df[['ticker', 'title', 'description']],
            use_container_width=True
        )
    else:
        st.write("No companies found matching your search criteria.")
else:
    st.write("Enter keywords to search through company descriptions.")