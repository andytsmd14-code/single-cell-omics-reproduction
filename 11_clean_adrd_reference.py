"""
11_clean_adrd_reference.py
-----------------------------
Clean the ADRD (Alzheimer's disease and related dementias) US reference
data (ADRD_disease_demographics_wide.csv), sourced from Matthews et al.
(2019) for ancestry, and multiple literature sources (GBD 2019, NCS,
Olmsted County study, etc.) for sex ratios per disease, as described in
the paper's Methods section.
"""

import pandas as pd

INPUT_FILE = "ADRD_disease_demographics_wide.csv"

# Disease label in the source file -> label used in PsychAD (10_clean_psychad.py)
DISEASE_NAME_MAPPING = {
    "AD/ADRD": "Alzheimer's Disease",
    "Bipolar disorder": "Bipolar Disorder",
    "Dementia with Lewy bodies": "Dementia with Lewy Bodies",
    "Frontotemporal dementia": "Frontotemporal Dementia",
    "Parkinson\u2019s disease": "Parkinson's Disease",
    "Schizophrenia": "Schizophrenia",
    "Tauopathies": "Tauopathies",
    "Vascular dementia": "Vascular Dementia",
}


def load_and_clean():
    df = pd.read_csv(INPUT_FILE)
    df.columns = [c.strip() for c in df.columns]
    df["Disease"] = df["Disease"].map(DISEASE_NAME_MAPPING)

    # --- Sex reference: already given as fractions that sum to 1 ---
    sex_ref = df[["Disease", "Female", "Male"]].copy()
    sex_ref["female_pct"] = sex_ref["Female"] * 100
    sex_ref["male_pct"] = sex_ref["Male"] * 100
    sex_ref = sex_ref[["Disease", "male_pct", "female_pct"]]

    # --- Ancestry reference: only available for AD/ADRD (Matthews et al. 2019) ---
    ad_row = df[df["Disease"] == "Alzheimer's Disease"].iloc[0]
    counts = {
        "European": ad_row["NH White"],
        "African": ad_row["Black"],
        "Asian": ad_row["Asian"],
        "Latino": ad_row["Hispanic"],
        "Other": ad_row["Other"],
    }
    total = sum(counts.values())
    ancestry_ref = pd.DataFrame({
        "ancestry": list(counts.keys()),
        "count": list(counts.values()),
        "pct_of_total": [round(v / total * 100, 1) for v in counts.values()],
    })

    return sex_ref, ancestry_ref


if __name__ == "__main__":
    sex_ref, ancestry_ref = load_and_clean()

    print("=== ADRD Sex Reference (% by disease) ===")
    print(sex_ref.to_string(index=False))
    sex_ref.to_csv("adrd_sex_reference_clean.csv", index=False)

    print("\n=== ADRD Ancestry Reference (Alzheimer's Disease only, Matthews et al. 2019) ===")
    print(ancestry_ref.to_string(index=False))
    print("\nNOTE: paper text states European 59.1%, African 12.2%, Latino 9.2%, Asian 6.6%")
    print("Our computed shares (count / sum of all 5 groups) do not match this exactly --")
    print("see discussion notes on normalization method.")
    ancestry_ref.to_csv("adrd_ancestry_reference_clean.csv", index=False)

    print("\nSaved: adrd_sex_reference_clean.csv, adrd_ancestry_reference_clean.csv")
