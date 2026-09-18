# Patient Adherence & Market Access Analytics

A pharma decision-analytics project analyzing medication adherence patterns across a synthetic 5,000-patient claims dataset — built to demonstrate the analytical stack used in pharma/life-sciences consulting: statistical modeling, cross-language validation, and client-facing interactive dashboards.

**Live Demos:**
- 📊 Streamlit Dashboard: [patient-adherence-analytics-xxxxx.streamlit.app](#)
- 📈 Tableau Public Dashboard: [public.tableau.com/app/profile/dhayal.ramesh/viz/PatientAdherenceAnalytics](https://public.tableau.com/app/profile/dhayal.ramesh/viz/PatientAdherenceAnalytics/PatientAdherenceMarketAccessAnalytics?publish=yes)

---

## Overview

Patient medication adherence — whether people actually take prescribed drugs as directed — is a core problem in pharma commercial analytics. Non-adherence drives poor health outcomes and lost revenue, and identifying *which patients are at risk and why* is a standard decision-analytics deliverable for pharma clients.

This project simulates that workflow end-to-end:
1. Generate a realistic synthetic patient claims dataset
2. Model the drivers of non-adherence using logistic regression
3. Validate the model across two languages (Python and R)
4. Segment patients into risk cohorts by region
5. Deliver findings through two interactive dashboards (Streamlit and Tableau Public)

## Dataset

Synthetic dataset of **5,000 patients** across 250 prescribers in 5 US regions, on 4 chronic-therapy drug classes (Statins, Antihypertensives, Antidiabetics, Anticoagulants). Adherence is measured using **PDC (Proportion of Days Covered)** — the industry-standard adherence metric — with the standard **0.80 threshold** for classifying non-adherence.

Patient-level fields:
- Demographics: age, region
- Clinical: drug class, number of comorbidities
- Behavioral/access: copay tier, mail-order pharmacy use, new-to-therapy status
- Outcome: PDC, binary non-adherent flag

Note: this is a synthetic dataset built for portfolio purposes, not real patient data. Effect sizes were designed to reflect realistic, published patterns in adherence research (e.g., higher copay and new-to-therapy status increasing non-adherence risk; mail-order use decreasing it).

## Methodology

**Logistic regression** models non-adherence as a function of age, copay tier, mail-order use, comorbidity count, and new-to-therapy status. The model was built independently in **Python (statsmodels)** and **R (glm)** using the identical formula, then cross-checked — odds ratios matched within rounding error across both implementations, confirming the result isn't an artifact of one tool's defaults.

**Key findings:**
| Factor | Odds Ratio | Effect |
|---|---|---|
| High copay tier | 13.8x | Strongest risk factor |
| New to therapy | 7.2x | Second strongest risk factor |
| Comorbidities (per unit) | 1.7x | Moderate risk factor |
| Mail-order pharmacy | 0.24x | Strongest protective factor (~76% odds reduction) |

**Risk cohorting:** Patients are scored into Low/Medium/High risk tiers based on copay tier, therapy status, comorbidity count, and mail-order use, then aggregated by region — surfacing priority segments (e.g., West region High Risk cohort: 99.3% non-adherent, avg. PDC 44.3%).

## Repository Structure

```
patient-adherence-analytics/
├── app.py                          # Streamlit dashboard
├── requirements.txt                # Python dependencies for Streamlit Cloud
├── data/
│   ├── patient_adherence.csv       # Full patient-level dataset (Python-generated)
│   ├── cohort_summary.csv          # Region x risk-cohort aggregates
│   └── logistic_regression_odds_ratios.csv
├── notebooks/
│   └── 01_data_and_model.ipynb     # Python: data generation, EDA, logistic regression
└── r/
    ├── 02_r_analysis.ipynb         # R: parallel model, cross-validated against Python
    ├── logistic_regression_odds_ratios_R.csv
    ├── cohort_summary_R.csv
    └── adherence_eda_R.png
```

## Tech Stack

- **Python**: pandas, statsmodels, matplotlib, seaborn (modeling & EDA)
- **R**: dplyr, ggplot2, broom (parallel modeling & validation)
- **Streamlit + Plotly**: interactive web dashboard, deployed on Streamlit Community Cloud
- **Tableau Public**: interactive BI dashboard with regional filtering and drill-down

## Dashboards

Both dashboards present the same underlying analysis through different tools, reflecting how the same insight might be delivered depending on a client's existing BI stack:

- **Streamlit**: full interactivity with live filtering (region, drug class, copay tier), 4-tab layout (Overview, Regional Cohorts, Model Drivers, Patient Explorer), and an odds-ratio forest plot.
- **Tableau Public**: region/copay/drug-class bar charts with a stacked risk-cohort view by region, built using standard Tableau aggregation and color-encoding techniques.

## Running Locally

**Streamlit app:**
```bash
git clone https://github.com/Dhayalramesh/patient-adherence-analytics.git
cd patient-adherence-analytics
pip install -r requirements.txt
streamlit run app.py
```

**Notebooks:** Open `notebooks/01_data_and_model.ipynb` or `r/02_r_analysis.ipynb` in Google Colab (Python and R runtimes respectively) and run all cells. The Python notebook generates the source dataset used by every other component.

## Author

**Dhayal R** — [GitHub](https://github.com/Dhayalramesh) | [LinkedIn](https://linkedin.com/in/dhayalsr)
