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

        # Find all document links
        doc_links = []
        for link in soup.find_all('a'):
            if '10-K' in link.text and 'html' in link.get('href', ''):
                doc_links.append(urllib.parse.urljoin(base_url, link['href']))
        
        if not doc_links:
            st.warning(f"No 10-K filings found for {ticker}")
            return None

        # Try each document link
        for doc_url in doc_links[:3]:  # Try the 3 most recent filings
            st.write(f"Trying document: {doc_url}")
            
            # Add a delay to respect rate limits
            time.sleep(0.1)

            # Fetch the document
            doc_response = requests.get(doc_url, headers=headers)
            if doc_response.status_code != 200:
                continue
                
            doc_soup = BeautifulSoup(doc_response.text, 'html.parser')
            
            # Try multiple methods to find the business description
            description = None
            
            # Method 1: Look for "Business" section
            for tag in doc_soup.find_all(['span', 'div', 'p', 'h1', 'h2', 'h3']):
                if tag.text.strip() == 'Business' or tag.text.strip() == 'Item 1. Business':
                    # Get the next few paragraphs
                    paragraphs = []
                    next_tag = tag.find_next(['p', 'div'])
                    while next_tag and len(paragraphs) < 5:
                        if len(next_tag.text.strip()) > 100:  # Only include substantial paragraphs
                            paragraphs.append(next_tag.text.strip())
                        next_tag = next_tag.find_next(['p', 'div'])
                    
                    if paragraphs:
                        description = ' '.join(paragraphs)
                        break
            
            if description:
                return description

        st.warning(f"Could not find business description in recent filings")
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
    
    # Add word count and summary stats
    word_count = len(description.split())
    st.info(f"Description length: {word_count} words")
    
    # Add download button
    st.download_button(
        label="Download Description",
        data=description,
        file_name="EXAS_description.txt",
        mime="text/plain"
    )
else:
    st.error("Could not fetch EXAS description")
    
    # Add alternative data sources
    st.write("Try these alternative sources:")
    st.write("1. [Yahoo Finance](https://finance.yahoo.com/quote/EXAS/profile)")
    st.write("2. [Company Website](https://www.exactsciences.com/)")
    st.write("3. [SEC EDGAR](https://www.sec.gov/edgar/searchedgar/companysearch)")