import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Marketing Data Cleaner",
    page_icon="📊",
    layout="wide"
)

st.title("Marketing Data Cleaner + Report Builder")

st.write(
    "Upload Google Ads and Meta Ads exports to clean, "
    "standardize, and combine your marketing performance data."
)

st.subheader("Upload your advertising data")

google_file = st.file_uploader(
    "Google Ads CSV",
    type="csv",
    key="google"
)

meta_file = st.file_uploader(
    "Meta Ads CSV",
    type="csv",
    key="meta"
)

# Preview uploaded Google Ads data
if google_file is not None:
    st.subheader("Google Ads Data Preview")

    google_data = pd.read_csv(google_file)

    st.dataframe(
        google_data,
        use_container_width=True
    )

# Preview uploaded Meta Ads data
if meta_file is not None:
    st.subheader("Meta Ads Data Preview")

    meta_data = pd.read_csv(meta_file)

    st.dataframe(
        meta_data,
        use_container_width=True
    )