---
Title: NHDES Cold Water Wadeable Stream Modeling
Authors: Sam Harris, Alec Rydeen
---

![Project Stage](https://img.shields.io/badge/stage-prototyping-orange)
![Models](https://img.shields.io/badge/models-logistic%20regression%20%7C%20xgboost-blue)
![Audience](https://img.shields.io/badge/audience-agency%20scientists%20%26%20collaborators-green)
![Domain](https://img.shields.io/badge/domain-cold%20water%20stream%20classification-2b7a78)

<img src="./docs/static/nhdes-logo.png" alt="NHDES Logo" width="210" />
<img src="./docs/static/unh_logo-transparent.png" alt="UNH Logo" width="190" />

# NHDES Cold Water Wadeable Stream Modeling

## Project Narrative
This project develops a reproducible classification workflow for identifying cold-water, wadeable streams (1st through 4th order) in New Hampshire. The effort builds from the 2007 NHDES logistic regression study and evaluates whether updated preprocessing and model selection can improve predictive performance while preserving scientific interpretability.

The intended audience is agency scientists and future collaborators who need to understand procedure, assumptions, and outcomes well enough to reuse and extend the workflow.

## Current Status
- Maturity: model prototyping and development.
- Two model notebooks are active: `src/lr_main.ipynb` (logistic regression) and `src/xg_main.ipynb` (XGBoost).
- Both models are implemented and cross-validated across five development-threshold datasets.
- Final outputs of models with best threshold and train/test split are in `src/outputs`. This include logistic regression equations and the sites included in each train/test split. 

## Research Questions
1. Can the original 2007 cold-water stream classification framework be reproduced with current data preparation steps?
2. Can predictive performance improve while maintaining clear interpretability for agency use?
3. Should the original species-count threshold (at least 30 SS/EBT) be retained, relaxed, or replaced based on cross-validated performance?
4. How sensitive are model outcomes to watershed area source and land disturbance threshold definitions?

## Reproducibility Quickstart

### 1) Environment setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

### 2) Data preparation
```powershell
jupyter notebook src/data_prep.ipynb
```

Run all cells in order. This notebook:
- Reads raw electrofishing records from `data/20260316_Fish_Data.xlsx`
- Derives watershed areas from NHDES shapefiles
- Extracts % developed land cover per site from NLCD rasters
- Builds `data/site_species_presence.csv` (577 sites × 51 species, binary presence/absence)
- Builds `data/site_species_presence_combined.csv` (locations with multiple visits merged into one row)
- Removes sites with no watershed area and produces diagnostic plots

Both output CSVs are required before running the model notebooks.

### 3) Logistic regression model
```powershell
jupyter notebook src/lr_main.ipynb
```

**Cells 1–2** load and filter the data by development threshold — run these first and leave them as-is.

**Optional — cells 3–4** run a cross-validation sweep across train/test split ratios for each threshold. These are slow; skip them if you just want to train a model.

**Last cell** trains a single logistic regression and saves a JSON report to `src/output/`. Adjust two flags at the top of that cell before running:

| Flag | Description | Example values |
|---|---|---|
| `THRESHOLD` | Maximum % developed land cover to include (`pct_dev`) | `3`, `5`, `7`, `10`, `15` |
| `TEST_SPLIT` | Fraction of observations held out for evaluation | `0.10`, `0.15`, `0.20`, `0.25`, `0.30` |

Output is saved to `src/output/lr_pct{THRESHOLD}_split{TEST_SPLIT*100}.json`.

### 4) XGBoost model
```powershell
jupyter notebook src/xg_main.ipynb
```

Identical workflow to `lr_main.ipynb`. **Cells 1–2** load and filter data. The **last cell** trains and evaluates an XGBoost classifier with the same two flags:

| Flag | Description | Example values |
|---|---|---|
| `THRESHOLD` | Maximum % developed land cover to include | `3`, `5`, `7`, `10`, `15` |
| `TEST_SPLIT` | Fraction held out for evaluation | `0.10`, `0.15`, `0.20`, `0.25`, `0.30` |

Output is saved to `src/output/xgb_pct{THRESHOLD}_split{TEST_SPLIT*100}.json`.

**Recommended starting point:** `THRESHOLD = 7`, `TEST_SPLIT = 0.20` — both models show strong AUC near these values without excessive class imbalance.

## Data Sources and Processing Logic

### NHDES EMD assemblage records
Primary electro-fishing fields used include:
- EMD station ID
- Collection date
- Stream order
- Latitude and longitude
- Fish species
- Number of fish collected

Original 2007 filter assumptions:
- 1st through 4th order streams only
- Valid latitude and longitude
- Focus on slimy sculpin (SS) and eastern brook trout (EBT)
- At least 30 SS and/or EBT observations

Current prototyping decisions under evaluation:
- Include strict warm-water specialists to increase useful contrast in labels
- Use cross validation to test whether sites with fewer than 30 SS/EBT can be retained
- Review ecological implications of potential deep-hole thermal refugia for wadeable stream interpretation

### Drainage area derivation
Two methods are being compared:
1. USGS NHD API using known COMID
2. NHDES watershed shapefiles with geospatial area calculation

Preliminary comparison indicates mean difference near 0.8 square miles between methods. Final selection criterion is still under evaluation.

### NLCD disturbance screening
The 2007 study excluded sites with significant human disturbance. This project re-estimates disturbance thresholds using NLCD by sampling year and evaluates threshold sensitivity with cross validation.

## Repository Map

```text
nhdes-cw-stream-modeling/
|-- README.md
|-- requirements.txt
|-- docs/
|   |-- Initial_Mtg.md
|   `-- static/
`-- src/
    |-- data_prep.ipynb          ← run first: builds all data CSVs
    |-- lr_main.ipynb            ← logistic regression training and evaluation
    |-- xg_main.ipynb            ← XGBoost training and evaluation
    |-- data/
    |   |-- site_species_presence.csv          (generated by data_prep)
    |   |-- site_species_presence_combined.csv (generated by data_prep)
    |   |-- watersheds_with_area_based-on-shp.csv
    |   |-- 20260316_Fish_Data.xlsx
    |   |-- Shapefiles/
    |   `-- NLCD tiffs/
    |-- output/                  ← JSON model reports written here
    `-- utils/
        |-- confusion.py
        `-- drainage.py
```

## Where To Start
- Data preparation: `src/data_prep.ipynb`
- Logistic regression: `src/lr_main.ipynb`
- XGBoost: `src/xg_main.ipynb`
- Drainage API and watershed logic: `src/utils/drainage.py`
- Confusion matrix and classification metrics: `src/utils/confusion.py`
- **Model outputs (parameters + train/test sites) for final Log Reg and XGBoost models:** `src/output`

