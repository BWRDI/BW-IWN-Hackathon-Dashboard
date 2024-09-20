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

# Load streamflow data based on the selected site
streamflow_file_paths = {
    "Kangaroo Creek": "clean_wims_406281.csv",
    "Little Coliban River": "clean_wims_406280.csv",
    "Five Mile Creek - Site 1": "clean_wims_406266.csv",
    "Five Mile Creek - Site 2": "clean_wims_406266.csv"
}

@st.cache_data
def load_streamflow_data(selected_file):
    streamflow_path = Path(__file__).parent.parent / 'data' / selected_file
    return pd.read_csv(streamflow_path, parse_dates=['datetime'])
    
# Convert Excel serial date to datetime for EcoDetection data
def excel_serial_date_to_datetime(excel_date):
    return (datetime(1899, 12, 30) + timedelta(days=excel_date))

# Load data
water_quality_data, lab_data = load_all_data()

# Convert timestamps to proper datetime format for EcoDetection data
water_quality_data['Date'] = pd.to_datetime(water_quality_data['timestamp'].apply(excel_serial_date_to_datetime), errors='coerce')

# Convert Lab data date format to datetime
lab_data['Date'] = pd.to_datetime(lab_data['date_sampled'], errors='coerce')

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
    # Display a warning for missing lab data for Five Mile Creek
    st.warning("⚠️ Missing lab data for Five Mile Creek. Please upload the lab data on the [Intro page](#).")
    
else:
    # Load the streamflow data for the selected site
    streamflow_data = load_streamflow_data(streamflow_file_paths[selected_site])

    # Convert datetime in streamflow data to datetime format
    streamflow_data['datetime'] = pd.to_datetime(streamflow_data['datetime'], errors='coerce')

    # Filter streamflow data to only include data after 9/2/2023
    start_date_filter = pd.to_datetime("2023-09-02")
    streamflow_data = streamflow_data[streamflow_data['datetime'] >= start_date_filter]
    
    # Filter data for the selected site
    eco_detection_data = water_quality_data[water_quality_data['location'] == selected_site]
    lab_data_filtered = lab_data[lab_data['Subsite_Code'] == selected_site]

    # Ensure datetime conversion
    eco_detection_data['Date'] = pd.to_datetime(eco_detection_data['Date'])
    lab_data_filtered['Date'] = pd.to_datetime(lab_data_filtered['Date'])

    # Determine the minimum and maximum dates for both datasets
    min_date_eco = eco_detection_data['Date'].min()
    max_date_eco = eco_detection_data['Date'].max()
    
    min_date_lab = lab_data_filtered['Date'].min()
    max_date_lab = lab_data_filtered['Date'].max()

    # Determine the overall min and max dates for the slider
    min_date = min(min_date_eco, min_date_lab).to_pydatetime()
    max_date = max(max_date_eco, max_date_lab).to_pydatetime()

    # Set default value for the last year
    default_start_date = max_date - timedelta(days=365)

    # Use session state to persist the date range across site selections
    if 'date_range' not in st.session_state:
        st.session_state.date_range = (default_start_date, max_date)

    # Add a date range slider for selecting the date range in the sidebar
    st.sidebar.markdown("### Select Date Range to Zoom In")
    selected_dates = st.sidebar.slider(
        "Date Range", 
        min_value=min_date, 
        max_value=max_date, 
        value=st.session_state.date_range,  # Use session state for persistence
        format="YYYY-MM-DD"
    )

    # Update session state when the slider changes
    st.session_state.date_range = selected_dates

    # Filter both datasets based on the selected date range
    eco_detection_data = eco_detection_data[
        (eco_detection_data['Date'] >= selected_dates[0]) & (eco_detection_data['Date'] <= selected_dates[1])
    ]

    lab_data_filtered = lab_data_filtered[
        (lab_data_filtered['Date'] >= selected_dates[0]) & (lab_data_filtered['Date'] <= selected_dates[1])
    ]

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

        # Detect outliers in EcoDetection data
        outliers = detect_outliers(eco_detection_param_data, 'result')

        if outliers.any():
            st.warning(f"Detected {outliers.sum()} likely sensor failures in EcoDetection data for {param} at {selected_site}.")
        
        # Option to hide outliers
        if hide_outliers:
            eco_detection_param_data = eco_detection_param_data[~outliers]

        # Create a combined dataframe for comparison
        combined_df = pd.DataFrame({
            'Date': pd.concat([eco_detection_param_data['Date'], lab_data_param_filtered['Date']]),
            'Source': ['EcoDetection'] * len(eco_detection_param_data) + ['Lab'] * len(lab_data_param_filtered),
            'Value': pd.concat([eco_detection_param_data['result'], lab_data_param_filtered['Result']]),
        }).dropna()

        # Create a line chart using Plotly with custom colors and add Streamflow data to the plot
        fig = make_subplots(specs=[[{"secondary_y": True}]])  # Secondary y-axis for Streamflow

        # Add EcoDetection data
        fig.add_trace(
            go.Scatter(
                x=eco_detection_param_data['Date'], 
                y=eco_detection_param_data['result'], 
                mode='lines', 
                name='EcoDetection',
            ),
            secondary_y=False
        )

        # Add Lab data
        fig.add_trace(
            go.Scatter(
                x=lab_data_param_filtered['Date'], 
                y=lab_data_param_filtered['Result'], 
                mode='lines', 
                name='Lab',
            ),
            secondary_y=False
        )

        # Add Streamflow data with 50% opacity if enabled and for Nitrate and Conductivity
        if param in ["Nitrate", "Conductivity"]:
            fig.add_trace(
                go.Scatter(
                    x=streamflow_data['datetime'], 
                    y=streamflow_data['discharge_ml_day'], 
                    mode='lines', 
                    name='Streamflow', 
                    line=dict(color='rgba(255, 171, 171, .8)')  # 50% opacity red line
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

# Explanation of the comparison
st.markdown("""
In the charts above, **EcoDetection** data is automatically converted where necessary (e.g., Nitrate, Nitrite, Phosphate) 
from **ppb** to **mg/L** to match the units used by the **Lab Data**. Each site is displayed separately for comparison. 
You can also hide outliers that are likely sensor failures by checking the option in the sidebar.
""")