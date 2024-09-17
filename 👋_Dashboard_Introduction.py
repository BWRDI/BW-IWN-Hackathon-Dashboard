import streamlit as st

st.title("Catchment Health Dashboard for Coliban Water")

st.sidebar.success("Navigate through the pages using the sidebar.")

st.markdown(
    """
    Welcome to **Barwon of a Kind**'s IWN Hackathon Dashboard, designed to provide comprehensive insights into the water quality data collected from the Little Coliban River catchment area.  
    This dashboard is built for **Coliban Water management** and focuses on comparing real-time sensor data with lab-based water quality measurements, rainfall, and streamflow data.
    
    ### Dashboard Overview:
    - **Data Collection Map**: See the exact locations of the data collection points within the catchment area.
    - **Water Quality Comparison**: Compare data from the Eco Dev sensors and lab tests for parameters such as turbidity, nitrate, and phosphorus.
    - **Rainfall & Streamflow**: Analyze how rainfall and streamflow impact water quality.
    - **Alerts**: Get notified when thresholds (e.g., 20mm of rainfall or high streamflow) are exceeded, triggering the need for further testing.
    - **Conclusions & Recommendations**: Summarize key findings and provide recommendations for ongoing sensor deployment and data management.
    
    **👈 Select a page from the sidebar** to start exploring the data.

    ### Need assistance?
    - Meet **James**, our AI assistant! James has access to all the water quality, rainfall, and streamflow data available on this dashboard.
    - You can ask James questions in a natural language format, and he'll provide insights, data summaries, and help you navigate through the dashboard.
    - To interact with James, click on the chat icon in the bottom right corner of any page.

    ### Want to dive deeper?
    - Explore the interactive data visualizations and insights on each site-specific page.
    """
)
