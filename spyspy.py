import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import plotly.express as px

# IMF API endpoint
IMF_API_ENDPOINT = "http://dataservices.imf.org/REST/SDMX_JSON.svc/"

# Dictionary of emerging market countries with their ISO codes
EMERGING_MARKETS = {
    'Brazil': 'BR', 'China': 'CN', 'India': 'IN', 'Russia': 'RU', 
    'South Africa': 'ZA', 'Mexico': 'MX', 'Indonesia': 'ID', 
    'Turkey': 'TR', 'Thailand': 'TH', 'Malaysia': 'MY',
    'Philippines': 'PH', 'Poland': 'PL', 'Vietnam': 'VN',
    'Chile': 'CL', 'Colombia': 'CO', 'Peru': 'PE'
}

def get_foreign_reserves(country_code):
    """
    Fetch foreign reserves data from IMF
    Using IFS database and RAXG_USD series (Total Reserves excluding Gold, USD)
    """
    try:
        url = f"{IMF_API_ENDPOINT}CompactData/IFS/{country_code}.RAXG_USD"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        series = data['CompactData']['DataSet']['Series']
        observations = series['Obs']
        
        # Convert to DataFrame
        df = pd.DataFrame(observations)
        df.columns = ['Date', 'Value']
        
        # Convert values to float and dates to datetime
        df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m')
        
        # Sort by date and get last 10 years
        df = df.sort_values('Date')
        ten_years_ago = datetime.now() - timedelta(days=365*10)
        df = df[df['Date'] > ten_years_ago]
        
        return df
    
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Streamlit UI
st.title("Foreign Reserves of Emerging Markets")
st.write("Data source: IMF International Financial Statistics")

# Search bar for countries
search_term = st.text_input("Search for a country:")

# Filter countries based on search
filtered_countries = [
    country for country in EMERGING_MARKETS.keys()
    if search_term.lower() in country.lower()
]

if search_term and filtered_countries:
    # Country selection from filtered list
    selected_country = st.selectbox("Select country:", filtered_countries)
    
    # Get country code and fetch data
    country_code = EMERGING_MARKETS[selected_country]
    data = get_foreign_reserves(country_code)
    
    if data is not None:
        # Create plot using plotly
        fig = px.line(
            data,
            x='Date',
            y='Value',
            title=f'Foreign Reserves for {selected_country} (USD)',
            labels={'Value': 'Reserves (USD)', 'Date': 'Year'}
        )
        
        # Customize layout
        fig.update_layout(
            hovermode='x unified',
            yaxis_title="USD (Millions)",
            xaxis_title="Date"
        )
        
        # Display plot
        st.plotly_chart(fig)
        
        # Display raw data
        if st.checkbox("Show raw data"):
            st.dataframe(data)

elif search_term:
    st.write("No matching countries found.")

