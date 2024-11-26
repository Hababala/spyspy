import streamlit as st
import yfinance as yf
import pandas as pd
import json
import time

# Load S&P 500 companies (you can expand this list)
@st.cache_data
def load_company_list():
    """Load list of companies and their tickers"""
    try:
        # You can expand this to include more companies
        sp500_url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
        df = pd.read_csv(sp500_url)
        return dict(zip(df['Symbol'], df['Name']))
    except:
        # Fallback to a smaller list for testing
        return {
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corporation',
            'GOOGL': 'Alphabet Inc.',
            'AMZN': 'Amazon.com Inc.',
            'META': 'Meta Platforms Inc.',
            'NVDA': 'NVIDIA Corporation',
            'TSLA': 'Tesla Inc.',
            'EXAS': 'Exact Sciences Corporation'
        }

@st.cache_data(ttl=24*3600)  # Cache for 24 hours
def get_all_company_descriptions():
    """Fetch and cache all company descriptions"""
    companies = load_company_list()
    descriptions = {}
    
    for ticker in companies.keys():
        try:
            company = yf.Ticker(ticker)
            info = company.info
            if 'longBusinessSummary' in info:
                descriptions[ticker] = {
                    'name': companies[ticker],
                    'description': info['longBusinessSummary'],
                    'sector': info.get('sector', 'N/A'),
                    'industry': info.get('industry', 'N/A'),
                    'website': info.get('website', 'N/A'),
                    'market_cap': info.get('marketCap', 0)
                }
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {str(e)}")
    
    return descriptions

def filter_companies_by_keywords(descriptions, keywords):
    """Filter companies based on keywords"""
    matching_companies = {}
    
    for ticker, info in descriptions.items():
        description = info['description'].lower()
        if all(keyword.lower() in description for keyword in keywords):
            matching_companies[ticker] = info
    
    return matching_companies

# Streamlit UI
st.title("Company Description Search")

# Initialize session state for descriptions
if 'descriptions' not in st.session_state:
    with st.spinner('Loading company descriptions...'):
        st.session_state.descriptions = get_all_company_descriptions()

# Keyword search
keywords = st.text_input("Enter keywords (separated by commas):", "").split(',')
keywords = [k.strip() for k in keywords if k.strip()]

# Sector filter
sectors = list(set(info['sector'] for info in st.session_state.descriptions.values()))
selected_sector = st.selectbox("Filter by sector:", ["All"] + sorted(sectors))

if keywords:
    # Filter companies
    matching_companies = filter_companies_by_keywords(st.session_state.descriptions, keywords)
    
    # Apply sector filter
    if selected_sector != "All":
        matching_companies = {
            ticker: info for ticker, info in matching_companies.items()
            if info['sector'] == selected_sector
        }
    
    # Display results
    if matching_companies:
        st.success(f"Found {len(matching_companies)} matching companies")
        
        # Sort companies by market cap
        sorted_companies = dict(sorted(
            matching_companies.items(),
            key=lambda x: x[1]['market_cap'],
            reverse=True
        ))
        
        # Company selection
        selected_ticker = st.selectbox(
            "Select a company to view details:",
            options=list(sorted_companies.keys()),
            format_func=lambda x: f"{x} - {sorted_companies[x]['name']}"
        )
        
        if selected_ticker:
            company_info = sorted_companies[selected_ticker]
            
            # Display company details
            st.subheader(f"{selected_ticker} - {company_info['name']}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Sector:**", company_info['sector'])
                st.write("**Industry:**", company_info['industry'])
            with col2:
                st.write("**Website:**", company_info['website'])
                st.write("**Market Cap:**", f"${company_info['market_cap']:,}")
            
            st.subheader("Business Description")
            st.write(company_info['description'])
            
            # Stock price chart
            st.subheader("Stock Price (1 Year)")
            stock = yf.Ticker(selected_ticker)
            hist = stock.history(period="1y")
            st.line_chart(hist.Close)
            
            # Download button
            if st.button("Download Company Info"):
                company_data = json.dumps(company_info, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=company_data,
                    file_name=f"{selected_ticker}_info.json",
                    mime="application/json"
                )
    else:
        st.warning("No companies found matching all keywords")

# Add helpful information
with st.sidebar:
    st.subheader("Search Tips")
    st.write("""
    - Enter multiple keywords separated by commas
    - All keywords must be present in the description
    - Filter by sector to narrow results
    - Companies are sorted by market cap
    """)
    
    st.subheader("Example Keywords")
    st.write("""
    - technology, cloud, software
    - healthcare, medical, diagnostic
    - retail, e-commerce
    - renewable, energy
    """)