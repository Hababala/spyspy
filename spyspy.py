import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
from openbb import obb

# Initialize OpenBB
obb.account.login(pat="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdXRoX3Rva2VuIjoiQWpIZ2hsazVtcXk0VEV5V1FEUFRlakpqS3NYQjcxOXd5NzhyRjI2MiIsImV4cCI6MTc2Mjg4OTc4N30.4cKXMKxmZxc9CgWPIyAjF7T8nCyH0gThySmeACR-I1o")

st.title("US Stock Market Search")

# Get all companies from OpenBB (cached)
@st.cache_data
def get_companies():
    return obb.equity.search("", provider="sec").to_df()

# Load companies
all_companies = get_companies()
symbols_list = all_companies['symbol'].tolist()

# Add search box
search_query = st.text_input("Search for a symbol:", "")

if search_query:
    # Filter symbols (show max 10 results)
    filtered_symbols = [s for s in symbols_list if search_query.upper() in s.upper()][:10]
    
    if filtered_symbols:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            selected_symbol = st.radio("Select a symbol:", filtered_symbols)
            st.session_state.selected_symbol = selected_symbol
        
        with col2:
            if selected_symbol:
                ticker = yf.Ticker(selected_symbol)
                current_data = ticker.history(period="1d")
                
                if not current_data.empty:
                    current_price = current_data['Close'].iloc[-1]
                    st.metric(
                        label="Current Price",
                        value=f"${current_price:.2f}",
                        delta=f"{(current_price - current_data['Open'].iloc[0]):.2f}"
                    )
        
        if selected_symbol:
            # Show detailed data in tabs
            tab1, tab2 = st.tabs(["Price Data", "Chart"])
            
            with tab1:
                st.write("Recent Price Data:")
                st.write(ticker.history(period="5d"))
            
            with tab2:
                hist_data = ticker.history(period="ytd")
                fig = go.Figure(data=go.Scatter(x=hist_data.index, y=hist_data['Close']))
                fig.update_layout(
                    title=f"{selected_symbol} YTD Performance",
                    yaxis_title="Price",
                    xaxis_title="Date"
                )
                st.plotly_chart(fig)
    else:
        st.write("No matching symbols found.")

# Add company info if a symbol is selected
if 'selected_symbol' in st.session_state:
    st.markdown("---")
    st.subheader("Company Information")
    
    try:
        ticker = yf.Ticker(st.session_state.selected_symbol)
        info = ticker.info
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Sector:**", info.get('sector', 'N/A'))
            st.write("**Industry:**", info.get('industry', 'N/A'))
            st.write("**Market Cap:**", f"${info.get('marketCap', 0):,}")
        
        with col2:
            st.write("**52 Week High:**", f"${info.get('fiftyTwoWeekHigh', 0):.2f}")
            st.write("**52 Week Low:**", f"${info.get('fiftyTwoWeekLow', 0):.2f}")
            st.write("**Beta:**", f"{info.get('beta', 0):.2f}")
        
        st.write("**Business Summary:**")
        st.write(info.get('longBusinessSummary', 'No description available.'))
        
    except Exception as e:
        st.error(f"Error loading company information: {str(e)}")