import pandas as pd


# ============================================================
# 1. SUPPORTED COLUMN NAMES
# ============================================================

COLUMN_ALIASES = {
    "Google Ads": {
        "campaign": [
            "Campaign",
            "Campaign name",
        ],
        "spend": [
            "Cost",
            "Cost (USD)",
            "Spend",
        ],
        "impressions": [
            "Impr.",
            "Impressions",
        ],
        "clicks": [
            "Clicks",
        ],
        "conversions": [
            "Conversions",
            "Conv.",
        ],
        "revenue": [
            "Conv. value",
            "Conversion value",
            "Conversion value (USD)",
        ],
    },
    "Meta Ads": {
        "campaign": [
            "Campaign name",
            "Campaign",
        ],
        "spend": [
            "Amount spent (USD)",
            "Amount spent",
            "Amount spent (US Dollars)",
        ],
        "impressions": [
            "Impressions",
        ],
        "clicks": [
            "Link clicks",
            "Link Clicks",
        ],
        "conversions": [
            "Results",
        ],
        "revenue": [
            "Purchases conversion value",
            "Purchases conversion value (USD)",
        ],
    },
}


# ============================================================
# 2. FLEXIBLE COLUMN MATCHING
# ============================================================

def normalize_column_name(name):
    """Ignore capitalization and extra spaces in headers."""

    return " ".join(
        str(name).strip().lower().split()
    )


def get_column_mapping(data, platform):
    """Match uploaded columns to standardized report fields."""

    aliases = COLUMN_ALIASES[platform]

    uploaded_columns = {
        normalize_column_name(column): column
        for column in data.columns
    }

    mapping = {}
    missing = []

    for standard_name, possible_names in aliases.items():

        matched_column = None

        for possible_name in possible_names:

            normalized_name = normalize_column_name(
                possible_name
            )

            if normalized_name in uploaded_columns:

                matched_column = uploaded_columns[
                    normalized_name
                ]

                break

        if matched_column is None:

            missing.append(
                {
                    "field": standard_name,
                    "accepted_names": possible_names,
                }
            )

        else:

            mapping[matched_column] = standard_name

    return mapping, missing


def validate_platform_columns(data, platform):
    """Return missing required fields for an uploaded CSV."""

    _, missing = get_column_mapping(
        data,
        platform
    )

    return missing


# ============================================================
# 3. NUMERIC CLEANING
# ============================================================

def clean_numeric_column(series):
    """Convert exported numeric values into usable numbers."""

    cleaned = (
        series
        .astype("string")
        .str.strip()
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.strip()
    )

    cleaned = cleaned.replace(
        {
            "": pd.NA,
            "-": pd.NA,
            "—": pd.NA,
            "N/A": pd.NA,
            "n/a": pd.NA,
            "None": pd.NA,
            "nan": pd.NA,
        }
    )

    return pd.to_numeric(
        cleaned,
        errors="coerce"
    )


# ============================================================
# 4. STANDARDIZE PLATFORM DATA
# ============================================================

def standardize_platform_data(data, platform):

    data = data.copy()

    column_mapping, missing = get_column_mapping(
        data,
        platform
    )

    if missing:

        missing_fields = ", ".join(
            item["field"]
            for item in missing
        )

        raise ValueError(
            f"{platform} is missing required fields: "
            f"{missing_fields}"
        )

    data = data.rename(
        columns=column_mapping
    )

    standard_columns = [
        "campaign",
        "spend",
        "impressions",
        "clicks",
        "conversions",
        "revenue",
    ]

    data = data[standard_columns].copy()

    data = data.dropna(
        how="all"
    )

    data["campaign"] = (
        data["campaign"]
        .astype("string")
        .str.strip()
    )

    data = data[
        data["campaign"].notna()
        & data["campaign"].ne("")
    ].copy()

    numeric_columns = [
        "spend",
        "impressions",
        "clicks",
        "conversions",
        "revenue",
    ]

    for column in numeric_columns:

        data[column] = clean_numeric_column(
            data[column]
        )

    # Preserve missing or unparseable values as NaN. A reported zero
    # is valid and must not be flagged as missing.
    data["data_quality_issues"] = data[numeric_columns].apply(
        lambda row: ", ".join(
            f"Missing {column}"
            for column in numeric_columns
            if pd.isna(row[column])
        ),
        axis=1,
    )
    data["data_quality_flag"] = data["data_quality_issues"].ne("")

    data["platform"] = platform

    if platform == "Google Ads":

        data["click_type"] = "Google Ads clicks"

        data["conversion_type"] = (
            "Google Ads conversions"
        )

    else:

        data["click_type"] = "Link clicks"

        data["conversion_type"] = (
            "Meta Ads results"
        )

    return data


# ============================================================
# 5. CLEAN AND COMBINE DATA
# ============================================================

def clean_marketing_data(google_data, meta_data):

    google_data = standardize_platform_data(
        google_data,
        "Google Ads"
    )

    meta_data = standardize_platform_data(
        meta_data,
        "Meta Ads"
    )

    combined_data = pd.concat(
        [google_data, meta_data],
        ignore_index=True
    )

    # ========================================================
    # 6. CALCULATE PERFORMANCE METRICS
    # ========================================================

    valid_impressions = (
        combined_data["impressions"]
        .replace(0, float("nan"))
    )

    valid_clicks = (
        combined_data["clicks"]
        .replace(0, float("nan"))
    )

    valid_conversions = (
        combined_data["conversions"]
        .replace(0, float("nan"))
    )

    valid_spend = (
        combined_data["spend"]
        .replace(0, float("nan"))
    )

    combined_data["ctr"] = (
        combined_data["clicks"]
        / valid_impressions
        * 100
    )

    combined_data["cpc"] = (
        combined_data["spend"]
        / valid_clicks
    )

    combined_data["cpm"] = (
        combined_data["spend"]
        / valid_impressions
        * 1000
    )

    combined_data["cpa"] = (
        combined_data["spend"]
        / valid_conversions
    )

    combined_data["cvr"] = (
        combined_data["conversions"]
        / valid_clicks
        * 100
    )

    combined_data["roas"] = (
        combined_data["revenue"]
        / valid_spend
    )

    # ========================================================
    # 7. RETURN STANDARDIZED REPORT
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
        "data_quality_issues",
    ]

    return (
        combined_data[report_columns]
        .round(2)
    )