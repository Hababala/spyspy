import streamlit as st
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import time
import urllib.parse

# Cache the company descriptions
@st.cache_data(ttl=24*3600)  # Cache for 24 hours
def get_company_description(ticker):
    """Fetch company description from SEC filings"""
    try:
        # Add proper headers to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

        # Construct the search URL properly
        base_url = "https://www.sec.gov"
        search_url = f"{base_url}/cgi-bin/browse-edgar"
        params = {
            'CIK': ticker,
            'owner': 'exclude',
            'action': 'getcompany',
            'type': '10-K'
        }
        
        # Make the initial request
        response = requests.get(search_url, params=params, headers=headers)
        if response.status_code != 200:
            st.warning(f"Failed to fetch data for {ticker}: Status {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the link to the most recent 10-K filing
        filing_links = soup.find_all('a', {'id': 'interactiveDataBtn'})
        if not filing_links:
            st.warning(f"No 10-K filings found for {ticker}")
            return None

        # Get the first (most recent) 10-K filing URL
        filing_url = urllib.parse.urljoin(base_url, filing_links[0]['href'])
        
        # Add a delay to respect rate limits
        time.sleep(0.1)

        # Fetch the 10-K filing
        filing_response = requests.get(filing_url, headers=headers)
        if filing_response.status_code != 200:
            st.warning(f"Failed to fetch 10-K for {ticker}: Status {filing_response.status_code}")
            return None
            
        filing_soup = BeautifulSoup(filing_response.text, 'html.parser')

        # Try different methods to find the business description
        description = None
        
        # Method 1: Look for "Business" section
        business_section = filing_soup.find('span', string='Business')
        if business_section:
            description = business_section.find_next('p')
            
        # Method 2: Look for "Item 1. Business" section
        if not description:
            business_section = filing_soup.find('span', string='Item 1. Business')
            if business_section:
                description = business_section.find_next('p')

        if description:
            return description.text.strip()
        else:
            st.warning(f"Could not find business description for {ticker}")
            return None

    except Exception as e:
        st.error(f"Error fetching description for {ticker}: {str(e)}")
        return None

def fetch_descriptions_batch(tickers, progress_bar):
    """Fetch descriptions for a batch of tickers with progress tracking"""
    descriptions = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        for ticker in tickers:
            description = get_company_description(ticker)
            if description:
                descriptions[ticker] = description
            progress_bar.progress((len(descriptions) + 1) / len(tickers))
            time.sleep(0.1)  # Respect SEC rate limits
    return descriptions

# Streamlit UI
st.title("SEC Company Description Search")

# Input for keywords
keywords = st.text_input("Enter keywords (separated by commas):", "").lower().split(',')
keywords = [k.strip() for k in keywords if k.strip()]

if keywords:
    # Load or fetch company descriptions
    if 'company_descriptions' not in st.session_state:
        st.session_state.company_descriptions = {}
        
        # Get list of tickers (you might want to customize this list)
        # For example, you could use a pre-defined list of major stocks
        example_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'EXAS']
        
        progress_bar = st.progress(0)
        st.write("Fetching company descriptions... This may take a while.")
        
        st.session_state.company_descriptions = fetch_descriptions_batch(example_tickers, progress_bar)
        progress_bar.empty()

    # Filter companies based on keywords
    matching_companies = {}
    for ticker, description in st.session_state.company_descriptions.items():
        if description and all(keyword in description.lower() for keyword in keywords):
            matching_companies[ticker] = description

    # Display results
    if matching_companies:
        st.success(f"Found {len(matching_companies)} companies matching all keywords")
        
        # Create a selection box for matching companies
        selected_ticker = st.selectbox(
            "Select a company to view full description:",
            options=list(matching_companies.keys())
        )
        
        if selected_ticker:
            st.subheader(f"{selected_ticker} Description")
            st.write(matching_companies[selected_ticker])
            
            # Add stock price chart
            try:
                stock = yf.Ticker(selected_ticker)
                hist = stock.history(period="1y")
                st.line_chart(hist.Close)
            except Exception as e:
                st.error(f"Error fetching stock data: {str(e)}")
            
            # Add download button for description
            if st.button("Download Description"):
                st.download_button(
                    label="Download as Text",
                    data=matching_companies[selected_ticker],
                    file_name=f"{selected_ticker}_description.txt",
                    mime="text/plain"
                )
    else:
        st.warning("No companies found matching all keywords")

# Add some helpful information
with st.sidebar:
    st.subheader("How to Use")
    st.write("""
    1. Enter keywords separated by commas
    2. The app will search for companies whose descriptions contain ALL keywords
    3. Select a company from the results to view its full description
    4. You can also view the stock price chart and download the description
    """)
    
    st.subheader("Example Keywords")
    st.write("""
    - technology, software
    - healthcare, medical
    - retail, consumer
    - energy, renewable
    """)