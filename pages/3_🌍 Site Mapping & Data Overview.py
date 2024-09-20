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
                 "Click on a station to view more details and set alarm sensitivities.")

# Station type filter in the sidebar
station_types = ["All", "Water Quality", "Rainfall", "Streamflow"]
selected_type = st.sidebar.selectbox("Filter by Station Type", station_types)

# Load the Excel file directly from the server
@st.cache_data
def load_station_data(file_path):
    return pd.read_excel(file_path)

# Path to the Excel file on the server
file_path = Path(__file__).parent.parent / 'data' / 'monitoring_stations.xlsx'

# Load the data
stations_df = load_station_data(file_path)

# Correct the typo in the column name
stations_df.rename(columns={'lattitude': 'latitude'}, inplace=True)

# Filter stations by the selected type (if not "All")
if selected_type != "All":
    stations_df = stations_df[stations_df["type"] == selected_type]

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

    else:
        st.success("No alarms for this site.")

# Create a map using Folium with clickable markers
m = folium.Map(location=[-37.814, 144.96332], zoom_start=9)

# Marker color based on station and alarm status
def get_marker_color(station_name):
    if station_name in ["Kangaroo Creek", "Little Coliban River"]:
        return "orange"  # Eco Detection vs Lab based alarm
    elif station_name == "Five Mile Creek - Woodend RWP Site 1":
        return "blue"  # Pre-Treatment alarm
    elif station_name == "Five Mile Creek - Woodend RWP Site 2":
        return "green"  # Post-Treatment alarm
    else:
        return "gray"

# Use session state to track selected station
if 'selected_station' not in st.session_state:
    st.session_state.selected_station = None

# Function to create marker popup with clickable link
def create_popup_html(station_name):
    return f'<b>{station_name}</b><br><a href="#" onclick="window.parent.postMessage(\'{station_name}\', \'*\')">View Alarms</a>'

# Add markers to the map with colors based on alarms
for _, row in stations_df.iterrows():
    marker_color = get_marker_color(row['station_name'])
    popup_html = create_popup_html(row['station_name'])
    folium.Marker([row['latitude'], row['longitude']], popup=popup_html, icon=folium.Icon(color=marker_color)).add_to(m)

# Display the map using Streamlit
folium_static(m)

# Check if a station was clicked
if st.session_state.selected_station:
    display_station_details(st.session_state.selected_station)

# JavaScript to receive messages from the iframe
st.components.v1.html(
    """
    <script>
    window.addEventListener('message', function(event) {
        const stationName = event.data;
        if (stationName) {
            window.parent.postMessage(stationName, '*');
            console.log('Station clicked:', stationName);
        }
    });
    </script>
    """, height=0
)

# Add Recent Data Insights section for the stations
st.subheader("Recent Data Insights")
recent_data = {
    "Kangaroo Creek": {"Turbidity": "7 NTU", "pH": "7.2", "Nitrate": "0.05 mg/L"},
    "Little Coliban River": {"Turbidity": "4 NTU", "pH": "7.0", "Nitrate": "0.04 mg/L"},
    "Five Mile Creek - Woodend RWP Site 1": {"Turbidity": "5 NTU", "pH": "6.9", "Nitrate": "0.03 mg/L"},
    "Five Mile Creek - Woodend RWP Site 2": {"Turbidity": "6 NTU", "pH": "7.1", "Nitrate": "0.06 mg/L"}
}

if st.session_state.selected_station:
    station_data = recent_data.get(st.session_state.selected_station, {})
    st.markdown(f"**Recent Data for {st.session_state.selected_station}**")
    for measure, value in station_data.items():
        st.write(f"- {measure}: {value}")
