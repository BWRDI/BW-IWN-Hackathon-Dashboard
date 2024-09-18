import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import timedelta

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

# Load rainfall data
@st.cache_data
def load_rainfall_data():
    rainfall_path = Path(__file__).parent.parent / 'data' / "clean_bom_data.csv"
    return pd.read_csv(rainfall_path, parse_dates=['date'], dayfirst=True)  # dayfirst=True for DD/MM/YYYY format

# Load streamflow data from the correct CSV file
@st.cache_data
def load_streamflow_data(selected_file):
    streamflow_path = Path(__file__).parent.parent / 'data' / selected_file
    # Handle date format in streamflow data with dayfirst=True
    return pd.read_csv(streamflow_path, parse_dates=['datetime'], dayfirst=True)

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

# Ensure all dates are in datetime format
if not site_rainfall.empty:
    site_rainfall['date'] = pd.to_datetime(site_rainfall['date'], dayfirst=True)

if not site_streamflow.empty:
    site_streamflow['datetime'] = pd.to_datetime(site_streamflow['datetime'], dayfirst=True)

# Determine the minimum and maximum dates for both datasets
if not site_rainfall.empty:
    min_date_rainfall = site_rainfall['date'].min().to_pydatetime()  # Convert to datetime
    max_date_rainfall = site_rainfall['date'].max().to_pydatetime()  # Convert to datetime
else:
    min_date_rainfall, max_date_rainfall = None, None

if not site_streamflow.empty:
    min_date_streamflow = site_streamflow['datetime'].min().to_pydatetime()  # Convert to datetime
    max_date_streamflow = site_streamflow['datetime'].max().to_pydatetime()  # Convert to datetime
else:
    min_date_streamflow, max_date_streamflow = None, None

# Determine the overall min and max dates for the slider
valid_dates = [d for d in [min_date_rainfall, min_date_streamflow] if d is not None]
min_date = min(valid_dates) if valid_dates else None
valid_dates = [d for d in [max_date_rainfall, max_date_streamflow] if d is not None]
max_date = max(valid_dates) if valid_dates else None

# Set default value for the last year
if max_date:
    default_start_date = max_date - timedelta(days=365)
else:
    default_start_date = None

# Use session state to persist the date range across site selections
if 'date_range' not in st.session_state:
    st.session_state.date_range = (default_start_date, max_date) if default_start_date and max_date else None

# Add a date range slider for selecting the date range in the sidebar
if min_date and max_date:
    st.sidebar.markdown("### Select Date Range to Zoom In")
    selected_dates = st.sidebar.slider(
        "Date Range", 
        min_value=min_date, 
        max_value=max_date, 
        value=st.session_state.date_range,  # Use session state for persistence
        format="YYYY-MM-DD"
    )

    # Update session state when the slider changes
    st.session_state.date_range = selected_dates
else:
    st.warning("No valid date range available for the selected site.")

# Filter the rainfall data based on the selected date range
if not site_rainfall.empty and 'date_range' in st.session_state:
    site_rainfall_filtered = site_rainfall[
        (site_rainfall['date'] >= st.session_state.date_range[0]) & (site_rainfall['date'] <= st.session_state.date_range[1])
    ]
else:
    site_rainfall_filtered = pd.DataFrame()

# Filter the streamflow data based on the selected date range
if not site_streamflow.empty and 'date_range' in st.session_state:
    site_streamflow_filtered = site_streamflow[
        (site_streamflow['datetime'] >= st.session_state.date_range[0]) & (site_streamflow['datetime'] <= st.session_state.date_range[1])
    ]
else:
    site_streamflow_filtered = pd.DataFrame()

# Plot Rainfall Data (if available)
if not site_rainfall_filtered.empty:
    st.subheader(f"Rainfall Data for {selected_site}")
    fig_rainfall = px.line(
        site_rainfall_filtered,
        x="date",
        y="rainfall",
        title=f"Rainfall at {selected_site}",
        labels={"rainfall": "Rainfall (mm)", "date": "Date"}
    )
    st.plotly_chart(fig_rainfall)
else:
    st.warning(f"No rainfall data available for {selected_site}. Please upload it to the uploads page.")

# Plot Streamflow Data (if available)
if not site_streamflow_filtered.empty:
    st.subheader(f"Streamflow Data for {selected_site}")
    fig_streamflow = px.line(
        site_streamflow_filtered,
        x="datetime",
        y="discharge_ml_day",
        title=f"Streamflow at {selected_site}",
        labels={"discharge_ml_day": "Streamflow (ML/day)", "datetime": "Date"}
    )
    st.plotly_chart(fig_streamflow)
else:
    st.warning(f"No streamflow data available for {selected_site}. Please upload it to the uploads page.")
