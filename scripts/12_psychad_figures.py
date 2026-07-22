"""
12_psychad_figures.py
------------------------
Reproduce Figure 3 (A-D) from Yang et al. (2026):
  A = PsychAD diseases by ancestry (stacked bar)
  B = Alzheimer's Disease ancestry: PsychAD vs ADRD reference (grouped bar)
  C = PsychAD diseases by sex (stacked bar)
  D = PsychAD vs ADRD reference sex composition, by disease (grouped bar)
"""

import pandas as pd
import numpy as np
from scipy.stats import chisquare
import matplotlib.pyplot as plt

PSYCHAD_FILE = "../outputs/psychad_clean.csv"
ADRD_SEX_FILE = "../outputs/adrd_sex_reference_clean.csv"
ADRD_ANCESTRY_FILE = "../outputs/adrd_ancestry_reference_clean.csv"

ETHNICITY_COLORS = {
    "African": "#b0413e", "Latino": "#e08214", "Asian": "#4575b4",
    "European": "#762a83", "Other": "#f4c78b",
}
SEX_COLORS = {"male": "#7ec8e3", "female": "#c9971e"}

DISEASE_ORDER = [
    "Alzheimer's Disease", "Bipolar Disorder", "Dementia with Lewy Bodies",
    "Dementia (not otherwise specified)", "Frontotemporal Dementia",
    "Parkinson's Disease", "Schizophrenia", "Tauopathies", "Vascular Dementia",
]

CAPTION = (
    "Reproduced from Yang et al. (2026), Cell Genomics, Figure 3A-D.\n"
    "Reproduced by NYCU Yaen Tseng, ID:114101057 using Python (pandas, matplotlib, scipy), July 2026.\n"
    "PsychAD data: Zenodo DOI 10.5281/zenodo.17161565. ADRD reference: Matthews et al. (2019) "
    "and literature sources cited in Yang et al. (2026) Methods."
)


def panel_A(ax, df):
    d = df[df["ancestry"] != "Unknown"].copy()
    order = ["Other", "Latino", "Asian", "European", "African"]
    table = pd.crosstab(d["disease"], d["ancestry"], normalize="index") * 100
    table = table.reindex(columns=[c for c in order if c in table.columns], fill_value=0)
    disease_order = [d_ for d_ in DISEASE_ORDER if d_ in table.index]
    table = table.loc[disease_order]
    counts = d.groupby("disease").size()
    labels = [f"{t} (n={counts[t]})" for t in disease_order]

    table.plot(kind="bar", stacked=True, ax=ax,
               color=[ETHNICITY_COLORS[c] for c in table.columns])
    ax.set_xticklabels(labels, rotation=90)
    ax.set_ylabel("Proportion")
    ax.set_title("A   PsychAD: Diseases by Ancestry", loc="left", fontweight="bold")
    ax.set_xlabel("")
    ax.legend(title="Ancestry", bbox_to_anchor=(1.02, 1), loc="upper left")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))


def panel_B(ax, df, adrd_ancestry):
    d = df[(df["disease"] == "Alzheimer's Disease") & (df["ancestry"] != "Unknown")]
    n = len(d)
    observed_pct = d["ancestry"].value_counts(normalize=True) * 100

    categories = ["African", "Asian", "European", "Latino", "Other"]
    ref_pct = adrd_ancestry.set_index("ancestry")["pct_of_total"]

    x = np.arange(len(categories))
    width = 0.35
    ax.bar(x - width/2, [observed_pct.get(c, 0) for c in categories], width,
           label=f"PsychAD AD cases (n={n})", color="#d9534f")
    ax.bar(x + width/2, [ref_pct.get(c, 0) for c in categories], width,
           label="ADRD Reference (Matthews et al. 2019)", color="#5b9bd5")
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel("Percentage (%)")
    ax.set_title("B   PsychAD vs ADRD: Ancestry (Alzheimer's Disease)", loc="left", fontweight="bold")
    ax.legend(fontsize=8)


