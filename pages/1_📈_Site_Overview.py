import streamlit as st
import pandas as pd
import altair as alt

# Set page title and icon
st.set_page_config(page_title="Site Overview", page_icon="📈")

# Page title
st.title("📈 Site Overview")

# Sidebar header for selecting a site
st.sidebar.header("Site Selection")

# Updated monitoring site options
site_options = [
    "Kangaroo Creek", 
    "Little Coliban River", 
    "Five Mile Creek - Woodend RWP Site 1", 
    "Five Mile Creek - Woodend RWP Site 2"
]
selected_site = st.sidebar.selectbox("Choose a site to view data", site_options)

st.sidebar.success(f"Viewing data for: {selected_site}")

# Introduction text for the selected site
st.markdown(
    f"""
    You are currently viewing the data overview for **{selected_site}**.
    
    This section provides key insights and visualizations for the selected monitoring site, 
    including water quality comparisons.
    
    **Select different sites from the sidebar** to compare data from various locations.
    """
)

# Load EcoDetection data using st.cache_data
@st.cache_data
def load_ecodetection_data():
    # Load the EcoDetection data from the correct CSV path
    return pd.read_csv("/workspaces/gdp-dashboard/data/ecodetection_clean_data.csv")

# Load the data
ecodetection_data = load_ecodetection_data()

# Convert the timestamp column from serial format (if it's in Excel serial date format)
ecodetection_data["timestamp"] = pd.to_datetime(ecodetection_data["timestamp"], origin="1899-12-30", unit="D")

# Filter the data based on the selected site
site_data_eco = ecodetection_data[ecodetection_data["location"] == selected_site]

# Convert units (e.g., ppb to mg/L if necessary) and process data as needed
site_data_eco["result_mg_L"] = site_data_eco.apply(
    lambda row: row["result"] * 0.001 if row["unit"] == "ppb" else row["result"], axis=1
)

# Group 1: Inorganic Chemicals
inorganic_chemicals = ["Chloride Concentration", "Fluoride Concentration", "Sulphate Concentration"]
inorganic_data = site_data_eco[site_data_eco["measurement"].isin(inorganic_chemicals)]

# Plotting Inorganic Chemicals using Altair
st.subheader("Inorganic Chemicals")
inorganic_chart = alt.Chart(inorganic_data).mark_line().encode(
    x='timestamp:T',
    y='result_mg_L:Q',
    color='measurement:N',
    tooltip=['timestamp:T', 'result_mg_L:Q', 'measurement:N']
).interactive().properties(
    title='Inorganic Chemicals Concentration'
)
st.altair_chart(inorganic_chart, use_container_width=True)

# Group 2: Nutrients
nutrients = ["Nitrate Concentration", "Nitrite Concentration", "Phosphate Concentration"]
nutrient_data = site_data_eco[site_data_eco["measurement"].isin(nutrients)]

# Plotting Nutrients using Altair
st.subheader("Nutrients")
nutrient_chart = alt.Chart(nutrient_data).mark_line().encode(
    x='timestamp:T',
    y='result_mg_L:Q',
    color='measurement:N',
    tooltip=['timestamp:T', 'result_mg_L:Q', 'measurement:N']
).interactive().properties(
    title='Nutrient Concentrations'
)
st.altair_chart(nutrient_chart, use_container_width=True)

# Group 3: Physical Properties
physical_properties = ["Conductivity", "Nephelo Turbidity", "Oxygen", "pH"]
physical_data = site_data_eco[site_data_eco["measurement"].isin(physical_properties)]

# Plotting Physical Properties using Altair
st.subheader("Physical Properties")
physical_chart = alt.Chart(physical_data).mark_line().encode(
    x='timestamp:T',
    y='result_mg_L:Q',
    color='measurement:N',
    tooltip=['timestamp:T', 'result_mg_L:Q', 'measurement:N']
).interactive().properties(
    title='Physical Properties'
)
st.altair_chart(physical_chart, use_container_width=True)

# Group 4: Environmental Data
environmental_data = ["Enclosure Temperature", "Temperature"]
env_data = site_data_eco[site_data_eco["measurement"].isin(environmental_data)]

# Plotting Environmental Data using Altair
st.subheader("Environmental Data")
env_chart = alt.Chart(env_data).mark_line().encode(
    x='timestamp:T',
    y='result_mg_L:Q',
    color='measurement:N',
    tooltip=['timestamp:T', 'result_mg_L:Q', 'measurement:N']
).interactive().properties(
    title='Environmental Data'
)
st.altair_chart(env_chart, use_container_width=True)

# Option to refresh or rerun
if st.button("Refresh Data"):
    st.query_params()
