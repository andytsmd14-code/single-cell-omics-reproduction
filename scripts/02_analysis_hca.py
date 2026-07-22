"""
02_analysis_hca.py
----------------------
Reproduces the official paper's Figure 1B (ancestry vs global reference) and
Figure 1D (sex vs global reference) -- both are grouped bar charts comparing
the HCA dataset's observed proportions against reference population baselines.

Also runs a chi-square goodness-of-fit test and computes representation
ratios (observed / expected), matching the paper's Methods description.
"""

import pandas as pd
from scipy.stats import chisquare
import matplotlib.pyplot as plt
import numpy as np

CLEAN_FILE = "../outputs/hca_clean.csv"

# Global ancestry reference cited in the paper's main text (UN 2021 continent shares)
GLOBAL_ANCESTRY_REF = {
    "European": 9.4,
    "Asian": 59.4,
    "African": 17.6,
    "Latino": 13.6,
}

# Global sex reference cited in the paper's Methods (UN WPP 2022)
GLOBAL_SEX_REF = {
    "male": 50.3,
    "female": 49.7,
}

CAPTION_TEXT = (
    "Reproduced from Yang et al. (2026), Cell Genomics, Figure 1B/1D.\n"
    "Reproduced by [Your Name/Group] using Python (pandas, matplotlib, scipy), [Date].\n"
    "Original data: Zenodo DOI 10.5281/zenodo.17161565."
)


def add_caption(fig, text=CAPTION_TEXT):
    fig.text(0.5, -0.05, text, wrap=True, horizontalalignment="center",
              fontsize=7, style="italic", color="dimgray")


def analyze_ancestry(df):
    non_missing = df[df["ethnicity"] != "Unknown"].copy()
    non_missing = non_missing[non_missing["ethnicity"].isin(GLOBAL_ANCESTRY_REF.keys())]

    observed_counts = non_missing["ethnicity"].value_counts().reindex(GLOBAL_ANCESTRY_REF.keys())
    n = observed_counts.sum()

    observed_pct = observed_counts / n * 100
    expected_pct = pd.Series(GLOBAL_ANCESTRY_REF)

    ratio = observed_pct / expected_pct
    print("=== Ancestry representation ratio (observed / expected) ===")
    print(ratio.round(2))
    print("(paper reports: European ~6x over, Asian 0.36x, African 0.59x, Latino 0.45x)\n")

    expected_counts = expected_pct / 100 * n
    chi2, p = chisquare(f_obs=observed_counts, f_exp=expected_counts)
    print(f"=== Ancestry chi-square goodness-of-fit test ===")
    print(f"chi2 = {chi2:.2f}, p = {p:.3e}")
    print("(paper reports p < 2e-16)\n")

    categories = list(GLOBAL_ANCESTRY_REF.keys())
    x = np.arange(len(categories))
    width = 0.35

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(x - width/2, observed_pct[categories], width, label="HCA Dataset", color="#d9534f")
    ax.bar(x + width/2, expected_pct[categories], width, label="Global Reference", color="#5b9bd5")

    ax.set_ylabel("Percentage (%)")
    ax.set_title("B   HCA: Ancestry Distribution vs Global Reference", loc="left", fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend()
    plt.tight_layout()
    add_caption(fig)
    plt.savefig("../figures/figure1B_reproduction.png", dpi=150, bbox_inches="tight")
    print("Saved: ../figures/figure1B_reproduction.png")


def analyze_sex(df):
    non_missing = df[df["sex"] != "Unknown"].copy()

    observed_counts = non_missing["sex"].value_counts().reindex(GLOBAL_SEX_REF.keys())
    n = observed_counts.sum()

    observed_pct = observed_counts / n * 100
    expected_pct = pd.Series(GLOBAL_SEX_REF)

    expected_counts = expected_pct / 100 * n
    chi2, p = chisquare(f_obs=observed_counts, f_exp=expected_counts)
    print(f"=== Sex chi-square goodness-of-fit test ===")
    print(f"chi2 = {chi2:.2f}, p = {p:.3e}\n")

    categories = list(GLOBAL_SEX_REF.keys())
    x = np.arange(len(categories))
    width = 0.35

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.bar(x - width/2, observed_pct[categories], width, label="HCA Dataset", color="#d9534f")
    ax.bar(x + width/2, expected_pct[categories], width, label="Global Reference", color="#5b9bd5")

    ax.set_ylabel("Percentage (%)")
    ax.set_title("D   HCA: Sex Distribution vs Global Reference", loc="left", fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend()
    plt.tight_layout()
    add_caption(fig)
    plt.savefig("../figures/figure1D_reproduction.png", dpi=150, bbox_inches="tight")
    print("Saved: ../figures/figure1D_reproduction.png")


if __name__ == "__main__":
    df = pd.read_csv(CLEAN_FILE)
    analyze_ancestry(df)
    analyze_sex(df)
