import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple

# ======= CONFIGURATION =======
APP_TITLE = "POCTIFY Operator Audit Suite"
LOGO_PATH = Path("POCTIFY Logo.png")
TEMPLATE_PATH = Path("usage_intelligence/data/template.csv")
REQUIRED_COLUMNS = ["Timestamp", "Operator_ID", "Device_ID"]

# ======= UTILITY FUNCTIONS =======

def show_logo(logo_path: Path) -> None:
    """Display logo in the sidebar if available."""
    if logo_path.is_file():
        st.sidebar.image(str(logo_path), use_container_width=True)

def show_instructions():
    """Show usage instructions in the sidebar."""
    st.sidebar.markdown("""
        ## How to Use
        1. Upload anonymized data using the provided template.
        2. Adjust detection rules and parameters as needed.
        3. Review flagged sessions, operators, locations, and analytics.
        4. Drill down, annotate, and export for audit.
        5. Track investigation progress.
        ---
        **No patient identifiers should ever be uploaded.**
    """)

def download_template_btn(template_path: Path) -> None:
    """Show a template download button if template exists."""
    if template_path.is_file():
        with open(template_path, "r") as f:
            st.sidebar.download_button("Download Template", f.read(), file_name="template.csv")
    else:
        st.sidebar.warning("Template not found.")

def sidebar_upload_and_params() -> Tuple[Optional[Any], int, int, int]:
    """Handle file upload and parameter selection in the sidebar."""
    st.sidebar.header("Upload Data")
    uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])
    st.sidebar.markdown("---")
    download_template_btn(TEMPLATE_PATH)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Detection Parameters")
    suspicion_window = st.sidebar.slider("Window for operator reuse (minutes)", 1, 120, 10)
    share_threshold = st.sidebar.slider("Flag if used by more than X operators in window", 1, 10, 2)
    rapid_threshold = st.sidebar.slider("Rapid test threshold (seconds)", 10, 600, 60)
    return uploaded_file, suspicion_window, share_threshold, rapid_threshold

def validate_columns(df: pd.DataFrame, required: List[str]) -> None:
    """Check if required columns exist in DataFrame."""
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}\nColumns found: {df.columns.tolist()}")

def read_uploaded_file(uploaded_file: Any) -> pd.DataFrame:
    """Read uploaded CSV/Excel, remove comment lines, clean headers."""
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, comment="#")
    else:
        df = pd.read_excel(uploaded_file)
    df.columns = [col.strip() for col in df.columns]
    return df

def parse_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """Parse the Timestamp column to datetime."""
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    return df

def ensure_unique_event_id(df: pd.DataFrame) -> pd.DataFrame:
    """Add a unique Event_ID for each row for tracking."""
    df = df.copy()
    df["Event_ID"] = np.arange(1, len(df) + 1)
    return df

# ======= ANALYSIS FUNCTIONS =======

def flag_rapid_tests(df: pd.DataFrame, rapid_threshold: int = 60) -> pd.DataFrame:
    """Flag events where the same operator performs a test too rapidly (possible automation misuse)."""
    flagged = []
    df_sorted = df.sort_values(["Operator_ID", "Timestamp"])
    for op_id, group in df_sorted.groupby("Operator_ID"):
        group = group.sort_values("Timestamp")
        prev_time = None
        for idx, row in group.iterrows():
            if prev_time is not None:
                delta = (row['Timestamp'] - prev_time).total_seconds()
                if delta < rapid_threshold:
                    flagged.append(idx)
            prev_time = row['Timestamp']
    df["Rapid_Flag"] = df.index.isin(flagged)
    return df

def flag_location_switch(df: pd.DataFrame, window_minutes: int = 10) -> pd.DataFrame:
    """Flag if the same operator uses different locations/devices within a short window (possible badge sharing)."""
    flagged = []
    df_sorted = df.sort_values(["Operator_ID", "Timestamp"])
    for op_id, group in df_sorted.groupby("Operator_ID"):
        group = group.sort_values("Timestamp")
        prev_row = None
        for idx, row in group.iterrows():
            if prev_row is not None:
                delta = (row['Timestamp'] - prev_row['Timestamp']).total_seconds() / 60
                if delta < window_minutes and (row['Device_ID'] != prev_row['Device_ID'] or row.get('Location', None) != prev_row.get('Location', None)):
                    flagged.append(idx)
            prev_row = row
    df["Switch_Flag"] = df.index.isin(flagged)
    return df

def flag_multiple_operators_per_device(df: pd.DataFrame, window_minutes: int = 10, share_threshold: int = 2) -> pd.DataFrame:
    """Flag if too many operators use the same device in a window."""
    flagged = []
    df_sorted = df.sort_values(["Device_ID", "Timestamp"])
    for device_id, group in df_sorted.groupby("Device_ID"):
        group = group.sort_values("Timestamp")
        for i in range(len(group)):
            window_start = group.iloc[i]["Timestamp"]
            window_end = window_start + timedelta(minutes=window_minutes)
            operators_in_window = group[(group["Timestamp"] >= window_start) & (group["Timestamp"] <= window_end)]["Operator_ID"].nunique()
            if operators_in_window >= share_threshold:
                flagged.append(group.index[i])
    df["Device_Share_Flag"] = df.index.isin(flagged)
    return df

