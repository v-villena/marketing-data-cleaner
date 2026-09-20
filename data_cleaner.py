import pandas as pd

# ============================================================
# 1. LOAD AND STANDARDIZE GOOGLE ADS DATA
# ============================================================

google_data = pd.read_csv("data/google_ads.csv")

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

# Clean Google Ads spend values
google_data["spend"] = (
    google_data["spend"]
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
    .astype(float)
)

# Flag missing conversion data
google_data["data_quality_flag"] = google_data["conversions"].isna()


# ============================================================
# 2. LOAD AND STANDARDIZE META ADS DATA
# ============================================================

meta_data = pd.read_csv("data/meta_ads.csv")

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

# Clean Meta Ads impressions and clicks
for column in ["impressions", "clicks"]:
    meta_data[column] = (
        meta_data[column]
        .str.replace(",", "", regex=False)
        .astype(int)
    )

# Clean Meta Ads spend values
meta_data["spend"] = (
    meta_data["spend"]
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
    .astype(float)
)

# Flag missing conversion data
meta_data["data_quality_flag"] = meta_data["conversions"].isna()


# ============================================================
# 3. COMBINE BOTH PLATFORMS
# ============================================================

combined_data = pd.concat(
    [google_data, meta_data],
    ignore_index=True
)

print("\nTOTAL CAMPAIGNS")
print(len(combined_data))


# ============================================================
# 4. PREPARE SAFE CALCULATIONS
# ============================================================

# Replace zero denominators with NaN to avoid division by zero
valid_impressions = combined_data["impressions"].replace(0, float("nan"))
valid_clicks = combined_data["clicks"].replace(0, float("nan"))
valid_conversions = combined_data["conversions"].replace(0, float("nan"))
valid_spend = combined_data["spend"].replace(0, float("nan"))


# ============================================================
# 5. CALCULATE TRAFFIC PERFORMANCE METRICS
# ============================================================

# Click-through rate (%)
combined_data["ctr"] = (
    combined_data["clicks"] / valid_impressions * 100
)

# Cost per click
combined_data["cpc"] = (
    combined_data["spend"] / valid_clicks
)

# Cost per thousand impressions
combined_data["cpm"] = (
    combined_data["spend"] / valid_impressions * 1000
)


# ============================================================
# 6. CALCULATE CONVERSION AND REVENUE METRICS
# ============================================================

# Cost per acquisition
combined_data["cpa"] = (
    combined_data["spend"] / valid_conversions
)

# Conversion rate (%)
combined_data["cvr"] = (
    combined_data["conversions"] / valid_clicks * 100
)

# Return on ad spend
combined_data["roas"] = (
    combined_data["revenue"] / valid_spend
)


# ============================================================
# 7. DISPLAY RESULTS
# ============================================================

print("\nCOMBINED MARKETING PERFORMANCE REPORT")

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
    "data_quality_flag",
]

print(
    combined_data[report_columns]
    .round(2)
    .to_string(index=False)
)

print("\nCAMPAIGNS REQUIRING DATA REVIEW")

print(
    combined_data.loc[
        combined_data["data_quality_flag"],
        ["platform", "campaign", "conversions"]
    ].to_string(index=False)
)

# ============================================================
# 8. EXPORT CLEANED PERFORMANCE DATA
# ============================================================

combined_data[report_columns].round(2).to_csv(
    "marketing_performance_report.csv",
    index=False
)

print("\nReport exported: marketing_performance_report.csv")