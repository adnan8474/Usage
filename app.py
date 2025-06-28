import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Optional, Tuple

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

def show_logo(logo_path: Path) -> None:
    if logo_path.is_file():
        st.sidebar.image(str(logo_path), width=120, use_column_width=False)

def show_instructions() -> None:
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

def sidebar_upload_and_params() -> Tuple[Optional[pd.DataFrame], int]:
    st.sidebar.header("Upload Data")
    uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])
    rapid_th = st.sidebar.slider("Rapid succession threshold (s)", min_value=10, max_value=300, value=60, step=10)
    st.sidebar.markdown("---")
    with open("usage_intelligence/data/template.csv", "r") as f:
        st.sidebar.download_button("Download Template", f.read(), file_name="template.csv")
    return uploaded_file, rapid_th

def load_data(uploaded_file) -> Optional[pd.DataFrame]:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, comment="#")
        else:
            df = pd.read_excel(uploaded_file)
        return df
    except Exception as e:
        st.error(f"Failed to read file: {e}")
        return None

def filter_data(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.markdown("### 🔍 Filter Options")
    with st.sidebar.expander("Filter Help", expanded=False):
        st.write("Use these filters to narrow the dataset before reviewing flags.")

    operator_ids = st.sidebar.multiselect("Operator ID", options=sorted(df['Operator_ID'].dropna().unique()))
    locations = st.sidebar.multiselect("Location", options=sorted(df['Location'].dropna().unique()))
    devices = st.sidebar.multiselect("Device ID", options=sorted(df['Device_ID'].dropna().unique()))
    test_types = st.sidebar.multiselect("Test Type", options=sorted(df['Test_Type'].dropna().unique()))
    date_range = st.sidebar.date_input(
        "Date Range",
        [df['Timestamp'].min().date(), df['Timestamp'].max().date()],
    )
    min_score = st.sidebar.slider("Min Suspicion Score", 0, 100, 10)

    df_filtered = df.copy()
    if operator_ids:
        df_filtered = df_filtered[df_filtered['Operator_ID'].isin(operator_ids)]
    if locations:
        df_filtered = df_filtered[df_filtered['Location'].isin(locations)]
    if devices:
        df_filtered = df_filtered[df_filtered['Device_ID'].isin(devices)]
    if test_types:
        df_filtered = df_filtered[df_filtered['Test_Type'].isin(test_types)]
    if date_range:
        start_date = date_range[0]
        end_date = date_range[1] if len(date_range) > 1 else date_range[0]
        df_filtered = df_filtered[
            (df_filtered['Timestamp'].dt.date >= start_date)
            & (df_filtered['Timestamp'].dt.date <= end_date)
        ]
    return df_filtered, min_score

def show_terms() -> None:
    st.markdown(
        """
        **Terms:** This tool is for internal POCT audit use only and should not be used for clinical decision-making. Do not upload patient names, MRNs, or clinical results.
        """
    )

def main():
    logo_path = Path("POCTIFY Logo.png")
    show_logo(logo_path)
    show_instructions()
    uploaded_file, rapid_th = sidebar_upload_and_params()

    if uploaded_file is not None:
        df = load_data(uploaded_file)
        if df is None:
            st.stop()
        try:
            df = parse_timestamps(df)
        except ValueError as e:
            st.error(str(e))
            st.stop()

        df = apply_flags(df, rapid_th)
        df_filtered, min_score = filter_data(df)

        scores = compute_scores(df_filtered)
        scores = scores[scores['Suspicion_Score'] >= min_score]
        df_filtered = df_filtered[df_filtered['Operator_ID'].isin(scores['Operator_ID'])]

        st.subheader("Suspicious Operators")
        st.dataframe(scores, use_container_width=True)

        op_selected = st.selectbox(
            "View Behaviour Timeline for Operator",
            scores['Operator_ID'] if not scores.empty else [''],
        )

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(heatmap_usage(df_filtered), use_container_width=True)
            st.plotly_chart(hourly_bar(df_filtered), use_container_width=True)
        with col2:
            st.plotly_chart(device_trend(df_filtered), use_container_width=True)
            st.plotly_chart(flag_pie(df_filtered), use_container_width=True)
        st.plotly_chart(interval_distribution(df_filtered), use_container_width=True)
        st.plotly_chart(behaviour_timeline(df_filtered, op_selected), use_container_width=True)

        st.subheader("Flagged Data")
        st.dataframe(df_filtered)
        csv_data = df_filtered.to_csv(index=False)
        st.download_button("Download Flags CSV", csv_data, file_name="flagged_summary.csv")
    else:
        st.info("Please upload a CSV or Excel file to begin.")

    show_terms()

if __name__ == "__main__":
    main()
