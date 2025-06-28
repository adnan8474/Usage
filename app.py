import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, List
import datetime

from usage_intelligence.analysis import (
    parse_timestamps, apply_flags, compute_scores
)
from usage_intelligence.visualization import (
    heatmap_usage, hourly_bar, device_trend, flag_pie, interval_distribution,
    behaviour_timeline
)

# --- PAGE CONFIG ---
st.set_page_config(page_title="POCTIFY Usage Intelligence", layout="wide")
st.title("POCTIFY Usage Intelligence: Supervisor Suite")

# --- SIDEBAR LOGO & INSTRUCTIONS ---
def show_logo(logo_path: Path) -> None:
    if logo_path.is_file():
        st.sidebar.image(str(logo_path), use_container_width=True)

def show_instructions() -> None:
    with st.sidebar.expander("ℹ️ Instructions", expanded=False):
        st.markdown(
            """
            **POCTIFY Usage Intelligence** provides comprehensive audit, compliance, and analytics for POCT teams.

            **How to use:**
            1. Download & review the data template.
            2. Upload anonymized logs (.csv/.xlsx).
            3. Adjust detection and compliance parameters.
            4. Explore dashboards and flagged results.
            5. Export audit trails and reports as needed.

            **This tool supports:**  
            - Operator compliance audit  
            - Device/location usage analytics  
            - Real-time and retrospective anomaly detection  
            - Full audit/export for regulatory compliance

            **Never upload patient names, MRNs, or clinical results.**
            """
        )

# --- SIDEBAR DATA UPLOAD AND PARAMETERS ---
def sidebar_upload_and_params() -> Tuple[Optional[pd.DataFrame], int, int, int]:
    st.sidebar.header("Upload Data")
    uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])
    rapid_th = st.sidebar.slider("Rapid Succession Threshold (s)", 10, 300, 60, 10)
    min_score = st.sidebar.slider("Min Suspicion Score", 0, 100, 10)
    min_tests = st.sidebar.slider("Min Tests per Operator", 0, 100, 0)
    st.sidebar.markdown("---")
    try:
        with open("usage_intelligence/data/template.csv", "r") as f:
            st.sidebar.download_button("Download Template", f.read(), file_name="template.csv")
    except Exception:
        st.sidebar.warning("Template file not found.")
    return uploaded_file, rapid_th, min_score, min_tests

# --- LOAD DATA ---
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

# --- SIDEBAR FILTERS ---
def sidebar_filters(df: pd.DataFrame):
    st.sidebar.subheader("🔍 Filter Data")
    operator_ids = st.sidebar.multiselect("Operator ID", options=sorted(df['Operator_ID'].dropna().unique()))
    locations = st.sidebar.multiselect("Location", options=sorted(df['Location'].dropna().unique()))
    devices = st.sidebar.multiselect("Device ID", options=sorted(df['Device_ID'].dropna().unique()))
    test_types = st.sidebar.multiselect("Test Type", options=sorted(df['Test_Type'].dropna().unique()))
    date_range = st.sidebar.date_input(
        "Date Range",
        [df['Timestamp'].min().date(), df['Timestamp'].max().date()] if not df.empty else [datetime.date.today(), datetime.date.today()],
    )
    shifts = st.sidebar.multiselect(
        "Shift",
        options=["Day", "Evening", "Night"],
        default=[]
    )
    return operator_ids, locations, devices, test_types, date_range, shifts

def apply_filters(
    df: pd.DataFrame,
    operator_ids: List[str],
    locations: List[str],
    devices: List[str],
    test_types: List[str],
    date_range: List[datetime.date],
    shifts: List[str]
) -> pd.DataFrame:
    if operator_ids:
        df = df[df['Operator_ID'].isin(operator_ids)]
    if locations:
        df = df[df['Location'].isin(locations)]
    if devices:
        df = df[df['Device_ID'].isin(devices)]
    if test_types:
        df = df[df['Test_Type'].isin(test_types)]
    if date_range and len(date_range) == 2:
        start_date, end_date = date_range
        df = df[
            (df['Timestamp'].dt.date >= start_date)
            & (df['Timestamp'].dt.date <= end_date)
        ]
    if shifts:
        df['Shift'] = df['Timestamp'].dt.hour.apply(lambda h: "Day" if 7 <= h < 15 else "Evening" if 15 <= h < 23 else "Night")
        df = df[df['Shift'].isin(shifts)]
    return df

