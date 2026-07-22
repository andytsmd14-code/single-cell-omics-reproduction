"""
09_htan_vs_seer.py
--------------------
The "real" reproduction of Figure 2A/2B (ancestry) and 2C/2D (sex):
compare the HTAN cohort against the actual SEER*Explorer 2018-2022
reference data (seer_ancestry_clean.csv, seer_sex_clean.csv), instead
of the earlier Taiwan substitution. This uses the true SEER incidence
rates converted to compositional shares, exactly matching the paper's
stated method: "For each cancer site, we converted rates to shares by
dividing each group's rate by the sum of rates across groups for that
site."
"""

import pandas as pd
import numpy as np
from scipy.stats import chisquare
import matplotlib.pyplot as plt

HTAN_FILE = "../outputs/htan_clean.csv"
SEER_ANCESTRY_FILE = "../outputs/seer_ancestry_clean.csv"
SEER_SEX_FILE = "../outputs/seer_sex_clean.csv"

ETHNICITY_COLORS = {
    "African": "#b0413e", "Latino": "#e08214", "Asian": "#4575b4",
    "European": "#762a83", "Other": "#f4c78b",
}
SEX_COLORS = {"male": "#7ec8e3", "female": "#c9971e"}

CAPTION_ANCESTRY = (
    "HTAN vs. SEER*Explorer 2018-2022 (actual reference data, Zenodo repository).\n"
    "Reproduction of Figure 2A/2B. By [Your Name/Group], Python (pandas, matplotlib, scipy), [Date]."
)
CAPTION_SEX = (
    "HTAN vs. SEER*Explorer 2018-2022 (actual reference data, Zenodo repository).\n"
    "Reproduction of Figure 2C/2D. By [Your Name/Group], Python (pandas, matplotlib, scipy), [Date]."
)


def add_caption(fig, text):
    fig.text(0.5, -0.05, text, wrap=True, horizontalalignment="center",
              fontsize=7, style="italic", color="dimgray")


def compositional_shares(rate_df, group_col):
    """Convert SEER rates to within-site shares (sum to 100% per cancer_type),
    matching the paper's compositional normalization method exactly."""
    pivot = rate_df.pivot(index="cancer_type", columns=group_col, values="seer_rate_per_100k")
    shares = pivot.div(pivot.sum(axis=1), axis=0) * 100
    return shares


def make_figure2(htan_ancestry_table, seer_ancestry_shares, ancestry_order,
                  htan_sex_table, seer_sex_shares, common_ancestry_types,
                  common_sex_types, ancestry_counts, sex_counts):
    """Build a single 2x2 figure matching the paper's Figure 2 layout exactly:
    A (top-left) = HTAN by ancestry, B (bottom-left) = SEER by ancestry,
    C (top-right) = HTAN by sex,      D (bottom-right) = SEER by sex."""

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    ax_A, ax_C = axes[0, 0], axes[0, 1]
    ax_B, ax_D = axes[1, 0], axes[1, 1]

    # --- Panel A: HTAN by ancestry ---
    htan_labels_a = [f"{t} (n={ancestry_counts[t]})" for t in common_ancestry_types]
    htan_ancestry_table.plot(kind="bar", stacked=True, ax=ax_A,
                              color=[ETHNICITY_COLORS[c] for c in ancestry_order])
    ax_A.set_xticklabels(htan_labels_a, rotation=90)
    ax_A.set_ylabel("Proportion")
    ax_A.set_title("A   HTAN: Cancer Types by Ancestry", loc="left", fontweight="bold")
    ax_A.set_xlabel("")
    ax_A.legend(title="Ancestry", bbox_to_anchor=(1.02, 1), loc="upper left")

    # --- Panel C: HTAN by sex ---
    htan_labels_c = [f"{t} (n={sex_counts[t]})" for t in common_sex_types]
    htan_sex_table.plot(kind="bar", stacked=True, ax=ax_C,
                         color=[SEX_COLORS[c] for c in ["male", "female"]])
    ax_C.set_xticklabels(htan_labels_c, rotation=90)
    ax_C.set_title("C   HTAN: Cancer Types by Sex", loc="left", fontweight="bold")
    ax_C.set_xlabel("")
    ax_C.legend(title="Sex", bbox_to_anchor=(1.02, 1), loc="upper left")

    # --- Panel B: SEER by ancestry ---
    seer_ancestry_shares.plot(kind="bar", stacked=True, ax=ax_B,
                               color=[ETHNICITY_COLORS[c] for c in ancestry_order])
    ax_B.set_xticklabels(common_ancestry_types, rotation=90)
    ax_B.set_ylabel("Proportion")
    ax_B.set_title("B   SEER Reference: Cancer Types by Ancestry", loc="left", fontweight="bold")
    ax_B.set_xlabel("Cancer Type")
    ax_B.legend(title="Ancestry", bbox_to_anchor=(1.02, 1), loc="upper left")

    # --- Panel D: SEER by sex ---
    seer_sex_shares.plot(kind="bar", stacked=True, ax=ax_D,
                          color=[SEX_COLORS[c] for c in ["male", "female"]])
    ax_D.set_xticklabels(common_sex_types, rotation=90)
    ax_D.set_title("D   SEER Reference: Cancer Types by Sex", loc="left", fontweight="bold")
    ax_D.set_xlabel("Cancer Type")
    ax_D.legend(title="Sex", bbox_to_anchor=(1.02, 1), loc="upper left")

    # Format y-axes as percentages, matching the paper style (0%, 25%, 50%...)
    for ax in [ax_A, ax_B, ax_C, ax_D]:
        ax.set_ylim(0, 100)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))

    fig.suptitle("Figure 2. Human Tumor Atlas Network ancestry and sex composition "
                  "across cancer types (Reproduction)", fontsize=13, y=1.02)
    plt.tight_layout()
    caption = (
        "Reproduced from Yang et al. (2026), Cell Genomics, Figure 2A-D.\n"
        "Reproduced by [Your Name/Group] using Python (pandas, matplotlib, scipy), [Date].\n"
        "HTAN data: Zenodo DOI 10.5281/zenodo.17161565. SEER reference: SEER*Explorer 2018-2022."
    )
    fig.text(0.5, -0.03, caption, wrap=True, horizontalalignment="center",
              fontsize=8, style="italic", color="dimgray")
    plt.savefig("../figures/figure2_reproduction.png", dpi=150, bbox_inches="tight")
    print("Saved: ../figures/figure2_reproduction.png")


