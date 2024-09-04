import streamlit as st


def main():
    # builds the sidebar menu
    with st.sidebar:
        st.page_link('streamlit_app.py', label='Individual Checker', icon='👋')
        st.page_link('pages/competition.py', label='Competition Checker', icon='🛡️')

    st.title(f'🔥 Individual Checker')

    # your content
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

if __name__ == '__main__':
    main()



