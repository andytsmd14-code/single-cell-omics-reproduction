"""
06_htan_stacked_bars.py
-------------------------
Standalone HTAN-only stacked bar charts: ancestry by cancer type and sex
by cancer type. Same logic as 03_tissue_stack_bar_hca.py, but grouped by
cancer_type instead of tissue, using htan_clean.csv as input.

NOTE: this script only plots the HTAN side (no SEER reference comparison).
It is superseded by 09_htan_vs_seer.py, which reproduces the full
four-panel Figure 2 (HTAN vs SEER, for both ancestry and sex) with
chi-square tests. This script is kept for reference / quick single-sided
plots only.
"""

import pandas as pd
import matplotlib.pyplot as plt

CLEAN_FILE = "../outputs/htan_clean.csv"

ETHNICITY_COLORS = {
    "African": "#b0413e",
    "Latino": "#e08214",
    "Asian": "#4575b4",
    "European": "#762a83",
    "Other": "#f4c78b",
}
SEX_COLORS = {
    "male": "#7ec8e3",
    "female": "#c9971e",
}

CAPTION_TEXT = (
    "Reproduced from Yang et al. (2026), Cell Genomics, Figure 2A/2C (HTAN side only).\n"
    "Reproduced by NYCU Yaen Tseng, ID:114101057 using Python (pandas, matplotlib), July 2026.\n"
    "Original data: Zenodo DOI 10.5281/zenodo.17161565."
)


def add_caption(fig, text=CAPTION_TEXT):
    fig.text(0.5, -0.02, text, wrap=True, horizontalalignment="center",
              fontsize=7, style="italic", color="dimgray")


def plot_ancestry_by_cancer(df):
    d = df[df["ethnicity"] != "Unknown"].copy()

    table = pd.crosstab(d["cancer_type"], d["ethnicity"], normalize="index") * 100
    order = ["Other", "Latino", "Asian", "European", "African"]
    order = [c for c in order if c in table.columns]
    table = table[order]

    # Keep only cancer types with enough samples to avoid an overcrowded chart
    # (the paper's Figure 2 also focuses on 11 major cancer categories)
    counts = d.groupby("cancer_type").size()
    keep = counts[counts >= 10].index  # require at least 10 samples, similar to the paper's approach
    table = table.loc[table.index.isin(keep)]
    counts = counts[keep]

    labels = [f"{t} (n={counts[t]})" for t in table.index]

    fig, ax = plt.subplots(figsize=(12, 6))
    table.plot(kind="bar", stacked=True, ax=ax, color=[ETHNICITY_COLORS[c] for c in order])
    ax.set_xticklabels(labels, rotation=90)
    ax.set_ylabel("Proportion (%)")
    ax.set_title("A   HTAN: Cancer Types by Ancestry", loc="left", fontweight="bold")
    ax.legend(title="Ancestry", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    add_caption(fig)
    plt.savefig("../figures/figure2A_htan_only.png", dpi=150, bbox_inches="tight")
    print("Saved: ../figures/figure2A_htan_only.png")


def plot_sex_by_cancer(df):
    d = df[df["sex"] != "Unknown"].copy()

    table = pd.crosstab(d["cancer_type"], d["sex"], normalize="index") * 100
    order = ["male", "female"]
    order = [c for c in order if c in table.columns]
    table = table[order]

    counts = d.groupby("cancer_type").size()
    keep = counts[counts >= 10].index
    table = table.loc[table.index.isin(keep)]
    counts = counts[keep]

    labels = [f"{t} (n={counts[t]})" for t in table.index]

    fig, ax = plt.subplots(figsize=(12, 6))
    table.plot(kind="bar", stacked=True, ax=ax, color=[SEX_COLORS[c] for c in order])
    ax.set_xticklabels(labels, rotation=90)
    ax.set_ylabel("Proportion (%)")
    ax.set_title("C   HTAN: Cancer Types by Sex", loc="left", fontweight="bold")
    ax.legend(title="Sex", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    add_caption(fig)
    plt.savefig("../figures/figure2C_htan_only.png", dpi=150, bbox_inches="tight")
    print("Saved: ../figures/figure2C_htan_only.png")


if __name__ == "__main__":
    df = pd.read_csv(CLEAN_FILE)
    plot_ancestry_by_cancer(df)
    plot_sex_by_cancer(df)