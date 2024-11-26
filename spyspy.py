import streamlit as st
import yfinance as yf
import polars as pl
import plotly.express as px
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup



def get_company_description(ticker):
    # Search for the company's filings
    search_url = f"https://www.sec.gov/cgi-bin/browse-edgar?company={ticker}&owner=exclude&action=getcompany"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the link to the most recent 10-K filing
    filings = soup.find_all('a', href=True)
    for filing in filings:
        if '10-K' in filing.text:
            filing_url = "https://www.sec.gov" + filing['href']
            break

    # Fetch the 10-K filing
    filing_response = requests.get(filing_url)
    filing_soup = BeautifulSoup(filing_response.text, 'html.parser')

    # Extract the company description
    description_section = filing_soup.find(text="Business").find_next('p')
    return description_section.text

# Example usage
ticker = "EXAS"  # Exact Sciences Corporation
description = get_company_description(ticker)
print(description)