import pandas as pd


def clean_marketing_data(google_data, meta_data):
    """
    Clean and combine Google Ads and Meta Ads campaign exports.
    Returns a standardized performance report.
    """

    # Work with copies to preserve the original uploaded data
    google_data = google_data.copy()
    meta_data = meta_data.copy()

    # ========================================================
    # 1. STANDARDIZE GOOGLE ADS
    # ========================================================

    google_data = google_data.rename(
        columns={
            "Campaign": "campaign",
            "Cost": "spend",
            "Impr.": "impressions",
            "Clicks": "clicks",
            "Conversions": "conversions",
            "Conv. value": "revenue",
        }
    )

    google_data["platform"] = "Google Ads"
    google_data["click_type"] = "Google Ads clicks"
    google_data["conversion_type"] = "Google Ads conversions"

    google_data["spend"] = (
        google_data["spend"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .astype(float)
    )

    google_data["data_quality_flag"] = google_data["conversions"].isna()

    # ========================================================
    # 2. STANDARDIZE META ADS
    # ========================================================

    meta_data = meta_data.rename(
        columns={
            "Campaign name": "campaign",
            "Amount spent (USD)": "spend",
            "Impressions": "impressions",
            "Link clicks": "clicks",
            "Results": "conversions",
            "Purchases conversion value": "revenue",
        }
    )

    meta_data["platform"] = "Meta Ads"
    meta_data["click_type"] = "Link clicks"
    meta_data["conversion_type"] = "Meta Ads results"

    for column in ["impressions", "clicks"]:
        meta_data[column] = (
            meta_data[column]
            .astype(str)
            .str.replace(",", "", regex=False)
            .astype(int)
        )

    meta_data["spend"] = (
        meta_data["spend"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .astype(float)
    )

    meta_data["data_quality_flag"] = meta_data["conversions"].isna()

    # ========================================================
    # 3. COMBINE DATA
    # ========================================================

    combined_data = pd.concat(
        [google_data, meta_data],
        ignore_index=True
    )

    # ========================================================
    # 4. CALCULATE PERFORMANCE METRICS
    # ========================================================

    valid_impressions = combined_data["impressions"].replace(
        0, float("nan")
    )
    valid_clicks = combined_data["clicks"].replace(
        0, float("nan")
    )
    valid_conversions = combined_data["conversions"].replace(
        0, float("nan")
    )
    valid_spend = combined_data["spend"].replace(
        0, float("nan")
    )

    combined_data["ctr"] = (
        combined_data["clicks"] / valid_impressions * 100
    )

    combined_data["cpc"] = (
        combined_data["spend"] / valid_clicks
    )

    combined_data["cpm"] = (
        combined_data["spend"] / valid_impressions * 1000
    )

    combined_data["cpa"] = (
        combined_data["spend"] / valid_conversions
    )

    combined_data["cvr"] = (
        combined_data["conversions"] / valid_clicks * 100
    )

    combined_data["roas"] = (
        combined_data["revenue"] / valid_spend
    )

    # ========================================================
    # 5. RETURN CLEANED REPORT
    # ========================================================

    report_columns = [
        "platform",
        "campaign",
        "spend",
        "impressions",
        "clicks",
        "conversions",
        "revenue",
        "ctr",
        "cpc",
        "cpm",
        "cpa",
        "cvr",
        "roas",
        "click_type",
        "conversion_type",
        "data_quality_flag",
    ]

    return combined_data[report_columns].round(2)