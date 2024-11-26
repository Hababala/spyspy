import streamlit as st
import yfinance as yf
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor
import time

@st.cache_data
def load_all_tickers():
    """Load all US listed companies"""
    try:
        # NASDAQ stocks
        nasdaq = pd.read_csv('https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqtraded.txt', sep='|')
        nasdaq_tickers = nasdaq[nasdaq['Test Issue'] == 'N']['Symbol'].tolist()
        
        # NYSE stocks (alternative source)
        nyse_url = "https://www.nyse.com/api/quotes/filter"
        nyse = pd.read_json(nyse_url)
        nyse_tickers = nyse['symbolTicker'].tolist()
        
        # Combine and clean tickers
        all_tickers = list(set(nasdaq_tickers + nyse_tickers))
        # Remove warrants, preferred stocks, etc.
        clean_tickers = [t for t in all_tickers if not any(x in t for x in ['-', '^', '.', '$'])]
        
        return clean_tickers
        
    except Exception as e:
        st.error(f"Error loading tickers: {str(e)}")
        # Fallback to a smaller list from Yahoo Finance
        return pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'].tolist()

@st.cache_data(ttl=24*3600)
def get_company_info(ticker):
    """Get company info for a single ticker"""
    try:
        company = yf.Ticker(ticker)
        info = company.info
        if 'longBusinessSummary' in info:
            return {
                'ticker': ticker,
                'name': info.get('longName', 'N/A'),
                'description': info['longBusinessSummary'],
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'website': info.get('website', 'N/A')
            }
    except Exception as e:
        return None

def fetch_companies_batch(tickers, progress_bar=None):
    """Fetch company info for a batch of tickers"""
    companies = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_ticker = {executor.submit(get_company_info, ticker): ticker for ticker in tickers}
        for i, future in enumerate(future_to_ticker):
            try:
                result = future.result()
                if result:
                    companies[result['ticker']] = result
                if progress_bar:
                    progress_bar.progress((i + 1) / len(tickers))
            except Exception as e:
                continue
    return companies

# Streamlit UI
st.title("US Stock Market Company Search")

# Initialize or load company data
if 'all_companies' not in st.session_state:
    st.session_state.all_companies = {}
    
    # Load tickers
    tickers = load_all_tickers()
    st.info(f"Loading data for {len(tickers)} companies... This may take a while.")
    
    # Create progress bar
    progress_bar = st.progress(0)
    
    # Fetch company data in batches
    batch_size = 100
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        companies_batch = fetch_companies_batch(batch)
        st.session_state.all_companies.update(companies_batch)
        progress_bar.progress(min((i + batch_size) / len(tickers), 1.0))
    
    progress_bar.empty()

# Search interface
col1, col2 = st.columns([2, 1])
with col1:
    keywords = st.text_input("Enter keywords (separated by commas):", "").split(',')
    keywords = [k.strip() for k in keywords if k.strip()]

with col2:
    min_market_cap = st.number_input("Minimum Market Cap (USD Millions)", 0, 1000000, 0)

# Sector filter
sectors = list(set(info['sector'] for info in st.session_state.all_companies.values() if info['sector'] != 'N/A'))
selected_sector = st.selectbox("Filter by sector:", ["All"] + sorted(sectors))

if keywords:
    # Filter companies
    matching_companies = {}
    for ticker, info in st.session_state.all_companies.items():
        if info['description'] and all(k.lower() in info['description'].lower() for k in keywords):
            if selected_sector == "All" or info['sector'] == selected_sector:
                if info['market_cap'] >= min_market_cap * 1_000_000:  # Convert to millions
                    matching_companies[ticker] = info
    
    # Display results
    if matching_companies:
        st.success(f"Found {len(matching_companies)} matching companies")
        
        # Sort by market cap
        sorted_companies = dict(sorted(
            matching_companies.items(),
            key=lambda x: x[1]['market_cap'],
            reverse=True
        ))
        
        # Company selection
        selected_ticker = st.selectbox(
            "Select a company:",
            options=list(sorted_companies.keys()),
            format_func=lambda x: f"{x} - {sorted_companies[x]['name']} (${sorted_companies[x]['market_cap']:,})"
        )
        
        if selected_ticker:
            company_info = sorted_companies[selected_ticker]
            
            # Display company details
            st.subheader(f"{selected_ticker} - {company_info['name']}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Sector:**", company_info['sector'])
                st.write("**Industry:**", company_info['industry'])
            with col2:
                st.write("**Website:**", company_info['website'])
                st.write("**Market Cap:** $", f"{company_info['market_cap']:,}")
            
            st.subheader("Business Description")
            st.write(company_info['description'])
            
            # Stock chart
            st.subheader("Stock Price (1 Year)")
            stock = yf.Ticker(selected_ticker)
            hist = stock.history(period="1y")
            st.line_chart(hist.Close)
    else:
        st.warning("No companies found matching all keywords")

# Sidebar with tips
with st.sidebar:
    st.subheader("Search Tips")
    st.write("""
    - Enter multiple keywords separated by commas
    - Filter by sector and market cap
    - Results are sorted by market cap
    - Data is cached for 24 hours
    """)
    
    st.subheader("Example Searches")
    st.write("""
    - biotech, cancer
    - cloud, software
    - electric vehicles
    - renewable energy
    """)