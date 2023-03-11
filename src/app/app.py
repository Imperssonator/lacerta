import streamlit as st
import pandas as pd
from lacerta.heatmap_scatter import heatmap_scatter
from bokeh.embed import file_html
from bokeh.resources import CDN
# import base64


st.set_page_config(layout="wide")
st.title("Interactive Correlation Heatmap")

# Upload CSV file
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    # Read CSV data
    df = pd.read_csv(uploaded_file)
    
    # Create Bokeh figure
    layout = heatmap_scatter(df, theme="night_sky")

    # Generate Bokeh HTML file and link to it in a new page
    html = file_html(layout, CDN, "Correlation Heatmap", theme="night_sky")
    st.components.v1.html(html, width=None, height=800, scrolling=True)
    
    # Display the data as a table
    st.write(df)

else:
    st.warning("Please upload a CSV file.")
