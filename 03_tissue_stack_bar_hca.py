"""
03_tissue_stack_bar_hca.py
------------------------------
Reproduces the paper's Figure 1C (ancestry by tissue type) and Figure 1E
(sex by tissue type) -- stacked bar charts showing the composition of each
of the 15 HCA tissue categories.
"""

import pandas as pd
import matplotlib.pyplot as plt

CLEAN_FILE = "hca_clean.csv"

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
    "Reproduced from Yang et al. (2026), Cell Genomics, Figure 1C/1E.\n"
    "Reproduced by [Your Name/Group] using Python (pandas, matplotlib), [Date].\n"
    "Original data: Zenodo DOI 10.5281/zenodo.17161565."
)


def add_caption(fig, text=CAPTION_TEXT):
    fig.text(0.5, -0.02, text, wrap=True, horizontalalignment="center",
              fontsize=7, style="italic", color="dimgray")


def plot_ancestry_by_tissue(df):
    d = df[df["ethnicity"] != "Unknown"].copy()

    table = pd.crosstab(d["tissue"], d["ethnicity"], normalize="index") * 100

    order = ["Other", "Latino", "Asian", "European", "African"]
    order = [c for c in order if c in table.columns]
    table = table[order]

    counts = d.groupby("tissue").size()
    labels = [f"{t} (n={counts[t]})" for t in table.index]

    fig, ax = plt.subplots(figsize=(12, 6))
    table.plot(kind="bar", stacked=True, ax=ax,
               color=[ETHNICITY_COLORS[c] for c in order])
    ax.set_xticklabels(labels, rotation=90)
    ax.set_ylabel("Proportion (%)")
    ax.set_title("C   HCA: Tissue Types by Ancestry", loc="left", fontweight="bold")
    ax.legend(title="Ancestry", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    add_caption(fig)
    plt.savefig("figure1C_reproduction.png", dpi=150, bbox_inches="tight")
    print("Saved: figure1C_reproduction.png")


def plot_sex_by_tissue(df):
    d = df[df["sex"] != "Unknown"].copy()

    table = pd.crosstab(d["tissue"], d["sex"], normalize="index") * 100
    order = ["male", "female"]
    order = [c for c in order if c in table.columns]
    table = table[order]

    counts = d.groupby("tissue").size()
    labels = [f"{t} (n={counts[t]})" for t in table.index]

    fig, ax = plt.subplots(figsize=(12, 6))
    table.plot(kind="bar", stacked=True, ax=ax,
               color=[SEX_COLORS[c] for c in order])
    ax.set_xticklabels(labels, rotation=90)
    ax.set_ylabel("Proportion (%)")
    ax.set_title("E   HCA: Tissue Types by Sex", loc="left", fontweight="bold")
    ax.legend(title="Sex", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    add_caption(fig)
    plt.savefig("figure1E_reproduction.png", dpi=150, bbox_inches="tight")
    print("Saved: figure1E_reproduction.png")


if __name__ == "__main__":
    df = pd.read_csv(CLEAN_FILE)
    plot_ancestry_by_tissue(df)
    plot_sex_by_tissue(df)