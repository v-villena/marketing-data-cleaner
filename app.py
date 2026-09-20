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

    # Required Google Ads columns
    google_required = [
        "Campaign",
        "Cost",
        "Impr.",
        "Clicks",
        "Conversions",
        "Conv. value",
    ]

    # Required Meta Ads columns
    meta_required = [
        "Campaign name",
        "Amount spent (USD)",
        "Impressions",
        "Link clicks",
        "Results",
        "Purchases conversion value",
    ]

    # Identify missing columns
    google_missing = [
        column for column in google_required
        if column not in google_data.columns
    ]

    meta_missing = [
        column for column in meta_required
        if column not in meta_data.columns
    ]

    # Display validation errors
    if google_missing:
        st.error(
            "Google Ads CSV is missing required columns: "
            + ", ".join(google_missing)
        )

    if meta_missing:
        st.error(
            "Meta Ads CSV is missing required columns: "
            + ", ".join(meta_missing)
        )

    # Stop if required columns are missing
    if google_missing or meta_missing:
        st.stop()

    # Clean and combine both platforms
    combined_data = clean_marketing_data(
        google_data,
        meta_data
    )

    st.success(
        "Your marketing data has been cleaned successfully!"
    )

    # ========================================================
    # 4. PERFORMANCE OVERVIEW
    # ========================================================

    st.subheader("Performance Overview")

    total_spend = combined_data["spend"].sum()
    total_impressions = combined_data["impressions"].sum()
    total_clicks = combined_data["clicks"].sum()
    total_revenue = combined_data["revenue"].sum()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Spend",
            f"${total_spend:,.2f}"
        )

    with col2:
        st.metric(
            "Total Impressions",
            f"{total_impressions:,.0f}"
        )

    with col3:
        st.metric(
            "Total Clicks",
            f"{total_clicks:,.0f}"
        )

    with col4:
        st.metric(
            "Reported Revenue",
            f"${total_revenue:,.2f}"
        )

    st.caption(
        "Figures reflect platform-reported data. Click and "
        "conversion definitions may differ between platforms, "
        "and attributed revenue may overlap."
    )

    # ========================================================
    # 5. PERFORMANCE BY PLATFORM
    # ========================================================

    st.subheader("Performance by Platform")

    # Aggregate campaign data by platform
    platform_summary = combined_data.groupby("platform").agg(
        spend=("spend", "sum"),
        impressions=("impressions", "sum"),
        clicks=("clicks", "sum"),
        conversions=("conversions", "sum"),
        revenue=("revenue", "sum"),
        missing_conversion_rows=("data_quality_flag", "sum"),
    ).reset_index()

    # Prepare safe denominators
    valid_impressions = platform_summary["impressions"].replace(
        0, float("nan")
    )

    valid_clicks = platform_summary["clicks"].replace(
        0, float("nan")
    )

    valid_conversions = platform_summary["conversions"].replace(
        0, float("nan")
    )

    valid_spend = platform_summary["spend"].replace(
        0, float("nan")
    )

    # Calculate platform-level CTR
    platform_summary["ctr"] = (
        platform_summary["clicks"] / valid_impressions * 100
    )

    # Calculate platform-level CPC
    platform_summary["cpc"] = (
        platform_summary["spend"] / valid_clicks
    )

    # Calculate platform-level CPM
    platform_summary["cpm"] = (
        platform_summary["spend"] / valid_impressions * 1000
    )

    # Calculate platform-level CPA
    platform_summary["cpa"] = (
        platform_summary["spend"] / valid_conversions
    )

    # Calculate platform-level CVR
    platform_summary["cvr"] = (
        platform_summary["conversions"] / valid_clicks * 100
    )

    # Calculate platform-level ROAS
    platform_summary["roas"] = (
        platform_summary["revenue"] / valid_spend
    )

    # Display platform breakdown
    st.dataframe(
        platform_summary.round(2),
        width="stretch",
        hide_index=True
    )

    if platform_summary["missing_conversion_rows"].sum() > 0:
        st.info(
            "Some platform-level conversion metrics are based "
            "on incomplete conversion data. Review the missing "
            "conversion rows before interpreting CPA or CVR."
        )

    # ========================================================
    # 6. COMBINED CAMPAIGN PERFORMANCE REPORT
    # ========================================================

    st.subheader("Combined Marketing Performance Report")

    st.dataframe(
        combined_data,
        width="stretch"
    )

    # ========================================================
    # 7. DATA QUALITY WARNINGS
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
            width="stretch",
            hide_index=True
        )

    else:

        st.success(
            "No missing conversion values detected."
        )

    # ========================================================
    # 8. DOWNLOAD CLEANED REPORT
    # ========================================================

    st.subheader("Export Your Report")

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