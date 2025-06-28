from __future__ import annotations

import io
from pathlib import Path
from typing import List, Tuple

import pandas as pd
import streamlit as stimport sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.resolve()))
"""Streamlit dashboard for **POCTIFY Usage Intelligence**.

This application provides an interactive interface for analysing
point-of-care testing (POCT) middleware logs. It focuses on detecting
barcode sharing, unusual device usage and other suspicious activity that
may indicate workflow breaches or training issues.

The code is heavily commented to help NHS POCT teams understand how the
analysis works and to encourage further contributions. The high level
workflow is as follows:

1. Users upload an anonymised CSV or Excel file containing POCT events.
2. The app parses timestamps, validates required columns and assigns
   unique event identifiers.
3. Several heuristics flag potential misuse, such as rapid succession of
   tests, location conflicts and device hopping.
4. Suspicion scores are computed per operator and displayed in multiple
   views including tables, charts and heatmaps.
5. Users can filter the dataset, view timelines, add notes and download
   summary reports or graphics for offline review.

The interface is designed for audit purposes only and does not process
patient identifiable data. It should be run inside a secure hospital
network in compliance with ISO 15189 information governance.
"""

from usage_intelligence.analysis import (
    FLAG_COLUMNS,
    compute_all_flags,
    compute_scores,
    ensure_unique_event_id,
    parse_timestamps,
)
from usage_intelligence.visualization import (
    behaviour_timeline,
    device_heatmap,
    device_trend,
    export_buttons,
    flag_pie,
    heatmap_usage,
    hourly_bar,
    interval_distribution,
    operator_heatmap,
    summary_cards,
    timeline_plot,
)

# ---------------------------------------------------------------------------
# NOTE TO DEVELOPERS
# ---------------------------------------------------------------------------
# The following code is intentionally verbose with extensive comments and
# docstrings. This is to ensure the logic is transparent for NHS audit
# teams reviewing or extending the application. Although Streamlit apps
# are often compact, clarity is prioritised over brevity here. Additional
# helper functions break down each aspect of the workflow so that future
# enhancements can be slotted in with minimal refactoring.


# ---------------------------------------------------------------------------
# CONSTANTS AND CONFIGURATION
# ---------------------------------------------------------------------------

REQUIRED_COLUMNS: List[str] = [
    "Timestamp",
    "Operator_ID",
    "Location",
    "Device_ID",
    "Test_Type",
]

st.set_page_config(page_title="POCTIFY Usage Intelligence", layout="wide")

# ---------------------------------------------------------------------------
# UTILITY FUNCTIONS
# ---------------------------------------------------------------------------

def load_logo() -> None:
    """Render POCTIFY logo at the top of the sidebar if present."""
    logo_path = Path("POCTIFY Logo.png")
    if logo_path.is_file():
        st.sidebar.image(str(logo_path), width=120, use_column_width=False)

def read_uploaded_file(uploaded: io.BytesIO) -> pd.DataFrame:
    """Read CSV or Excel upload into a DataFrame."""
    name = uploaded.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded, comment="#")
    return pd.read_excel(uploaded)

def validate_columns(df: pd.DataFrame, required: List[str]) -> None:
    """Ensure dataframe contains all required columns."""
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

def apply_filters(
    df: pd.DataFrame,
    *,
    operator_ids: List[str] | None = None,
    locations: List[str] | None = None,
    devices: List[str] | None = None,
    test_types: List[str] | None = None,
    date_range: Tuple[pd.Timestamp, pd.Timestamp] | None = None,
    min_score: int = 0,
) -> pd.DataFrame:
    """Apply sidebar filters to the dataframe and return the subset.

    The filters mirror the sidebar widgets allowing users to narrow the
    dataset by operator, location, device or test type. Date ranges are
    compared against the parsed timestamp column. A minimum suspicion
    score can be supplied to focus on high risk operators only.
    """
    data = df.copy()
    if operator_ids:
        data = data[data["Operator_ID"].isin(operator_ids)]
    if locations:
        data = data[data["Location"].isin(locations)]
    if devices:
        data = data[data["Device_ID"].isin(devices)]
    if test_types:
        data = data[data["Test_Type"].isin(test_types)]
    if date_range and len(date_range) == 2:
        start, end = date_range
        data = data[
            (data["Timestamp"].dt.date >= start)
            & (data["Timestamp"].dt.date <= end)
        ]
    if min_score:
        scores = compute_scores(data)
        keep_ops = scores[scores["Suspicion_Score"] >= min_score]["Operator_ID"]
        data = data[data["Operator_ID"].isin(keep_ops)]
    return data

