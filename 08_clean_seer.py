"""
08_clean_seer.py
------------------
Clean the raw SEER*Explorer 2018-2022 export (SEER_combined_cancer_demographics.csv).
The raw file mixes real data rows with metadata/footnote rows (source notes,
methodology text) that share the same column structure but have Value = NaN.
This script:
  1. Drops the footnote/metadata rows (Value is NaN)
  2. Maps SEER cancer-site names and race/ethnicity group names to the
     canonical categories used in Yang et al. (2026) / our HTAN cleaning
  3. Outputs two tidy reference tables: one for ancestry, one for sex
"""

import pandas as pd

INPUT_FILE = "SEER_combined_cancer_demographics.csv"

# SEER cancer-site name -> HTAN cancer_type category
# Blood Tumors combines Leukemia + Non-Hodgkin Lymphoma + Myeloma, matching
# the paper's grouping of "all common hematologic malignancies"
CANCER_SITE_MAPPING = {
    "Female Breast": "Breast",
    "Lung and Bronchus": "Lung",
    "Colon and Rectum (including Appendix)": "Colorectal",
    "Melanoma of the Skin": "Skin",
    "Liver and Intrahepatic Bile Duct": "Liver",
    "Pancreas": "Pancreas",
    "Ovary": "Ovary",
    "Cervix Uteri": "Cervix",
    "Leukemia": "Blood Tumors",
    "Non-Hodgkin Lymphoma": "Blood Tumors",
    "Myeloma": "Blood Tumors",
    "Brain and Other Nervous System": "Brain",
    "Bones and Joints": "Bones",
}

# SEER race/ethnicity group -> canonical ancestry category (matches HTAN/HCA labels)
ANCESTRY_MAPPING = {
    "Non-Hispanic White": "European",
    "Non-Hispanic Black": "African",
    "Non-Hispanic Asian/Pacific Islander": "Asian",
    "Hispanic (any race)": "Latino",
    "Non-Hispanic American Indian/Alaska Native": "Other",
}

SEX_MAPPING = {"Male": "male", "Female": "female"}


def load_and_clean():
    df = pd.read_csv(INPUT_FILE)

    # Drop footnote/metadata rows: real data rows always have a numeric Value
    df = df[df["Value"].notna()].copy()
    df["Value"] = df["Value"].astype(float)

    # Only keep cancer sites we have a mapping for
    df = df[df["CancerType"].isin(CANCER_SITE_MAPPING.keys())].copy()
    df["cancer_type"] = df["CancerType"].map(CANCER_SITE_MAPPING)

    ancestry_df = df[df["Measure"] == "Ancestry"].copy()
    ancestry_df["ancestry"] = ancestry_df["Group"].map(ANCESTRY_MAPPING)
    # For Blood Tumors, sum the rate across Leukemia + NHL + Myeloma per ancestry group
    ancestry_clean = (
        ancestry_df.groupby(["cancer_type", "ancestry"])["Value"]
        .sum()
        .reset_index()
        .rename(columns={"Value": "seer_rate_per_100k"})
    )

    sex_df = df[df["Measure"] == "Sex"].copy()
    sex_df["sex"] = sex_df["Group"].map(SEX_MAPPING)
    sex_clean = (
        sex_df.groupby(["cancer_type", "sex"])["Value"]
        .sum()
        .reset_index()
        .rename(columns={"Value": "seer_rate_per_100k"})
    )

    return ancestry_clean, sex_clean


if __name__ == "__main__":
    ancestry_clean, sex_clean = load_and_clean()

    print("=== SEER Ancestry Reference (rate per 100,000) ===")
    print(ancestry_clean.to_string(index=False))
    ancestry_clean.to_csv("seer_ancestry_clean.csv", index=False)

    print("\n=== SEER Sex Reference (rate per 100,000) ===")
    print(sex_clean.to_string(index=False))
    sex_clean.to_csv("seer_sex_clean.csv", index=False)

    print("\nSaved: seer_ancestry_clean.csv, seer_sex_clean.csv")
