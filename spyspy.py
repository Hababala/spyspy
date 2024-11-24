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
    Indicator: FM.AST.CGLD.M (Total Reserves minus Gold, Monthly)
    """
    try:
        # Calculate last 10 years
        end_year = datetime.now().year
        start_year = end_year - 10
        
        # World Bank API parameters
        params = {
            'format': 'json',
            'per_page': 500,  # Increased to accommodate monthly data
            'date': f'{start_year}M01:{end_year}M12'  # Monthly format
        }
        
        # Make API request
        url = f"{WB_API_ENDPOINT}/country/{country_code}/indicator/FM.AST.CGLD.M"
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        # World Bank API returns a list where [0] is metadata and [1] is data
        data = response.json()[1]
        
        if not data:
            st.error(f"No monthly data available for {country_code}")
            # Try annual data as fallback
            return get_annual_reserves(country_code)
            
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Clean up the data
        df = df[['date', 'value']].copy()
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df['date'] = pd.to_datetime(df['date'], format='%YM%m')
        
        # Sort by date
        df = df.sort_values('date')
        
        # Convert from dollars to millions of dollars
        df['value'] = df['value'] / 1_000_000
        
        return df
        
    except Exception as e:
        st.error(f"Error fetching monthly data: {e}")
        # Try annual data as fallback
        return get_annual_reserves(country_code)

def get_annual_reserves(country_code):
    """
    Fallback function to get annual data
    Indicator: FI.RES.TOTL.CD (Total reserves including gold, Annual)
    """
    try:
        end_year = datetime.now().year
        start_year = end_year - 10
        
        params = {
            'format': 'json',
            'per_page': 100,
            'date': f'{start_year}:{end_year}'
        }
        
        url = f"{WB_API_ENDPOINT}/country/{country_code}/indicator/FI.RES.TOTL.CD"
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()[1]
        
        if not data:
            st.error(f"No data available for {country_code}")
            return None
            
        df = pd.DataFrame(data)
        df = df[['date', 'value']].copy()
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df['date'] = pd.to_datetime(df['date'], format='%Y')
        df = df.sort_values('date')
        df['value'] = df['value'] / 1_000_000
        
        st.info("Only annual data available for this country")
        return df
        
    except Exception as e:
        st.error(f"Error fetching annual data: {e}")
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
    
    # Add this to the UI section
    frequency = st.selectbox(
        "Select data frequency:",
        ["Monthly", "Annual"]
    )
    
    # Modify the data fetch based on frequency
    if frequency == "Monthly":
        data = get_foreign_reserves(country_code)
    else:
        data = get_annual_reserves(country_code)
    
    if data is not None:
        # Create plot using plotly
        fig = px.line(
            data,
            x='date',
            y='value',
            title=f'Foreign Reserves for {selected_country}',
            labels={'value': 'Reserves (USD Millions)', 'date': 'Date'}
        )
        
        # Customize layout for monthly data
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

