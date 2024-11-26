import streamlit as st
import pandas as pd
import requests
import yfinance as yf
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

def fetch_company_details(ticker):
    """Fetch additional company details using yfinance"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            'description': info.get('longBusinessSummary', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'market_cap': info.get('marketCap', 'N/A')
        }
    except Exception as e:
        return {
            'description': 'N/A',
            'sector': 'N/A',
            'market_cap': 'N/A'
        }

# Fetch and display companies
companies_df = fetch_us_companies()

if not companies_df.empty:
    # Add a search bar
    search_query = st.text_input("Search for a company:", "")
    
    if search_query:
        # Filter companies based on search query
        filtered_df = companies_df[companies_df['title'].str.contains(search_query, case=False, na=False)]
        
        # Fetch additional details for each filtered company
        details_list = []
        for _, row in filtered_df.iterrows():
            details = fetch_company_details(row['ticker'])
            details_list.append({
                'Ticker': row['ticker'],
                'Name': row['title'],
                'Description': details['description'],
                'Sector': details['sector'],
                'Market Cap': details['market_cap']
            })
        
        # Convert to DataFrame for display
        detailed_df = pd.DataFrame(details_list)
        
        if not detailed_df.empty:
            st.write("Filtered Companies:")
            st.dataframe(detailed_df)
        else:
            st.write("No companies match the search criteria.")
    else:
        st.write("Enter a keyword to search for companies.")
else:
    st.write("No data available.")