
import pandas as pd
import plotly.express as px
import os
import streamlit as st

# --- Path setup (retained for robustness) ---
SCRIPT_DIR_UTILS = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT_GUESS_FROM_UTILS = os.path.abspath(os.path.join(SCRIPT_DIR_UTILS, os.pardir))
ABSOLUTE_DATA_PATH_FOR_UTILS = os.path.join(PROJECT_ROOT_GUESS_FROM_UTILS, 'data')
# --- End of path setup ---

def load_country_data(country_name_lower):
    """Loads cleaned data for a single country."""
    file_path = os.path.join(ABSOLUTE_DATA_PATH_FOR_UTILS, f"{country_name_lower}_clean.csv")

    try:
        df = pd.read_csv(file_path, index_col='Timestamp', parse_dates=True)
        df['Country'] = country_name_lower.capitalize()
        return df
    except FileNotFoundError:
        st.error(f"Data file not found for {country_name_lower.capitalize()}. Expected at: {file_path}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading {file_path}: {e}")
        return pd.DataFrame()

def load_all_selected_data(selected_countries_lower):
    """Loads and concatenates data for all selected countries."""
    all_dfs = []
    if not selected_countries_lower:
        # This case should ideally be handled by main.py before calling
        return pd.DataFrame()

    for country_lower in selected_countries_lower:
        df_country = load_country_data(country_lower)
        if not df_country.empty:
            all_dfs.append(df_country)
        # else: error already shown by load_country_data

    if not all_dfs:
        # This message can be useful if all individual loads failed silently for some reason
        # st.warning("Utils: Failed to load data for any of the selected countries.")
        return pd.DataFrame()
    
    return pd.concat(all_dfs)

def generate_ghi_boxplot(df_combined, selected_countries_display):
    """Generates a GHI boxplot for selected countries."""
    if df_combined.empty or 'GHI' not in df_combined.columns or 'Country' not in df_combined.columns:
        # st.warning("Boxplot: Not enough data or missing 'GHI'/'Country' columns for GHI boxplot.")
        return None
    
    fig = px.box(df_combined, x='Country', y='GHI',
                 color='Country',
                 title="GHI Distribution by Country",
                 labels={"GHI": "Global Horizontal Irradiance (W/m²)", "Country": "Country"},
                 notched=True)
    fig.update_layout(title_x=0.5)
    return fig

def get_top_regions_table(df_combined):
    """
    Generates a table of countries ranked by mean GHI.
    """
    if df_combined.empty or 'GHI' not in df_combined.columns or 'Country' not in df_combined.columns:
        # st.warning("Table: Not enough data or missing 'GHI'/'Country' columns for summary table.")
        return pd.DataFrame({'Rank': [], 'Country': [], 'Mean GHI (W/m²)': []})

    summary = df_combined.groupby('Country')['GHI'].agg(['mean', 'median', 'std']).reset_index()
    summary = summary.sort_values(by='mean', ascending=False).reset_index(drop=True)
    summary.rename(columns={'mean': 'Mean GHI (W/m²)',
                            'median': 'Median GHI (W/m²)',
                            'std': 'Std Dev GHI (W/m²)'}, inplace=True)
    summary['Rank'] = summary.index + 1
    return summary[['Rank', 'Country', 'Mean GHI (W/m²)', 'Median GHI (W/m²)', 'Std Dev GHI (W/m²)']]

def generate_timeseries_plot(df_country, metric='GHI'):
    """Generates a time series plot for a given metric of a single country's data."""
    if df_country.empty or metric not in df_country.columns:
        # st.warning(f"Timeseries: Data for {metric} not found or dataframe empty for timeseries plot.")
        return None
    
    country_name_for_title = "Selected Country"
    if 'Country' in df_country.columns and not df_country['Country'].empty:
        country_name_for_title = df_country['Country'].iloc[0]
        
    try:
        df_resampled = df_country[metric].resample('D').mean()
    except Exception as e:
        st.error(f"Timeseries: Error resampling data for {metric}: {e}")
        return None
        
    fig = px.line(df_resampled, y=metric, title=f"Daily Average {metric} for {country_name_for_title}")
    fig.update_layout(title_x=0.5)
    return fig







#code with debugging


# import pandas as pd
# import plotly.express as px
# import os
# import streamlit as st # Import streamlit here if you use st.write for debugging

# # --- Debug lines to understand pathing ---
# SCRIPT_DIR_UTILS = os.path.dirname(os.path.abspath(__file__))
# # This st.write might not appear if utils.py is just imported and not directly run,
# # but the variables will be set for use within functions.
# # We can move these prints into a function called from main.py if needed.
# # For now, let's assume SCRIPT_DIR_UTILS is correctly set.
# PROJECT_ROOT_GUESS_FROM_UTILS = os.path.abspath(os.path.join(SCRIPT_DIR_UTILS, os.pardir)) # Goes one level up from 'app'
# ABSOLUTE_DATA_PATH_GUESS_FROM_UTILS = os.path.join(PROJECT_ROOT_GUESS_FROM_UTILS, 'data')
# # --- End of debug path setup ---


