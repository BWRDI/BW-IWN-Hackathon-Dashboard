import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import folium
from streamlit_folium import folium_static

# Set page title and icon
st.set_page_config(page_title="Site Mapping & Data Overview", page_icon="🌍")

# Page title
st.title("🌍 Site Mapping & Data Overview")

# Sidebar explanation
st.sidebar.header("Station Details Overview")
st.sidebar.write("Click a marker on the map to view alarms and data for that specific site.")

# Load the station data (as an example)
@st.cache_data
def load_station_data(file_path):
    return pd.read_excel(file_path)

# Load the data (replace this with your actual data file)
file_path = Path(__file__).parent.parent / 'data' / 'monitoring_stations.xlsx'
stations_df = load_station_data(file_path)
stations_df.rename(columns={'lattitude': 'latitude'}, inplace=True)

# Create a folium map with markers
m = folium.Map(location=[-37.814, 144.96332], zoom_start=9)

# Function to create popup with clickable link
def create_popup_html(station_name):
    return f'<b>{station_name}</b><br><a href="/Alarms?site={station_name}" target="_self">View Alarms</a>'

# Add markers to the map
for _, row in stations_df.iterrows():
    popup_html = create_popup_html(row['station_name'])
    folium.Marker([row['latitude'], row['longitude']], popup=popup_html).add_to(m)

# Display the map using Streamlit
folium_static(m)