# --- TERMS ---
def show_terms() -> None:
    st.markdown(
        """
        **Terms:** Internal POCT audit use only. No clinical decisions. Do not upload patient names, MRNs, or clinical results.
        """
    )

# --- SUMMARY STATS ---
def summary_statistics(df: pd.DataFrame):
    st.markdown("### 📊 Quick Stats")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Tests", len(df))
    col2.metric("Unique Operators", df['Operator_ID'].nunique())
    col3.metric("Unique Devices", df['Device_ID'].nunique())
    col4.metric("Locations", df['Location'].nunique())
    col5.metric("Avg. Tests/Day", int(len(df)/df['Timestamp'].dt.date.nunique()) if not df.empty else 0)

# --- MAIN APP ---
def main():
    logo_path = Path("POCTIFY Logo.png")
    show_logo(logo_path)
    show_instructions()

    uploaded_file, rapid_th, min_score, min_tests = sidebar_upload_and_params()

    if uploaded_file is not None:
        df = load_data(uploaded_file)
        if df is None:
            st.stop()

        try:
            df = parse_timestamps(df)
        except ValueError as e:
            st.error(str(e))
            st.stop()

        # --- Core Usage & Audit Analytics ---
        st.markdown("## 📈 Usage & Audit Analytics")
        df = apply_flags(df, rapid_th)
        scores = compute_scores(df)
        scores = scores[scores['Suspicion_Score'] >= min_score]
        if min_tests > 0:
            op_counts = df.groupby('Operator_ID').size()
            eligible_ops = op_counts[op_counts >= min_tests].index
            scores = scores[scores['Operator_ID'].isin(eligible_ops)]

        operator_ids, locations, devices, test_types, date_range, shifts = sidebar_filters(df)
        filtered_ops = list(scores['Operator_ID'].unique())
        if filtered_ops:
            if operator_ids:
                operator_ids = [op for op in operator_ids if op in filtered_ops]
            else:
                operator_ids = filtered_ops

        df_filtered = apply_filters(df, operator_ids, locations, devices, test_types, date_range, shifts)

        summary_statistics(df_filtered)

        st.subheader("Suspicious Operators")
        st.dataframe(scores, use_container_width=True)

        st.markdown("#### Operator Behaviour Timeline")
        op_selected = st.selectbox(
            "Select Operator",
            scores['Operator_ID'] if not scores.empty else [''],
        )

        # --- GRAPHS ---
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(heatmap_usage(df_filtered), use_container_width=True)
            st.plotly_chart(hourly_bar(df_filtered), use_container_width=True)
        with col2:
            st.plotly_chart(device_trend(df_filtered), use_container_width=True)
            st.plotly_chart(flag_pie(df_filtered), use_container_width=True)
        st.plotly_chart(interval_distribution(df_filtered), use_container_width=True)
        st.plotly_chart(behaviour_timeline(df_filtered, op_selected), use_container_width=True)

        # --- Export ---
        st.subheader("Export & Audit Trail")
        csv_data = df_filtered.to_csv(index=False)
        st.download_button("Download Flags CSV", csv_data, file_name="flagged_summary.csv")

        # --- Deep Dive: More Stats & Controls ---
        with st.expander("🔬 Deep Dive: More Analytics & Controls"):
            st.markdown("**Tests per Operator**")
            st.bar_chart(df_filtered['Operator_ID'].value_counts())
            st.markdown("**Tests per Device**")
            st.bar_chart(df_filtered['Device_ID'].value_counts())
            st.markdown("**Tests per Location**")
            st.bar_chart(df_filtered['Location'].value_counts())
            st.markdown("**Hourly Distribution**")
            st.bar_chart(df_filtered['Timestamp'].dt.hour.value_counts().sort_index())

    else:
        st.info("Please upload a CSV or Excel file to begin.")

    show_terms()

if __name__ == "__main__":
    main()
