import streamlit as st
import pandas as pd
import plotly.express as px

# Page title and setup
st.set_page_config(page_title="Site Mapping & Data Overview", page_icon="🌍")
st.title("🌍 Site Mapping & Data Overview")

# Sidebar explanation
st.sidebar.header("Station Details Overview")
st.sidebar.write("This page shows the monitoring stations on an interactive map. "
                 "You can hover over each station to see detailed information about the type of data collected.")

# Load the Excel file directly from the server
@st.cache_data
def load_station_data(file_path):
    return pd.read_excel(file_path)

# Path to the Excel file on the server
file_path = "/workspaces/gdp-dashboard/data/monitoring_stations.xlsx"

# Load the data
stations_df = load_station_data(file_path)

# Correct the typo in the column name
stations_df.rename(columns={'lattitude': 'latitude'}, inplace=True)

# Blurb about the project and site relationships
st.subheader("Project Overview")
st.markdown("""
The purpose of this project is to visualize key monitoring stations across various sites in the catchment area. 
These stations collect critical data on water quality, rainfall, streamflow, and other environmental factors. 
By mapping these stations, we can better understand the relationships between different monitoring sites and 
how data from these locations interact to provide insights into catchment health and management decisions.

- **Water Quality Stations**: Monitor critical parameters such as turbidity, pH, and nutrient concentrations.
- **Rainfall Stations**: Measure precipitation to track storm events and their impact on streamflow and water quality.
- **Streamflow Stations**: Provide data on the flow of water through rivers and streams, allowing for the analysis of hydrological patterns.
""")

# Customize hover data to make it more user-friendly
hover_data = {
    'station_name': False,  # Show station name in hover, but don't repeat the column label
    'type': True,           # Show type of station with label
    'owner': True,          # Show owner with label
    'latitude': False,       # Hide latitude from hover data
    'longitude': False       # Hide longitude from hover data
}

# Create a map using Plotly Express with larger markers and custom hover data
fig = px.scatter_mapbox(stations_df, 
                        lat="latitude", 
                        lon="longitude", 
                        hover_name="station_name", 
                        hover_data=hover_data,
                        color="type", 
                        size_max=20,  # Maximum marker size
                        zoom=9, 
                        height=600)

# Update the layout for Plotly Mapbox to enhance the markers and improve the legend
fig.update_traces(marker=dict(size=18, opacity=0.9))  # Increase size and opacity for better visibility
fig.update_layout(mapbox_style="open-street-map", 
                  title="Monitoring Stations Map", 
                  margin={"r":0, "t":0, "l":0, "b":0},
                  legend_title_text="Station Type")  # Improved legend title

# Display the map
st.plotly_chart(fig)
