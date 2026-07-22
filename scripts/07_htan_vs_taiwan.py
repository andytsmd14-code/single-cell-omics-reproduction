"""
07_htan_vs_taiwan.py
----------------------
Compare the HTAN cohort's sex composition against Taiwan's national
cancer incidence sex ratios (2022), for the cancer types where both
datasets have matching categories. This is the "reanalysis" component:
substituting Taiwan Health Promotion Administration (HPA) data for the
original paper's SEER (US) reference, to test whether the paper's
finding of sex-representation skew is specific to the US population
context or holds against a different national reference.

Outputs:
  - taiwan_reference_clean_en.csv   (from 05_taiwan_reference.py)
  - htan_clean.csv                 (from 04_clean_htan.py)
  - figure_htan_vs_taiwan_sex.png
  - chi-square test results printed to console
"""

import pandas as pd
import numpy as np
from scipy.stats import chisquare
import matplotlib.pyplot as plt

HTAN_FILE = "../outputs/htan_clean.csv"
TAIWAN_FILE = "../outputs/taiwan_reference_clean_en.csv"

CAPTION_TEXT = (
    "HTAN sex composition vs. Taiwan HPA national cancer registry (2022),\n"
    "reanalysis substituting Taiwan reference for the original SEER (US) reference.\n"
    "Reproduced by [Your Name/Group] using Python (pandas, matplotlib, scipy), [Date].\n"
    "HTAN data: Zenodo DOI 10.5281/zenodo.17161565. Taiwan data: HPA Cancer Registry."
)


def add_caption(fig, text=CAPTION_TEXT):
    fig.text(0.5, -0.05, text, wrap=True, horizontalalignment="center",
              fontsize=7, style="italic", color="dimgray")


def main():
    htan = pd.read_csv(HTAN_FILE)
    taiwan = pd.read_csv(TAIWAN_FILE)

    cancer_types = taiwan["cancer_type"].unique().tolist()

    results = []
    for cancer_type in cancer_types:
        htan_subset = htan[
            (htan["cancer_type"] == cancer_type) & (htan["sex"] != "Unknown")
        ]
        n = len(htan_subset)
        if n == 0:
            continue

        htan_male_pct = (htan_subset["sex"] == "male").mean() * 100
        htan_female_pct = 100 - htan_male_pct

        tw_row = taiwan[taiwan["cancer_type"] == cancer_type]
        tw_male_rate = tw_row[tw_row["sex"] == "male"]["taiwan_age_std_rate_per_100k"].values[0]
        tw_female_rate = tw_row[tw_row["sex"] == "female"]["taiwan_age_std_rate_per_100k"].values[0]

        if tw_male_rate == 0 or tw_female_rate == 0:
            # Sex-specific cancer (e.g. Breast, Ovary, Cervix) -> not a
            # meaningful sex-ratio comparison, skip chi-square test
            tw_male_pct = np.nan
            tw_female_pct = np.nan
            chi2, p = np.nan, np.nan
        else:
            total_rate = tw_male_rate + tw_female_rate
            tw_male_pct = tw_male_rate / total_rate * 100
            tw_female_pct = tw_female_rate / total_rate * 100

            observed = [
                (htan_subset["sex"] == "male").sum(),
                (htan_subset["sex"] == "female").sum(),
            ]
            expected = [n * tw_male_pct / 100, n * tw_female_pct / 100]
            chi2, p = chisquare(f_obs=observed, f_exp=expected)

        results.append({
            "cancer_type": cancer_type,
            "n_htan": n,
            "htan_male_pct": round(htan_male_pct, 1),
            "htan_female_pct": round(htan_female_pct, 1),
            "taiwan_male_pct": round(tw_male_pct, 1) if not np.isnan(tw_male_pct) else "N/A (sex-specific cancer)",
            "taiwan_female_pct": round(tw_female_pct, 1) if not np.isnan(tw_female_pct) else "N/A (sex-specific cancer)",
            "chi2": round(chi2, 2) if not np.isnan(chi2) else "N/A",
            "p_value": f"{p:.2e}" if not np.isnan(p) else "N/A",
        })

    results_df = pd.DataFrame(results)
    print(results_df.to_string(index=False))
    results_df.to_csv("../outputs/htan_vs_taiwan_sex_comparison.csv", index=False)
    print("\nSaved: ../outputs/htan_vs_taiwan_sex_comparison.csv")

    # --- Plot: side-by-side comparison for cancers with both sexes present ---
    plot_df = results_df[results_df["taiwan_male_pct"] != "N/A (sex-specific cancer)"].copy()
    plot_df["taiwan_male_pct"] = plot_df["taiwan_male_pct"].astype(float)
    plot_df["htan_male_pct"] = plot_df["htan_male_pct"].astype(float)

    x = np.arange(len(plot_df))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width/2, plot_df["htan_male_pct"], width, label="HTAN (% male)", color="#7ec8e3")
    ax.bar(x + width/2, plot_df["taiwan_male_pct"], width, label="Taiwan HPA reference (% male)", color="#2f6f9f")
    ax.axhline(50, color="gray", linestyle="--", linewidth=1)
    ax.set_ylabel("Percent male (%)")
    ax.set_title("HTAN vs. Taiwan Cancer Registry: Sex Composition by Cancer Type")
    ax.set_xticks(x)
    ax.set_xticklabels(plot_df["cancer_type"], rotation=45, ha="right")
    ax.legend()
    plt.tight_layout()
    add_caption(fig)
    plt.savefig("../figures/figure_htan_vs_taiwan_sex.png", dpi=150, bbox_inches="tight")
    print("Saved: ../figures/figure_htan_vs_taiwan_sex.png")


if __name__ == "__main__":
    main()
