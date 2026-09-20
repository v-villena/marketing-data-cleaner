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


# ============================================================
# 2. DASHBOARD STYLING
# ============================================================

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3 {
            color: #202638;
        }

        div[data-testid="stMetric"] {
            background-color: #F7F9FC;
            border: 1px solid #E4E9F2;
            border-radius: 14px;
            padding: 22px 24px;
        }

        div[data-testid="stMetricLabel"] {
            color: #647084;
            font-size: 14px;
        }

        div[data-testid="stMetricValue"] {
            color: #202638;
            font-weight: 700;
        }

        div[data-testid="stMetric"]:hover {
            border-color: #1A6BFF;
        }

        div[data-testid="stDownloadButton"] button {
            background-color: #1A6BFF;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
        }

        div[data-testid="stDownloadButton"] button:hover {
            background-color: #1558D6;
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 3. HELPER FUNCTIONS
# ============================================================

def safe_divide(numerator, denominator):
    """Return a missing value when division is not possible."""

    if pd.isna(denominator) or denominator == 0:
        return float("nan")

    return numerator / denominator


def format_currency(value):
    if pd.isna(value):
        return "N/A"

    return f"${value:,.2f}"


def format_number(value):
    if pd.isna(value):
        return "N/A"

    return f"{value:,.0f}"


def format_percent(value):
    if pd.isna(value):
        return "N/A"

    return f"{value:.2f}%"


def format_roas(value):
    if pd.isna(value):
        return "N/A"

    return f"{value:.2f}x"


def format_summary_table(data):
    """Create a presentation-friendly copy of a summary table."""

    formatted = data.copy()

    currency_columns = [
        "Spend",
        "Revenue",
        "CPC",
        "CPM",
        "CPA",
    ]

    for column in currency_columns:
        if column in formatted.columns:
            formatted[column] = formatted[column].map(
                format_currency
            )

    number_columns = [
        "Impressions",
        "Clicks",
        "Conversions",
        "Missing Conversion Rows",
    ]

    for column in number_columns:
        if column in formatted.columns:
            formatted[column] = formatted[column].map(
                format_number
            )

    for column in ["CTR", "CVR"]:
        if column in formatted.columns:
            formatted[column] = formatted[column].map(
                format_percent
            )

    if "ROAS" in formatted.columns:
        formatted["ROAS"] = formatted["ROAS"].map(
            format_roas
        )

    return formatted


# ============================================================
# 4. PAGE HEADER
# ============================================================

st.title("Marketing Data Cleaner + Report Builder")

st.write(
    "Upload Google Ads and Meta Ads exports to clean, "
    "standardize, and combine your marketing performance data."
)


# ============================================================
# 5. FILE UPLOADS
# ============================================================

st.subheader("Upload Your Advertising Data")

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
# 6. PROCESS UPLOADED FILES
# ============================================================

if google_file is not None and meta_file is not None:

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

    if google_missing or meta_missing:
        st.stop()

    # Clean and combine platform data
    combined_data = clean_marketing_data(
        google_data,
        meta_data
    )

    st.success(
        "Your marketing data has been cleaned successfully!"
    )

    # ========================================================
    # 7. CALCULATE OVERALL PERFORMANCE
    # ========================================================

    total_spend = combined_data["spend"].sum()
    total_impressions = combined_data["impressions"].sum()
    total_clicks = combined_data["clicks"].sum()
    total_conversions = combined_data["conversions"].sum()
    total_revenue = combined_data["revenue"].sum()

    missing_conversion_rows = int(
        combined_data["data_quality_flag"].sum()
    )

    blended_ctr = (
        safe_divide(total_clicks, total_impressions) * 100
    )

    blended_cpc = safe_divide(
        total_spend,
        total_clicks
    )

    blended_cpm = (
        safe_divide(total_spend, total_impressions) * 1000
    )

    blended_cpa = safe_divide(
        total_spend,
        total_conversions
    )

    blended_cvr = (
        safe_divide(total_conversions, total_clicks) * 100
    )

    blended_roas = safe_divide(
        total_revenue,
        total_spend
    )

    # ========================================================
    # 8. HEADLINE KPI CARDS
    # ========================================================

    st.subheader("Performance Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Spend",
            format_currency(total_spend)
        )

    with col2:
        st.metric(
            "Reported Revenue",
            format_currency(total_revenue)
        )

    with col3:
        st.metric(
            "Blended CPA",
            format_currency(blended_cpa)
        )

    with col4:
        st.metric(
            "Blended ROAS",
            format_roas(blended_roas)
        )

    st.caption(
        "KPIs use combined platform-reported totals. "
        "Google Ads and Meta Ads may use different click, "
        "conversion, and attribution definitions. "
        "Attributed revenue may overlap across platforms."
    )

    # ========================================================
    # 9. OVERALL PERFORMANCE TABLE
    # ========================================================

    st.subheader("Overall Performance")

    overall_summary = pd.DataFrame(
        [
            {
                "Spend": total_spend,
                "Impressions": total_impressions,
                "Clicks": total_clicks,
                "CTR": blended_ctr,
                "CPC": blended_cpc,
                "CPM": blended_cpm,
                "Conversions": total_conversions,
                "CPA": blended_cpa,
                "CVR": blended_cvr,
                "Revenue": total_revenue,
                "ROAS": blended_roas,
            }
        ]
    )

    st.dataframe(
        format_summary_table(overall_summary),
        width="stretch",
        hide_index=True
    )

    # ========================================================
    # 10. PERFORMANCE BY PLATFORM
    # ========================================================

    st.subheader("Performance by Platform")

    platform_summary = combined_data.groupby(
        "platform"
    ).agg(
        spend=("spend", "sum"),
        impressions=("impressions", "sum"),
        clicks=("clicks", "sum"),
        conversions=("conversions", "sum"),
        revenue=("revenue", "sum"),
        missing_conversion_rows=(
            "data_quality_flag",
            "sum"
        ),
    ).reset_index()

    # Calculate platform-level metrics from totals
    platform_summary["ctr"] = (
        platform_summary["clicks"]
        / platform_summary["impressions"].replace(
            0, float("nan")
        )
        * 100
    )

    platform_summary["cpc"] = (
        platform_summary["spend"]
        / platform_summary["clicks"].replace(
            0, float("nan")
        )
    )

    platform_summary["cpm"] = (
        platform_summary["spend"]
        / platform_summary["impressions"].replace(
            0, float("nan")
        )
        * 1000
    )

    platform_summary["cpa"] = (
        platform_summary["spend"]
        / platform_summary["conversions"].replace(
            0, float("nan")
        )
    )

    platform_summary["cvr"] = (
        platform_summary["conversions"]
        / platform_summary["clicks"].replace(
            0, float("nan")
        )
        * 100
    )

    platform_summary["roas"] = (
        platform_summary["revenue"]
        / platform_summary["spend"].replace(
            0, float("nan")
        )
    )

    # Rename columns for the dashboard
    platform_summary = platform_summary.rename(
        columns={
            "platform": "Platform",
            "spend": "Spend",
            "impressions": "Impressions",
            "clicks": "Clicks",
            "conversions": "Conversions",
            "revenue": "Revenue",
            "missing_conversion_rows": (
                "Missing Conversion Rows"
            ),
            "ctr": "CTR",
            "cpc": "CPC",
            "cpm": "CPM",
            "cpa": "CPA",
            "cvr": "CVR",
            "roas": "ROAS",
        }
    )

    # Arrange columns in reporting order
    platform_summary = platform_summary[
        [
            "Platform",
            "Spend",
            "Impressions",
            "Clicks",
            "CTR",
            "CPC",
            "CPM",
            "Conversions",
            "CPA",
            "CVR",
            "Revenue",
            "ROAS",
            "Missing Conversion Rows",
        ]
    ]

    st.dataframe(
        format_summary_table(platform_summary),
        width="stretch",
        hide_index=True
    )

    if missing_conversion_rows > 0:
        st.info(
            "Some conversion metrics are based on incomplete "
            "platform data. Review flagged campaigns before "
            "interpreting CPA, CVR, or reported conversions."
        )

    # ========================================================
    # 11. CAMPAIGN PERFORMANCE REPORT
    # ========================================================

    st.subheader("Campaign Performance")

    st.dataframe(
        combined_data,
        width="stretch",
        hide_index=True,
        column_config={
            "spend": st.column_config.NumberColumn(
                "Spend",
                format="$%.2f"
            ),
            "revenue": st.column_config.NumberColumn(
                "Revenue",
                format="$%.2f"
            ),
            "ctr": st.column_config.NumberColumn(
                "CTR",
                format="%.2f%%"
            ),
            "cpc": st.column_config.NumberColumn(
                "CPC",
                format="$%.2f"
            ),
            "cpm": st.column_config.NumberColumn(
                "CPM",
                format="$%.2f"
            ),
            "cpa": st.column_config.NumberColumn(
                "CPA",
                format="$%.2f"
            ),
            "cvr": st.column_config.NumberColumn(
                "CVR",
                format="%.2f%%"
            ),
            "roas": st.column_config.NumberColumn(
                "ROAS",
                format="%.2fx"
            ),
            "data_quality_flag": (
                st.column_config.CheckboxColumn(
                    "Needs Review"
                )
            ),
        }
    )

    # ========================================================
    # 12. DATA QUALITY
    # ========================================================

    st.subheader("Data Quality")

    flagged_data = combined_data[
        combined_data["data_quality_flag"]
    ]

    if not flagged_data.empty:

        st.warning(
            f"{len(flagged_data)} campaign(s) "
            "require data review."
        )

        st.dataframe(
            flagged_data[
                [
                    "platform",
                    "campaign",
                    "conversions",
                ]
            ],
            width="stretch",
            hide_index=True
        )

    else:

        st.success(
            "No missing conversion values detected."
        )

    # ========================================================
    # 13. EXPORT
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