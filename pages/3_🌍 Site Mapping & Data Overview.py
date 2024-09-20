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

# Load station data from table (replace with actual data if necessary)
data = {
    'owner': ['Coliban Water', 'Coliban Water', 'Greater Western Water', 'Greater Western Water', 'Bureau of Meteorology',
              'Bureau of Meteorology', 'Bureau of Meteorology', 'DEECA', 'DEECA', 'DEECA', 'Coliban Water', 'Coliban Water'],
    'reference': ['cw_a', 'cw_b', 'gww_a', 'gww_b', '88037', '88061', '88051', '406281', '406280', '406266', 'Site2', 'Site17'],
    'station_name': ['Kangaroo Creek', 'Little Coliban River', 'Five Mile Creek - Site 1', 'Five Mile Creek - Site 2',
                     'Lauriston Reservoir', 'Woodend', 'Redesdale', 'Kangaroo Creek', 'Little Coliban River', 'Five Mile Creek',
                     'Little Coliban River', 'Kangaroo Creek'],
    'type': ['Water Quality (sensor)', 'Water Quality (sensor)', 'Water Quality (sensor)', 'Water Quality (sensor)', 'Rainfall',
             'Rainfall', 'Temperature', 'Stream flow', 'Stream flow', 'Stream flow', 'Water Quality (lab)', 'Water Quality (lab)'],
    'latitude': [-37.23092, -37.28939, -37.33819, -37.33288, -37.2535, -37.3578, -37.0194, -37.23897, -37.28958, -37.33775,
                 -37.2893731, -37.2391],
    'longitude': [144.34361, 144.43381, 144.51067, 144.51034, 144.3825, 144.539, 144.5203, 144.3392, 144.4339, 144.5115,
                  144.4338769, 144.3397]
}

stations_df = pd.DataFrame(data)

# Sidebar: Sensor Type Selection
sensor_types = ["Overview", "Water Quality Sensor", "Rainfall Sensor", "Temperature Sensor", "Stream Flow Sensor", "Water Quality Sampling Point"]
selected_sensor_type = st.sidebar.selectbox("Select Sensor Type", sensor_types)

# Sidebar: Site Selection
site_options = ["Kangaroo Creek", "Little Coliban River", "Five Mile Creek - Woodend RWP Site 1", "Five Mile Creek - Woodend RWP Site 2"]
selected_site = st.sidebar.selectbox("Select a site", site_options)

# Function to return color based on the type of station
def get_marker_color(station_type):
    if station_type == "Rainfall":
        return "blue"
    elif station_type == "Temperature":
        return "black"
    elif station_type == "Water Quality (lab)":
        return "pink"
    elif station_type == "Stream flow":
        return "blue"
    else:
        return "green"

# Filter the DataFrame based on the selected sensor type
if selected_sensor_type != "Overview":
    stations_df = stations_df[stations_df["type"].str.contains(selected_sensor_type)]

# Apply default colors
stations_df['color'] = stations_df['type'].apply(get_marker_color)

# Checkbox to simulate triggered alarms
trigger_alarms = st.sidebar.checkbox("Simulate Alarms")

# Simulate alarms and change marker colors if triggered
if trigger_alarms:
    st.warning("⚠️ Simulated Alarms: Kangaroo Creek (orange) and Little Coliban River (red).")
    # Modify colors only for specific rows (by boolean masking)
    stations_df.loc[stations_df['station_name'] == "Kangaroo Creek", 'color'] = "orange"
    stations_df.loc[stations_df['station_name'] == "Little Coliban River", 'color'] = "red"

    # Display warning and error messages for the alarms
    st.warning("Kangaroo Creek: Eco Detection vs Lab Based Data Difference Alarm triggered.")
    st.error("Little Coliban River: Eco Detection vs Lab Based Data Difference Alarm triggered.")

# Create a map with Folium
m = folium.Map(location=[-37.268, 144.442], zoom_start=9)

# Add markers to the map
for _, row in stations_df.iterrows():
    folium.Marker(
        [row['latitude'], row['longitude']],
        popup=f"{row['station_name']} - {row['type']}",  # Include station type in the popup
        icon=folium.Icon(color=row['color'])
    ).add_to(m)

# Display the map using Streamlit
folium_static(m)

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

# Show station details and alarms based on the selected site
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
