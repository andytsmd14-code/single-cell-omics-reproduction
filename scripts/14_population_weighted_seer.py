"""
14_population_weighted_seer.py
---------------------------------
SENSITIVITY ANALYSIS (not a replacement for 09_htan_vs_seer.py).

The paper's method for converting SEER incidence rates to ancestry
"shares" (compositional_shares() in 09_htan_vs_seer.py) divides each
group's rate by the sum of rates across groups. This implicitly assumes
each ancestry group has roughly equal population size in the US -- which
is not true (non-Hispanic White Americans are ~57.8% of the US
population per the 2020 Census, far more than any other single group).

This script re-does the ancestry share calculation WITH population
weighting (share = rate x population_pct, normalized per cancer type),
and re-runs the chi-square tests, to see whether accounting for real
population sizes changes which cancer types are flagged as
significantly different from the SEER reference.

Population weights source: U.S. Census Bureau, 2020 Decennial Census
(Non-Hispanic White, Non-Hispanic Black, Hispanic any race, Asian/API,
and AIAN+multiracial as "Other"), as compiled by the Economic Policy
Institute's racial/ethnic disparities chartbook. See
../data/us_population_by_race_2020.csv for the full citation per group.
"""

import pandas as pd
import numpy as np
from scipy.stats import chisquare

SEER_ANCESTRY_FILE = "../outputs/seer_ancestry_clean.csv"
HTAN_FILE = "../outputs/htan_clean.csv"
POPULATION_FILE = "../data/us_population_by_race_2020.csv"


def load_population_weights():
    """Load US population share by ancestry group from the source CSV
    (see the file itself for citation: U.S. Census Bureau, 2020 Decennial Census)."""
    pop_df = pd.read_csv(POPULATION_FILE)
    return dict(zip(pop_df["ancestry"], pop_df["population_pct"]))


def unweighted_shares(pivot):
    """The paper's original method: assumes equal population per group."""
    return pivot.div(pivot.sum(axis=1), axis=0) * 100


def population_weighted_shares(pivot, population_weights):
    """Alternative method: weight each group's rate by its actual US
    population share before normalizing, so shares approximate real
    case-count proportions rather than assuming equal population size."""
    weighted = pivot.copy()
    for ancestry in pivot.columns:
        weighted[ancestry] = pivot[ancestry] * population_weights.get(ancestry, np.nan)
    return weighted.div(weighted.sum(axis=1), axis=0) * 100


def main():
    seer = pd.read_csv(SEER_ANCESTRY_FILE)
    htan = pd.read_csv(HTAN_FILE)
    population_weights = load_population_weights()

    pivot = seer.pivot(index="cancer_type", columns="ancestry", values="seer_rate_per_100k")

    unweighted = unweighted_shares(pivot)
    weighted = population_weighted_shares(pivot, population_weights)

    print("=== Comparison: unweighted vs. population-weighted European share (%) ===")
    comparison = pd.DataFrame({
        "unweighted_European_pct": unweighted["European"].round(1),
        "weighted_European_pct": weighted["European"].round(1),
        "difference": (weighted["European"] - unweighted["European"]).round(1),
    })
    print(comparison.to_string())
    comparison.to_csv("../outputs/seer_weighted_vs_unweighted_european.csv")
    print()

    # --- Re-run chi-square tests using population-weighted expected shares ---
    d = htan[htan["ethnicity"] != "Unknown"].copy()
    order = ["Other", "Latino", "Asian", "European", "African"]

    results = []
    for cancer_type in weighted.index:
        htan_subset = d[d["cancer_type"] == cancer_type]
        n = len(htan_subset)
        if n < 5:
            continue

        observed = [(htan_subset["ethnicity"] == cat).sum() for cat in order]
        expected_weighted = [n * weighted.loc[cancer_type, cat] / 100 for cat in order]
        expected_unweighted = [n * unweighted.loc[cancer_type, cat] / 100 for cat in order]

        if min(expected_weighted) <= 0:
            continue

        chi2_w, p_w = chisquare(f_obs=observed, f_exp=expected_weighted)
        chi2_u, p_u = chisquare(f_obs=observed, f_exp=expected_unweighted)

        results.append({
            "cancer_type": cancer_type,
            "n": n,
            "chi2_unweighted": round(chi2_u, 2),
            "p_unweighted": f"{p_u:.2e}",
            "chi2_weighted": round(chi2_w, 2),
            "p_weighted": f"{p_w:.2e}",
            "significant_unweighted": p_u < 0.05,
            "significant_weighted": p_w < 0.05,
        })

    results_df = pd.DataFrame(results)
    print("=== Chi-square test: unweighted vs. population-weighted expected shares ===")
    print(results_df.to_string(index=False))
    results_df.to_csv("../outputs/htan_vs_seer_weighted_chisq_comparison.csv", index=False)
    print("\nSaved: ../outputs/htan_vs_seer_weighted_chisq_comparison.csv")

    n_changed = (results_df["significant_unweighted"] != results_df["significant_weighted"]).sum()
    print(f"\nCancer types where significance verdict CHANGED after weighting: {n_changed} / {len(results_df)}")


if __name__ == "__main__":
    main()