def sidebar_instructions() -> None:
    """Show collapsible instructions in sidebar."""
    with st.sidebar.expander("ℹ️ Instructions", expanded=False):
        st.markdown(
            """
            **POCTIFY Usage Intelligence** helps POCT teams spot barcode sharing,
            location conflicts and unusual testing patterns.

            **Steps**
            1. Download the CSV template.
            2. Upload your anonymised log file (.csv or .xlsx).
            3. Adjust the rapid succession slider to tune barcode-sharing detection.
            4. Explore dashboards and flagged results.

            Only use anonymised data. Patient names, MRNs or results must not be uploaded.
            Invalid timestamps will be reported with line numbers.
            """
        )

def sidebar_controls(df: pd.DataFrame) -> Tuple[pd.DataFrame, int, int, int]:
    """Render sidebar widgets and return filtered data and thresholds."""
    st.sidebar.header("Upload Data")
    suspicion_window = st.sidebar.slider(
        "Device sharing window (min)", 1, 30, 5, help="Window for device hopping checks"
    )
    share_threshold = st.sidebar.slider(
        "Device share threshold", 2, 10, 3, help="Unique devices in window to flag"
    )
    rapid_threshold = st.sidebar.slider(
        "Rapid succession threshold (s)", 10, 300, 60, step=10
    )
    st.sidebar.markdown("### 🔍 Filter Options")
    operator_ids = st.sidebar.multiselect(
        "Operator ID", options=sorted(df["Operator_ID"].dropna().unique())
    )
    locations = st.sidebar.multiselect(
        "Location", options=sorted(df["Location"].dropna().unique())
    )
    devices = st.sidebar.multiselect(
        "Device ID", options=sorted(df["Device_ID"].dropna().unique())
    )
    test_types = st.sidebar.multiselect(
        "Test Type", options=sorted(df["Test_Type"].dropna().unique())
    )
    # Dates default to min/max in data
    if not df.empty:
        date_range = st.sidebar.date_input(
            "Date Range",
            [df["Timestamp"].min().date(), df["Timestamp"].max().date()],
        )
    else:
        import datetime
        date_range = st.sidebar.date_input(
            "Date Range",
            [datetime.date.today(), datetime.date.today()],
        )
    min_score = st.sidebar.slider("Min Suspicion Score", 0, 100, 10)
    filtered = apply_filters(
        df,
        operator_ids=operator_ids,
        locations=locations,
        devices=devices,
        test_types=test_types,
        date_range=date_range,
        min_score=min_score,
    )
    return filtered, suspicion_window, share_threshold, rapid_threshold

# ---------------------------------------------------------------------------
# MAIN DISPLAY FUNCTIONS
# ---------------------------------------------------------------------------

def operator_overview(df: pd.DataFrame) -> None:
    """Display operator table and suspicion scores."""
    st.subheader("Operator Overview & Risk Scoring")
    stats = df.groupby("Operator_ID").agg(
        Event_Count=("Event_ID", "count"),
        Flagged_Count=("Flagged", "sum"),
    )
    flag_breakdown = df.groupby("Operator_ID")[FLAG_COLUMNS].sum()
    stats = stats.join(flag_breakdown)
    stats["Suspicion_Score"] = (
        stats["Flagged_Count"] * 2
        + stats.get("RAPID", 0) * 1.5
        + stats.get("LOC_CONFLICT", 0) * 1.25
        + stats.get("DEVICE_HOP", 0) * 1
    )
    stats = stats.sort_values("Suspicion_Score", ascending=False)
    st.dataframe(stats, use_container_width=True)
    st.bar_chart(stats["Suspicion_Score"], use_container_width=True)

