import streamlit as st
import pandas as pd
import os # For path operations
from utils import (
    load_all_selected_data,
    generate_ghi_boxplot,
    get_top_regions_table,
    generate_timeseries_plot
)

# Page Configuration
st.set_page_config(layout="wide", page_title="Solar Data Analysis Dashboard")

# --- Robust Path to Data Directory (relative to this main.py script) ---
SCRIPT_DIR_MAIN = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT_FROM_MAIN = os.path.abspath(os.path.join(SCRIPT_DIR_MAIN, os.pardir))
DATA_DIR_PATH = os.path.join(PROJECT_ROOT_FROM_MAIN, 'data')
# --- End Path Setup ---

# --- Helper to check if data files exist for selected countries ---
def check_data_files_globally(data_directory_path, country_files_needed_lower):
    """
    Checks if the data directory exists and if all required country files are present.
    Returns True if all conditions met, False otherwise.
    """
    if not os.path.isdir(data_directory_path):
        st.error(f"Critical Error: The data directory ('{data_directory_path}') was not found. Please ensure it exists at the project root and contains the cleaned CSV files.")
        return False

    all_files_found = True
    for country_file_base in country_files_needed_lower:
        file_path = os.path.join(data_directory_path, f"{country_file_base}_clean.csv")
        if not os.path.exists(file_path):
            st.warning(f"Data file missing: {country_file_base}_clean.csv (Expected in '{data_directory_path}')")
            all_files_found = False
    
    if not all_files_found:
        st.error("One or more required data files are missing. Dashboard functionality will be limited.")
    return all_files_found


# --- Main App ---
st.title("☀️ Cross-Country Solar Farm Analysis Dashboard")
st.markdown("""
Welcome to the Solar Data Analysis Dashboard.
Use the sidebar to select countries and explore visualizations.
**Note:** This app reads cleaned data CSVs (e.g., `benin_clean.csv`) from a local `data/` directory.
This `data/` directory is expected to be at the same level as the `app/` directory (i.e., in the project root).
Ensure these files are present for the dashboard to function correctly.
""")

# --- Sidebar for User Inputs ---
st.sidebar.header("🌍 Country Selection")
available_countries_display = ["Benin", "Sierra Leone", "Togo"]
available_countries_lower = [name.lower().replace(" ", "") for name in available_countries_display]

# Initial check if data directory and ANY of the essential files are present at app start
# This provides a general status before user interaction.
initial_data_check_ok = check_data_files_globally(DATA_DIR_PATH, available_countries_lower)

selected_countries_display = st.sidebar.multiselect(
    "Select countries to analyze:",
    options=available_countries_display,
    default=available_countries_display[:1] if initial_data_check_ok else [] # Default to first if data ok, else empty
)
selected_countries_lower = [name.lower().replace(" ", "") for name in selected_countries_display]


# --- Data Loading ---
df_combined = pd.DataFrame()
data_load_successful = False

if not initial_data_check_ok:
    st.warning("Initial data check failed. Please ensure the 'data' directory and required CSV files are correctly placed. See messages above.")
elif not selected_countries_lower:
    st.info("Please select at least one country from the sidebar to see visualizations.")
else:
    # At this point, initial_data_check_ok is True, and countries are selected
    # We can be more optimistic or re-check specifically for selected countries if desired,
    # but utils.load_country_data will handle individual file errors.
    with st.spinner(f"Loading data for {', '.join(selected_countries_display)}..."):
        df_combined = load_all_selected_data(selected_countries_lower)

    if not df_combined.empty:
        data_load_successful = True
    else:
        st.error(f"Failed to load data for the selected countries. Please check previous error messages if any, or ensure the CSV files are not empty/corrupted.")


# --- Dashboard Sections ---
if data_load_successful:
    st.header("📊 Comparative Analysis")

    # 1. Boxplot of GHI
    st.subheader("Global Horizontal Irradiance (GHI) Comparison")
    ghi_boxplot_fig = generate_ghi_boxplot(df_combined, selected_countries_display)
    if ghi_boxplot_fig:
        st.plotly_chart(ghi_boxplot_fig, use_container_width=True)
    else:
        st.write("Could not display GHI boxplot. (Data might be missing 'GHI' or 'Country' columns).")

    # 2. Top Regions (Countries) Table
    st.subheader("🏆 Country Performance Summary (by Mean GHI)")
    top_regions_df = get_top_regions_table(df_combined)
    if not top_regions_df.empty:
        st.dataframe(top_regions_df, use_container_width=True)
    else:
        st.write("Could not display the performance summary.")

    # 3. (Optional) Time Series Plot for selected metric
    st.header("📈 Time Series Exploration")
    if len(selected_countries_display) == 1:
        country_df_for_ts = df_combined # df_combined already filtered if one country selected
        
        metrics_for_ts = ['GHI', 'DNI', 'DHI', 'Tamb', 'RH', 'WS']
        available_metrics_for_ts = [m for m in metrics_for_ts if m in country_df_for_ts.columns]

        if available_metrics_for_ts:
            selected_metric = st.selectbox(
                f"Select metric for {selected_countries_display[0]} time series:",
                options=available_metrics_for_ts,
                index=0 if 'GHI' in available_metrics_for_ts else 0
            )
            if selected_metric:
                ts_fig = generate_timeseries_plot(country_df_for_ts, selected_metric)
                if ts_fig:
                    st.plotly_chart(ts_fig, use_container_width=True)
                else:
                    st.write(f"Could not generate time series plot for {selected_metric}.")
        else:
            st.write(f"No standard metrics available for time series plot for {selected_countries_display[0]}.")

    elif len(selected_countries_display) > 1:
        st.info("Select a single country from the sidebar to view detailed time series plots for that country.")
    
