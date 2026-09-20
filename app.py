import streamlit as st
import pandas as pd

from data_cleaner import clean_marketing_data


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

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


# ============================================================
# 2. FILE UPLOADS
# ============================================================

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


# ============================================================
# 3. PROCESS UPLOADED FILES
# ============================================================

if google_file is not None and meta_file is not None:

    # Read uploaded CSV files
    google_data = pd.read_csv(google_file)
    meta_data = pd.read_csv(meta_file)

    # Clean and combine both platforms
    combined_data = clean_marketing_data(
        google_data,
        meta_data
    )

    st.success("Your marketing data has been cleaned successfully!")

    # ========================================================
    # 4. DISPLAY PERFORMANCE REPORT
    # ========================================================

    st.subheader("Combined Marketing Performance Report")

    st.dataframe(
        combined_data,
        width="stretch"
    )

    # ========================================================
    # 5. DISPLAY DATA QUALITY WARNINGS
    # ========================================================

    flagged_data = combined_data[
        combined_data["data_quality_flag"]
    ]

    if not flagged_data.empty:

        st.warning(
            f"{len(flagged_data)} campaign(s) require data review."
        )

        st.dataframe(
            flagged_data[
                ["platform", "campaign", "conversions"]
            ],
            width="stretch"
        )

    # ========================================================
    # 6. DOWNLOAD CLEANED REPORT
    # ========================================================

    csv_data = combined_data.to_csv(index=False)

    st.download_button(
        label="Download Cleaned Performance Report",
        data=csv_data,
        file_name="marketing_performance_report.csv",
        mime="text/csv"
    )

else:

    st.info(
        "Upload both Google Ads and Meta Ads CSV files "
        "to generate your performance report."
    )