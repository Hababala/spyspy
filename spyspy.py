import streamlit as st
import pandas as pd
import requests

st.title("US Listed Companies")

@st.cache_data
def fetch_us_companies():
    """Fetch all US listed companies using a different API"""
    # Example using a different API endpoint
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'www.sec.gov'
    }
    
    try:
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