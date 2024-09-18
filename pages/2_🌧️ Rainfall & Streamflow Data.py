import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Set page title and icon
st.set_page_config(page_title="Rainfall & Streamflow Data", page_icon="🌧️")

# Page title
st.title("🌧️ Rainfall & Streamflow Data")

# Sidebar header for selecting a site
st.sidebar.header("Site Selection")

# Site options for selecting a location
site_options = [
    "Kangaroo Creek", 
    "Little Coliban River", 
    "Five Mile Creek - Woodend RWP Site 1", 
    "Five Mile Creek - Woodend RWP Site 2"
]
selected_site = st.sidebar.selectbox("Choose a site to view data", site_options)

st.sidebar.success(f"Viewing data for: {selected_site}")

# Define file paths for the streamflow data
streamflow_file_paths = {
    "Kangaroo Creek": "clean_wims_406281.csv",
    "Little Coliban River": "clean_wims_406280.csv",
    "Five Mile Creek - Woodend RWP Site 1": "clean_wims_406266.csv",
    "Five Mile Creek - Woodend RWP Site 2": "clean_wims_406266.csv"
}

# Load rainfall data (assuming it's not too large)
@st.cache_data
def load_rainfall_data():
    rainfall_path = Path(__file__).parent.parent / 'data' / "clean_bom_data.csv"
    return pd.read_csv(rainfall_path, parse_dates=['date'])

# Load streamflow data from the correct CSV file
@st.cache_data
def load_streamflow_data(selected_file):
    streamflow_path = Path(__file__).parent.parent / 'data' / selected_file
    return pd.read_csv(streamflow_path, parse_dates=['datetime'])

# Mapping site names to station numbers for both rainfall and streamflow
station_mapping = {
    "Kangaroo Creek": {"rainfall_station": None, "streamflow_station": "406281"},
    "Little Coliban River": {"rainfall_station": 88037, "streamflow_station": "406280"},
    "Five Mile Creek - Woodend RWP Site 1": {"rainfall_station": 88061, "streamflow_station": "406266"},
    "Five Mile Creek - Woodend RWP Site 2": {"rainfall_station": 88061, "streamflow_station": "406266"}
}

# Get the station numbers and corresponding file based on the selected site
selected_rainfall_station = station_mapping[selected_site]["rainfall_station"]
selected_streamflow_file = streamflow_file_paths[selected_site]

# Load and filter rainfall data if available
if selected_rainfall_station:
    site_rainfall = load_rainfall_data()
    site_rainfall = site_rainfall[site_rainfall["station_number"] == selected_rainfall_station]
else:
    site_rainfall = pd.DataFrame()

# Load streamflow data for the selected site
site_streamflow = load_streamflow_data(selected_streamflow_file)

# Plot Rainfall Data (if available)
if not site_rainfall.empty:
    st.subheader(f"Rainfall Data for {selected_site}")
    fig_rainfall = px.line(
        site_rainfall,
        x="date",
        y="rainfall",
        title=f"Rainfall at {selected_site}",
        labels={"rainfall": "Rainfall (mm)", "date": "Date"}
    )
    st.plotly_chart(fig_rainfall)
else:
    st.warning(f"No rainfall data available for {selected_site}. Please upload it to the uploads page.")

# Plot Streamflow Data (if available)
if not site_streamflow.empty:
    st.subheader(f"Streamflow Data for {selected_site}")
    fig_streamflow = px.line(
        site_streamflow,
        x="datetime",
        y="discharge_ml_day",
        title=f"Streamflow at {selected_site}",
        labels={"discharge_ml_day": "Streamflow (ML/day)", "datetime": "Date"}
    )
    st.plotly_chart(fig_streamflow)
else:
    st.warning(f"No streamflow data available for {selected_site}. Please upload it to the uploads page.")