def panel_C(ax, df):
    d = df[df["sex"] != "Unknown"].copy()
    table = pd.crosstab(d["disease"], d["sex"], normalize="index") * 100
    table = table.reindex(columns=["male", "female"], fill_value=0)
    disease_order = [d_ for d_ in DISEASE_ORDER if d_ in table.index]
    table = table.loc[disease_order]
    counts = d.groupby("disease").size()
    labels = [f"{t} (n={counts[t]})" for t in disease_order]

    table.plot(kind="bar", stacked=True, ax=ax,
               color=[SEX_COLORS[c] for c in ["male", "female"]])
    ax.set_xticklabels(labels, rotation=90)
    ax.set_title("C   PsychAD: Diseases by Sex", loc="left", fontweight="bold")
    ax.set_xlabel("")
    ax.legend(title="Sex", bbox_to_anchor=(1.02, 1), loc="upper left")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))


def panel_D(ax, df, adrd_sex):
    d = df[df["sex"] != "Unknown"].copy()
    table = pd.crosstab(d["disease"], d["sex"], normalize="index") * 100
    table = table.reindex(columns=["male", "female"], fill_value=0)

    ref = adrd_sex.set_index("Disease")
    disease_order = [d_ for d_ in DISEASE_ORDER if d_ in ref.index and d_ in table.index]
    ref = ref.loc[disease_order]

    ref_plot = pd.DataFrame({
        "male": ref["male_pct"], "female": ref["female_pct"],
    }, index=disease_order)

    ref_plot.plot(kind="bar", stacked=True, ax=ax,
                   color=[SEX_COLORS[c] for c in ["male", "female"]])
    ax.set_xticklabels(disease_order, rotation=90)
    ax.set_title("D   ADRD Reference: Diseases by Sex", loc="left", fontweight="bold")
    ax.set_xlabel("Disease Type")
    ax.legend(title="Sex", bbox_to_anchor=(1.02, 1), loc="upper left")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))

    # Chi-square test: PsychAD observed sex counts vs ADRD reference proportions
    results = []
    for dis in disease_order:
        n = len(d[d["disease"] == dis])
        male_pct = ref.loc[dis, "male_pct"]
        female_pct = ref.loc[dis, "female_pct"]
        if n < 5 or male_pct == 0 or female_pct == 0:
            chi2, p = np.nan, np.nan
        else:
            observed = [
                (d[d["disease"] == dis]["sex"] == "male").sum(),
                (d[d["disease"] == dis]["sex"] == "female").sum(),
            ]
            expected = [n * male_pct / 100, n * female_pct / 100]
            chi2, p = chisquare(f_obs=observed, f_exp=expected)
        results.append({"disease": dis, "n": n,
                         "chi2": round(chi2, 2) if not np.isnan(chi2) else "N/A",
                         "p_value": f"{p:.2e}" if not np.isnan(p) else "N/A"})
    results_df = pd.DataFrame(results)
    print("=== PsychAD vs ADRD: Sex chi-square test per disease ===")
    print(results_df.to_string(index=False))
    results_df.to_csv("../outputs/psychad_vs_adrd_sex_chisq.csv", index=False)


if __name__ == "__main__":
    psychad = pd.read_csv(PSYCHAD_FILE)
    adrd_sex = pd.read_csv(ADRD_SEX_FILE)
    adrd_ancestry = pd.read_csv(ADRD_ANCESTRY_FILE)

    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    panel_A(axes[0, 0], psychad)
    panel_B(axes[0, 1], psychad, adrd_ancestry)
    panel_C(axes[1, 0], psychad)
    panel_D(axes[1, 1], psychad, adrd_sex)

    fig.suptitle("Figure 3. PsychAD ancestry and sex composition across "
                  "neuropsychiatric and neurodegenerative diagnoses (Reproduction)",
                  fontsize=13, y=1.02)
    plt.tight_layout()
    fig.text(0.5, -0.05, CAPTION, wrap=True, horizontalalignment="center",
              fontsize=8, style="italic", color="dimgray")
    plt.savefig("../figures/figure3_reproduction.png", dpi=150, bbox_inches="tight")
    print("\nSaved: ../figures/figure3_reproduction.png")