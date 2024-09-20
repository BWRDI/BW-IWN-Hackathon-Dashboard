import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from pathlib import Path

# Page title and setup
st.set_page_config(page_title="Site Mapping & Data Overview", page_icon="🌍")
st.title("🌍 Site Mapping & Data Overview")

# Sidebar explanation and filters
st.sidebar.header("Station Details Overview")
st.sidebar.write("This page shows the monitoring stations on an interactive map. "
                 "You can select a station from the sidebar to view more details and set alarm sensitivities.")

# Load station data (replace with your actual data)
@st.cache_data
def load_station_data(file_path):
    return pd.read_excel(file_path)

# Path to the Excel file on the server
file_path = Path(__file__).parent.parent / 'data' / 'monitoring_stations.xlsx'

# Load the data
stations_df = load_station_data(file_path)

# Correct the typo in the column name
stations_df.rename(columns={'lattitude': 'latitude'}, inplace=True)

# Sidebar: Sensor Type Selection
sensor_types = ["Overview", "Water Quality Sensor", "Rainfall Sensor", "Temperature Sensor", "Stream Flow Sensor", "Water Quality Sampling Point"]
selected_sensor_type = st.sidebar.selectbox("Select Sensor Type", sensor_types)

# Sidebar: Site Selection
site_options = ["Kangaroo Creek", "Little Coliban River", "Five Mile Creek - Woodend RWP Site 1", "Five Mile Creek - Woodend RWP Site 2"]
selected_site = st.sidebar.selectbox("Select a site", site_options)

# Filter stations by selected sensor type
if selected_sensor_type != "Overview":
    stations_df = stations_df[stations_df['type'] == selected_sensor_type]

# Function to display station details and alarms with sensitivity sliders
def display_station_details(station_name):
    st.subheader(f"Details for {station_name}")

    # Alarms and sensitivity sliders for specific stations
    if station_name == "Kangaroo Creek":
        st.warning("🚨 Eco Detection vs Lab Based Data Difference Alarm")
        sensitivity = st.slider("Set Sensitivity for Kangaroo Creek", 0, 100, 50)
        st.write(f"Sensitivity: {sensitivity}")

    elif station_name == "Little Coliban River":
        st.warning("🚨 Eco Detection vs Lab Based Data Difference Alarm")
        sensitivity = st.slider("Set Sensitivity for Little Coliban River", 0, 100, 50)
        st.write(f"Sensitivity: {sensitivity}")

    elif station_name == "Five Mile Creek - Woodend RWP Site 1":
        st.warning("🚨 Pre-Treatment Water Quality Alarm (Upstream)")
        sensitivity = st.slider("Set Sensitivity for Pre-Treatment at Five Mile Creek 1", 0, 100, 50)
        st.write(f"Sensitivity: {sensitivity}")

    elif station_name == "Five Mile Creek - Woodend RWP Site 2":
        st.warning("🚨 Post-Treatment Water Quality Alarm (Downstream)")
        sensitivity = st.slider("Set Sensitivity for Post-Treatment at Five Mile Creek 2", 0, 100, 50)
        st.write(f"Sensitivity: {sensitivity}")

# Create a map with Folium and add markers for filtered stations
m = folium.Map(location=[-37.814, 144.96332], zoom_start=9)

# Marker color based on station and alarm status
marker_colors = {station: "green" for station in site_options}

# Checkbox to simulate triggered alarms
trigger_alarms = st.sidebar.checkbox("Simulate Alarms")

# Simulate alarms and change marker colors
if trigger_alarms:
    marker_colors["Kangaroo Creek"] = "orange"
    marker_colors["Little Coliban River"] = "red"
    
    # Display warning and error messages for these two sites
    st.warning("⚠️ Warning: Kangaroo Creek has a triggered alarm.")
    st.error("❌ Error: Little Coliban River has a severe issue.")

# Add markers to the map with dynamic colors
for _, row in stations_df.iterrows():
    station_name = row['station_name']
    marker_color = marker_colors.get(station_name, "green")  # Default to green if not triggered
    folium.Marker(
        [row['latitude'], row['longitude']], 
        popup=row['station_name'], 
        icon=folium.Icon(color=marker_color)
    ).add_to(m)

# Display the map using Streamlit
folium_static(m)

# Show station details and alarms based on sidebar selection
if selected_site:
    display_station_details(selected_site)

# Add Recent Data Insights section for the stations
st.subheader("Recent Data Insights")
recent_data = {
    "Kangaroo Creek": {"Turbidity": "7 NTU", "pH": "7.2", "Nitrate": "0.05 mg/L"},
    "Little Coliban River": {"Turbidity": "4 NTU", "pH": "7.0", "Nitrate": "0.04 mg/L"},
    "Five Mile Creek - Woodend RWP Site 1": {"Turbidity": "5 NTU", "pH": "6.9", "Nitrate": "0.03 mg/L"},
    "Five Mile Creek - Woodend RWP Site 2": {"Turbidity": "6 NTU", "pH": "7.1", "Nitrate": "0.06 mg/L"}
}

if selected_site:
    station_data = recent_data.get(selected_site, {})
    st.markdown(f"**Recent Data for {selected_site}**")
    for measure, value in station_data.items():
        st.write(f"- {measure}: {value}")