def device_overview(df: pd.DataFrame) -> None:
    """Display device-centric statistics."""
    st.subheader("Device Overview & Risk Scoring")
    stats = df.groupby("Device_ID").agg(
        Event_Count=("Event_ID", "count"),
        Flagged_Count=("Flagged", "sum"),
        Operator_Count=("Operator_ID", "nunique"),
    )
    stats["Device_Risk_Score"] = (
        stats["Flagged_Count"] * 2 + stats["Operator_Count"] * 1.5
    )
    stats = stats.sort_values("Device_Risk_Score", ascending=False)
    st.dataframe(stats, use_container_width=True)
    st.bar_chart(stats["Device_Risk_Score"], use_container_width=True)

def location_overview(df: pd.DataFrame) -> None:
    """Show location-based activity summaries if location column exists."""
    if "Location" not in df.columns:
        return
    st.subheader("Location Activity")
    stats = df.groupby("Location").agg(
        Event_Count=("Event_ID", "count"),
        Flagged_Count=("Flagged", "sum"),
        Operator_Count=("Operator_ID", "nunique"),
        Device_Count=("Device_ID", "nunique"),
    )
    st.dataframe(stats, use_container_width=True)
    st.bar_chart(stats["Event_Count"], use_container_width=True)

def temporal_trends(df: pd.DataFrame) -> None:
    """Plot daily and hourly event totals for trend analysis."""
    st.subheader("Temporal Trends")
    df["Hour"] = df["Timestamp"].dt.hour
    df["Date"] = df["Timestamp"].dt.date
    hourly = df.groupby("Hour")["Event_ID"].count()
    daily = df.groupby("Date")["Event_ID"].count()
    st.line_chart(hourly, use_container_width=True)
    st.line_chart(daily, use_container_width=True)

def heatmaps(df: pd.DataFrame) -> None:
    """Render operator and device heatmaps."""
    st.subheader("Operator vs Hour Heatmap")
    st.plotly_chart(operator_heatmap(df), use_container_width=True)
    st.subheader("Device vs Hour Heatmap")
    st.plotly_chart(device_heatmap(df), use_container_width=True)

def distributions_and_outliers(df: pd.DataFrame) -> None:
    """Show distribution charts and highlight outlier operators."""
    st.subheader("Distribution: Event Count per Operator")
    st.bar_chart(df["Operator_ID"].value_counts(), use_container_width=True)
    st.subheader("Distribution: Time Between Events (minutes)")
    df_sorted = df.sort_values("Timestamp")
    df_sorted["Time_Delta"] = df_sorted["Timestamp"].diff().dt.total_seconds() / 60
    st.plotly_chart(interval_distribution(df_sorted), use_container_width=True)
    st.subheader("Operators with Unusually High Event Counts")
    op_stats = df.groupby("Operator_ID").size()
    cutoff = op_stats.mean() + 2 * op_stats.std()
    outliers = op_stats[op_stats > cutoff]
    st.dataframe(outliers, use_container_width=True)

def flag_breakdown_table(df: pd.DataFrame) -> None:
    """Display a table summarising counts per flag type."""
    st.subheader("Flag Breakdown")
    counts = pd.DataFrame(df[FLAG_COLUMNS].sum()).reset_index()
    counts.columns = ["Flag", "Count"]
    st.dataframe(counts, use_container_width=True)

def probability_summary(df: pd.DataFrame) -> None:
    """Show misuse probability for each operator."""
    st.subheader("Operator Risk Probability")
    scores = compute_scores(df)
    st.dataframe(scores[["Operator_ID", "Suspicion_Score", "Risk_Level"]], use_container_width=True)

def dashboard_charts(df: pd.DataFrame) -> None:
    """Display interactive dashboards with multiple charts."""
    st.subheader("Interactive Dashboards")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(heatmap_usage(df), use_container_width=True)
        st.plotly_chart(hourly_bar(df), use_container_width=True)
    with col2:
        st.plotly_chart(device_trend(df), use_container_width=True)
        st.plotly_chart(flag_pie(df), use_container_width=True)
    st.plotly_chart(interval_distribution(df), use_container_width=True)

