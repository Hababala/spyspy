import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.title("Stock Price Analysis")

# Add a search box for stock symbols
search_query = st.text_input("Search for a stock symbol:", "AAPL")

@st.cache_data
def get_stock_data(symbol):
    """Fetch stock data for the last year"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1y")
        return data
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return pd.DataFrame()

if search_query:
    # Get the data
    df = get_stock_data(search_query)
    
    if not df.empty:
        # Show current price and daily change
        current_price = df['Close'].iloc[-1]
        price_change = current_price - df['Open'].iloc[-1]
        
        st.metric(
            label="Current Price",
            value=f"${current_price:.2f}",
            delta=f"${price_change:.2f}"
        )
        
        # Create tabs for different views
        tab1, tab2 = st.tabs(["Chart", "Data"])
        
        with tab1:
            # Create interactive plot with Plotly
            fig = go.Figure()
            
            # Add candlestick chart
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='OHLC'
            ))
            
            # Update layout
            fig.update_layout(
                title=f"{search_query} Stock Price - Last Year",
                yaxis_title="Price ($)",
                xaxis_title="Date",
                template="plotly_dark"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add volume chart
            volume_fig = go.Figure()
            volume_fig.add_trace(go.Bar(
                x=df.index,
                y=df['Volume'],
                name='Volume'
            ))
            
            volume_fig.update_layout(
                title="Trading Volume",
                yaxis_title="Volume",
                xaxis_title="Date",
                template="plotly_dark"
            )
            
            st.plotly_chart(volume_fig, use_container_width=True)
        
        with tab2:
            st.write("Historical Data:")
            st.dataframe(df)
            
            # Add basic statistics
            st.subheader("Summary Statistics")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("Price Statistics")
                st.write(f"Average Price: ${df['Close'].mean():.2f}")
                st.write(f"Highest Price: ${df['High'].max():.2f}")
                st.write(f"Lowest Price: ${df['Low'].min():.2f}")
            
            with col2:
                st.write("Volume Statistics")
                st.write(f"Average Volume: {df['Volume'].mean():,.0f}")
                st.write(f"Max Volume: {df['Volume'].max():,.0f}")
                st.write(f"Min Volume: {df['Volume'].min():,.0f}")
    else:
        st.write(f"Error loading data for {search_query}")