"""
05_taiwan_reference.py
------------------------
Build an English-language Taiwan cancer incidence reference table from
Taiwan HPA (Health Promotion Administration) national cancer registry data:
"Cancer Incidence Statistics 1979-2022 by County, Sex, and Cancer Site".

Filters to national level ("全國"), the latest available year (2022),
split by sex, and maps Taiwan cancer-site names to the HTAN cancer
categories used in Yang et al. (2026) Cell Genomics, so the two can be
compared directly. Output columns and cancer-type labels are in English
so the table is readable by non-Chinese-speaking reviewers.
"""

import pandas as pd

TAIWAN_FILE = "taiwan_cancer_registry.csv"
LATEST_YEAR = 2022  # Most recent year in the source file (Taiwan calendar year 111)

RATE_COL = "年齡標準化發生率  WHO 2000世界標準人口 (每10萬人口) "
COUNT_COL = "癌症發生數"
YEAR_COL = "癌症診斷年"
COUNTY_COL = "縣市別"
SEX_COL = "性別"
SITE_COL = "癌症別"

# HTAN cancer category -> Taiwan cancer-site name(s) (original Chinese labels
# as they appear in the source file). Blood Tumors maps to three separate
# Taiwan categories that get summed, matching how the paper grouped all
# common hematologic malignancies into one "Blood Tumors" category.
CANCER_MAPPING = {
    "Breast": ["女性乳房"],
    "Lung": ["肺、支氣管及氣管"],
    "Colorectal": ["結直腸"],
    "Skin": ["皮膚"],
    "Liver": ["肝及肝內膽管"],
    "Pancreas": ["胰"],
    "Ovary": ["卵巢、輸卵管及寬韌帶"],
    "Cervix": ["子宮頸"],
    "Blood Tumors": ["白血病", "何杰金氏淋巴瘤", "非何杰金氏淋巴瘤"],
    "Brain": ["腦"],
}

SEX_MAPPING = {"男": "male", "女": "female"}


def load_taiwan_reference():
    df = pd.read_csv(TAIWAN_FILE, encoding="utf-8")

    # Keep national-level, latest-year, sex-specific rows only
    # (exclude the "全" row, which is the combined male+female total)
    latest = df[
        (df[COUNTY_COL] == "全國")
        & (df[YEAR_COL] == LATEST_YEAR)
        & (df[SEX_COL].isin(["男", "女"]))
    ].copy()

    # Convert count column from a comma-formatted string (e.g. "9,989 ") to int
    latest[COUNT_COL] = (
        latest[COUNT_COL].astype(str).str.replace(",", "").str.strip().astype(int)
    )

    rows = []
    for cancer_type_en, taiwan_names in CANCER_MAPPING.items():
        for sex_zh, sex_en in SEX_MAPPING.items():
            subset = latest[
                (latest[SEX_COL] == sex_zh) & (latest[SITE_COL].isin(taiwan_names))
            ]
            # For Blood Tumors, sum the age-standardized rates and counts
            # across the three underlying Taiwan categories
            total_rate = subset[RATE_COL].sum()
            total_count = subset[COUNT_COL].sum()
            rows.append({
                "cancer_type": cancer_type_en,
                "sex": sex_en,
                "taiwan_age_std_rate_per_100k": round(total_rate, 2),
                "taiwan_case_count": int(total_count),
            })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    ref = load_taiwan_reference()
    print(ref.to_string(index=False))
    ref.to_csv("taiwan_reference_clean_en.csv", index=False)
    print("\nSaved: taiwan_reference_clean_en.csv")
    print(f"Source: Taiwan Health Promotion Administration (HPA), Ministry of")
    print(f"Health and Welfare. Cancer Incidence Statistics by County, Sex, and")
    print(f"Cancer Site, 1979-2022 (Taiwan calendar years 68-111). Year used: {LATEST_YEAR}.")
