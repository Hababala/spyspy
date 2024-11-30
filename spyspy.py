import streamlit as st
import pandas as pd
import requests
import numpy as np

st.title("Economic Indicators Comparison (2024-2025)")

# Country codes and indicators
countries = {
    'BRA': 'Brazil',
    'ZAF': 'South Africa',
    'KAZ': 'Kazakhstan'
}

indicators = {
    'FP.CPI.TOTL.ZG': 'CPI (%)',
    'BN.CAB.XOKA.GD.ZS': 'Current Account (% of GDP)',
    'GC.BAL.CASH.GD.ZS': 'Budget Balance (% of GDP)',
    'NY.GDP.MKTP.KD.ZG': 'Real GDP Growth (%)'
}

try:
    # Initialize data storage
    data_dict = {}
    
    # Fetch data for each country and indicator
    for country_code in countries.keys():
        data_dict[country_code] = {}
        
        for indicator_code in indicators.keys():
            url = f"http://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}"
            params = {
                "format": "json",
                "per_page": "100",
                "date": "2024:2025"
            }
            
            response = requests.get(url, params=params)
            json_data = response.json()
            
            # Create DataFrame with default NaN values
            data_dict[country_code][indicator_code] = pd.DataFrame({'date': ['2024', '2025'], 'value': [np.nan, np.nan]})
            
            # Update with actual values if available
            if len(json_data) > 1 and json_data[1]:
                df = pd.DataFrame(json_data[1])
                if not df.empty:
                    df['value'] = pd.to_numeric(df['value'])
                    data_dict[country_code][indicator_code] = df
    
    # Create comparison table
    comparison_data = []
    for country_code, country_name in countries.items():
        row_2024 = {'Country': country_name, 'Year': 2024}
        row_2025 = {'Country': country_name, 'Year': 2025}
        row_delta = {'Country': f'{country_name} Δ', 'Year': '2025-2024'}
        
        for indicator_code, indicator_name in indicators.items():
            df = data_dict[country_code][indicator_code]
            val_2024 = df[df['date'] == '2024']['value'].iloc[0] if not df[df['date'] == '2024'].empty else np.nan
            val_2025 = df[df['date'] == '2025']['value'].iloc[0] if not df[df['date'] == '2025'].empty else np.nan
            delta = val_2025 - val_2024 if (not np.isnan(val_2024) and not np.isnan(val_2025)) else np.nan
            
            row_2024[indicator_name] = val_2024
            row_2025[indicator_name] = val_2025
            row_delta[indicator_name] = delta
        
        comparison_data.extend([row_2024, row_2025, row_delta])
    
    # Create and style the DataFrame
    comparison_df = pd.DataFrame(comparison_data)
    styled_df = comparison_df.style\
        .format({col: '{:.1f}' for col in indicators.values()})\
        .applymap(lambda v: 'color: red' if v < 0 else 'color: green', subset=list(indicators.values()))\
        .set_properties(**{'background-color': '#f0f2f6', 'color': 'black'})\
        .set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#0e1117'), ('color', 'white')]},
            {'selector': 'tr:nth-child(3n)', 'props': [('background-color', '#e6e9f0')]}
        ])
    
    st.dataframe(styled_df, use_container_width=True)

except Exception as e:
    st.error(f"Error fetching data: {str(e)}")

