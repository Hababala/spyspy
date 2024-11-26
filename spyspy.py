import streamlit as st
import pandas as pd
import requests
import json
import os
from datetime import datetime, timedelta

st.title("US Listed Companies")

@st.cache_data
def fetch_us_companies():
    """Fetch basic company list from SEC API"""
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
def fetch_company_description(cik):
    """Fetch company description from SEC filings only when needed"""
    url = "https://api.sec-api.io/full-text-search"
    api_key = "your_api_key_here"
    
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
        response = requests.post(f"{url}?cik={cik}", headers=headers, json=query)
        if response.status_code == 200:
            data = response.json()
            if data['filings']:
                text = data['filings'][0]['text']
                start = text.find("Item 1. Business")
                end = text.find("Item 1A. Risk Factors")
                if start != -1 and end != -1:
                    return text[start:end].strip()[:1000] + "..."
        return "No description available"
    except Exception as e:
        return f"Error fetching description: {str(e)}"

# Load basic company list (this is fast)
companies_df = fetch_us_companies()

# Search interface
search_query = st.text_input("Search for companies by name:", "").lower()

if search_query:
    # First filter by company name (instant)
    name_filtered_df = companies_df[
        companies_df['title'].str.lower().str.contains(search_query, na=False)
    ]
    
    if not name_filtered_df.empty:
        st.write(f"Found {len(name_filtered_df)} companies matching your search.")
        
        # Option to fetch detailed descriptions
        if st.button("Load company descriptions"):
            with st.spinner('Fetching company descriptions...'):
                # Only fetch descriptions for filtered companies
                name_filtered_df['description'] = name_filtered_df['cik_str'].apply(
                    lambda x: fetch_company_description(str(x).zfill(10))
                )
                st.dataframe(
                    name_filtered_df[['ticker', 'title', 'description']],
                    use_container_width=True
                )
        else:
            # Show basic info without descriptions
            st.dataframe(
                name_filtered_df[['ticker', 'title']],
                use_container_width=True
            )
    else:
        st.write("No companies found matching your search criteria.")
else:
    st.write("Enter a company name to search.")