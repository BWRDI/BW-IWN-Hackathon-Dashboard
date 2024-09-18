import streamlit as st
import pandas as pd
import plotly.express as px

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

# Introduction text for Rainfall & Streamflow data
st.markdown(
    f"""
    You are currently viewing the rainfall and streamflow data for **{selected_site}**.
    
    This section provides a detailed look into the environmental factors affecting water quality, 
    including rainfall and streamflow data.
    
    **Select different sites from the sidebar** to compare data from various locations.
    """
)

# Load Rainfall and Streamflow data using st.cache_data
@st.cache_data
def load_data():
    # Load rainfall and streamflow data from the correct paths
    rainfall_data = pd.read_csv("/workspaces/gdp-dashboard/data/clean_bom_data.csv")
    streamflow_data = pd.read_csv("/workspaces/gdp-dashboard/data/clean_wims_data.csv")
    return rainfall_data, streamflow_data

# Load the datasets
rainfall_data, streamflow_data = load_data()

# Mapping site names to station numbers for both rainfall and streamflow
station_mapping = {
    "Kangaroo Creek": {"rainfall_station": None, "streamflow_station": 406281},
    "Little Coliban River": {"rainfall_station": 88037, "streamflow_station": 406280},
    "Five Mile Creek - Woodend RWP Site 1": {"rainfall_station": 88061, "streamflow_station": 406266},
    "Five Mile Creek - Woodend RWP Site 2": {"rainfall_station": 88061, "streamflow_station": 406266}
}

# Get the station numbers based on the selected site
selected_rainfall_station = station_mapping[selected_site]["rainfall_station"]
selected_streamflow_station = station_mapping[selected_site]["streamflow_station"]

# Filter the rainfall data based on the station number (if available)
if selected_rainfall_station:
    site_rainfall = rainfall_data[rainfall_data["station_number"] == selected_rainfall_station]
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
    st.write(f"No rainfall data available for {selected_site}")

# Filter the streamflow data based on the station number
site_streamflow = streamflow_data[streamflow_data["station_number"] == selected_streamflow_station]
st.subheader(f"Streamflow Data for {selected_site}")
fig_streamflow = px.line(
    site_streamflow, 
    x="datetime", 
    y="discharge_ml_day", 
    title=f"Streamflow at {selected_site}", 
    labels={"discharge_ml_day": "Streamflow (ML/day)", "datetime": "Date"}
)
st.plotly_chart(fig_streamflow)