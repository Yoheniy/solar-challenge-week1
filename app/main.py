# app/main.py
import streamlit as st
import pandas as pd
from utils import (
    load_all_selected_data,
    generate_ghi_boxplot,
    get_top_regions_table,
    generate_timeseries_plot # Added for more interactivity
)
import os

# Page Configuration
st.set_page_config(layout="wide", page_title="Solar Data Analysis Dashboard")

# --- Helper to check if data directory and files exist ---
def check_data_availability(country_list_lower):
    missing_files = []
    data_dir_exists = os.path.isdir('../data')
    if not data_dir_exists:
        st.error("Error: The 'data' directory does not exist adjacent to the 'app' directory. Please create it and add the cleaned CSV files.")
        return False, []

    for country_lower in country_list_lower:
        file_path = os.path.join('../data', f"{country_lower}_clean.csv")
        if not os.path.exists(file_path):
            missing_files.append(f"{country_lower}_clean.csv")
    
    if missing_files:
        st.warning(f"The following data files are missing from the '../data/' directory: {', '.join(missing_files)}. Some features may not work correctly.")
        if len(missing_files) == len(country_list_lower): # All files missing
             st.error("No data files found. Please ensure benin_clean.csv, sierraleone_clean.csv, and togo_clean.csv are in the '../data/' directory.")
             return False, missing_files
    return True, missing_files


# --- Main App ---
st.title("☀️ Cross-Country Solar Farm Analysis Dashboard")
st.markdown("""
Welcome to the Solar Data Analysis Dashboard.
Use the sidebar to select countries and explore visualizations.
**Note:** This app reads cleaned data CSVs (e.g., `benin_clean.csv`) from a local `data/` directory
(expected to be at the same level as the `app/` directory).
Ensure these files are present for the dashboard to function correctly.
""")

# --- Sidebar for User Inputs ---
st.sidebar.header("🌍 Country Selection")
available_countries_display = ["Benin", "Sierra Leone", "Togo"]
available_countries_lower = [name.lower().replace(" ", "") for name in available_countries_display] # e.g. "sierraleone"

# Check data availability before proceeding
data_available, _ = check_data_availability(available_countries_lower)

selected_countries_display = st.sidebar.multiselect(
    "Select countries to analyze:",
    options=available_countries_display,
    default=available_countries_display[:1] # Default to the first country
)

selected_countries_lower = [name.lower().replace(" ", "") for name in selected_countries_display]

# --- Data Loading ---
df_combined = pd.DataFrame()
if selected_countries_lower and data_available: # Only load if countries are selected and data potentially available
    with st.spinner(f"Loading data for {', '.join(selected_countries_display)}..."):
        df_combined = load_all_selected_data(selected_countries_lower)

    if df_combined.empty and selected_countries_lower:
        st.error(f"Could not load data for the selected countries. Please check if the corresponding CSV files exist in the '../data/' directory and are not empty.")
elif not selected_countries_lower:
    st.info("Please select at least one country from the sidebar to see visualizations.")


# --- Dashboard Sections ---
if not df_combined.empty:
    st.header("📊 Comparative Analysis")

    # 1. Boxplot of GHI
    st.subheader("Global Horizontal Irradiance (GHI) Comparison")
    ghi_boxplot_fig = generate_ghi_boxplot(df_combined, selected_countries_display)
    if ghi_boxplot_fig:
        st.plotly_chart(ghi_boxplot_fig, use_container_width=True)
    else:
        st.write("Not enough data to display GHI boxplot.")

    # 2. Top Regions (Countries) Table
    st.subheader("🏆 Country Performance Summary (by Mean GHI)")
    top_regions_df = get_top_regions_table(df_combined)
    if not top_regions_df.empty:
        st.dataframe(top_regions_df, use_container_width=True)
    else:
        st.write("Not enough data to display the performance summary.")

    # 3. (Optional) Time Series Plot for selected metric
    st.header("📈 Time Series Exploration")
    if len(selected_countries_display) == 1: # Simpler to show for one country
        country_df_for_ts = df_combined[df_combined['Country'] == selected_countries_display[0]]
        
        metrics_for_ts = ['GHI', 'DNI', 'DHI', 'Tamb', 'RH', 'WS']
        # Filter metrics that are actually in the dataframe
        available_metrics_for_ts = [m for m in metrics_for_ts if m in country_df_for_ts.columns]

        if available_metrics_for_ts:
            selected_metric = st.selectbox(
                f"Select metric for {selected_countries_display[0]} time series:",
                options=available_metrics_for_ts,
                index=0 # Default to GHI
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
        st.info("Select a single country to view detailed time series plots.")
    
else:
    if selected_countries_lower and data_available: # Tried to load but failed
        st.warning("No data to display. This might be due to missing or empty data files for the selected countries.")
    elif not data_available:
        st.markdown("---") # Separator
        st.warning("Dashboard cannot display data visualizations due to missing 'data' directory or essential data files.")


st.sidebar.markdown("---")
st.sidebar.info("Dashboard developed for 10 Academy Challenge.")