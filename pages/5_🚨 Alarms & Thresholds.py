import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# Set page title
st.set_page_config(page_title="Alarms & Thresholds", page_icon="🚨")
st.title("🚨 Alarms & Thresholds")

st.markdown("""
This page allows users to monitor key water quality parameters and receive alerts 
when they exceed defined thresholds, helping to detect potential water quality issues 
early and take corrective actions.
""")

# Set threshold values
col1, col2 = st.columns(2)

with col1:
    turbidity_threshold = st.slider("Set Turbidity Threshold (NTU)", 0, 100, 10)

with col2:
    rainfall_threshold = st.slider("Set Rainfall Threshold (mm)", 0, 100, 20)

# Add a threshold for matching Eco and Lab data
eco_lab_threshold = st.slider("Set Threshold for Eco vs Lab Data Matching (%)", 0, 100, 5)

# Add an example alarm button
if st.button("Trigger Example Alarm"):
    st.markdown(
        """
        <div style="background-color:#FF6347; padding:20px; border-radius:5px; text-align:center;">
            <h2 style="color:white; font-size:32px;">
                🚨 EXAMPLE ALARM! 🚨
            </h2>
            <p style="color:white; font-size:24px;">
                Turbidity or rainfall has exceeded the threshold!
            </p>
        </div>
        """, unsafe_allow_html=True
    )

# Load water quality, rainfall, and lab data
@st.cache_data
def load_alarm_data():
    water_quality_data = pd.read_csv(Path(__file__).parent.parent / 'data' / "ecodetection_clean_data.csv")
    rainfall_data = pd.read_csv(Path(__file__).parent.parent / 'data' / "clean_bom_data.csv")
    lab_data = pd.read_excel(Path(__file__).parent.parent / 'data' / 'cw_catchment_sampling_filtered.xlsx')
    return water_quality_data, rainfall_data, lab_data

# Convert Excel serial date to datetime (and only keep the date)
def excel_serial_date_to_datetime(excel_date):
    return (datetime(1899, 12, 30) + timedelta(days=excel_date)).date()

# Load data
water_quality_data, rainfall_data, lab_data = load_alarm_data()

# Convert 'timestamp' in water quality data (turbidity) to proper datetime format (yyyy-mm-dd) and rename the column to 'Date'
water_quality_data['Date'] = water_quality_data['timestamp'].apply(excel_serial_date_to_datetime)
water_quality_data.drop(columns=['timestamp'], inplace=True)

# Convert rainfall 'date' column to proper datetime format (yyyy-mm-dd) and rename the column to 'Date'
rainfall_data['Date'] = pd.to_datetime(rainfall_data['date'], errors='coerce').dt.date
rainfall_data.drop(columns=['date'], inplace=True)

# Convert lab data date format
lab_data['Date'] = pd.to_datetime(lab_data['date_sampled'], errors='coerce').dt.date

# Filter water quality data for turbidity
turbidity_data = water_quality_data[water_quality_data['measurement'] == 'Nephelo Turbidity']

# Sort both datasets by the most recent date (descending order)
turbidity_data = turbidity_data.sort_values(by='Date', ascending=False)
rainfall_data = rainfall_data.sort_values(by='Date', ascending=False)

# Add a new column with the unit name in the column header (Value (NTU))
turbidity_data['Value (NTU)'] = turbidity_data['result']
rainfall_data['Rainfall (mm)'] = rainfall_data['rainfall']

# Remove unnecessary columns
turbidity_data.drop(columns=['unit', 'result', 'measurement'], inplace=True)
rainfall_data.drop(columns=['rainfall'], inplace=True)

# Check for turbidity values exceeding the threshold
exceeded_turbidity = turbidity_data[turbidity_data['Value (NTU)'] > turbidity_threshold]

# Filter rainfall data based on the threshold
exceeded_rainfall = rainfall_data[rainfall_data['Rainfall (mm)'] > rainfall_threshold]

# Filter lab data to exclude Five Mile Creek stations (assuming 'SITE2' is for Little Coliban and 'SITE17' for Kangaroo Creek)
valid_lab_sites = ['Little Coliban River', 'Kangaroo Creek']
lab_data_filtered = lab_data[lab_data['Subsite_Code'].isin(valid_lab_sites)]

# Check for mismatches between EcoDetection and Lab data for turbidity
turbidity_lab_data = lab_data_filtered[lab_data_filtered['Measure'] == 'Turbidity']
merged_data = pd.merge(turbidity_data, turbidity_lab_data, on='Date', suffixes=('_eco', '_lab'))

# Calculate the difference between Eco and Lab values
merged_data['Difference (%)'] = abs(merged_data['Value (NTU)'] - merged_data['Result']) / merged_data['Result'] * 100

# Find mismatches where the difference exceeds the eco_lab_threshold
mismatched_data = merged_data[merged_data['Difference (%)'] > eco_lab_threshold]

# Display alarms
st.subheader("Alarms")

if not exceeded_turbidity.empty:
    st.warning(f"Turbidity has exceeded the threshold at {len(exceeded_turbidity)} occurrences!")

if not exceeded_rainfall.empty:
    st.warning(f"Rainfall has exceeded the threshold at {len(exceeded_rainfall)} occurrences!")

if not mismatched_data.empty:
    st.error(f"EcoDetection turbidity does not match lab data at {len(mismatched_data)} occurrences!")

if exceeded_turbidity.empty and exceeded_rainfall.empty and mismatched_data.empty:
    st.success("All parameters are within the defined thresholds.")

# Display details if there are any alarms
st.subheader("Recent Data Sorted by Most Recent")

if not exceeded_turbidity.empty:
    st.write("Turbidity exceedances:")
    st.dataframe(exceeded_turbidity[['Date', 'location', 'Value (NTU)']])

if not exceeded_rainfall.empty:
    st.write("Rainfall exceedances:")
    st.dataframe(exceeded_rainfall[['Date', 'station_number', 'Rainfall (mm)']])

if not mismatched_data.empty:
    st.write("Eco vs Lab Mismatches:")
    st.dataframe(mismatched_data[['Date', 'location', 'Value (NTU)', 'Result', 'Difference (%)']])

# Show warning for missing lab data for Five Mile Creek sites
selected_site = st.sidebar.selectbox(
    "Select a site to view alarms:",
    ["Kangaroo Creek", "Little Coliban River", "Five Mile Creek - Site 1", "Five Mile Creek - Site 2"]
)

if "Five Mile Creek" in selected_site:
    st.warning(f"Lab data for {selected_site} is missing. Please upload the lab data on the uploads page.")
