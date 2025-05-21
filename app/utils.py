# app/utils.py
import pandas as pd
import plotly.express as px
import os

BASE_DATA_PATH = '../data/' # Assuming data folder is one level up from app/

def load_country_data(country_name_lower):
    """Loads cleaned data for a single country."""
    file_path = os.path.join(BASE_DATA_PATH, f"{country_name_lower}_clean.csv")
    try:
        df = pd.read_csv(file_path, index_col='Timestamp', parse_dates=True)
        df['Country'] = country_name_lower.capitalize() # Add country column for easier concatenation
        return df
    except FileNotFoundError:
        # st.error(f"Data file not found for {country_name_lower.capitalize()}: {file_path}")
        return pd.DataFrame() # Return empty DataFrame if file not found

def load_all_selected_data(selected_countries_lower):
    """Loads and concatenates data for all selected countries."""
    all_dfs = []
    for country_lower in selected_countries_lower:
        df_country = load_country_data(country_lower)
        if not df_country.empty:
            all_dfs.append(df_country)

    if not all_dfs:
        return pd.DataFrame()
    return pd.concat(all_dfs)

def generate_ghi_boxplot(df_combined, selected_countries_display):
    """Generates a GHI boxplot for selected countries."""
    if df_combined.empty or 'GHI' not in df_combined.columns or 'Country' not in df_combined.columns:
        return None # Or an empty figure
    
    # Ensure 'Country' column has the display names if they are different from loaded names
    # For simplicity, we assume loaded country names match display names for now
    
    fig = px.box(df_combined, x='Country', y='GHI',
                 color='Country',
                 title="GHI Distribution by Country",
                 labels={"GHI": "Global Horizontal Irradiance (W/m²)", "Country": "Country"},
                 notched=True) # Notched box plot shows confidence interval around the median
    fig.update_layout(title_x=0.5)
    return fig

def get_top_regions_table(df_combined):
    """
    Generates a table of countries ranked by mean GHI.
    'Regions' here is interpreted as 'Countries' given the dataset.
    """
    if df_combined.empty or 'GHI' not in df_combined.columns or 'Country' not in df_combined.columns:
        return pd.DataFrame({'Rank': [], 'Country': [], 'Mean GHI (W/m²)': []})

    summary = df_combined.groupby('Country')['GHI'].agg(['mean', 'median', 'std']).reset_index()
    summary = summary.sort_values(by='mean', ascending=False).reset_index(drop=True)
    summary.rename(columns={'mean': 'Mean GHI (W/m²)',
                            'median': 'Median GHI (W/m²)',
                            'std': 'Std Dev GHI (W/m²)'}, inplace=True)
    summary['Rank'] = summary.index + 1
    return summary[['Rank', 'Country', 'Mean GHI (W/m²)', 'Median GHI (W/m²)', 'Std Dev GHI (W/m²)']]

# You can add more utility functions here for other plots or data processing
def generate_timeseries_plot(df_country, metric='GHI'):
    """Generates a time series plot for a given metric of a single country's data."""
    if df_country.empty or metric not in df_country.columns:
        return None
    # Resample to daily mean for better visualization if data is high frequency
    df_resampled = df_country[metric].resample('D').mean()
    fig = px.line(df_resampled, y=metric, title=f"Daily Average {metric} for {df_country['Country'].iloc[0]}")
    fig.update_layout(title_x=0.5)
    return fig