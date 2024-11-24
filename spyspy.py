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
    Fetch foreign reserves data from IMF with expanded options
    """
    try:
        # Try different databases and indicators
        combinations = [
            ('IFS', 'RASA_USD'),    # IFS Total Reserves
            ('IFS', 'RAXG_USD'),    # IFS Reserves excluding gold
            ('IFTSTSUB', 'TMGO'),   # International Financial Statistics
            ('BOP', 'BFRA_BP6_USD') # Balance of Payments reserves
        ]
        
        for database, indicator in combinations:
            url = f"{IMF_API_ENDPOINT}CompactData/{database}/{country_code}.{indicator}"
            
            # Debug info
            st.write(f"Trying database: {database}, indicator: {indicator}")
            st.write(f"URL: {url}")
            
            response = requests.get(url)
            
            if response.status_code != 200:
                continue
                
            data = response.json()
            
            # Print raw response for debugging
            if st.checkbox(f"Show raw response for {database}.{indicator}"):
                st.json(data)
            
            dataset = data['CompactData']['DataSet']
            
            if 'Series' in dataset and dataset['Series']:
                series = dataset['Series']
                if isinstance(series, list):
                    observations = series[0].get('Obs', [])
                else:
                    observations = series.get('Obs', [])
                    
                if observations:
                    df = pd.DataFrame(observations)
                    df.columns = ['Date', 'Value']
                    
                    # Convert values to float and dates to datetime
                    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
                    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m')
                    
                    # Sort by date and get last 10 years
                    df = df.sort_values('Date')
                    ten_years_ago = datetime.now() - timedelta(days=365*10)
                    df = df[df['Date'] > ten_years_ago]
                    
                    if not df.empty:
                        st.success(f"Found data using {database}.{indicator}")
                        return df
        
        # If we get here, no data was found
        st.error(f"No reserves data available for {country_code}")
        return None
            
    except Exception as e:
        st.error(f"Error processing data: {e}")
        st.write("Full error:", str(e))
        return None

def get_available_indicators(country_code):
    """Check what indicators are available for a country"""
    try:
        databases = ['IFS', 'BOP', 'IFTSTSUB']
        for db in databases:
            url = f"{IMF_API_ENDPOINT}DataStructure/{db}"
            response = requests.get(url)
            if response.status_code == 200:
                st.write(f"Available indicators in {db} for {country_code}:")
                st.json(response.json())
    except Exception as e:
        st.error(f"Error checking indicators: {e}")

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

        # Add this to your UI section
        if st.checkbox("Debug Mode"):
            st.write("Country Code:", country_code)
            if st.button("Check Available Indicators"):
                get_available_indicators(country_code)

elif search_term:
    st.write("No matching countries found.")

