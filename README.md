# Reproducing and Reanalyzing "Are Different Populations Fairly Represented in Single-Cell Omic Atlases?"

Personal reproduction project based on:

> Yang, C., Saravanan, K., Saharan, A., & Huang, K.-L. (2026). Are different populations fairly represented in single-cell omic atlases? *Cell Genomics*. https://doi.org/10.1016/j.xgen.2026.101300

## What this project does

This repository reproduces the three main demographic-representation analyses
from the paper (HCA, HTAN, and PsychAD, each compared against its respective
reference population) using Python, and adds one reanalysis: substituting
Taiwan's national cancer registry data for the paper's original US SEER
reference in the HTAN sex-composition comparison.

## Data sources

- **HCA / HTAN / PsychAD curated metadata and reference datasets**: Zenodo, https://doi.org/10.5281/zenodo.17161565
- **Taiwan cancer incidence data**: data.gov.tw, dataset 6399, "Cancer Incidence Statistics by County, Sex, and Cancer Site, 1979–2022" (癌症發生統計-68-111年縣市別性別癌症別發生率資料), Health Promotion Administration, Ministry of Health and Welfare. https://data.gov.tw/dataset/6399
- **SEER reference data**: SEER*Explorer 2018-2022 (included in the Zenodo repository above)
- **ADRD reference data**: Matthews et al. (2019), *Alzheimer's & Dementia*, as curated in the Zenodo repository above

## How to run

Run scripts in numeric order (01-12). Each cleaning script's output CSV feeds
into the analysis/figure scripts that follow it.

```
pip install pandas openpyxl scipy matplotlib
```

### Part 1 — Human Cell Atlas (HCA), reproduces Figure 1

| Script | Input | Output |
|---|---|---|
| `01_clean_hca.py` | `HCA_scrnaseq_data_final.xlsx` | `hca_clean.csv` |
| `02_analysis_hca.py` | `hca_clean.csv` | `figure1B_reproduction.png` (ancestry vs global reference), `figure1D_reproduction.png` (sex vs global reference) |
| `03_tissue_stack_bar_hca.py` | `hca_clean.csv` | `figure1C_reproduction.png` (ancestry by tissue), `figure1E_reproduction.png` (sex by tissue) |

### Part 2 — Human Tumor Atlas Network (HTAN) vs SEER, reproduces Figure 2

| Script | Input | Output |
|---|---|---|
| `04_clean_htan.py` | `HTAN_Data_Final.xlsx` | `htan_clean.csv` |
| `08_clean_seer.py` | `SEER_combined_cancer_demographics.csv` | `seer_ancestry_clean.csv`, `seer_sex_clean.csv` |
| `09_htan_vs_seer.py` | `htan_clean.csv`, `seer_ancestry_clean.csv`, `seer_sex_clean.csv` | **`figure2_reproduction.png`** (4-panel A/B/C/D, the main reproduction of Figure 2) + chi-square test result CSVs |
| `06_htan_stacked_bars.py` *(optional, standalone)* | `htan_clean.csv` | `figure2A_htan_only.png`, `figure2C_htan_only.png` — HTAN-only panels without the SEER side; superseded by `09`, kept for quick reference |

### Part 3 — Reanalysis: HTAN vs Taiwan cancer registry (sex composition)

| Script | Input | Output |
|---|---|---|
| `05_taiwan_reference.py` | `taiwan_cancer_registry.csv` (Taiwan HPA cancer registry, dataset 6399 from data.gov.tw — rename the downloaded file to this) | `taiwan_reference_clean_en.csv` |
| `07_htan_vs_taiwan.py` | `htan_clean.csv`, `taiwan_reference_clean_en.csv` | `figure_htan_vs_taiwan_sex.png` + chi-square test CSV |

### Part 4 — PsychAD vs ADRD reference, reproduces Figure 3

| Script | Input | Output |
|---|---|---|
| `10_clean_psychad.py` | `psych-AD_media-1.csv` | `psychad_clean.csv` |
| `11_clean_adrd_reference.py` | `ADRD_disease_demographics_wide.csv` | `adrd_sex_reference_clean.csv`, `adrd_ancestry_reference_clean.csv` |
| `12_psychad_figures.py` | `psychad_clean.csv`, `adrd_sex_reference_clean.csv`, `adrd_ancestry_reference_clean.csv` | **`figure3_reproduction.png`** (4-panel A/B/C/D) + chi-square test CSV |

### Part 5 — Reproduction accuracy check (our values vs. paper's reported values)

| Script | Input | Output |
|---|---|---|
| `13_compare_with_paper.py` | `hca_clean.csv`, `htan_clean.csv`, `psychad_clean.csv` | `hca_vs_paper_comparison.csv`, `htan_vs_paper_comparison.csv`, `psychad_vs_paper_comparison.csv` |

This script checks specific percentages and sample sizes quoted in the paper's main text against our own reproduced values, and labels each as Exact / Close / Gap / Large gap. It requires Parts 1, 2, and 4 to have been run first (needs `hca_clean.csv`, `htan_clean.csv`, `psychad_clean.csv`).

### Suggested execution order (copy-paste)