# def print_utils_debug_paths():
#     """Helper function to print debug paths from utils, callable from main.py"""
#     st.sidebar.markdown("--- `utils.py` Debug Info ---")
#     st.sidebar.text(f"Utils Script Dir: {SCRIPT_DIR_UTILS}")
#     st.sidebar.text(f"Utils Guessed Proj Root: {PROJECT_ROOT_GUESS_FROM_UTILS}")
#     st.sidebar.text(f"Utils Guessed Data Path: {ABSOLUTE_DATA_PATH_GUESS_FROM_UTILS}")
#     st.sidebar.text(f"Utils: Data Path Exists? {os.path.exists(ABSOLUTE_DATA_PATH_GUESS_FROM_UTILS)}")
#     st.sidebar.text(f"Utils: Data Path Is Dir? {os.path.isdir(ABSOLUTE_DATA_PATH_GUESS_FROM_UTILS)}")
#     if os.path.exists(ABSOLUTE_DATA_PATH_GUESS_FROM_UTILS) and os.path.isdir(ABSOLUTE_DATA_PATH_GUESS_FROM_UTILS):
#         try:
#             st.sidebar.text(f"Utils: Data Contents: {os.listdir(ABSOLUTE_DATA_PATH_GUESS_FROM_UTILS)}")
#         except Exception as e:
#             st.sidebar.text(f"Utils: Error listing data contents: {e}")
#     st.sidebar.markdown("--- End `utils.py` Debug ---")


# def load_country_data(country_name_lower):
#     """Loads cleaned data for a single country."""
#     # Construct the path robustly from where this script (utils.py) is located
#     # Assumes utils.py is in 'app/' and 'data/' is sibling to 'app/'
    
#     # Using the pre-calculated absolute path for data
#     file_path = os.path.join(ABSOLUTE_DATA_PATH_GUESS_FROM_UTILS, f"{country_name_lower}_clean.csv")
    
#     # This debug message will appear for each attempt to load a country's data
#     st.info(f"Utils: Attempting to load data from: {file_path}")

#     try:
#         df = pd.read_csv(file_path, index_col='Timestamp', parse_dates=True)
#         df['Country'] = country_name_lower.capitalize()
#         # st.success(f"Utils: Successfully loaded {file_path}") # Can be noisy
#         return df
#     except FileNotFoundError:
#         st.error(f"Utils: FileNotFoundError for {country_name_lower.capitalize()}. Expected at: {file_path}")
#         return pd.DataFrame()
#     except Exception as e:
#         st.error(f"Utils: Error loading {file_path}: {e}")
#         return pd.DataFrame()

# def load_all_selected_data(selected_countries_lower):
#     """Loads and concatenates data for all selected countries."""
#     all_dfs = []
#     if not selected_countries_lower:
#         st.warning("Utils: No countries selected for data loading.")
#         return pd.DataFrame()

#     for country_lower in selected_countries_lower:
#         df_country = load_country_data(country_lower)
#         if not df_country.empty:
#             all_dfs.append(df_country)
#         else:
#             st.warning(f"Utils: No data loaded for {country_lower.capitalize()}. Check previous error messages.")


#     if not all_dfs:
#         st.error("Utils: Failed to load data for any of the selected countries.")
#         return pd.DataFrame()
    
#     st.success(f"Utils: Successfully loaded data for: {', '.join(c.capitalize() for c in selected_countries_lower)}")
#     return pd.concat(all_dfs)

# def generate_ghi_boxplot(df_combined, selected_countries_display):
#     """Generates a GHI boxplot for selected countries."""
#     if df_combined.empty or 'GHI' not in df_combined.columns or 'Country' not in df_combined.columns:
#         st.warning("Boxplot: Not enough data or missing 'GHI'/'Country' columns for GHI boxplot.")
#         return None
    
#     fig = px.box(df_combined, x='Country', y='GHI',
#                  color='Country',
#                  title="GHI Distribution by Country",
#                  labels={"GHI": "Global Horizontal Irradiance (W/m²)", "Country": "Country"},
#                  notched=True)
#     fig.update_layout(title_x=0.5)
#     return fig

# def get_top_regions_table(df_combined):
#     """
#     Generates a table of countries ranked by mean GHI.
#     'Regions' here is interpreted as 'Countries' given the dataset.
#     """
#     if df_combined.empty or 'GHI' not in df_combined.columns or 'Country' not in df_combined.columns:
#         st.warning("Table: Not enough data or missing 'GHI'/'Country' columns for summary table.")
#         return pd.DataFrame({'Rank': [], 'Country': [], 'Mean GHI (W/m²)': []})

#     summary = df_combined.groupby('Country')['GHI'].agg(['mean', 'median', 'std']).reset_index()
#     summary = summary.sort_values(by='mean', ascending=False).reset_index(drop=True)
#     summary.rename(columns={'mean': 'Mean GHI (W/m²)',
#                             'median': 'Median GHI (W/m²)',
#                             'std': 'Std Dev GHI (W/m²)'}, inplace=True)
#     summary['Rank'] = summary.index + 1
#     return summary[['Rank', 'Country', 'Mean GHI (W/m²)', 'Median GHI (W/m²)', 'Std Dev GHI (W/m²)']]

# def generate_timeseries_plot(df_country, metric='GHI'):
#     """Generates a time series plot for a given metric of a single country's data."""
#     if df_country.empty or metric not in df_country.columns:
#         st.warning(f"Timeseries: Data for {metric} not found or dataframe empty for timeseries plot.")
#         return None
    
#     # Ensure 'Country' column exists and has at least one value to avoid iloc error
#     country_name_for_title = "Selected Country"
#     if 'Country' in df_country.columns and not df_country['Country'].empty:
#         country_name_for_title = df_country['Country'].iloc[0]
        
#     # Resample to daily mean for better visualization if data is high frequency
#     try:
#         df_resampled = df_country[metric].resample('D').mean()
#     except Exception as e:
#         st.error(f"Timeseries: Error resampling data for {metric}: {e}")
#         return None
        
#     fig = px.line(df_resampled, y=metric, title=f"Daily Average {metric} for {country_name_for_title}")
#     fig.update_layout(title_x=0.5)
#     return fig

