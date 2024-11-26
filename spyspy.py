import streamlit as st
import pandas as pd
import requests
import time

st.title("US Listed Companies")

@st.cache_data
def fetch_us_companies():
    """Fetch all US listed companies using a different API"""
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {
        'User-Agent': 'YourAppName/1.0 (Contact: your-email@example.com)',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'www.sec.gov'
    }
    
    try:
        # Add a delay to avoid rate limiting
        time.sleep(1)
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            st.error(f"Error: Status code {response.status_code}")
            st.write("Response content:", response.text)
            return pd.DataFrame()
        
        companies_dict = response.json()
        
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(companies_dict, orient='index')
        df.columns = ['cik_str', 'ticker', 'title']
        return df
    
    except Exception as e:
        st.error(f"Error fetching companies: {str(e)}")
        return pd.DataFrame()

# Fetch and display companies
companies_df = fetch_us_companies()

if not companies_df.empty:
    st.write("List of US Listed Companies:")
    st.dataframe(companies_df)
else:
    st.write("No data available.")