"""
A/B Testing Simulator
======================
Interactive Streamlit dashboard for analysing A/B test results.
Computes statistical significance, confidence intervals, lift, and visual reports.

Author: Amrutha Satyamoorthy
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats
import io

st.set_page_config(page_title="A/B Testing Simulator", layout="wide")
st.title("A/B Testing Simulator")
st.markdown("Analyse experiment results for conversion rate improvements using Z-tests and t-tests.")

st.sidebar.header("Input Parameters")
input_mode = st.sidebar.radio("Input mode", ["Manual entry", "Upload CSV"])

def get_manual_inputs():
    st.sidebar.subheader("Control group")
    n_c = st.sidebar.number_input("Sample size (control)", min_value=10, value=1000)
    conv_c = st.sidebar.number_input("Conversions (control)", min_value=0, value=120)
    st.sidebar.subheader("Treatment group")
    n_t = st.sidebar.number_input("Sample size (treatment)", min_value=10, value=1000)
    conv_t = st.sidebar.number_input("Conversions (treatment)", min_value=0, value=145)
    alpha = st.sidebar.selectbox("Significance level", [0.05, 0.01, 0.10], index=0)
    return n_c, conv_c, n_t, conv_t, alpha

if input_mode == "Upload CSV":
    uploaded = st.sidebar.file_uploader("Upload experiment CSV", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        st.write("Preview:", df.head())
        group_col = st.selectbox("Group column", df.columns)
        outcome_col = st.selectbox("Outcome column (binary: 0/1)", df.columns)
        ctrl_label = st.text_input("Control label", "control")
        treat_label = st.text_input("Treatment label", "treatment")
        alpha = st.selectbox("Significance level", [0.05, 0.01, 0.10], index=0)
        ctrl = df[df[group_col] == ctrl_label][outcome_col]
        treat = df[df[group_col] == treat_label][outcome_col]
        n_c, conv_c, n_t, conv_t = len(ctrl), int(ctrl.sum()), len(treat), int(treat.sum())
    else:
        st.info("Upload a CSV or switch to manual entry.")
        st.stop()
else:
    n_c, conv_c, n_t, conv_t, alpha = get_manual_inputs()

p_c = conv_c / n_c
p_t = conv_t / n_t
lift = (p_t - p_c) / p_c if p_c > 0 else 0
abs_diff = p_t - p_c
p_pool = (conv_c + conv_t) / (n_c + n_t)
se_pool = np.sqrt(p_pool * (1 - p_pool) * (1/n_c + 1/n_t))
z_stat = abs_diff / se_pool if se_pool > 0 else 0
p_value_z = 2 * (1 - stats.norm.cdf(abs(z_stat)))
z_crit = stats.norm.ppf(1 - alpha/2)
se_diff = np.sqrt(p_c*(1-p_c)/n_c + p_t*(1-p_t)/n_t)
ci_lower = abs_diff - z_crit * se_diff
ci_upper = abs_diff + z_crit * se_diff
ctrl_arr = np.array([1]*conv_c + [0]*(n_c - conv_c))
treat_arr = np.array([1]*conv_t + [0]*(n_t - conv_t))
t_stat, p_value_t = stats.ttest_ind(ctrl_arr, treat_arr)
significant = p_value_z < alpha

st.markdown("---")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Control rate", f"{p_c:.2%}")
col2.metric("Treatment rate", f"{p_t:.2%}", delta=f"{abs_diff:+.2%}")
col3.metric("Relative lift", f"{lift:+.1%}")
col4.metric("p-value (Z-test)", f"{p_value_z:.4f}", delta="Significant" if significant else "Not significant", delta_color="normal" if significant else "inverse")
st.markdown("---")

if significant:
    st.success(f"Result is statistically significant at the {alpha} level (p = {p_value_z:.4f}).")
else:
    st.warning(f"Result is not statistically significant at the {alpha} level (p = {p_value_z:.4f}).")

stats_df = pd.DataFrame({
    "Metric": ["Control n", "Treatment n", "Control conversions", "Treatment conversions",
               "Control rate", "Treatment rate", "Absolute diff", "Relative lift",
               "Z-stat", "p-value (Z)", "t-stat", "p-value (t)",
               f"{int((1-alpha)*100)}% CI lower", f"{int((1-alpha)*100)}% CI upper"],
    "Value": [n_c, n_t, conv_c, conv_t, f"{p_c:.4f}", f"{p_t:.4f}",
              f"{abs_diff:+.4f}", f"{lift:+.2%}", f"{z_stat:.4f}", f"{p_value_z:.4f}",
              f"{t_stat:.4f}", f"{p_value_t:.4f}", f"{ci_lower:+.4f}", f"{ci_upper:+.4f}"]
})
st.subheader("Statistical Summary")
st.table(stats_df)

fig = plt.figure(figsize=(13, 5))
gs = gridspec.GridSpec(1, 3, figure=fig)
ax1 = fig.add_subplot(gs[0])
bars = ax1.bar(["Control", "Treatment"], [p_c, p_t], color=["#888888", "#1a6faf"], edgecolor="white", width=0.5)
ax1.set_ylabel("Conversion Rate"); ax1.set_title("Conversion Rate Comparison")
ax1.set_ylim(0, max(p_c, p_t) * 1.3)
for bar, val in zip(bars, [p_c, p_t]):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.002, f"{val:.2%}", ha="center", fontsize=10)
ax1.spines["top"].set_visible(False); ax1.spines["right"].set_visible(False)
ax2 = fig.add_subplot(gs[1])
ax2.errorbar(["Difference"], [abs_diff], yerr=[[abs_diff - ci_lower], [ci_upper - abs_diff]], fmt="o", color="#1a6faf", capsize=10, capthick=1.5, markersize=8)
ax2.axhline(0, color="black", linewidth=0.8, linestyle="--", alpha=0.6)
ax2.set_title(f"{int((1-alpha)*100)}% Confidence Interval"); ax2.set_ylabel("Conversion rate difference")
ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)
ax3 = fig.add_subplot(gs[2])
ax3.barh(["p-value", f"alpha ({alpha})"], [p_value_z, alpha], color=["#d4600a" if p_value_z >= alpha else "#2ca05a", "#dddddd"], edgecolor="white")
ax3.set_title("p-value vs Significance Level"); ax3.spines["top"].set_visible(False); ax3.spines["right"].set_visible(False)
plt.tight_layout()
st.subheader("Visual Summary")
st.pyplot(fig)

buf = io.BytesIO()
fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
st.download_button("Download chart as PNG", buf.getvalue(), "ab_test_chart.png", "image/png")
st.download_button("Download results as CSV", stats_df.to_csv(index=False), "ab_test_results.csv", "text/csv")
