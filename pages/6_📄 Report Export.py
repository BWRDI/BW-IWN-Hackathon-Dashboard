import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime, timedelta
import xlsxwriter  # Importing xlsxwriter for Excel export
from pathlib import Path

# Set page title
st.set_page_config(page_title="Report Export", page_icon="📄")
st.title("📄 Report Export")

st.markdown("""
This page allows you to export the report of recent data, including all available EcoDetection data, lab data, and rainfall exceedances.
You can customize the report to include any combination of data types.
""")

# Load all available data
@st.cache_data
def load_all_data():
    water_quality_data = pd.read_csv(Path(__file__).parent.parent / 'data' / "ecodetection_clean_data.csv")
    rainfall_data = pd.read_csv(Path(__file__).parent.parent / 'data' / "clean_bom_data.csv")
    lab_data = pd.read_csv(Path(__file__).parent.parent / 'data' / "cw_catchment_sampling.csv")  # Load the lab data
    return water_quality_data, rainfall_data, lab_data

# Convert Excel serial date to datetime
def excel_serial_date_to_datetime(excel_date):
    return (datetime(1899, 12, 30) + timedelta(days=excel_date)).date()

# Load data
water_quality_data, rainfall_data, lab_data = load_all_data()

# Convert timestamps to proper date format
water_quality_data['Date'] = water_quality_data['timestamp'].apply(excel_serial_date_to_datetime)
rainfall_data['Date'] = pd.to_datetime(rainfall_data['date'], errors='coerce').dt.date

# Process water quality data (all EcoDetection measurements)
eco_detection_measurements = [
    "Chloride Concentration", "Fluoride Concentration", "Nitrate Concentration", 
    "Nitrite Concentration", "Phosphate Concentration", "Sulphate Concentration", 
    "Enclosure Temperature", "Conductivity", "Nephelo Turbidity", "Oxygen", "pH", "Temperature"
]

# Filter and pivot the data for export
water_quality_data_filtered = water_quality_data[water_quality_data['measurement'].isin(eco_detection_measurements)]
water_quality_data_filtered = water_quality_data_filtered.pivot_table(index=['Date', 'location'], columns='measurement', values='result')

# Process rainfall data
rainfall_data['Rainfall (mm)'] = rainfall_data['rainfall']

# Process lab data
lab_data['Date'] = pd.to_datetime(lab_data['date_sampled'], errors='coerce').dt.date
lab_data_filtered = lab_data[['Date', 'Subsite_Name', 'Measure', 'Result', 'Units']].sort_values(by='Date', ascending=False)

# Sort the data by most recent date
water_quality_data_filtered = water_quality_data_filtered.reset_index().sort_values(by='Date', ascending=False)
rainfall_data = rainfall_data[['Date', 'station_number', 'Rainfall (mm)']].sort_values(by='Date', ascending=False)

# Allow selection of all available data for export
st.subheader("Customize Your Report")
include_eco_detection = st.checkbox("Include EcoDetection Data (All Parameters)", value=True)
include_rainfall = st.checkbox("Include Rainfall Data", value=True)
include_lab_data = st.checkbox("Include Lab Data", value=True)

# Combine the selected data
def generate_report():
    report_data_list = []
    
    if include_eco_detection:
        report_data_list.append(water_quality_data_filtered)
        
    if include_rainfall:
        report_data_list.append(rainfall_data)
        
    if include_lab_data:
        report_data_list.append(lab_data_filtered)
    
    if report_data_list:
        return pd.concat(report_data_list, keys=["EcoDetection", "Rainfall", "Lab"])
    else:
        return pd.DataFrame()

report_data = generate_report()

# Export as CSV
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Export as Excel
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    return processed_data

# Generate download buttons if report data is available
if not report_data.empty:
    st.subheader("Download Your Report")
    
    # Export as CSV
    csv_data = convert_df_to_csv(report_data)
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name='report.csv',
        mime='text/csv'
    )

    # Export as Excel
    excel_data = convert_df_to_excel(report_data)
    st.download_button(
        label="Download Excel",
        data=excel_data,
        file_name='report.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
else:
    st.warning("Please select at least one data type to include in the report.")
