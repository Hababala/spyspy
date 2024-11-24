import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Dictionary of MSCI Emerging Markets ETFs
EM_ETFS = {
    'iShares MSCI Emerging Markets ETF': 'EEM',
    'Vanguard FTSE Emerging Markets ETF': 'VWO',
    'iShares Core MSCI Emerging Markets ETF': 'IEMG',
    'SPDR Portfolio Emerging Markets ETF': 'SPEM',
    'Schwab Emerging Markets Equity ETF': 'SCHE',
    'iShares MSCI Brazil ETF': 'EWZ',
    'iShares MSCI China ETF': 'MCHI',
    'iShares MSCI India ETF': 'INDA',
    'iShares MSCI South Korea ETF': 'EWY',
    'iShares MSCI Taiwan ETF': 'EWT',
    'iShares MSCI South Africa ETF': 'EZA',
    'iShares MSCI Mexico ETF': 'EWW'
}

@st.cache_data(ttl=3600)  # Cache data for 1 hour
def get_all_etf_data():
    """
    Fetch data for all ETFs and calculate YTD returns
    """
    etf_data = {}
    for name, ticker in EM_ETFS.items():
        try:
            # Get data for last year
            end_date = datetime.now()
            start_date = datetime(end_date.year, 1, 1)  # Start of current year
            
            # Fetch data
            etf = yf.Ticker(ticker)
            df = etf.history(start=start_date, end=end_date)
            
            # Calculate YTD return
            ytd_return = ((df['Close'][-1] / df['Close'][0]) - 1) * 100
            
            etf_data[name] = {
                'ticker': ticker,
                'ytd_return': ytd_return,
                'current_price': df['Close'][-1]
            }
            
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {e}")
    
    return etf_data

def get_etf_historical_data(ticker):
    """
    Fetch historical data for a single ETF
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*10)
        
        etf = yf.Ticker(ticker)
        df = etf.history(start=start_date, end=end_date)
        df = df.reset_index()
        df['Daily_Return'] = df['Close'].pct_change()
        df['YTD_Return'] = df['Close'].pct_change(periods=252)
        
        return df
        
    except Exception as e:
        st.error(f"Error fetching historical data for {ticker}: {e}")
        return None

# Streamlit UI
st.title("MSCI Emerging Markets ETF Explorer")
st.write("Data source: Yahoo Finance")

# Get data for all ETFs
all_etf_data = get_all_etf_data()

# Create a DataFrame for filtering
etf_df = pd.DataFrame.from_dict(all_etf_data, orient='index')

# YTD Return filter
st.sidebar.subheader("Filter ETFs")
min_ytd = float(etf_df['ytd_return'].min())
max_ytd = float(etf_df['ytd_return'].max())
ytd_range = st.sidebar.slider(
    "YTD Return Range (%)",
    min_value=min_ytd,
    max_value=max_ytd,
    value=(min_ytd, max_ytd)
)

# Filter ETFs based on YTD return
filtered_etfs = etf_df[
    (etf_df['ytd_return'] >= ytd_range[0]) & 
    (etf_df['ytd_return'] <= ytd_range[1])
].sort_values('ytd_return', ascending=False)

# Display filtered ETFs
st.subheader("Filtered ETFs by YTD Return")
for idx, row in filtered_etfs.iterrows():
    st.write(f"{idx} ({row['ticker']}): {row['ytd_return']:.2f}%")

# ETF selection from filtered list
selected_etf_name = st.selectbox(
    "Select an ETF for detailed view:",
    filtered_etfs.index.tolist()
)

if selected_etf_name:
    ticker = EM_ETFS[selected_etf_name]
    data = get_etf_historical_data(ticker)
    
    if data is not None:
        # Display basic info
        st.subheader(f"{selected_etf_name} ({ticker})")
        
        # Create price chart
        fig = px.line(
            data,
            x='Date',
            y='Close',
            title=f'Price History for {selected_etf_name}',
            labels={'Close': 'Price (USD)', 'Date': 'Date'}
        )
        
        fig.update_layout(
            hovermode='x unified',
            xaxis_title="Date",
            yaxis_title="Price (USD)"
        )
        
        fig.update_xaxes(rangeslider_visible=True)
        
        st.plotly_chart(fig)
        
        # Display key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            daily_return = data['Daily_Return'].iloc[-1] * 100
            st.metric("Daily Return", f"{daily_return:.2f}%")
            
        with col2:
            ytd_return = filtered_etfs.loc[selected_etf_name, 'ytd_return']
            st.metric("YTD Return", f"{ytd_return:.2f}%")
            
        with col3:
            current_price = data['Close'].iloc[-1]
            st.metric("Current Price", f"${current_price:.2f}")
        
        # Display raw data
        if st.checkbox("Show raw data"):
            st.dataframe(data)
            
        # Add download button
        if st.button("Download Data"):
            csv = data.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f'{ticker}_data.csv',
                mime='text/csv'
            )

