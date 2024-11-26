import streamlit as st
import yfinance as yf
import pandas as pd
import concurrent.futures

st.title("1000 Largest US Stocks")

@st.cache_data
def get_sp500_symbols():
    """Get S&P 500 symbols"""
    try:
        sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
        return sp500['Symbol'].tolist()
    except:
        return []

@st.cache_data
def get_russell1000_symbols():
    """Get Russell 1000 symbols"""
    try:
        russell = pd.read_html('https://en.wikipedia.org/wiki/Russell_1000_Index')[1]
        return russell['Ticker'].tolist()
    except:
        return []

@st.cache_data
def get_stock_info(symbol):
    """Get stock information including market cap and description"""
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        return {
            'Symbol': symbol,
            'Name': info.get('longName', 'N/A'),
            'Market Cap': info.get('marketCap', 0),
            'Description': info.get('longBusinessSummary', 'N/A'),
            'Sector': info.get('sector', 'N/A'),
            'Industry': info.get('industry', 'N/A')
        }
    except:
        return None

# Get symbols from indices
symbols_list = list(set(get_sp500_symbols() + get_russell1000_symbols()))

# Show progress
progress_bar = st.progress(0)
status_text = st.empty()

# Fetch data for all stocks in parallel
stocks_data = []
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    future_to_symbol = {executor.submit(get_stock_info, symbol): symbol for symbol in symbols_list}
    completed = 0
    
    for future in concurrent.futures.as_completed(future_to_symbol):
        symbol = future_to_symbol[future]
        try:
            data = future.result()
            if data and data['Market Cap'] > 0:
                stocks_data.append(data)
        except Exception as e:
            st.error(f"Error processing {symbol}: {str(e)}")
        
        completed += 1
        progress = completed / len(symbols_list)
        progress_bar.progress(progress)
        status_text.text(f"Processed {completed}/{len(symbols_list)} stocks...")

# Convert to DataFrame and sort by market cap
df = pd.DataFrame(stocks_data)
df = df.sort_values('Market Cap', ascending=False).head(1000)

# Format market cap
df['Market Cap'] = df['Market Cap'].apply(lambda x: f"${x/1e9:.2f}B")

# Add search functionality
search_query = st.text_input("Search companies by name, symbol, or description:", "")

if search_query:
    # Case-insensitive search across multiple columns
    mask = (
        df['Symbol'].str.contains(search_query, case=False, na=False) |
        df['Name'].str.contains(search_query, case=False, na=False) |
        df['Description'].str.contains(search_query, case=False, na=False) |
        df['Sector'].str.contains(search_query, case=False, na=False) |
        df['Industry'].str.contains(search_query, case=False, na=False)
    )
    filtered_df = df[mask]
    st.write(f"Found {len(filtered_df)} matching companies")
    st.dataframe(filtered_df)
else:
    st.write(f"Showing all {len(df)} companies")
    st.dataframe(df)

# Add download button
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name="largest_us_stocks.csv",
    mime="text/csv"
)