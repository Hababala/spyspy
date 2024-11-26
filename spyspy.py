import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import urllib.parse

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
        
        st.write("Searching for SEC filings...")
        response = requests.get(search_url, params=params, headers=headers)
        st.write(f"Search response status: {response.status_code}")
        
        if response.status_code != 200:
            st.warning(f"Failed to fetch data for {ticker}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        st.write("Parsing search results...")

        # Find the link to the most recent 10-K filing
        filing_links = soup.find_all('a', {'id': 'interactiveDataBtn'})
        if not filing_links:
            st.warning(f"No 10-K filings found for {ticker}")
            return None

        # Get the first (most recent) 10-K filing URL
        filing_url = urllib.parse.urljoin(base_url, filing_links[0]['href'])
        st.write(f"Found 10-K filing URL: {filing_url}")
        
        # Add a delay to respect rate limits
        time.sleep(0.1)

        # Fetch the 10-K filing
        filing_response = requests.get(filing_url, headers=headers)
        st.write(f"Filing response status: {filing_response.status_code}")
        
        if filing_response.status_code != 200:
            st.warning(f"Failed to fetch 10-K")
            return None
            
        filing_soup = BeautifulSoup(filing_response.text, 'html.parser')
        st.write("Parsing 10-K content...")

        # Try different methods to find the business description
        description = None
        
        # Method 1: Look for "Business" section
        business_section = filing_soup.find('span', string='Business')
        if business_section:
            description = business_section.find_next('p')
            st.write("Found description using Method 1")
            
        # Method 2: Look for "Item 1. Business" section
        if not description:
            business_section = filing_soup.find('span', string='Item 1. Business')
            if business_section:
                description = business_section.find_next('p')
                st.write("Found description using Method 2")

        if description:
            return description.text.strip()
        else:
            st.warning(f"Could not find business description")
            return None

    except Exception as e:
        st.error(f"Error fetching description: {str(e)}")
        return None

# Streamlit UI
st.title("EXAS Company Description")

description = get_company_description('EXAS')
if description:
    st.subheader("Company Description")
    st.write(description)
else:
    st.error("Could not fetch EXAS description")