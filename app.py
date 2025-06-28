import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, List
import datetime
import sys

# --- DYNAMIC PATH SETUP FOR MODULES ---
BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))

# --- USAGE_INTELLIGENCE MODULES ---
try:
    from usage_intelligence.analysis import (
        parse_timestamps, apply_flags, compute_scores, get_qc_status,
        get_error_events, get_training_status, detect_anomalies
    )
    from usage_intelligence.visualization import (
        heatmap_usage, hourly_bar, device_trend, flag_pie, interval_distribution,
        behaviour_timeline, operator_compliance_chart, device_error_chart, qc_result_chart
    )
except ImportError as e:
    st.error(f"Module import error: {e}")
    st.stop()

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
            4. Explore dashboards, compliance panels, and flagged results.
            5. Export audit trails and reports as needed.

            **This tool supports:**  
            - Operator certification/compliance audit  
            - Device/location usage & error analytics  
            - QC/QA tracking  
            - Real-time and retrospective anomaly detection  
            - Full audit/export for regulatory compliance

            **Never upload patient names, MRNs, or clinical results.**
            """
        )

def sidebar_upload_and_params() -> Tuple[Optional[pd.DataFrame], int, int, int, int]:
    st.sidebar.header("Upload Data")
    uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])
    rapid_th = st.sidebar.slider("Rapid Succession Threshold (s)", 10, 300, 60, 10)
    min_score = st.sidebar.slider("Min Suspicion Score", 0, 100, 10)
    min_tests = st.sidebar.slider("Min Tests per Operator", 0, 100, 0)
    anomaly_sensitivity = st.sidebar.slider("Anomaly Detection Sensitivity", 1, 10, 5)
    st.sidebar.markdown("---")
    template_path = BASE / "usage_intelligence" / "data" / "template.csv"
    if template_path.is_file():
        with open(template_path, "r") as f:
            st.sidebar.download_button("Download Template", f.read(), file_name="template.csv")
    else:
        st.sidebar.warning("Template file not found.")
    return uploaded_file, rapid_th, min_score, min_tests, anomaly_sensitivity

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
            (df['Timestamp'].dt.date

