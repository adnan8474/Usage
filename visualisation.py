import streamlit as st
import plotly.express as px

def summary_cards(events):
    st.metric("Flagged Events", len(events))
    st.metric("Unique Barcodes Flagged", events['Barcode'].nunique())
    st.metric("Operators Flagged", events['Operator_ID'].nunique())

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
    return events[['Timestamp', 'Barcode', 'Operator_ID', 'Device_ID', 'Flag', 'Suspicion_Score']]

def investigation_notes(tracker, event_id):
    st.markdown("### Investigation Notes")
    notes = tracker.get_notes(event_id)
    new_note = st.text_area("Add note", "")
    if st.button("Save Note"):
        tracker.add_note(event_id, new_note)
        st.success("Note saved.")
