import streamlit as st
import pandas as pd
import requests
import numpy as np

st.title("Economic Indicators Comparison (2023-2025)")

# Country codes and indicators (using IMF codes)
countries = {
    'BRA': 'Brazil',
    'ZAF': 'South Africa',
    'KAZ': 'Kazakhstan'
}

# IMF indicator codes
indicators = {
    'PCPIPCH': 'CPI (%)',
    'BCA_NGDPD': 'Current Account (% of GDP)',
    'GGR_NGDP': 'Budget Balance (% of GDP)',
    'NGDP_RPCH': 'Real GDP Growth (%)'
}

try:
    # Initialize data storage
    data_dict = {}
    
    # IMF API base URL
    base_url = "http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/WEO"
    
    # Fetch data for each country and indicator
    for country_code in countries.keys():
        data_dict[country_code] = {}
        
        for indicator_code in indicators.keys():
            # IMF API request
            url = f"{base_url}/{indicator_code}.{country_code}"
            response = requests.get(url)
            json_data = response.json()
            
            # Create DataFrame with default NaN values
            data_dict[country_code][indicator_code] = pd.DataFrame({'date': ['2023', '2025'], 'value': [np.nan, np.nan]})
            
            # Extract data from IMF response
            try:
                series = json_data['CompactData']['DataSet']['Series']
                obs = series['Obs'] if isinstance(series['Obs'], list) else [series['Obs']]
                
                df = pd.DataFrame(obs)
                df.columns = ['date', 'value']
                df['value'] = pd.to_numeric(df['value'])
                df = df[df['date'].isin(['2023', '2025'])]
                
                if not df.empty:
                    data_dict[country_code][indicator_code] = df
            except (KeyError, TypeError):
                continue
    
    # Create comparison table
    comparison_data = []
    for country_code, country_name in countries.items():
        row_2023 = {'Country': country_name, 'Year': '2023 (Actual)'}
        row_2025 = {'Country': country_name, 'Year': '2025 (Forecast)'}
        row_delta = {'Country': f'{country_name} Δ', 'Year': '2025-2023'}
        
        for indicator_code, indicator_name in indicators.items():
            df = data_dict[country_code][indicator_code]
            val_2023 = df[df['date'] == '2023']['value'].iloc[0] if not df[df['date'] == '2023'].empty else np.nan
            val_2025 = df[df['date'] == '2025']['value'].iloc[0] if not df[df['date'] == '2025'].empty else np.nan
            delta = val_2025 - val_2023 if (not np.isnan(val_2023) and not np.isnan(val_2025)) else np.nan
            
            row_2023[indicator_name] = val_2023
            row_2025[indicator_name] = val_2025
            row_delta[indicator_name] = delta
        
        comparison_data.extend([row_2023, row_2025, row_delta])
    
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

