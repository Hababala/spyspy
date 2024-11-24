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

def get_etf_data(ticker):
    """
    Fetch ETF data from Yahoo Finance
    """
    try:
        # Get data for last 10 years
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*10)
        
        # Fetch data
        etf = yf.Ticker(ticker)
        df = etf.history(start=start_date, end=end_date)
        
        # Reset index to make date a column
        df = df.reset_index()
        
        # Calculate additional metrics
        df['Daily_Return'] = df['Close'].pct_change()
        df['YTD_Return'] = df['Close'].pct_change(periods=252)
        
        return df
        
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None

# Streamlit UI
st.title("MSCI Emerging Markets ETF Explorer")
st.write("Data source: Yahoo Finance")

# ETF selection
selected_etf_name = st.selectbox(
    "Select an ETF:",
    list(EM_ETFS.keys())
)

if selected_etf_name:
    ticker = EM_ETFS[selected_etf_name]
    data = get_etf_data(ticker)
    
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
        
        # Customize layout
        fig.update_layout(
            hovermode='x unified',
            xaxis_title="Date",
            yaxis_title="Price (USD)"
        )
        
        # Add range slider
        fig.update_xaxes(rangeslider_visible=True)
        
        # Display plot
        st.plotly_chart(fig)
        
        # Display key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            daily_return = data['Daily_Return'].iloc[-1] * 100
            st.metric("Daily Return", f"{daily_return:.2f}%")
            
        with col2:
            ytd_return = data['YTD_Return'].iloc[-1] * 100
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

