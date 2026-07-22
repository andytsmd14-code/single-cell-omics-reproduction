"""
13_compare_with_paper.py
---------------------------
Computes our reproduced percentages/sample sizes from the cleaned datasets
and compares them against the specific numbers quoted in the paper's main
text (Yang et al., 2026, Cell Genomics), for HCA, HTAN, and PsychAD.

This produces the "comprehensive reproduction check" tables used in the
report and the overview notebook (Tables 2b, 4b, 6b).

Inputs (from ../outputs/, produced by earlier cleaning scripts):
  hca_clean.csv      (from 01_clean_hca.py)
  htan_clean.csv     (from 04_clean_htan.py)
  psychad_clean.csv  (from 10_clean_psychad.py)

Outputs (to ../outputs/):
  hca_vs_paper_comparison.csv
  htan_vs_paper_comparison.csv
  psychad_vs_paper_comparison.csv

Every "paper value" below is a number explicitly stated in the paper's
main text -- see the comment above each dictionary for where it comes from.
"""

import pandas as pd

HCA_FILE = "../outputs/hca_clean.csv"
HTAN_FILE = "../outputs/htan_clean.csv"
PSYCHAD_FILE = "../outputs/psychad_clean.csv"


def pct_match_label(ours, paper, tol_close=1.5, tol_exact=0.15):
    """Classify how closely our computed value matches the paper's value."""
    try:
        diff = abs(float(ours) - float(paper))
    except (TypeError, ValueError):
        return "N/A"
    if diff <= tol_exact:
        return "Exact"
    if diff <= tol_close:
        return "Close"
    if diff <= 5:
        return "Gap"
    return "Large gap"


def add_row(rows, metric, ours, paper, match=None):
    if match is None:
        match = pct_match_label(ours, paper)
    rows.append({"metric": metric, "our_value": ours, "paper_value": paper, "match": match})


# ============================================================
# HCA
# ============================================================
def compare_hca():
    hca = pd.read_csv(HCA_FILE)
    rows = []

    # Tissue sample sizes (paper main text, HCA section)
    tissue_counts = hca["tissue"].value_counts()
    paper_tissue_n = {"Immune": 3704, "Gut": 883, "Skin": 906, "Lung": 743, "Kidney": 601}
    for tissue, paper_n in paper_tissue_n.items():
        match = [c for c in tissue_counts.index if c.strip().lower() == tissue.lower()]
        ours = int(tissue_counts[match[0]]) if match else None
        add_row(rows, f"{tissue} tissue n", ours, paper_n,
                "Exact" if ours == paper_n else "Mismatch")

    d = hca[hca["ethnicity"] != "Unknown"]
    euro_by_tissue = d.groupby("tissue")["ethnicity"].apply(lambda x: (x == "European").mean() * 100).round(1)
    asian_by_tissue = d.groupby("tissue")["ethnicity"].apply(lambda x: (x == "Asian").mean() * 100).round(1)
    afr_by_tissue = d.groupby("tissue")["ethnicity"].apply(lambda x: (x == "African").mean() * 100).round(1)
    lat_by_tissue = d.groupby("tissue")["ethnicity"].apply(lambda x: (x == "Latino").mean() * 100).round(1)

    def lookup(series, tissue):
        match = [c for c in series.index if c.strip().lower() == tissue.lower()]
        return series[match[0]] if match else None

    # % European by tissue (paper: tissue-level ancestry skew paragraph)
    paper_euro = {"Skin": 82.9, "Lung": 79.3, "Eye": 77.8, "Musculoskeletal": 76.2,
                  "Heart": 65.5, "Immune": 46.5, "Gut": 39.2}
    for tissue, paper_v in paper_euro.items():
        add_row(rows, f"% European, {tissue} tissue", lookup(euro_by_tissue, tissue), paper_v)

    # % Asian, immune/gut callout
    paper_asian = {"Immune": 41.7, "Gut": 41.6}
    for tissue, paper_v in paper_asian.items():
        add_row(rows, f"% Asian, {tissue} tissue", lookup(asian_by_tissue, tissue), paper_v)

    # % African callouts
    paper_afr = {"Development": 45.2, "Kidney": 25.3, "Breast": 23.9}
    for tissue, paper_v in paper_afr.items():
        add_row(rows, f"% African, {tissue}", lookup(afr_by_tissue, tissue), paper_v)

    # % Latino callouts
    paper_lat = {"Liver": 27.4, "Adipose": 21.4, "Reproduction": 18.9}
    for tissue, paper_v in paper_lat.items():
        add_row(rows, f"% Latino, {tissue}", lookup(lat_by_tissue, tissue), paper_v)

    # Sex by tissue (paper: sex ratios paragraph)
    s = hca[hca["sex"] != "Unknown"]
    female_by_tissue = s.groupby("tissue")["sex"].apply(lambda x: (x == "female").mean() * 100).round(1)
    male_by_tissue = s.groupby("tissue")["sex"].apply(lambda x: (x == "male").mean() * 100).round(1)

    paper_female = {"Breast": 89.0, "Reproduction": 66.2}
    for tissue, paper_v in paper_female.items():
        add_row(rows, f"% Female, {tissue} tissue", lookup(female_by_tissue, tissue), paper_v)

    paper_male = {"Immune": 54.3, "Eye": 68.1, "Lung": 56.1}
    for tissue, paper_v in paper_male.items():
        add_row(rows, f"% Male, {tissue} tissue", lookup(male_by_tissue, tissue), paper_v)

    return pd.DataFrame(rows)


