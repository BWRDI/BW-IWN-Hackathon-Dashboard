import streamlit as st
import pandas as pd
import altair as alt

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
    # Load and convert the date columns inside the cached function
    rainfall_data = pd.read_csv("/workspaces/gdp-dashboard/data/clean_bom_data.csv")
    streamflow_data = pd.read_csv("/workspaces/gdp-dashboard/data/clean_wims_data.csv")
    
    # Convert 'date' and 'datetime' columns to datetime types only once (cached)
    rainfall_data['date'] = pd.to_datetime(rainfall_data['date'], errors='coerce')
    streamflow_data['datetime'] = pd.to_datetime(streamflow_data['datetime'], errors='coerce')
    
    return rainfall_data, streamflow_data

# Load the datasets (cached)
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
    site_rainfall = rainfall_data[rainfall_data["station_number"] == selected_rainfall_station].dropna(subset=["rainfall"])
    
    # Limit the size of the dataset for display (reduce data for performance)
    site_rainfall = site_rainfall.tail(500)  # Display the last 500 rows
    
    if site_rainfall.empty:
        st.warning(f"No valid rainfall data available for {selected_site}.")
    else:
        st.subheader(f"Rainfall Data for {selected_site}")
    
        # Create Altair chart for rainfall data
        rainfall_chart = alt.Chart(site_rainfall).mark_line().encode(
            x='date:T',
            y='rainfall:Q',
            tooltip=['date:T', 'rainfall:Q']
        ).properties(
            title=f"Rainfall at {selected_site}"
        ).interactive()  # Makes the chart zoomable and panable
    
        st.altair_chart(rainfall_chart, use_container_width=True)
else:
    st.write(f"No rainfall data available for {selected_site}")

# Filter the streamflow data based on the station number
site_streamflow = streamflow_data[streamflow_data["station_number"] == selected_streamflow_station].dropna(subset=["discharge_ml_day"])

# Limit the size of the dataset for display (reduce data for performance)
# site_streamflow = site_streamflow.tail(500)  # Display the last 500 rows

if site_streamflow.empty:
    st.warning(f"No valid streamflow data available for {selected_site}.")
else:
    st.subheader(f"Streamflow Data for {selected_site}")

    # Create Altair chart for streamflow data
    streamflow_chart = alt.Chart(site_streamflow).mark_line().encode(
        x='datetime:T',
        y='discharge_ml_day:Q',
        tooltip=['datetime:T', 'discharge_ml_day:Q']
    ).properties(
        title=f"Streamflow at {selected_site}"
    ).interactive()

    st.altair_chart(streamflow_chart, use_container_width=True)

# Option to reload or refresh the page
if st.button("Refresh Data"):
    st.experimental_set_query_params()  # This refreshes the app by resetting query parameters
