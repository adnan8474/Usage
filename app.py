import streamlit as st
import pandas as pd
from pathlib import Path
import datetime
from usage_intelligence.analysis import (
    parse_timestamps, apply_flags, compute_scores, detect_sessions, filter_events, session_summary
)
from usage_intelligence.visualization import (
    barcode_timeline, barcode_heatmap, operator_heatmap, session_drilldown, summary_cards, rules_panel, investigation_notes, event_table
)
from usage_intelligence.rules import RULES, user_rule_builder
from usage_intelligence.investigation import InvestigationTracker

# --- PAGE CONFIG ---
st.set_page_config(page_title="POCTIFY Barcode Audit Suite", layout="wide", initial_sidebar_state="expanded")
st.title("POCTIFY Barcode Audit Suite")

# --- SIDEBAR LOGO & INSTRUCTIONS ---
def show_logo(logo_path: Path) -> None:
    if logo_path.is_file():
        st.sidebar.image(str(logo_path), use_container_width=True)

def show_instructions():
    st.sidebar.markdown("""
        ## How to Use
        1. Upload anonymized data.
        2. Adjust detection rules.
        3. Review flagged events, sessions, and operator/device analytics.
        4. Drill down, annotate, and export for audit.
        5. Track progress of investigations.
        ---
        **No patient identifiers should ever be uploaded.**
    """)

# --- DATA UPLOAD & PARAMS ---
def sidebar_upload_and_params():
    st.sidebar.header("Upload Data")
    uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])
    st.sidebar.markdown("---")
    with open("usage_intelligence/data/template.csv", "r") as f:
        st.sidebar.download_button("Download Template", f.read(), file_name="template.csv")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Detection Parameters")
    suspicion_window = st.sidebar.slider("Window for barcode reuse (minutes)", 1, 120, 10)
    share_threshold = st.sidebar.slider("Flag if used by more than X operators in window", 1, 5, 2)
    rapid_threshold = st.sidebar.slider("Rapid test threshold (seconds)", 10, 300, 60)
    return uploaded_file, suspicion_window, share_threshold, rapid_threshold

# --- MAIN APP ---
def main():
    logo_path = Path("POCTIFY Logo.png")
    show_logo(logo_path)
    show_instructions()
    uploaded_file, suspicion_window, share_threshold, rapid_threshold = sidebar_upload_and_params()
    tracker = InvestigationTracker()

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
        df = parse_timestamps(df)
        # --- Flag barcode misuse ---
        flagged, events = apply_flags(
            df, suspicion_window, share_threshold, rapid_threshold, custom_rules=RULES
        )
        scores = compute_scores(events)
        sessions = detect_sessions(events)
        filtered = filter_events(events, st.sidebar)
        summary_cards(filtered)
        
        # --- NAVIGATION ---
        nav = st.sidebar.radio("Navigate", ["Flagged Events", "Barcodes", "Operators", "Sessions", "Analytics", "Rules", "Investigation"])
        if nav == "Flagged Events":
            st.header("Flagged Barcode Events")
            st.dataframe(event_table(filtered), use_container_width=True)
            st.plotly_chart(barcode_heatmap(filtered))
            st.plotly_chart(operator_heatmap(filtered))
            st.plotly_chart(barcode_timeline(filtered))
            barcode = st.selectbox("Review barcode:", filtered['Barcode'].unique())
            st.plotly_chart(barcode_timeline(filtered, barcode))
        elif nav == "Barcodes":
            st.header("Barcode Drilldown")
            barcode = st.selectbox("Select Barcode", flagged['Barcode'].unique())
            st.plotly_chart(barcode_timeline(events, barcode))
            st.dataframe(filtered[filtered['Barcode'] == barcode])
            st.markdown("#### Session Drilldown")
            st.plotly_chart(session_drilldown(sessions, barcode))
        elif nav == "Operators":
            st.header("Operator Drilldown")
            operator = st.selectbox("Select Operator", flagged['Operator_ID'].unique())
            st.plotly_chart(operator_heatmap(events, operator))
            st.dataframe(filtered[filtered['Operator_ID'] == operator])
        elif nav == "Sessions":
            st.header("Suspicious Sessions")
            st.dataframe(session_summary(sessions))
            session_id = st.selectbox("Review Session ID", sessions['Session_ID'].unique())
            st.dataframe(sessions[sessions['Session_ID'] == session_id])
        elif nav == "Analytics":
            st.header("Analytics & Trends")
            st.plotly_chart(barcode_heatmap(events))
            st.plotly_chart(operator_heatmap(events))
            st.plotly_chart(barcode_timeline(events))
        elif nav == "Rules":
            st.header("Detection Rules")
            rules_panel(RULES)
            user_rule_builder()
        elif nav == "Investigation":
            st.header("Investigation Tracker")
            st.dataframe(tracker.get_investigations(events))
            event_id = st.selectbox("Select Event", events['Event_ID'])
            investigation_notes(tracker, event_id)
        
        st.sidebar.markdown("---")
        st.sidebar.download_button("Export Flagged", filtered.to_csv(index=False), file_name="flagged_events.csv")
        st.sidebar.download_button("Export Sessions", sessions.to_csv(index=False), file_name="sessions.csv")
    else:
        st.info("Please upload a file to begin.")

if __name__ == "__main__":
    main()
