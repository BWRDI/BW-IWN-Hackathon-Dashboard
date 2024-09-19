import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
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

# Sidebar: Add subheading and checkboxes for secondary axis options
st.sidebar.markdown("### Secondary Axis Settings")
use_secondary_axis_conductivity = st.sidebar.checkbox("Move Conductivity to Secondary Axis", value=True)
use_secondary_axis_chloride = st.sidebar.checkbox("Move Chloride Concentration to Secondary Axis", value=True)

# Load EcoDetection data using st.cache_data
@st.cache_data
def load_ecodetection_data():
    # Load the EcoDetection data from the correct CSV path
    return pd.read_csv(Path(__file__).parent.parent / 'data' / "ecodetection_clean_data.csv")

# Load the data
ecodetection_data = load_ecodetection_data()

# Convert the 'timestamp' column to proper datetime format
ecodetection_data['timestamp'] = pd.to_datetime(ecodetection_data['timestamp'], origin='1899-12-30', unit='D')

# Filter the data based on the selected site
site_data_eco = ecodetection_data[ecodetection_data["location"] == selected_site]

# Convert units (e.g., ppb to mg/L if necessary) and process data as needed
site_data_eco["result_mg_L"] = site_data_eco.apply(
    lambda row: row["result"] * 0.001 if row["unit"] == "ppb" else row["result"], axis=1
)

# Get the minimum and maximum dates from the filtered dataset
min_date = site_data_eco['timestamp'].min().to_pydatetime()  # Convert to datetime
max_date = site_data_eco['timestamp'].max().to_pydatetime()  # Convert to datetime

# Move the date range slider to the left-hand sidebar
st.sidebar.markdown("### Select Date Range to Zoom In")
selected_dates = st.sidebar.slider("Date Range", min_value=min_date, max_value=max_date, value=(min_date, max_date), format="YYYY-MM-DD")

# Filter the data based on the selected date range
site_data_eco_filtered = site_data_eco[(site_data_eco['timestamp'] >= selected_dates[0]) & (site_data_eco['timestamp'] <= selected_dates[1])]

# Group 1: Inorganic Chemicals
st.subheader("Inorganic Chemicals")
fig_inorganic = make_subplots(specs=[[{"secondary_y": True}]])

# Plot Chloride on primary or secondary axis
inorganic_chemicals = ["Chloride Concentration", "Fluoride Concentration", "Sulphate Concentration"]
for chemical in inorganic_chemicals:
    filtered_data = site_data_eco_filtered[site_data_eco_filtered["measurement"] == chemical]
    
    fig_inorganic.add_trace(
        go.Scatter(x=filtered_data['timestamp'], y=filtered_data['result_mg_L'], name=chemical),
        secondary_y=use_secondary_axis_chloride if chemical == "Chloride Concentration" else False
    )

# Update layout for inorganic chemicals chart
fig_inorganic.update_layout(
    title="Inorganic Chemicals Concentration",
    xaxis_title="Date",
    yaxis_title="Concentration (mg/L)",
    yaxis2_title="Chloride Concentration (mg/L)" if use_secondary_axis_chloride else None,
    legend_title="Measurements",
    height=600,
)

# Adjust line colors for clarity on secondary axis
fig_inorganic.update_traces(line=dict(color='blue'), selector=dict(secondary_y=False))
fig_inorganic.update_traces(line=dict(color='orange'), selector=dict(secondary_y=True))

st.plotly_chart(fig_inorganic)

# Group 2: Nutrients
st.subheader("Nutrients")
fig_nutrients = px.line(
    site_data_eco_filtered[site_data_eco_filtered["measurement"].isin(["Nitrate Concentration", "Nitrite Concentration", "Phosphate Concentration"])],
    x="timestamp", y="result_mg_L", color="measurement",
    title="Nutrient Concentrations",
    labels={"result_mg_L": "Concentration (mg/L)", "timestamp": "Date"}
)
st.plotly_chart(fig_nutrients)

# Group 3: Physical Properties
st.subheader("Physical Properties")
fig_physical = make_subplots(specs=[[{"secondary_y": True}]])

# Plot Conductivity on primary or secondary axis
physical_properties = ["Conductivity", "Nephelo Turbidity", "Oxygen", "pH"]
for property in physical_properties:
    filtered_data = site_data_eco_filtered[site_data_eco_filtered["measurement"] == property]
    
    fig_physical.add_trace(
        go.Scatter(x=filtered_data['timestamp'], y=filtered_data['result_mg_L'], name=property),
        secondary_y=use_secondary_axis_conductivity if property == "Conductivity" else False
    )

# Update layout for physical properties chart
fig_physical.update_layout(
    title="Physical Properties",
    xaxis_title="Date",
    yaxis_title="Value",
    yaxis2_title="Conductivity (μS/cm)" if use_secondary_axis_conductivity else None,
    legend_title="Measurements",
    height=600,
)

# Adjust line colors for clarity on secondary axis
fig_physical.update_traces(line=dict(color='green'), selector=dict(secondary_y=False))
fig_physical.update_traces(line=dict(color='red'), selector=dict(secondary_y=True))

st.plotly_chart(fig_physical)

# Group 4: Environmental Data
st.subheader("Environmental Data")
fig_environmental = px.line(
    site_data_eco_filtered[site_data_eco_filtered["measurement"].isin(["Enclosure Temperature", "Temperature"])],
    x="timestamp", y="result_mg_L", color="measurement",
    title="Environmental Data",
    labels={"result_mg_L": "Temperature (°C)", "timestamp": "Date"}
)
st.plotly_chart(fig_environmental)

# Explanation of the comparison
st.markdown("""
In the charts above, you can choose to move **Conductivity** and **Chloride Concentration** to a secondary axis in the 
**Physical Properties** and **Inorganic Chemicals** charts for better comparison with other parameters. 
Use the checkboxes in the sidebar to toggle between the two options. The color and legend will adjust accordingly.
""")
