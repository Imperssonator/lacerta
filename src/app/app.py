import streamlit as st
import pandas as pd
from lacerta.correlations import calculate_correlations, correlation_heatmap_scatter
from bokeh.embed import file_html
from bokeh.resources import CDN
# import base64


# Set default page config
st.set_page_config(
    page_title="Interactive Correlation Heatmap",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Upload CSV file
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    # Read CSV data
    df = pd.read_csv(uploaded_file)

    # Calculate correlations
    df_corr = calculate_correlations(df, exclude_self=True, exclude_dupe=True)
    
    # Create Bokeh figure
    layout = correlation_heatmap_scatter(df)

    # Generate Bokeh HTML file and link to it in a new page
    html = file_html(layout, CDN, "Correlation Heatmap")
    st.components.v1.html(html, width=None, height=800, scrolling=True)
    
    # Display the data as a table
    st.write(df_corr.sort_values("p_value"))

else:
    st.warning("Please upload a CSV file.")
