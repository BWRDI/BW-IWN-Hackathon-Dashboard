import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from pathlib import Path

# Set page title
st.set_page_config(page_title="EcoDetection vs Lab Data Comparison", page_icon="📊")
st.title("📊 EcoDetection vs Lab Data Comparison")

st.markdown("""
This page provides a detailed comparison between **EcoDetection** sensor data and **Lab data** for key water quality parameters. 
The parameters compared are **Turbidity**, **Nitrate**, **Nitrite**, **Phosphate**, and **Conductivity**, which were identified as 
the only matching series between the two datasets based on thorough analysis.

These comparisons allow you to evaluate the accuracy and consistency between real-time sensor readings and lab-certified measurements. 
Outliers, which are likely sensor failures, are identified using the **Interquartile Range (IQR)** method. This approach highlights 
any unusually high or low values that may fall outside the expected range of data.

You can choose to hide these outliers to focus on the core data trends by selecting the appropriate option in the sidebar.
""")

# Load all available data
@st.cache_data
def load_all_data():
    water_quality_data = pd.read_csv(Path(__file__).parent.parent / 'data' / 'ecodetection_clean_data.csv')
    lab_data = pd.read_excel(Path(__file__).parent.parent / 'data' / 'cw_catchment_sampling_filtered.xlsx')
    return water_quality_data, lab_data

# Convert Excel serial date to datetime for EcoDetection data
def excel_serial_date_to_datetime(excel_date):
    return (datetime(1899, 12, 30) + timedelta(days=excel_date))

# Load data
water_quality_data, lab_data = load_all_data()

# Convert timestamps to proper datetime format for EcoDetection data
water_quality_data['Date'] = pd.to_datetime(water_quality_data['timestamp'].apply(excel_serial_date_to_datetime), errors='coerce')

# Convert Lab data date format to datetime
lab_data['Date'] = pd.to_datetime(lab_data['date_sampled'], errors='coerce')

# Sidebar: Add dropdown to select between sites
selected_site = st.sidebar.selectbox(
    "Select a site to view:",
    ["Kangaroo Creek", "Little Coliban River", "Five Mile Creek - Site 1", "Five Mile Creek - Site 2"]
)

# Sidebar: Enable/Disable Streamflow Overlay
enable_streamflow_overlay = st.sidebar.checkbox("Show Streamflow Trend", value=False)

# Load streamflow data based on the selected site
streamflow_file_paths = {
    "Kangaroo Creek": "clean_wims_406281.csv",
    "Little Coliban River": "clean_wims_406280.csv",
    "Five Mile Creek - Site 1": "clean_wims_406266.csv",
    "Five Mile Creek - Site 2": "clean_wims_406266.csv"
}

# Load streamflow data
@st.cache_data
def load_streamflow_data(selected_file):
    streamflow_path = Path(__file__).parent.parent / 'data' / selected_file
    return pd.read_csv(streamflow_path, parse_dates=['datetime'])

# Load the correct streamflow data file
streamflow_data = load_streamflow_data(streamflow_file_paths[selected_site])

# Convert datetime in streamflow data to datetime format
streamflow_data['datetime'] = pd.to_datetime(streamflow_data['datetime'], errors='coerce')

# Filter streamflow data to only include data after 9/2/2023
start_date_filter = pd.to_datetime("2023-09-02")
streamflow_data = streamflow_data[streamflow_data['datetime'] >= start_date_filter]

# Filter Lab Data by Site and rename sites
lab_data['Subsite_Code'] = lab_data['Subsite_Code'].replace({
    'SITE2': 'Little Coliban River', 
    'SITE17': 'Kangaroo Creek'
})

# Sort the lab data by date
lab_data = lab_data.sort_values(by='Date')

# Filter EcoDetection and Lab Data based on selected site
eco_detection_data = water_quality_data[water_quality_data['location'] == selected_site]
lab_data_filtered = lab_data[lab_data['Subsite_Code'] == selected_site]

# Ensure datetime conversion
eco_detection_data['Date'] = pd.to_datetime(eco_detection_data['Date'])
lab_data_filtered['Date'] = pd.to_datetime(lab_data_filtered['Date'])

# Define matching parameters
matching_parameters = {
    "Turbidity": ["Nephelo Turbidity", "Turbidity"],
    "Nitrate": ["Nitrate Concentration", "Nitrate - Nitrogen"],
    "Nitrite": ["Nitrite Concentration", "Nitrite - Nitrogen"],
    "Phosphate": ["Phosphate Concentration", "Phosphate"],
    "Conductivity": ["Conductivity", "Electrical Conductivity"]
}

# Conversion function for EcoDetection data from ppb to mg/L
def convert_ppb_to_mg_l(value):
    return value * 0.001 if pd.notna(value) else value

# Process data for each matching parameter
for param, (ecodev_param, lab_param) in matching_parameters.items():
    
    st.subheader(f"{param} Comparison (EcoDetection vs Lab Data)")
    
    # Filter EcoDetection data for the selected site and parameter
    eco_detection_param_data = eco_detection_data[
        (eco_detection_data['measurement'] == ecodev_param)
    ]

    if ecodev_param in ["Nitrate Concentration", "Nitrite Concentration", "Phosphate Concentration"]:
        eco_detection_param_data['result'] = eco_detection_param_data['result'].apply(convert_ppb_to_mg_l)
    
    # Filter Lab data for the parameter
    lab_data_param_filtered = lab_data_filtered[(lab_data_filtered['Measure'] == lab_param)]

    # Create a subplot with secondary y-axis enabled
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add EcoDetection data to the plot
    fig.add_trace(
        go.Scatter(
            x=eco_detection_param_data['Date'], 
            y=eco_detection_param_data['result'], 
            mode='lines', 
            name='EcoDetection',
            line=dict(color='blue')
        ),
        secondary_y=False
    )

    # Add Lab data to the plot
    fig.add_trace(
        go.Scatter(
            x=lab_data_param_filtered['Date'], 
            y=lab_data_param_filtered['Result'], 
            mode='lines', 
            name='Lab',
            line=dict(color='orange')
        ),
        secondary_y=False
    )

    # Add streamflow data with 50% opacity if enabled and for Nitrate and Conductivity
    if enable_streamflow_overlay and param in ["Nitrate", "Conductivity"]:
        fig.add_trace(
            go.Scatter(
                x=streamflow_data['datetime'], 
                y=streamflow_data['discharge_ml_day'], 
                mode='lines', 
                name='Streamflow', 
                line=dict(color='rgba(0, 0, 255, 0.5)')  # 50% opacity blue line
            ),
            secondary_y=True  # Use secondary y-axis for streamflow
        )

        # Update the layout to add a secondary y-axis for streamflow
        fig.update_layout(
            yaxis2=dict(
                title="Streamflow (ML/day)",
                overlaying="y",
                side="right"
            )
        )

    # Update layout and display the plot
    fig.update_layout(
        title=f'{param} Trend Comparison for {selected_site}',
        xaxis_title="Date",
        yaxis_title=f'{param} (mg/L)' if param != "Turbidity" else f'{param} (NTU)',
        legend_title="Source",
        height=600
    )
    
    st.plotly_chart(fig)
