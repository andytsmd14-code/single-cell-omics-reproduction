"""
10_clean_psychad.py
----------------------
Clean the PsychAD consortium metadata (psych-AD_media-1.csv).

Structure differs from HCA/HTAN: instead of one disease column, each
diagnosis is a separate binary column (crossDis_AD, crossDis_SCZ, ...),
because a donor can carry more than one diagnosis. This script reshapes
the data into long format (one row per donor-diagnosis pair), matching
the paper's approach of treating each donor's diagnoses independently
for the per-disease stacked bar charts (Figure 3A/3C).

Ancestry mapping (per paper Methods):
  AFR -> African, AMR -> Latino, EUR -> European,
  EAS/SAS/EAS_SAS -> Asian, everything else -> Unknown
"""

import pandas as pd

INPUT_FILE = "psych-AD_media-1.csv"
OUTPUT_FILE = "psychad_clean.csv"

ANCESTRY_MAPPING = {
    "EUR": "European",
    "AFR": "African",
    "AMR": "Latino",
    "EAS": "Asian",
    "SAS": "Asian",
    "EAS_SAS": "Asian",
}

# crossDis_* column -> disease label used in the paper's Figure 3
DISEASE_COLUMNS = {
    "crossDis_AD": "Alzheimer's Disease",
    "crossDis_SCZ": "Schizophrenia",
    "crossDis_DLBD": "Dementia with Lewy Bodies",
    "crossDis_Vas": "Vascular Dementia",
    "crossDis_BD": "Bipolar Disorder",
    "crossDis_Tau": "Tauopathies",
    "crossDis_PD": "Parkinson's Disease",
    "crossDis_FTD": "Frontotemporal Dementia",
}


def map_ancestry(raw):
    if pd.isna(raw):
        return "Unknown"
    return ANCESTRY_MAPPING.get(str(raw).strip(), "Unknown")


def map_sex(raw):
    if pd.isna(raw):
        return "Unknown"
    val = str(raw).strip().lower()
    return val if val in ("male", "female") else "Unknown"


def load_and_clean():
    df = pd.read_csv(INPUT_FILE)

    df["ancestry"] = df["Ancestry"].apply(map_ancestry)
    df["sex_clean"] = df["sex"].apply(map_sex)

    # "Dementia not otherwise specified": Dementia == 1.0 in the source file
    df["is_dementia_nos"] = df["Dementia"] == 1.0

    long_rows = []
    for col, disease_label in DISEASE_COLUMNS.items():
        subset = df[df[col] == 1.0]
        for _, row in subset.iterrows():
            long_rows.append({
                "donor_id": row["DonorID"],
                "disease": disease_label,
                "ancestry": row["ancestry"],
                "sex": row["sex_clean"],
            })

    # add Dementia NOS as its own disease category
    for _, row in df[df["is_dementia_nos"]].iterrows():
        long_rows.append({
            "donor_id": row["DonorID"],
            "disease": "Dementia (not otherwise specified)",
            "ancestry": row["ancestry"],
            "sex": row["sex_clean"],
        })

    long_df = pd.DataFrame(long_rows)
    return df, long_df


if __name__ == "__main__":
    wide_df, long_df = load_and_clean()

    print(f"Total donors: {len(wide_df)}  (paper: 1,494)")
    print()
    print("=== Overall ancestry distribution ===")
    print(wide_df["ancestry"].value_counts())
    print(f"  -> European %: {(wide_df['ancestry']=='European').mean()*100:.1f}  (paper: 65.9%)")
    print(f"  -> African %:  {(wide_df['ancestry']=='African').mean()*100:.1f}  (paper: 22.6%)")
    print(f"  -> Latino %:   {(wide_df['ancestry']=='Latino').mean()*100:.1f}  (paper: 9.0%)")
    print(f"  -> Asian %:    {(wide_df['ancestry']=='Asian').mean()*100:.1f}  (paper: 1.8%)")
    print()
    print("=== Overall sex distribution ===")
    print(wide_df["sex_clean"].value_counts())
    print(f"  -> female %: {(wide_df['sex_clean']=='female').mean()*100:.1f}  (paper: 51.6%)")
    print()
    print("=== Disease category sample sizes (long format) ===")
    print(long_df["disease"].value_counts())

    long_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved: {OUTPUT_FILE}")