```bash
# Part 1 — HCA
python 01_clean_hca.py
python 02_analysis_hca.py
python 03_tissue_stack_bar_hca.py

# Part 2 — HTAN vs SEER
python 04_clean_htan.py
python 08_clean_seer.py
python 09_htan_vs_seer.py
python 06_htan_stacked_bars.py    # optional

# Part 3 — HTAN vs Taiwan (reanalysis)
python 05_taiwan_reference.py
python 07_htan_vs_taiwan.py

# Part 4 — PsychAD vs ADRD
python 10_clean_psychad.py
python 11_clean_adrd_reference.py
python 12_psychad_figures.py

# Part 5 — Reproduction accuracy check (run after Parts 1, 2, and 4)
python 13_compare_with_paper.py
```

## Key findings from the reproduction

- HCA, HTAN, and PsychAD sample counts and demographic proportions were
  reproduced almost exactly from the raw data (see each script's console
  output for side-by-side comparisons with the numbers reported in the
  paper's text).
- Chi-square tests confirm the paper's core finding: European ancestry is
  significantly overrepresented across nearly all tissue types (HCA) and
  cancer types (HTAN) relative to reference populations. Sex composition
  also shows statistically significant deviations from reference
  proportions in several cases (e.g., HCA overall sex ratio vs. global
  reference, chi2 = 7.09, p = 0.0078), consistent with the paper's
  description of HCA sex ratios (34.0% female / 36.6% male / 29.4%
  unreported).
- Reanalysis with Taiwan's cancer registry as the reference population
  (instead of US SEER) changes which cancer types show statistically
  significant sex skew — e.g., liver cancer shows a much larger sex
  disparity against the Taiwan reference than against SEER, reflecting real
  differences in liver cancer risk factors between the two populations.
  This illustrates how the choice of reference population affects
  representation-gap conclusions.
- Taiwan's national cancer registry does not use the US-style ancestry/race
  categorization framework, so the ancestry-representation comparison could
  not be extended to the Taiwan context — a genuine methodological
  limitation of cross-national reproduction, not an error in either dataset.

## Known reproduction limitations

- **HCA ancestry classification**: our classification rules for ambiguous
  raw values (e.g., "Homo sapiens", "Not provided") were implemented from
  the paper's written Methods description and may not exactly match the
  original authors' internal classification logic, producing small
  (~2 percentage point) differences in the "Other" and "Unknown"
  categories.
- **PsychAD ADRD ancestry reference (Figure 3B)**: we reproduced the raw
  case counts from the Zenodo-hosted reference file exactly, but computing
  composition percentages from those counts (case count ÷ total) yields
  81.3% European, versus 59.1% reported in the paper's text. Cross-checking
  the original source (Matthews et al., 2019) shows that publication
  reports ADRD **prevalence rates within each ancestry group** (e.g., 11.3%
  of white Medicare beneficiaries have ADRD), which is a different
  statistic from the ancestry **composition** of the ADRD-affected
  population. Converting between the two requires 2014 US
  population-by-race data (65+ age group) as an additional weighting step;
  this data is not included in the Zenodo repository, and could not be
  obtained in time via the U.S. Census Bureau API (which requires a
  personal API key to query). This is documented as an open reproduction
  gap rather than resolved.
- **HTAN Skin cancer sample count**: our reproduction finds only 44 records
  tagged "Skin" in the raw `Tissue Site` column of the Zenodo-hosted
  `HTAN_Data_Final.xlsx`, versus 79 reported in the paper's text, with no
  alternative labels (e.g., "Melanoma") accounting for the remaining
  records. This may reflect a dataset version difference between what we
  downloaded and what the original authors analyzed.
- **HTAN Blood Tumors ancestry composition**: our computed African ancestry
  share for the paper-defined "Blood Tumors" category (13.8%) differs
  substantially from the paper's reported 27.3%. Since Blood Tumors is a
  merge of several raw hematologic malignancy labels (per the paper's
  Methods), our merge rule may not exactly replicate which raw categories
  the original authors included.
- A full, automated comparison of every value above against the paper's
  quoted numbers is available in `13_compare_with_paper.py` and its output
  CSVs (`hca_vs_paper_comparison.csv`, `htan_vs_paper_comparison.csv`,
  `psychad_vs_paper_comparison.csv`).

## Additional materials

- **`overview.ipynb`** — a narrative walkthrough of all four parts, with
  every figure embedded inline alongside plain-language explanations and
  the statistical results tables. Renders directly on GitHub.
- **`statistical_tables.docx`** — a Word document compiling all chi-square
  test results and paper-comparison tables, formatted for direct use in a
  written report.

## Repository structure

```
scripts/                 01-13 analysis scripts, run in numeric order (see above)
data/                     raw input datasets (HCA, HTAN, SEER, Taiwan, PsychAD, ADRD)
outputs/                  cleaned intermediate datasets, reference tables, chi-square
                          results, and paper-comparison CSVs produced by the scripts
figures/                  reproduced figures (.png)
overview.ipynb            narrative overview with embedded figures and tables
statistical_tables.docx    all results tables, formatted for a written report
```

## Author's note

This is an independent reproduction exercise, not an official submission or
critique of the original paper. Any discrepancies noted above reflect the
inherent difficulty of exactly reproducing a published analysis from a
written Methods section, not an assessment of the original work's quality.