# ============================================================
# HTAN
# ============================================================
def compare_htan():
    htan = pd.read_csv(HTAN_FILE)
    rows = []

    d = htan[htan["ethnicity"] != "Unknown"]

    # Overall ancestry composition (paper: HTAN ancestry paragraph)
    n_ancestry = len(d)
    add_row(rows, "Total ancestry-annotated n", n_ancestry, 1719,
            "Exact" if n_ancestry == 1719 else "Mismatch")
    props = (d["ethnicity"].value_counts(normalize=True) * 100).round(1)
    paper_overall = {"European": 78.3, "African": 17.3, "Asian": 2.0, "Latino": 2.0}
    for cat, paper_v in paper_overall.items():
        add_row(rows, f"Overall % {cat}", props.get(cat), paper_v)

    # Cancer-type sample sizes (paper: HTAN dataset description)
    counts = htan["cancer_type"].value_counts()
    paper_n = {"Breast": 993, "Colorectal": 151, "Pancreas": 47, "Ovary": 26, "Lung": 245, "Skin": 79}
    for ct, paper_v in paper_n.items():
        ours = int(counts.get(ct, 0))
        add_row(rows, f"{ct} n", ours, paper_v,
                "Exact" if ours == paper_v else ("Close" if abs(ours - paper_v) <= 5 else "Large gap"))

    # % European by cancer type
    euro_by_ct = d.groupby("cancer_type")["ethnicity"].apply(lambda x: (x == "European").mean() * 100).round(1)
    paper_euro = {"Pancreas": 93.6, "Ovary": 92.3, "Lung": 87.1, "Liver": 88.9, "Skin": 96.1}
    for ct, paper_v in paper_euro.items():
        add_row(rows, f"% European, {ct}", euro_by_ct.get(ct), paper_v)

    # % African by cancer type
    afr_by_ct = d.groupby("cancer_type")["ethnicity"].apply(lambda x: (x == "African").mean() * 100).round(1)
    paper_afr = {"Breast": 25.3, "Cervix": 21.1, "Blood Tumors": 27.3}
    for ct, paper_v in paper_afr.items():
        add_row(rows, f"% African, {ct}", afr_by_ct.get(ct), paper_v)

    # % Female by cancer type (paper: sex distribution paragraph)
    s = htan[htan["sex"] != "Unknown"]
    female_by_ct = s.groupby("cancer_type")["sex"].apply(lambda x: (x == "female").mean() * 100).round(1)
    paper_female = {"Lung": 49.0, "Liver": 68.4, "Blood Tumors": 58.3}
    for ct, paper_v in paper_female.items():
        add_row(rows, f"% Female, {ct}", female_by_ct.get(ct), paper_v)

    return pd.DataFrame(rows)


