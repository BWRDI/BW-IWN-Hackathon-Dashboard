import streamlit as st
import pandas as pd
import plotly.express as px
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

# Convert Excel serial date to datetime
def excel_serial_date_to_datetime(excel_date):
    return (datetime(1899, 12, 30) + timedelta(days=excel_date)).date()

# Load data
water_quality_data, lab_data = load_all_data()

# Convert timestamps to proper date format for EcoDetection data
water_quality_data['Date'] = water_quality_data['timestamp'].apply(excel_serial_date_to_datetime)

# Convert Lab data date format
lab_data['Date'] = pd.to_datetime(lab_data['date_sampled'], errors='coerce').dt.date

# Filter Lab Data by Site and rename sites
lab_data['Subsite_Code'] = lab_data['Subsite_Code'].replace({
    'SITE2': 'Little Coliban River', 
    'SITE17': 'Kangaroo Creek'
})

# Sort the lab data by date
lab_data = lab_data.sort_values(by='Date')

# Sidebar: Add dropdown to select between sites
selected_site = st.sidebar.selectbox(
    "Select a site to view:",
    ["Kangaroo Creek", "Little Coliban River", "Five Mile Creek - Site 1", "Five Mile Creek - Site 2"]
)

# Option to hide outliers
hide_outliers = st.sidebar.checkbox("Hide outliers (likely sensor failures)")

# Function to detect outliers using IQR
def detect_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    outlier_mask = (df[column] < (Q1 - 1.5 * IQR)) | (df[column] > (Q3 + 1.5 * IQR))
    return outlier_mask

# Show warning if Five Mile Creek is selected
if selected_site in ["Five Mile Creek - Site 1", "Five Mile Creek - Site 2"]:
    st.warning(f"Lab data for {selected_site} is missing. Please upload the lab data on the uploads page.")
else:
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
        eco_detection_data = water_quality_data[(water_quality_data['measurement'] == ecodev_param) &
                                                (water_quality_data['location'] == selected_site)]
        if ecodev_param in ["Nitrate Concentration", "Nitrite Concentration", "Phosphate Concentration"]:
            eco_detection_data['result'] = eco_detection_data['result'].apply(convert_ppb_to_mg_l)
        
        # Filter Lab data for the parameter and the selected site
        lab_data_param_filtered = lab_data[lab_data['Measure'] == lab_param]
        lab_data_param_filtered = lab_data_param_filtered[lab_data_param_filtered['Subsite_Code'] == selected_site]

        # Detect outliers in EcoDetection data
        outliers = detect_outliers(eco_detection_data, 'result')

        if outliers.any():
            st.warning(f"Detected {outliers.sum()} likely sensor failures in EcoDetection data for {param} at {selected_site}.")
        
        # Option to hide outliers
        if hide_outliers:
            eco_detection_data = eco_detection_data[~outliers]

        # Create a combined dataframe for comparison
        combined_df = pd.DataFrame({
            'Date': pd.concat([eco_detection_data['Date'], lab_data_param_filtered['Date']]),
            'Source': ['EcoDetection'] * len(eco_detection_data) + ['Lab'] * len(lab_data_param_filtered),
            'Value': pd.concat([eco_detection_data['result'], lab_data_param_filtered['Result']]),
            'Site': pd.concat([eco_detection_data['location'], lab_data_param_filtered['Subsite_Code']])
        }).dropna()

        # Create a line chart using Plotly with custom colors
        fig = px.line(
            combined_df, 
            x='Date', y='Value', 
            color='Source', 
            line_dash='Site',
            color_discrete_map={"EcoDetection": "#1f77b4", "Lab": "#ff7f0e"},  # Set custom colors
            labels={'Value': f'{param} (mg/L)' if param != "Turbidity" else f'{param} (NTU)'},
            title=f'{param} Trend Comparison for {selected_site}'
        )

        st.plotly_chart(fig)

# Explanation of the comparison
st.markdown("""
In the charts above, **EcoDetection** data is automatically converted where necessary (e.g., Nitrate, Nitrite, Phosphate) 
from **ppb** to **mg/L** to match the units used by the **Lab Data**. Each site is displayed separately for comparison. 
You can also hide outliers that are likely sensor failures by checking the option in the sidebar.
""")
