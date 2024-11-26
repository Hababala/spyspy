import streamlit as st
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import time

# Cache the company descriptions
@st.cache_data(ttl=24*3600)  # Cache for 24 hours
def get_company_description(ticker):
    """Fetch company description from SEC filings"""
    try:
        # Search for the company's filings
        search_url = f"https://www.sec.gov/cgi-bin/browse-edgar?company={ticker}&owner=exclude&action=getcompany"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the link to the most recent 10-K filing
        filings = soup.find_all('a', href=True)
        filing_url = None
        for filing in filings:
            if '10-K' in filing.text:
                filing_url = "https://www.sec.gov" + filing['href']
                break
        
        if not filing_url:
            return None

        # Fetch the 10-K filing
        filing_response = requests.get(filing_url, headers=headers)
        filing_soup = BeautifulSoup(filing_response.text, 'html.parser')

        # Extract the company description
        description_section = filing_soup.find(text="Business").find_next('p')
        if description_section:
            return description_section.text.strip()
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