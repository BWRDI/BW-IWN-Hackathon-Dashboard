import streamlit as st

st.set_page_config(
    page_title="Team Barwon",
    page_icon="👋",
)

st.write("# Barwon Water's IWN Hackathon Dashboard! 👋")

st.sidebar.success("Select a site above.")

st.markdown(
    """
    This dashboard is organized into five pages, providing detailed insights for each monitoring site along with an overall summary.  
    **👈 Select a page from the sidebar** to explore data for each site.  
    ### Need assistance?
    - James, our AI Chat Bot, is ready to help in the bottom right corner of each page.
    - Simply click on James for quick answers to any questions related to the dashboard or the data you're viewing.
    ### Want to dive deeper?
    - Explore detailed data visualizations on each site page.
"""
)