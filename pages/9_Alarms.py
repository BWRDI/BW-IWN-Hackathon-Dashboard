import streamlit as st
import pandas as pd
import urllib.parse

# Set page title
st.set_page_config(page_title="Alarms & Thresholds", page_icon="🚨")
st.title("🚨 Alarms & Thresholds")

st.markdown("This page shows alarms and thresholds for the selected site.")

# Get the query parameter from the URL
query_params = st.experimental_get_query_params()

# Extract the site parameter from the URL (default to 'Unknown' if no site is selected)
selected_site = query_params.get("site", ["Unknown"])[0]

st.subheader(f"Alarms for {selected_site}")

# Example alarm data (replace this with your actual alarm data)
alarms_data = {
    "Kangaroo Creek": ["Turbidity Exceeded", "Rainfall Trigger"],
    "Little Coliban River": ["Nitrogen Exceeded"],
    "Five Mile Creek - Woodend RWP Site 1": ["Phosphate Exceeded", "Oxygen Drop"],
    "Five Mile Creek - Woodend RWP Site 2": []
}

# Display the alarms for the selected site
if selected_site in alarms_data and alarms_data[selected_site]:
    for alarm in alarms_data[selected_site]:
        st.warning(f"🚨 {alarm}")
else:
    st.success("No alarms for this site.")