def compute_all_flags(df: pd.DataFrame, suspicion_window: int, share_threshold: int, rapid_threshold: int) -> pd.DataFrame:
    """Run all flagging functions and combine results."""
    df = flag_rapid_tests(df, rapid_threshold)
    df = flag_location_switch(df, suspicion_window)
    df = flag_multiple_operators_per_device(df, suspicion_window, share_threshold)
    df["Flagged"] = df[["Rapid_Flag", "Switch_Flag", "Device_Share_Flag"]].any(axis=1)
    return df

# ======= VISUALIZATION FUNCTIONS =======

def operator_heatmap(df: pd.DataFrame, value: str = "count") -> None:
    """Plot a heatmap of operators by hour of day."""
    df = df.copy()
    df["Hour"] = df["Timestamp"].dt.hour
    op_counts = df.groupby(["Operator_ID", "Hour"]).size().reset_index(name="Count")
    fig = px.density_heatmap(op_counts, x="Hour", y="Operator_ID", z="Count",
                             color_continuous_scale="Viridis",
                             title="Operator Activity by Hour")
    st.plotly_chart(fig, use_container_width=True)

def device_heatmap(df: pd.DataFrame) -> None:
    """Plot a heatmap of device usage over time."""
    if "Device_ID" in df.columns:
        df = df.copy()
        df["Hour"] = df["Timestamp"].dt.hour
        dev_counts = df.groupby(["Device_ID", "Hour"]).size().reset_index(name="Count")
        fig = px.density_heatmap(dev_counts, x="Hour", y="Device_ID", z="Count",
                                 color_continuous_scale="Plasma",
                                 title="Device Usage by Hour")
        st.plotly_chart(fig, use_container_width=True)

def timeline_plot(df: pd.DataFrame, id_col: str = "Operator_ID") -> None:
    """Show a timeline of activity for a selected identifier."""
    st.subheader(f"{id_col} Activity Timeline")
    ids = df[id_col].unique().tolist()
    selected_id = st.selectbox(f"Select {id_col}", ids)
    plot_df = df[df[id_col] == selected_id].sort_values("Timestamp")
    fig = px.scatter(plot_df, x="Timestamp", y="Device_ID", color="Flagged",
                     hover_data=df.columns.tolist(),
                     title=f"{id_col} Timeline")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(plot_df)

def summary_cards(df: pd.DataFrame) -> None:
    """Show summary cards for flagged events, operators, and devices."""
    st.markdown("### Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Events", len(df))
    c2.metric("Flagged Events", df["Flagged"].sum())
    c3.metric("Unique Operators", df["Operator_ID"].nunique())
    c4.metric("Unique Devices", df["Device_ID"].nunique())

def flagged_table(df: pd.DataFrame) -> None:
    """Show a table of flagged events."""
    st.markdown("#### Flagged Events Table")
    st.dataframe(df[df["Flagged"]], use_container_width=True)

def investigation_notes(df: pd.DataFrame) -> None:
    """Add and display notes for flagged events."""
    st.markdown("#### Investigation Notes")
    flagged = df[df["Flagged"]]
    selected_idx = st.selectbox("Select Event ID for Notes", flagged.index)
    notes_key = f"notes_{selected_idx}"
    note = st.text_area("Add investigation note:", value=st.session_state.get(notes_key, ""), key=notes_key)
    st.session_state[notes_key] = note
    st.info(f"Note for Event {selected_idx}: {note}")

def export_buttons(df: pd.DataFrame) -> None:
    """Provide buttons to export flagged and all events."""
    st.sidebar.markdown("---")
    st.sidebar.download_button("Export Flagged Events", df[df["Flagged"]].to_csv(index=False), file_name="flagged_events.csv")
    st.sidebar.download_button("Export All Events", df.to_csv(index=False), file_name="all_events.csv")

# ======= MAIN APP =======

def main():
    st.set_page_config(page_title=APP_TITLE, layout="wide", initial_sidebar_state="expanded")
    st.title(APP_TITLE)
    show_logo(LOGO_PATH)
    show_instructions()
    uploaded_file, suspicion_window, share_threshold, rapid_threshold = sidebar_upload_and_params()

    if uploaded_file is not None:
        try:
            df = read_uploaded_file(uploaded_file)
            st.write("Columns in uploaded file:", df.columns.tolist())
            validate_columns(df, REQUIRED_COLUMNS)
            df = parse_timestamps(df)
            df = ensure_unique_event_id(df)
            df = compute_all_flags(df, suspicion_window, share_threshold, rapid_threshold)
            summary_cards(df)

            # Navigation
            nav = st.sidebar.radio("Navigate", [
                "Flagged Events", "Operator Drilldown", "Device Drilldown", "Analytics", "Investigation"
            ])

            if nav == "Flagged Events":
                flagged_table(df)

            elif nav == "Operator Drilldown":
                timeline_plot(df, id_col="Operator_ID")

            elif nav == "Device Drilldown":
                timeline_plot(df, id_col="Device_ID")

            elif nav == "Analytics":
                st.header("Operator/Device Analytics")
                operator_heatmap(df)
                device_heatmap(df)
                if "Location" in df.columns:
                    st.markdown("#### Events per Location")
                    st.bar_chart(df["Location"].value_counts())

            elif nav == "Investigation":
                investigation_notes(df)

            export_buttons(df)

        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()
    else:
        st.info("Please upload a file to begin.")

# ================= MAIN CALL =================
if __name__ == "__main__":
    main()

# ======= (You can extend this file with more functions, classes, and modular analysis below) =======

# ---- Future extensibility placeholder ----
# For example: session analysis, location-based flagging, audit trails, user authentication, etc.
