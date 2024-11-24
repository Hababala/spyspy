import streamlit as st
import yfinance as yf
import polars as pl
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
    etf_data = []
    errors = []
    
    for name, ticker in EM_ETFS.items():
        try:
            # Get data for last year
            end_date = datetime.now()
            start_date = datetime(end_date.year, 1, 1)  # Start of current year
            
            # Fetch data
            etf = yf.Ticker(ticker)
            df = etf.history(start=start_date, end=end_date)
            
            if df.empty:
                errors.append(f"No data available for {ticker}")
                continue
                
            # Convert to Polars
            df = pl.from_pandas(df)
            
            # Calculate YTD return
            first_close = df.select('Close').row(0)[0]
            last_close = df.select('Close').row(-1)[0]
            ytd_return = ((last_close / first_close) - 1) * 100
            
            etf_data.append({
                'name': name,
                'ticker': ticker,
                'ytd_return': ytd_return,
                'current_price': last_close
            })
            
        except Exception as e:
            errors.append(f"Error fetching data for {ticker}: {e}")
    
    if errors:
        st.warning("Some ETFs could not be loaded:")
        for error in errors:
            st.write(error)
    
    if not etf_data:
        st.error("No ETF data could be loaded. Please try again later.")
        return pl.DataFrame()
    
    return pl.DataFrame(etf_data)

def get_etf_historical_data(ticker):
    """
    Fetch historical data for a single ETF
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*10)
        
        etf = yf.Ticker(ticker)
        df = etf.history(start=start_date, end=end_date)
        
        # Convert to Polars and reset index
        df = pl.from_pandas(df.reset_index())
        
        # Calculate additional metrics
        df = df.with_columns([
            pl.col('Close').pct_change().alias('Daily_Return'),
            pl.col('Close').pct_change(252).alias('YTD_Return')
        ])
        
        return df
        
    except Exception as e:
        st.error(f"Error fetching historical data for {ticker}: {e}")
        return None

# Streamlit UI
st.title("MSCI Emerging Markets ETF Explorer")
st.write("Data source: Yahoo Finance")

# Get data for all ETFs
all_etf_data = get_all_etf_data()

# Check if we have data
if all_etf_data.height == 0:
    st.error("No ETF data available. Please try again later.")
else:
    try:
        # YTD Return filter
        st.sidebar.subheader("Filter ETFs")
        
        # Safely get min and max values with fallbacks
        try:
            min_ytd = float(all_etf_data.select('ytd_return').min()[0])
            max_ytd = float(all_etf_data.select('ytd_return').max()[0])
        except (IndexError, ValueError):
            st.warning("Could not calculate YTD return range. Using default values.")
            min_ytd = -30.0
            max_ytd = 30.0
        
        ytd_range = st.sidebar.slider(
            "YTD Return Range (%)",
            min_value=min_ytd,
            max_value=max_ytd,
            value=(min_ytd, max_ytd)
        )

        # Filter ETFs based on YTD return
        filtered_etfs = (
            all_etf_data
            .filter(
                (pl.col('ytd_return') >= ytd_range[0]) & 
                (pl.col('ytd_return') <= ytd_range[1])
            )
            .sort('ytd_return', descending=True)
        )

        # Display filtered ETFs
        st.subheader("Filtered ETFs by YTD Return")
        if filtered_etfs.height > 0:
            for row in filtered_etfs.iter_rows(named=True):
                st.write(f"{row['name']} ({row['ticker']}): {row['ytd_return']:.2f}%")
        else:
            st.warning("No ETFs found in the selected range.")

        # ETF selection from filtered list
        if filtered_etfs.height > 0:
            selected_etf_name = st.selectbox(
                "Select an ETF for detailed view:",
                filtered_etfs.select('name').to_series().to_list()
            )
            
            if selected_etf_name:
                selected_etf = filtered_etfs.filter(pl.col('name') == selected_etf_name).row(0, named=True)
                ticker = selected_etf['ticker']
                data = get_etf_historical_data(ticker)
                
                if data is not None:
                    # Display basic info
                    st.subheader(f"{selected_etf_name} ({ticker})")
                    
                    # Convert to pandas for plotly (plotly works better with pandas)
                    plot_data = data.to_pandas()
                    
                    # Create price chart
                    fig = px.line(
                        plot_data,
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
                        daily_return = float(data.select('Daily_Return').tail(1)[0]) * 100
                        st.metric("Daily Return", f"{daily_return:.2f}%")
                        
                    with col2:
                        ytd_return = selected_etf['ytd_return']
                        st.metric("YTD Return", f"{ytd_return:.2f}%")
                        
                    with col3:
                        current_price = selected_etf['current_price']
                        st.metric("Current Price", f"${current_price:.2f}")
                    
                    # Display raw data
                    if st.checkbox("Show raw data"):
                        st.dataframe(data.to_pandas())
                        
                    # Add download button
                    if st.button("Download Data"):
                        csv = data.write_csv()
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f'{ticker}_data.csv',
                            mime='text/csv'
                        )
                else:
                    st.error(f"Could not load historical data for {ticker}")
        else:
            st.info("Please adjust the YTD return range to see available ETFs.")
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Please try refreshing the page or contact support if the issue persists.")