# ============================================================
# PsychAD
# ============================================================
def compare_psychad():
    psychad = pd.read_csv(PSYCHAD_FILE)
    rows = []

    # Disease sample sizes (paper: PsychAD dataset description)
    counts = psychad["disease"].value_counts()
    paper_n = {
        "Alzheimer's Disease": 373, "Schizophrenia": 120, "Dementia with Lewy Bodies": 112,
        "Vascular Dementia": 85, "Bipolar Disorder": 55, "Tauopathies": 47,
        "Parkinson's Disease": 40, "Frontotemporal Dementia": 15,
        "Dementia (not otherwise specified)": 439,
    }
    for disease, paper_v in paper_n.items():
        ours = int(counts.get(disease, 0))
        add_row(rows, f"{disease} n", ours, paper_v,
                "Exact" if ours == paper_v else "Mismatch")

    # AD case ancestry (paper: AD-specific ancestry paragraph)
    ad = psychad[(psychad["disease"] == "Alzheimer's Disease") & (psychad["ancestry"] != "Unknown")]
    ad_props = (ad["ancestry"].value_counts(normalize=True) * 100).round(1)
    paper_ad = {"European": 71.6, "African": 17.2, "Latino": 9.4}
    for cat, paper_v in paper_ad.items():
        add_row(rows, f"AD case % {cat}", ad_props.get(cat), paper_v)

    # Ancestry by disease callouts
    d = psychad[psychad["ancestry"] != "Unknown"]
    euro_by_dis = d.groupby("disease")["ancestry"].apply(lambda x: (x == "European").mean() * 100).round(1)
    paper_euro = {"Frontotemporal Dementia": 86.7, "Bipolar Disorder": 81.8, "Dementia with Lewy Bodies": 77.7}
    for dis, paper_v in paper_euro.items():
        add_row(rows, f"% European, {dis}", euro_by_dis.get(dis), paper_v)

    afr_by_dis = d.groupby("disease")["ancestry"].apply(lambda x: (x == "African").mean() * 100).round(1)
    paper_afr = {"Vascular Dementia": 31.8, "Schizophrenia": 26.7}
    for dis, paper_v in paper_afr.items():
        add_row(rows, f"% African, {dis}", afr_by_dis.get(dis), paper_v)

    lat_by_dis = d.groupby("disease")["ancestry"].apply(lambda x: (x == "Latino").mean() * 100).round(1)
    paper_lat = {"Tauopathies": 19.2, "Frontotemporal Dementia": 13.3}
    for dis, paper_v in paper_lat.items():
        add_row(rows, f"% Latino, {dis}", lat_by_dis.get(dis), paper_v)

    asian_by_dis = d.groupby("disease")["ancestry"].apply(lambda x: (x == "Asian").mean() * 100).round(1)
    paper_asian = {"Parkinson's Disease": 7.5, "Bipolar Disorder": 5.5}
    for dis, paper_v in paper_asian.items():
        add_row(rows, f"% Asian, {dis}", asian_by_dis.get(dis), paper_v)

    # Sex by disease (paper: sex composition paragraph; some derived from "% male" quotes)
    s = psychad[psychad["sex"] != "Unknown"]
    female_by_dis = s.groupby("disease")["sex"].apply(lambda x: (x == "female").mean() * 100).round(1)
    paper_female = {
        "Alzheimer's Disease": 64.6,
        "Vascular Dementia": 63.5,
        "Schizophrenia": 100 - 59.2,        # paper quotes 59.2% male
        "Bipolar Disorder": 100 - 54.6,     # paper quotes 54.6% male
        "Frontotemporal Dementia": 100 - 60,  # paper quotes 60% male
    }
    for dis, paper_v in paper_female.items():
        add_row(rows, f"% Female, {dis}", female_by_dis.get(dis), round(paper_v, 1))

    return pd.DataFrame(rows)


if __name__ == "__main__":
    hca_df = compare_hca()
    htan_df = compare_htan()
    psychad_df = compare_psychad()

    hca_df.to_csv("../outputs/hca_vs_paper_comparison.csv", index=False)
    htan_df.to_csv("../outputs/htan_vs_paper_comparison.csv", index=False)
    psychad_df.to_csv("../outputs/psychad_vs_paper_comparison.csv", index=False)

    for name, df in [("HCA", hca_df), ("HTAN", htan_df), ("PsychAD", psychad_df)]:
        n_total = len(df)
        n_match = (df["match"].isin(["Exact", "Close"])).sum()
        print(f"=== {name}: {n_match}/{n_total} values match exactly or closely ===")
        print(df.to_string(index=False))
        print()

    print("Saved: ../outputs/hca_vs_paper_comparison.csv")
    print("Saved: ../outputs/htan_vs_paper_comparison.csv")
    print("Saved: ../outputs/psychad_vs_paper_comparison.csv")