elif selected_countries_lower and initial_data_check_ok: # Attempted load but failed
    st.markdown("---")
    st.warning("No data to display for the selected countries. Please check for specific error messages above regarding file loading or data processing issues.")
# (If initial_data_check_ok was False, messages are already shown)
# (If no countries selected, the st.info message above handles it)

st.sidebar.markdown("---")
st.sidebar.info("Dashboard developed for 10 Academy Challenge.")






#code with debugging
# import streamlit as st
# import pandas as pd
# import os # For path operations
# from utils import (
#     load_all_selected_data,
#     generate_ghi_boxplot,
#     get_top_regions_table,
#     generate_timeseries_plot,
#     print_utils_debug_paths # Import the debug print function
# )

# # Page Configuration
# st.set_page_config(layout="wide", page_title="Solar Data Analysis Dashboard")

# # --- Debugging Information from main.py perspective ---
# SCRIPT_DIR_MAIN = os.path.dirname(os.path.abspath(__file__))
# PROJECT_ROOT_GUESS_FROM_MAIN = os.path.abspath(os.path.join(SCRIPT_DIR_MAIN, os.pardir))
# DATA_DIR_EXPECTED_FROM_MAIN = os.path.join(PROJECT_ROOT_GUESS_FROM_MAIN, 'data')

# st.sidebar.markdown("--- `main.py` Debug Info ---")
# st.sidebar.text(f"Main Script Dir: {SCRIPT_DIR_MAIN}")
# st.sidebar.text(f"Main Guessed Proj Root: {PROJECT_ROOT_GUESS_FROM_MAIN}")
# st.sidebar.text(f"Main Expected Data Dir: {DATA_DIR_EXPECTED_FROM_MAIN}")
# st.sidebar.text(f"Main: Data Dir Exists? {os.path.exists(DATA_DIR_EXPECTED_FROM_MAIN)}")
# st.sidebar.text(f"Main: Data Dir Is Dir? {os.path.isdir(DATA_DIR_EXPECTED_FROM_MAIN)}")
# if os.path.exists(DATA_DIR_EXPECTED_FROM_MAIN) and os.path.isdir(DATA_DIR_EXPECTED_FROM_MAIN):
#     try:
#         st.sidebar.text(f"Main: Data Contents: {os.listdir(DATA_DIR_EXPECTED_FROM_MAIN)}")
#     except Exception as e:
#         st.sidebar.text(f"Main: Error listing data contents: {e}")
# st.sidebar.markdown("--- End `main.py` Debug ---")

# # --- Call the debug print function from utils.py ---
# print_utils_debug_paths()


# # --- Helper to check if data files exist for selected countries ---
# def check_data_files_availability(country_list_lower, data_directory_path):
#     """Checks if individual CSV files exist for the given countries in the data_directory_path."""
#     missing_files_details = []
#     all_files_present = True

#     if not os.path.isdir(data_directory_path):
#         st.error(f"CRITICAL: The data directory '{data_directory_path}' does not exist or is not a directory.")
#         return False, [f"Data directory missing: {data_directory_path}"]

#     for country_lower in country_list_lower:
#         file_path = os.path.join(data_directory_path, f"{country_lower}_clean.csv")
#         if not os.path.exists(file_path):
#             missing_files_details.append(f"{country_lower}_clean.csv (expected at {file_path})")
#             all_files_present = False
#             st.warning(f"File missing: {file_path}") # Immediate feedback
    
#     if not all_files_present:
#         st.error(f"One or more required data files are missing from '{data_directory_path}'. Details: {', '.join(missing_files_details)}")
    
#     return all_files_present, missing_files_details


