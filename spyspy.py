import streamlit as st
import pandas as pd
import requests

st.title("US Listed Companies")

@st.cache_data
def fetch_us_companies():
    """Fetch all US listed companies using a reliable API"""
    api_key = "ebded077ff8114c8e3a431c1dcfa8a8a3bab629171ac5a00d68024d113d50c56"
    url = "https://api.sec-api.io?token={api_key}&query={{'query':{{'query_string':{{'query':'*'}}}},'from':0,'size':10000}}"
    headers = {'Authorization': f'{api_key}'}
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            st.error(f"Error: Status code {response.status_code}")
            st.write("Response content:", response.text)
            return pd.DataFrame()
        
        data = response.json()
        df = pd.DataFrame(data['hits']['hits'])
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