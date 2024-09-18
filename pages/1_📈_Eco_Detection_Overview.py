import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Set page title and icon
st.set_page_config(page_title="Eco Detection Site Overview", page_icon="📈")

# Page title
st.title("📈 Eco Detection Site Overview")

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
    return pd.read_csv(Path(__file__).parent.parent / 'data' / "ecodetection_clean_data.csv")

# Load the data
ecodetection_data = load_ecodetection_data()

# Convert the 'timestamp' column to proper datetime format (assuming Excel serial date)
ecodetection_data['timestamp'] = pd.to_datetime(ecodetection_data['timestamp'], origin='1899-12-30', unit='D')

# Filter the data based on the selected site
site_data_eco = ecodetection_data[ecodetection_data["location"] == selected_site]

# Convert units (e.g., ppb to mg/L if necessary) and process data as needed
site_data_eco["result_mg_L"] = site_data_eco.apply(
    lambda row: row["result"] * 0.001 if row["unit"] == "ppb" else row["result"], axis=1
)

# Group 1: Inorganic Chemicals
inorganic_chemicals = ["Chloride Concentration", "Fluoride Concentration", "Sulphate Concentration"]
inorganic_data = site_data_eco[site_data_eco["measurement"].isin(inorganic_chemicals)]
st.subheader("Inorganic Chemicals")
fig_inorganic = px.line(inorganic_data, x="timestamp", y="result_mg_L", color="measurement", 
                        title="Inorganic Chemicals Concentration", labels={"result_mg_L": "Concentration (mg/L)", "timestamp": "Date"})
st.plotly_chart(fig_inorganic)

# Group 2: Nutrients
nutrients = ["Nitrate Concentration", "Nitrite Concentration", "Phosphate Concentration"]
nutrient_data = site_data_eco[site_data_eco["measurement"].isin(nutrients)]
st.subheader("Nutrients")
fig_nutrients = px.line(nutrient_data, x="timestamp", y="result_mg_L", color="measurement", 
                        title="Nutrient Concentrations", labels={"result_mg_L": "Concentration (mg/L)", "timestamp": "Date"})
st.plotly_chart(fig_nutrients)

# Group 3: Physical Properties
physical_properties = ["Conductivity", "Nephelo Turbidity", "Oxygen", "pH"]
physical_data = site_data_eco[site_data_eco["measurement"].isin(physical_properties)]
st.subheader("Physical Properties")
fig_physical = px.line(physical_data, x="timestamp", y="result_mg_L", color="measurement", 
                       title="Physical Properties", labels={"result_mg_L": "Value", "timestamp": "Date"})
st.plotly_chart(fig_physical)

# Group 4: Environmental Data
environmental_data = ["Enclosure Temperature", "Temperature"]
env_data = site_data_eco[site_data_eco["measurement"].isin(environmental_data)]
st.subheader("Environmental Data")
fig_environmental = px.line(env_data, x="timestamp", y="result_mg_L", color="measurement", 
                            title="Environmental Data", labels={"result_mg_L": "Temperature (°C)", "timestamp": "Date"})
st.plotly_chart(fig_environmental)
