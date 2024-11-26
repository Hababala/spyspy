import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import time

@st.cache_data
def load_sec_companies():
    """Load all companies from SEC API"""
    try:
        # SEC Company Tickers API endpoint
        url = "https://www.sec.gov/files/company_tickers.json"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        companies_dict = response.json()
        
        # Convert to DataFrame
        companies_df = pd.DataFrame.from_dict(companies_dict, orient='index')
        companies_df['ticker'] = companies_df['ticker'].str.strip()
        
        # Initialize dictionary to store company info
        all_companies = {}
        
        # Create progress bar
        progress_bar = st.progress(0)
        total_companies = len(companies_df)
        
        for i, row in companies_df.iterrows():
            try:
                company = yf.Ticker(row['ticker'])
                info = company.info
                if 'longBusinessSummary' in info:
                    description = info['longBusinessSummary']
                    summary = description.split('.')[0] + '.' if '.' in description else description[:200] + '...'
                    
                    all_companies[row['ticker']] = {
                        'ticker': row['ticker'],
                        'name': info.get('longName', row['title']),
                        'description': summary,
                        'sector': info.get('sector', 'N/A'),
                        'industry': info.get('industry', 'N/A'),
                        'market_cap': info.get('marketCap', 0),
                        'full_description': description
                    }
            except Exception as e:
                continue
            
            # Update progress
            progress_bar.progress(min((i + 1) / total_companies, 1.0))
            time.sleep(0.1)  # Rate limiting
        
        progress_bar.empty()
        return all_companies
        
    except Exception as e:
        st.error(f"Error loading companies: {str(e)}")
        return {}

# Streamlit UI
st.title("US Stock Market Company Search")

# Initialize or load company data
if 'all_companies' not in st.session_state:
    st.info("Loading company data... This may take a while.")
    st.session_state.all_companies = load_sec_companies()

# Search interface
col1, col2 = st.columns([2, 1])
with col1:
    keywords = st.text_input("Enter keywords (separated by commas):", "").split(',')
    keywords = [k.strip() for k in keywords if k.strip()]

with col2:
    min_market_cap = st.number_input("Minimum Market Cap (USD Millions)", 0, 1000000, 0)

# Sector filter
sectors = list(set(info['sector'] for info in st.session_state.all_companies.values() if info['sector'] != 'N/A'))
selected_sector = st.selectbox("Filter by sector:", ["All"] + sorted(sectors))

# Display results
if keywords:
    matching_companies = {}
    for ticker, info in st.session_state.all_companies.items():
        if info['description'] and all(k.lower() in info['description'].lower() for k in keywords):
            if selected_sector == "All" or info['sector'] == selected_sector:
                if info['market_cap'] >= min_market_cap * 1_000_000:
                    matching_companies[ticker] = info
    
    if matching_companies:
        st.success(f"Found {len(matching_companies)} matching companies")
        
        # Sort by market cap
        sorted_companies = dict(sorted(
            matching_companies.items(),
            key=lambda x: x[1]['market_cap'],
            reverse=True
        ))
        
        # Create display DataFrame
        display_data = []
        for ticker, info in sorted_companies.items():
            display_data.append({
                'Ticker': ticker,
                'Company Name': info['name'],
                'Description': info['description'],
                'Sector': info['sector'],
                'Market Cap ($M)': f"${info['market_cap']/1_000_000:,.0f}M"
            })
        
        # Display as table
        st.dataframe(
            pd.DataFrame(display_data),
            column_config={
                'Ticker': st.column_config.TextColumn('Ticker', width='small'),
                'Company Name': st.column_config.TextColumn('Company Name', width='medium'),
                'Description': st.column_config.TextColumn('Description', width='large'),
                'Sector': st.column_config.TextColumn('Sector', width='medium'),
                'Market Cap ($M)': st.column_config.TextColumn('Market Cap', width='medium')
            },
            use_container_width=True
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