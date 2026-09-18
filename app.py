import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Patient Adherence & Market Access Analytics",
    page_icon="💊",
    layout="wide"
)

# ---------- Data loading ----------
@st.cache_data
def load_data():
    df = pd.read_csv("data/patient_adherence.csv")
    cohort = pd.read_csv("data/cohort_summary.csv")
    odds = pd.read_csv("data/logistic_regression_odds_ratios.csv")
    odds = odds.rename(columns={odds.columns[0]: "term"})
    return df, cohort, odds

df, cohort, odds = load_data()

# ---------- Header ----------
st.title("💊 Patient Adherence & Market Access Analytics")
st.caption(
    "Synthetic pharma claims dataset (5,000 patients) — adherence modeling, "
    "risk cohorting, and prescriber-region analysis. Model cross-validated in Python and R."
)

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")
regions = st.sidebar.multiselect("Region", sorted(df["region"].unique()), default=sorted(df["region"].unique()))
drug_classes = st.sidebar.multiselect("Drug Class", sorted(df["drug_class"].unique()), default=sorted(df["drug_class"].unique()))
copay_tiers = st.sidebar.multiselect("Copay Tier", ["Low", "Medium", "High"], default=["Low", "Medium", "High"])

filtered = df[
    df["region"].isin(regions) &
    df["drug_class"].isin(drug_classes) &
    df["copay_tier"].isin(copay_tiers)
]

st.sidebar.markdown("---")
st.sidebar.metric("Patients in view", f"{len(filtered):,}")
st.sidebar.metric("Non-adherence rate", f"{filtered['non_adherent'].mean():.1%}" if len(filtered) else "—")

# ---------- Top KPIs ----------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Patients", f"{len(filtered):,}")
col2.metric("Avg PDC", f"{filtered['pdc'].mean():.1%}" if len(filtered) else "—")
col3.metric("Non-Adherent Rate", f"{filtered['non_adherent'].mean():.1%}" if len(filtered) else "—")
col4.metric("High-Risk Patients", f"{(filtered['risk_cohort']=='High Risk').sum():,}" if len(filtered) else "0")

st.markdown("---")

# ---------- Tabs ----------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Adherence Overview", "🗺️ Regional Cohorts", "📈 Model Drivers", "🔍 Patient Explorer"])

with tab1:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Non-Adherence Rate by Copay Tier")
        rate_by_copay = filtered.groupby("copay_tier")["non_adherent"].mean().reindex(["Low", "Medium", "High"]).reset_index()
        fig = px.bar(rate_by_copay, x="copay_tier", y="non_adherent",
                     labels={"non_adherent": "Non-Adherent Rate", "copay_tier": "Copay Tier"},
                     color="non_adherent", color_continuous_scale="Reds")
        fig.update_layout(yaxis_tickformat=".0%", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Non-Adherence Rate by Drug Class")
        rate_by_drug = filtered.groupby("drug_class")["non_adherent"].mean().reset_index()
        fig = px.bar(rate_by_drug, x="drug_class", y="non_adherent",
                     labels={"non_adherent": "Non-Adherent Rate", "drug_class": "Drug Class"},
                     color="non_adherent", color_continuous_scale="Blues")
        fig.update_layout(yaxis_tickformat=".0%", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("PDC Distribution: New vs Existing Patients")
    fig = px.histogram(filtered, x="pdc", color="new_to_therapy", nbins=30, opacity=0.7,
                        barmode="overlay",
                        labels={"pdc": "Proportion of Days Covered (PDC)", "new_to_therapy": "New to Therapy"},
                        color_discrete_map={0: "#1f77b4", 1: "#ff7f0e"})
    fig.add_vline(x=0.80, line_dash="dash", line_color="red", annotation_text="PDC = 0.80 threshold")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Risk Cohort Distribution by Region")
    cohort_filtered = cohort[cohort["region"].isin(regions)] if regions else cohort

    fig = px.bar(cohort_filtered, x="region", y="patients", color="risk_cohort",
                 barmode="stack",
                 category_orders={"risk_cohort": ["Low Risk", "Medium Risk", "High Risk"]},
                 color_discrete_map={"Low Risk": "#2ca02c", "Medium Risk": "#ff7f0e", "High Risk": "#d62728"},
                 labels={"patients": "Patients", "region": "Region"})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Cohort Summary Table")
    st.dataframe(
        cohort_filtered.style.format({"avg_pdc": "{:.1%}", "non_adherent_rate": "{:.1%}"}),
        use_container_width=True
    )

    st.subheader("Average PDC Heatmap: Region × Risk Cohort")
    pivot = cohort_filtered.pivot(index="region", columns="risk_cohort", values="avg_pdc")
    pivot = pivot[["Low Risk", "Medium Risk", "High Risk"]] if "Low Risk" in pivot.columns else pivot
    fig = px.imshow(pivot, text_auto=".1%", color_continuous_scale="RdYlGn",
                     labels=dict(color="Avg PDC"))
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Logistic Regression: Drivers of Non-Adherence")
    st.caption("Odds ratios > 1 increase risk of non-adherence; < 1 decrease it. Model validated in Python (statsmodels) and R (glm).")

    odds_plot = odds[odds["term"] != "Intercept"].copy()
    odds_plot = odds_plot.sort_values("odds_ratio")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=odds_plot["odds_ratio"], y=odds_plot["term"],
        error_x=dict(type="data", symmetric=False,
                      array=odds_plot["OR_high"] - odds_plot["odds_ratio"],
                      arrayminus=odds_plot["odds_ratio"] - odds_plot["OR_low"]),
        mode="markers", marker=dict(size=12, color="steelblue")
    ))
    fig.add_vline(x=1, line_dash="dash", line_color="gray")
    fig.update_layout(xaxis_title="Odds Ratio (95% CI)", yaxis_title="",
                       title="Effect of Each Factor on Non-Adherence Odds")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(odds.style.format({"odds_ratio": "{:.3f}", "OR_low": "{:.3f}", "OR_high": "{:.3f}"}),
                 use_container_width=True)

    st.markdown("""
    **Reading the chart:** High copay tier and new-to-therapy status are the strongest risk factors for
    non-adherence. Mail-order pharmacy use is the strongest protective factor — patients using mail order
    have roughly 76% lower odds of non-adherence, all else equal.
    """)

with tab4:
    st.subheader("Patient-Level Explorer")
    st.dataframe(
        filtered[["patient_id", "age", "region", "drug_class", "copay_tier",
                  "n_comorbidities", "mail_order", "new_to_therapy", "pdc", "risk_cohort"]]
        .sort_values("pdc"),
        use_container_width=True,
        height=500
    )
    st.caption(f"Showing {len(filtered):,} of {len(df):,} patients based on current filters.")

st.markdown("---")
st.caption("Synthetic dataset built for portfolio purposes. Adherence modeled using PDC (Proportion of Days Covered), the industry-standard metric, with a 0.80 threshold for non-adherence.")
