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
        
        # Add debug information
        if 'CompactData' not in data or 'DataSet' not in data['CompactData']:
            st.error(f"No data available for {country_code}")
            return None
            
        # Check if Series exists and has data
        dataset = data['CompactData']['DataSet']
        if 'Series' not in dataset or not dataset['Series']:
            st.error(f"No reserves data available for {country_code}")
            return None
            
        # Handle both single and multiple series cases
        series = dataset['Series']
        if isinstance(series, list):
            observations = series[0].get('Obs', [])
        else:
            observations = series.get('Obs', [])
            
        if not observations:
            st.error(f"No observations found for {country_code}")
            return None
        
        # Rest of the function remains the same
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
    
    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {e}")
        return None
    except Exception as e:
        st.error(f"Error processing data: {e}")
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

