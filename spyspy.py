import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import plotly.express as px

# World Bank API endpoint
WB_API_ENDPOINT = "https://api.worldbank.org/v2"

# Dictionary of emerging market countries with their ISO codes
EMERGING_MARKETS = {
    'Brazil': 'BRA', 'China': 'CHN', 'India': 'IND', 'Russia': 'RUS', 
    'South Africa': 'ZAF', 'Mexico': 'MEX', 'Indonesia': 'IDN', 
    'Turkey': 'TUR', 'Thailand': 'THA', 'Malaysia': 'MYS',
    'Philippines': 'PHL', 'Poland': 'POL', 'Vietnam': 'VNM',
    'Chile': 'CHL', 'Colombia': 'COL', 'Peru': 'PER'
}

def get_foreign_reserves(country_code):
    """
    Fetch foreign reserves data from World Bank
    Indicator: FI.RES.TOTL.CD (Total reserves including gold)
    """
    try:
        # Calculate last 10 years
        end_year = datetime.now().year
        start_year = end_year - 10
        
        # World Bank API parameters
        params = {
            'format': 'json',
            'per_page': 100,
            'date': f'{start_year}:{end_year}'
        }
        
        # Make API request
        url = f"{WB_API_ENDPOINT}/country/{country_code}/indicator/FI.RES.TOTL.CD"
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        # World Bank API returns a list where [0] is metadata and [1] is data
        data = response.json()[1]
        
        if not data:
            st.error(f"No data available for {country_code}")
            return None
            
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Clean up the data
        df = df[['date', 'value']].copy()
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df['date'] = pd.to_datetime(df['date'], format='%Y')
        
        # Sort by date
        df = df.sort_values('date')
        
        # Convert from dollars to millions of dollars
        df['value'] = df['value'] / 1_000_000
        
        return df
        
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        st.write("Full error:", str(e))
        return None

# Streamlit UI
st.title("Foreign Reserves of Emerging Markets")
st.write("Data source: World Bank")

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
            x='date',
            y='value',
            title=f'Foreign Reserves for {selected_country}',
            labels={'value': 'Reserves (USD Millions)', 'date': 'Year'}
        )
        
        # Customize layout
        fig.update_layout(
            hovermode='x unified',
            yaxis_title="USD (Millions)",
            xaxis_title="Year"
        )
        
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

