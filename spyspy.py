import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import plotly.express as px

# DBnomics API endpoint
DBNOM_API_ENDPOINT = "https://api.db.nomics.world/v22"

# Dictionary of emerging market countries with their ISO codes and providers
EMERGING_MARKETS = {
    'Brazil': {'code': 'BR', 'provider': 'IMF', 'dataset': 'IFS'},
    'China': {'code': 'CN', 'provider': 'IMF', 'dataset': 'IFS'},
    'India': {'code': 'IN', 'provider': 'IMF', 'dataset': 'IFS'},
    'Russia': {'code': 'RU', 'provider': 'IMF', 'dataset': 'IFS'},
    'South Africa': {'code': 'ZA', 'provider': 'IMF', 'dataset': 'IFS'},
    'Mexico': {'code': 'MX', 'provider': 'IMF', 'dataset': 'IFS'},
    'Indonesia': {'code': 'ID', 'provider': 'IMF', 'dataset': 'IFS'},
    'Turkey': {'code': 'TR', 'provider': 'IMF', 'dataset': 'IFS'},
    'Thailand': {'code': 'TH', 'provider': 'IMF', 'dataset': 'IFS'},
    'Malaysia': {'code': 'MY', 'provider': 'IMF', 'dataset': 'IFS'},
    'Philippines': {'code': 'PH', 'provider': 'IMF', 'dataset': 'IFS'},
    'Poland': {'code': 'PL', 'provider': 'IMF', 'dataset': 'IFS'},
    'Vietnam': {'code': 'VN', 'provider': 'IMF', 'dataset': 'IFS'},
    'Chile': {'code': 'CL', 'provider': 'IMF', 'dataset': 'IFS'},
    'Colombia': {'code': 'CO', 'provider': 'IMF', 'dataset': 'IFS'},
    'Peru': {'code': 'PE', 'provider': 'IMF', 'dataset': 'IFS'}
}

# Alternative indicators to try
RESERVE_INDICATORS = [
    'RAXG_USD',  # Reserves excluding gold
    'RASA_USD',  # Total reserves
    'RAFAB_USD'  # Foreign assets
]

def get_foreign_reserves(country_info):
    """
    Fetch foreign reserves data from DBnomics
    Using IMF IFS dataset with RAXG_USD series (Total Reserves minus Gold)
    """
    try:
        # Try different frequency codes (Monthly, Quarterly)
        frequencies = ['M', 'Q']
        
        for freq in frequencies:
            # Construct the API URL
            url = f"{DBNOM_API_ENDPOINT}/series/IMF/IFS/{freq}.{country_info['code']}.RAXG_USD.N"
            
            # Parameters for the API request
            params = {
                'limit': 1000,
                'format': 'json',
                'observations': True  # Make sure we get the actual data
            }
            
            # Debug info
            st.write(f"Trying {freq} frequency data...")
            st.write("Requesting URL:", url)
            
            # Make API request
            response = requests.get(url, params=params)
            
            # Check if request was successful
            if response.status_code != 200:
                st.write(f"Failed to fetch {freq} frequency data")
                continue
                
            data = response.json()
            
            # Check if we have valid data
            if ('series' in data and 
                data['series'] and 
                'observations' in data['series'][0] and 
                data['series'][0]['observations']):
                
                # Extract the time series data
                observations = data['series'][0]['observations']
                
                # Create DataFrame
                df = pd.DataFrame(observations)
                df.columns = ['date', 'value']
                
                # Convert to datetime and numeric
                df['date'] = pd.to_datetime(df['date'])
                df['value'] = pd.to_numeric(df['value'], errors='coerce')
                
                # Sort by date and get last 10 years
                df = df.sort_values('date')
                ten_years_ago = datetime.now() - timedelta(days=365*10)
                df = df[df['date'] > ten_years_ago]
                
                # Convert to millions of USD
                df['value'] = df['value'] / 1_000_000
                
                st.success(f"Found {freq}frequency data")
                return df
        
        # If we get here, no data was found
        st.error(f"No data available for {country_info['code']}")
        return None
        
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        st.write("Full error:", str(e))
        if 'response' in locals():
            st.write("Response content:", response.text[:500])  # Show first 500 chars
        return None

# Streamlit UI
st.title("Foreign Reserves of Emerging Markets")
st.write("Data source: DBnomics (IMF IFS)")

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
    
    # Get country info and fetch data
    country_info = EMERGING_MARKETS[selected_country]
    data = get_foreign_reserves(country_info)
    
    if data is not None:
        # Create plot using plotly
        fig = px.line(
            data,
            x='date',
            y='value',
            title=f'Foreign Reserves for {selected_country}',
            labels={'value': 'Reserves (USD Millions)', 'date': 'Date'}
        )
        
        # Customize layout
        fig.update_layout(
            hovermode='x unified',
            yaxis_title="USD (Millions)",
            xaxis_title="Date",
            xaxis_tickformat='%Y-%m'  # Format x-axis to show year-month
        )
        
        # Add range slider
        fig.update_xaxes(rangeslider_visible=True)
        
        # Display plot
        st.plotly_chart(fig)
        
        # Display raw data
        if st.checkbox("Show raw data"):
            st.dataframe(data)
            
        # Add download button
        if st.button("Download Data"):
            csv = data.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f'reserves_{selected_country}.csv',
                mime='text/csv'
            )

elif search_term:
    st.write("No matching countries found.")