def download_plots(df: pd.DataFrame) -> None:
    """Offer downloads of key visualisations as PNG files."""
    st.subheader("Download Plots")
    plot_fig = heatmap_usage(df)
    st.download_button(
        "Download Heatmap PNG",
        plot_fig.to_image(format="png"),
        file_name="heatmap.png",
    )

def drilldown_section(df: pd.DataFrame) -> None:
    """Interactive timeline views for operators and devices."""
    st.subheader("Operator Drilldown")
    st.plotly_chart(timeline_plot(df, "Operator_ID"), use_container_width=True)
    st.subheader("Device Drilldown")
    st.plotly_chart(timeline_plot(df, "Device_ID"), use_container_width=True)

def investigation_notes(df: pd.DataFrame) -> None:
    """Simple note-taking area allowing users to record observations."""
    notes = st.text_area(
        "Add investigation notes here (not stored)",
        help="Use this area to summarise findings or actions",
    )
    if notes:
        st.write("Notes saved locally in browser session.")

def about_section() -> None:
    """Display information about the project and future work."""
    st.sidebar.markdown("---")
    with st.sidebar.expander("About", expanded=False):
        st.markdown(
            """
            **POCTIFY Usage Intelligence** was created to help POCT managers
            review device usage more efficiently. Future releases will include
            automated shift pattern learning, QR code validation and direct
            middleware integrations.
            """
        )

def privacy_notice() -> None:
    """Show privacy disclaimer in sidebar."""
    with st.sidebar.expander("Privacy", expanded=False):
        st.markdown(
            """
            This tool processes anonymised audit data only. Do **not** upload
            patient names, medical record numbers or clinical results. Data is
            analysed in-memory and not retained after the browser session.
            """
        )

def future_options_placeholder() -> None:
    """Display upcoming features."""
    with st.sidebar.expander("Future Options", expanded=False):
        st.markdown(
            """
            - EQA Performance Tracker *(coming soon)*
            - Operator Login Frequency Dashboard
            - Middleware API connector module for live data
            """
        )

def main():
    """Entry point for the Streamlit application."""
    st.title("POCTIFY Usage Intelligence")
    load_logo()
    sidebar_instructions()
    privacy_notice()
    future_options_placeholder()
    st.sidebar.header("Upload File")
    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV or Excel", type=["csv", "xlsx"]
    )
    # Download template
    template_path = Path("usage_intelligence/data/template.csv")
    if template_path.is_file():
        with open(template_path, "r") as f:
            st.sidebar.download_button("Download Template", f.read(), file_name="template.csv")

    if uploaded_file is None:
        st.info("Please upload a file to begin.")
        st.stop()
    try:
        df = read_uploaded_file(uploaded_file)
        st.write("Columns in uploaded file:", df.columns.tolist())
        validate_columns(df, REQUIRED_COLUMNS)
        df = parse_timestamps(df)
        df = ensure_unique_event_id(df)
    except Exception as e:
        st.error(f"Failed to process file: {e}")
        st.stop()

    filtered, suspicion_window, share_threshold, rapid_threshold = sidebar_controls(df)
    flagged_df = compute_all_flags(
        filtered,
        rapid_th=rapid_threshold,
        hop_threshold=share_threshold,
        window_minutes=suspicion_window,
    )

    summary_cards(flagged_df)
    flag_breakdown_table(flagged_df)
    probability_summary(flagged_df)
    st.subheader("Flagged Events Table")
    st.dataframe(flagged_df[flagged_df["Flagged"]], use_container_width=True)
    operator_overview(flagged_df)
    device_overview(flagged_df)
    location_overview(flagged_df)
    temporal_trends(flagged_df)
    heatmaps(flagged_df)
    distributions_and_outliers(flagged_df)
    dashboard_charts(flagged_df)
    drilldown_section(flagged_df)
    investigation_notes(flagged_df)
    export_buttons(flagged_df)
    download_plots(flagged_df)
    about_section()
    st.markdown(
        """
        **Terms:** This tool is for internal POCT audit use only and should not be used for
        clinical decision-making. Do not upload patient names, MRNs, or clinical results.
        """
    )

if __name__ == "__main__":
    main()
