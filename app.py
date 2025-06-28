import streamlit as st
import pandas as pd

from usage_intelligence.analysis import parse_timestamps, apply_flags, compute_scores
from usage_intelligence.visualization import (
    heatmap_usage,
    hourly_bar,
    device_trend,
    flag_pie,
    interval_distribution,
    behaviour_timeline,
)

st.set_page_config(page_title="POCTIFY Usage Intelligence", layout="wide")

st.title("POCTIFY Usage Intelligence")
st.sidebar.image(
    "https://raw.githubusercontent.com/streamlit/branding/master/streamlit-logo-primary-colormark-darktext.png",
    width=150,
)

with st.sidebar.expander("ℹ️ Instructions", expanded=False):
    st.markdown(
        """
        **POCTIFY Usage Intelligence** helps POCT teams spot barcode sharing and abnormal device usage.

        **Steps**:
        1. Download the CSV template.
        2. Upload your anonymised log file (.csv or .xlsx).
        3. Adjust the rapid succession slider to tune barcode-sharing sensitivity.
        4. Review the dashboards and flagged results.

        Use the provided template format. Invalid dates will be highlighted if parsing fails.

        Avoid uploading patient names, MRNs or test results.
        """
    )

st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"]) 
rapid_th = st.sidebar.slider("Rapid succession threshold (s)", min_value=10, max_value=300, value=60, step=10)

st.sidebar.markdown("---")
with open("usage_intelligence/data/template.csv", "r") as f:
    st.sidebar.download_button("Download Template", f.read(), file_name="template.csv")

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Failed to read file: {e}")
        st.stop()
    try:
        df = parse_timestamps(df)
    except ValueError as e:
        st.error(str(e))
        st.stop()

    df = apply_flags(df, rapid_th)
    scores = compute_scores(df)

    st.subheader("Suspicious Operators")
    st.dataframe(scores, use_container_width=True)

    op_selected = st.selectbox(
        "View Behaviour Timeline for Operator",
        scores['Operator_ID'],
    )

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(heatmap_usage(df), use_container_width=True)
        st.plotly_chart(hourly_bar(df), use_container_width=True)
    with col2:
        st.plotly_chart(device_trend(df), use_container_width=True)
        st.plotly_chart(flag_pie(df), use_container_width=True)
    st.plotly_chart(interval_distribution(df), use_container_width=True)
    st.plotly_chart(behaviour_timeline(df, op_selected), use_container_width=True)

    st.subheader("Flagged Data")
    st.dataframe(df)
    csv_data = df.to_csv(index=False)
    st.download_button("Download Flags CSV", csv_data, file_name="flagged_summary.csv")
else:
    st.info("Please upload a CSV or Excel file to begin.")

st.markdown(
    """
    **Terms:** This tool is for internal POCT audit use only and should not be used for clinical decision-making. Do not upload patient names, MRNs, or clinical results.
    """
)
