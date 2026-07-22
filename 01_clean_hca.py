"""
01_clean_hca.py
------------------
Reads all 15 worksheets (one per tissue type) from HCA_scrnaseq_data_final.xlsx,
cleans the ethnicity and sex columns, and combines them into a single tidy
long-format DataFrame for downstream analysis.

Classification rules (per the paper's Methods section):
- East asian / South asian / South-east asian / Asian -> Asian
- American -> Latino (the paper states "American" includes Hispanic/Latino
  and Native American individuals)
- European (including whitespace variants) -> European
- African -> African
- Other / Mixed / Not provided -> Other
- Missing (NaN) / Unknown / clearly erroneous values (e.g. "Homo sapiens",
  "yes") -> Unknown
"""

import pandas as pd

INPUT_FILE = "HCA_scrnaseq_data_final.xlsx"
OUTPUT_FILE = "hca_clean.csv"

# The ethnicity column has this name in most worksheets; the Lung worksheet
# uses a different column name, handled separately below.
ETHNICITY_COL_STANDARD = "donor_organism.human_specific.ethnicity.ontology_aggregated"
SEX_COL_STANDARD = "donor_organism.sex"


def map_ethnicity(raw):
    """Map a raw ethnicity string to one of six canonical categories."""
    if pd.isna(raw):
        return "Unknown"
    val = str(raw).strip().lower()

    if val in ("", "nan", "not provided", "unknown"):
        return "Unknown"
    if val in ("homo sapiens", "yes"):  # clearly mis-entered values
        return "Unknown"
    if "european" in val:
        return "European"
    if "african" in val:
        return "African"
    if val == "american":
        return "Latino"
    if "asian" in val:  # covers Asian / East asian / South asian / South-east asian
        return "Asian"
    if val in ("other", "mixed"):
        return "Other"
    return "Other"


def map_sex(raw):
    """Map a raw sex string to female / male / Unknown."""
    if pd.isna(raw):
        return "Unknown"
    val = str(raw).strip().lower()
    if val == "female":
        return "female"
    if val == "male":
        return "male"
    return "Unknown"  # covers unknown / yes / homo sapiens and other errors


def load_and_clean():
    xls = pd.ExcelFile(INPUT_FILE)
    all_rows = []

    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet)

        # Find the ethnicity column (the Lung worksheet may use a different name)
        eth_col = None
        for candidate in [ETHNICITY_COL_STANDARD, "harmonized_ethnicity"]:
            if candidate in df.columns:
                eth_col = candidate
                break
        if eth_col is None:
            raise ValueError(f"Ethnicity column not found: sheet={sheet}, columns={df.columns.tolist()}")

        sex_col = SEX_COL_STANDARD if SEX_COL_STANDARD in df.columns else None
        if sex_col is None:
            raise ValueError(f"Sex column not found: sheet={sheet}")

        clean = pd.DataFrame({
            "tissue": sheet.strip(),  # strip trailing whitespace from sheet names (e.g. 'Eye ')
            "ethnicity_raw": df[eth_col],
            "sex_raw": df[sex_col],
        })
        clean["ethnicity"] = clean["ethnicity_raw"].apply(map_ethnicity)
        clean["sex"] = clean["sex_raw"].apply(map_sex)

        all_rows.append(clean)

    full = pd.concat(all_rows, ignore_index=True)
    return full


if __name__ == "__main__":
    df = load_and_clean()
    print(f"Total samples: {len(df)}  (paper's Table 1 reports 10,125)")
    print()
    print("=== Ethnicity distribution (including Unknown) ===")
    print(df["ethnicity"].value_counts())
    print()
    print("=== Sex distribution (including Unknown) ===")
    print(df["sex"].value_counts())

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved: {OUTPUT_FILE}")