# # --- Main App ---
# st.title("☀️ Cross-Country Solar Farm Analysis Dashboard")
# st.markdown("""
# Welcome to the Solar Data Analysis Dashboard.
# Use the sidebar to select countries and explore visualizations.
# **Note:** This app reads cleaned data CSVs (e.g., `benin_clean.csv`) from a local `data/` directory.
# This `data/` directory is expected to be at the same level as the `app/` directory (i.e., in the project root).
# Ensure these files are present for the dashboard to function correctly.
# """)

# # --- Sidebar for User Inputs ---
# st.sidebar.header("🌍 Country Selection")
# available_countries_display = ["Benin", "Sierra Leone", "Togo"]
# # Ensure lowercase names match your CSV filenames (e.g., 'sierraleone' not 'sierra leone')
# available_countries_lower = [name.lower().replace(" ", "") for name in available_countries_display]

# selected_countries_display = st.sidebar.multiselect(
#     "Select countries to analyze:",
#     options=available_countries_display,
#     default=available_countries_display[:1] # Default to the first country
# )
# selected_countries_lower = [name.lower().replace(" ", "") for name in selected_countries_display]


# # --- Data Loading ---
# df_combined = pd.DataFrame()
# data_load_attempted = False

# if selected_countries_lower:
#     data_load_attempted = True
#     # DATA_DIR_EXPECTED_FROM_MAIN is the absolute path to the 'data' directory
#     files_ok, _ = check_data_files_availability(selected_countries_lower, DATA_DIR_EXPECTED_FROM_MAIN)
    
#     if files_ok:
#         with st.spinner(f"Loading data for {', '.join(selected_countries_display)}..."):
#             df_combined = load_all_selected_data(selected_countries_lower)

#         if df_combined.empty:
#             st.error(f"Data loading failed for selected countries, even though files might exist. Check console/terminal for detailed errors from utils.py or if files are empty/corrupted.")
#     else:
#         st.error("Data loading cannot proceed due to missing files as detailed above.")
        
# elif not selected_countries_lower:
#     st.info("Please select at least one country from the sidebar to see visualizations.")


# # --- Dashboard Sections ---
# if not df_combined.empty:
#     st.header("📊 Comparative Analysis")

#     # 1. Boxplot of GHI
#     st.subheader("Global Horizontal Irradiance (GHI) Comparison")
#     ghi_boxplot_fig = generate_ghi_boxplot(df_combined, selected_countries_display)
#     if ghi_boxplot_fig:
#         st.plotly_chart(ghi_boxplot_fig, use_container_width=True)
#     else:
#         st.write("Could not display GHI boxplot. Ensure data is loaded and contains 'GHI' and 'Country' columns.")

#     # 2. Top Regions (Countries) Table
#     st.subheader("🏆 Country Performance Summary (by Mean GHI)")
#     top_regions_df = get_top_regions_table(df_combined)
#     if not top_regions_df.empty:
#         st.dataframe(top_regions_df, use_container_width=True)
#     else:
#         st.write("Could not display the performance summary. Ensure data is loaded.")

#     # 3. (Optional) Time Series Plot for selected metric
#     st.header("📈 Time Series Exploration")
#     if len(selected_countries_display) == 1:
#         # df_combined will contain data for only one country if only one is selected
#         country_df_for_ts = df_combined 
        
#         metrics_for_ts = ['GHI', 'DNI', 'DHI', 'Tamb', 'RH', 'WS']
#         available_metrics_for_ts = [m for m in metrics_for_ts if m in country_df_for_ts.columns]

#         if available_metrics_for_ts:
#             selected_metric = st.selectbox(
#                 f"Select metric for {selected_countries_display[0]} time series:",
#                 options=available_metrics_for_ts,
#                 index=0 if 'GHI' in available_metrics_for_ts else 0 # Default to GHI or first available
#             )
#             if selected_metric:
#                 ts_fig = generate_timeseries_plot(country_df_for_ts, selected_metric)
#                 if ts_fig:
#                     st.plotly_chart(ts_fig, use_container_width=True)
#                 else:
#                     st.write(f"Could not generate time series plot for {selected_metric}.")
#         else:
#             st.write(f"No standard metrics available for time series plot for {selected_countries_display[0]}.")

#     elif len(selected_countries_display) > 1:
#         st.info("Select a single country from the sidebar to view detailed time series plots for that country.")
    
# else:
#     if data_load_attempted: # Only show this if we actually tried to load data
#         st.markdown("---")
#         st.warning("No data to display. This might be due to missing, empty, or corrupted data files, or issues during data processing. Please check messages above and in the sidebar for details.")
#     elif not selected_countries_lower: # No countries selected yet
#         pass # The st.info message above handles this.


# st.sidebar.markdown("---")
# st.sidebar.info("Dashboard developed for 10 Academy Challenge.")