def analyze_ancestry():
    htan = pd.read_csv(HTAN_FILE)
    seer = pd.read_csv(SEER_ANCESTRY_FILE)
    seer_shares = compositional_shares(seer, "ancestry")

    order = ["Other", "Latino", "Asian", "European", "African"]
    order = [c for c in order if c in seer_shares.columns]
    seer_shares = seer_shares[order]

    d = htan[htan["ethnicity"] != "Unknown"].copy()
    htan_table = pd.crosstab(d["cancer_type"], d["ethnicity"], normalize="index") * 100
    htan_table = htan_table.reindex(columns=order, fill_value=0)

    common_types = [c for c in seer_shares.index if c in htan_table.index]
    htan_table = htan_table.loc[common_types]
    seer_shares = seer_shares.loc[common_types]

    counts = d.groupby("cancer_type").size()

    # Chi-square test per cancer type
    results = []
    for cancer_type in common_types:
        n = counts[cancer_type]
        observed = [
            (d[d["cancer_type"] == cancer_type]["ethnicity"] == cat).sum()
            for cat in order
        ]
        expected = [n * seer_shares.loc[cancer_type, cat] / 100 for cat in order]
        if min(expected) <= 0 or n < 5:
            chi2, p = np.nan, np.nan
        else:
            chi2, p = chisquare(f_obs=observed, f_exp=expected)
        results.append({"cancer_type": cancer_type, "n": n,
                         "chi2": round(chi2, 2) if not np.isnan(chi2) else "N/A",
                         "p_value": f"{p:.2e}" if not np.isnan(p) else "N/A"})

    results_df = pd.DataFrame(results)
    print("=== HTAN vs SEER: Ancestry chi-square test per cancer type ===")
    print(results_df.to_string(index=False))
    results_df.to_csv("../outputs/htan_vs_seer_ancestry_chisq.csv", index=False)

    return htan_table, seer_shares, order, common_types, counts


def analyze_sex():
    htan = pd.read_csv(HTAN_FILE)
    seer = pd.read_csv(SEER_SEX_FILE)
    seer_pivot = seer.pivot(index="cancer_type", columns="sex", values="seer_rate_per_100k")
    seer_shares = seer_pivot.div(seer_pivot.sum(axis=1), axis=0) * 100
    seer_shares = seer_shares.reindex(columns=["male", "female"])

    d = htan[htan["sex"] != "Unknown"].copy()
    htan_table = pd.crosstab(d["cancer_type"], d["sex"], normalize="index") * 100
    htan_table = htan_table.reindex(columns=["male", "female"], fill_value=0)

    common_types = [c for c in seer_shares.index if c in htan_table.index]
    htan_table = htan_table.loc[common_types]
    seer_shares_plot = seer_shares.loc[common_types]

    counts = d.groupby("cancer_type").size()

    results = []
    for cancer_type in common_types:
        n = counts[cancer_type]
        male_share = seer_shares.loc[cancer_type, "male"] if not pd.isna(seer_shares.loc[cancer_type, "male"]) else None
        female_share = seer_shares.loc[cancer_type, "female"] if not pd.isna(seer_shares.loc[cancer_type, "female"]) else None
        if male_share is None or female_share is None or male_share == 0 or female_share == 0 or n < 5:
            chi2, p = np.nan, np.nan
        else:
            observed = [
                (d[d["cancer_type"] == cancer_type]["sex"] == "male").sum(),
                (d[d["cancer_type"] == cancer_type]["sex"] == "female").sum(),
            ]
            expected = [n * male_share / 100, n * female_share / 100]
            chi2, p = chisquare(f_obs=observed, f_exp=expected)
        results.append({"cancer_type": cancer_type, "n": n,
                         "chi2": round(chi2, 2) if not np.isnan(chi2) else "N/A",
                         "p_value": f"{p:.2e}" if not np.isnan(p) else "N/A"})

    results_df = pd.DataFrame(results)
    print("\n=== HTAN vs SEER: Sex chi-square test per cancer type ===")
    print(results_df.to_string(index=False))
    results_df.to_csv("../outputs/htan_vs_seer_sex_chisq.csv", index=False)

    return htan_table, seer_shares_plot, common_types, counts


if __name__ == "__main__":
    htan_a_table, seer_a_shares, a_order, a_types, a_counts = analyze_ancestry()
    htan_s_table, seer_s_shares, s_types, s_counts = analyze_sex()
    make_figure2(htan_a_table, seer_a_shares, a_order,
                 htan_s_table, seer_s_shares, a_types, s_types,
                 a_counts, s_counts)
