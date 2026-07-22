"""
04_clean_htan.py
-------------------
Cleans the HTAN participant metadata (HTAN_Data_Final.xlsx).

Ethnicity classification (per the paper's Methods):
- HTAN raw data has TWO separate columns: "Ethnicity" (hispanic / not
  hispanic) and "Race" (white / black / asian / ...). Hispanic/Latino
  identifiers take priority over race, matching the paper's rule:
    - Hispanic or Latino (regardless of Race)     -> Latino
    - Race = White (and not Hispanic)              -> European
    - Race = Black / African American               -> African
    - Race = East Asian / South Asian / EAS_SAS      -> Asian
    - Other reported values                         -> Other
    - Unknown / missing                              -> Unknown

Cancer type classification:
- All common hematologic malignancies (blood, bone marrow, lymph node
  samples) are grouped into a single "Blood Tumors" category.
- Bone / spine / pelvis samples are grouped into "Bones".
- "Colon" and "Colorectal" are merged into a single "Colorectal" category.
"""

import pandas as pd

INPUT_FILE = "HTAN_Data_Final.xlsx"
OUTPUT_FILE = "htan_clean.csv"


def map_ethnicity(ethnicity_raw, race_raw):
    eth = str(ethnicity_raw).strip().lower() if pd.notna(ethnicity_raw) else ""
    race = str(race_raw).strip().lower() if pd.notna(race_raw) else ""

    if "hispanic or latino" in eth and "not" not in eth:
        return "Latino"
    if race == "white":
        return "European"
    if "african" in race or "black" in race:
        return "African"
    if "asian" in race:
        return "Asian"
    if race in ("not reported", "unknown", "") and eth in ("not reported", "unknown", "", "not allowed to collect"):
        return "Unknown"
    if race == "other":
        return "Other"
    return "Unknown"


def map_sex(raw):
    if pd.isna(raw):
        return "Unknown"
    val = str(raw).strip().lower()
    if val == "female":
        return "female"
    if val == "male":
        return "male"
    return "Unknown"


def map_cancer_type(tissue_site):
    """Merge granular Tissue Site values into the paper's cancer-type
    categories: hematologic malignancies -> Blood Tumors, bone-related
    sites -> Bones, colon/colorectal -> Colorectal."""
    if pd.isna(tissue_site):
        return "Other"
    t = str(tissue_site).strip().lower()

    blood_keywords = ["blood", "bone marrow", "lymph node", "lymph nodes"]
    bone_keywords = ["bone", "spine", "pelvis"]

    if any(k in t for k in blood_keywords):
        return "Blood Tumors"
    if any(k in t for k in bone_keywords):
        return "Bones"
    if t in ("colon", "colorectal"):
        return "Colorectal"

    return str(tissue_site).strip().title()


def load_and_clean():
    df = pd.read_excel(INPUT_FILE)

    clean = pd.DataFrame({
        "cancer_type": df["Tissue Site"].apply(map_cancer_type),
        "sex": df["Gender"].apply(map_sex),
        "ethnicity": [
            map_ethnicity(e, r) for e, r in zip(df["Ethnicity"], df["Race"])
        ],
    })
    return clean


if __name__ == "__main__":
    df = load_and_clean()
    print(f"Total samples: {len(df)}  (paper reports 1,959)")
    print()
    print("=== Cancer type distribution (top 15) ===")
    print(df["cancer_type"].value_counts().head(15))
    print()
    print("=== Ethnicity distribution ===")
    print(df["ethnicity"].value_counts())
    print()
    print("=== Sex distribution ===")
    print(df["sex"].value_counts())

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved: {OUTPUT_FILE}")