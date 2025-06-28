import streamlit as st
import plotly.express as px

def summary_cards(events):
    """Display key metrics summarising the flagged dataset."""
    st.metric("Flagged Events", len(events))
    if "Barcode" in events.columns:
        st.metric("Unique Barcodes Flagged", events["Barcode"].nunique())
    st.metric("Operators Flagged", events["Operator_ID"].nunique())

def barcode_heatmap(events, barcode=None):
    data = events if barcode is None else events[events['Barcode'] == barcode]
    heat = data.groupby(['Barcode', 'Operator_ID']).size().reset_index(name='Count')
    fig = px.density_heatmap(heat, x='Barcode', y='Operator_ID', z='Count', color_continuous_scale='Reds')
    return fig

def operator_heatmap(events, operator=None):
    data = events if operator is None else events[events['Operator_ID'] == operator]
    heat = data.groupby(['Operator_ID', 'Device_ID']).size().reset_index(name='Count')
    fig = px.density_heatmap(heat, x='Operator_ID', y='Device_ID', z='Count', color_continuous_scale='Blues')
    return fig

def barcode_timeline(events, barcode=None):
    data = events if barcode is None else events[events['Barcode'] == barcode]
    fig = px.scatter(data, x='Timestamp', y='Operator_ID', color='Device_ID', hover_data=['Flag'])
    return fig

def session_drilldown(sessions, barcode):
    data = sessions[sessions['Barcode'] == barcode]
    fig = px.timeline(data, x_start='Timestamp', x_end='Timestamp', y='Operator_ID', color='Session_ID')
    return fig

def rules_panel(rules):
    st.markdown("### Active Detection Rules")
    for rule in rules:
        st.write(f"- {rule.__doc__ or rule.__name__}")

def event_table(events):
    """Return a tidy dataframe for display of flagged events."""
    cols = ["Timestamp", "Operator_ID", "Device_ID", "Flag", "Suspicion_Score"]
    if "Barcode" in events.columns:
        cols.insert(1, "Barcode")
    return events[cols]

def investigation_notes(tracker, event_id):
    st.markdown("### Investigation Notes")
    notes = tracker.get_notes(event_id)
    new_note = st.text_area("Add note", "")
    if st.button("Save Note"):
        tracker.add_note(event_id, new_note)
        st.success("Note saved.")


def heatmap_usage(df):
    """Heatmap of operator vs device usage counts."""
    heat = df.groupby(["Operator_ID", "Device_ID"]).size().reset_index(name="Count")
    fig = px.density_heatmap(
        heat,
        x="Device_ID",
        y="Operator_ID",
        z="Count",
        color_continuous_scale="Viridis",
    )
    return fig


def device_heatmap(df):
    df = df.copy()
    df["Hour"] = df["Timestamp"].dt.hour
    heat = df.groupby(["Device_ID", "Hour"]).size().reset_index(name="Count")
    fig = px.density_heatmap(
        heat,
        x="Hour",
        y="Device_ID",
        z="Count",
        color_continuous_scale="YlOrRd",
    )
    return fig


def operator_heatmap(events, operator=None):
    data = events if operator is None else events[events['Operator_ID'] == operator]
    heat = data.groupby(['Operator_ID', 'Device_ID']).size().reset_index(name='Count')
    fig = px.density_heatmap(heat, x='Operator_ID', y='Device_ID', z='Count', color_continuous_scale='Blues')
    return fig


def hourly_bar(df):
    df = df.copy()
    df["Hour"] = df["Timestamp"].dt.hour
    counts = df.groupby("Hour").size().reset_index(name="Count")
    fig = px.bar(counts, x="Hour", y="Count")
    return fig


def device_trend(df):
    df = df.copy()
    df["Date"] = df["Timestamp"].dt.date
    counts = df.groupby(["Date", "Device_ID"]).size().reset_index(name="Count")
    fig = px.line(counts, x="Date", y="Count", color="Device_ID")
    return fig


def flag_pie(df):
    flags = df[[c for c in df.columns if c in {"RAPID", "LOC_CONFLICT", "DEVICE_HOP"}]]
    counts = flags.sum().reset_index()
    counts.columns = ["Flag", "Count"]
    fig = px.pie(counts, values="Count", names="Flag")
    return fig


def interval_distribution(df):
    if "Time_Delta" not in df.columns:
        df = df.sort_values("Timestamp")
        df["Time_Delta"] = df["Timestamp"].diff().dt.total_seconds() / 60
    fig = px.histogram(df, x="Time_Delta", nbins=50)
    return fig


def timeline_plot(df, column):
    fig = px.scatter(
        df.sort_values("Timestamp"),
        x="Timestamp",
        y=column,
        color="Flagged",
        hover_data=["Operator_ID", "Device_ID", "Location"],
    )
    return fig


def behaviour_timeline(df, column="Operator_ID"):
    """Simpler wrapper around ``timeline_plot`` for backwards compatibility."""
    return timeline_plot(df, column)


def export_buttons(df):
    csv = df.to_csv(index=False)
    st.download_button("Download CSV", csv, file_name="flagged_events.csv")
