import pandas as pd
import plotly.express as px
from .analysis import compute_scores


def heatmap_usage(df: pd.DataFrame):
    df['Hour'] = df['Timestamp'].dt.hour
    heat = df.pivot_table(index='Operator_ID', columns='Hour', values='Device_ID', aggfunc='count', fill_value=0)
    fig = px.imshow(heat, labels=dict(color='Tests'), aspect='auto')
    return fig


def hourly_bar(df: pd.DataFrame):
    df['Hour'] = df['Timestamp'].dt.hour
    hourly = df.groupby('Hour').size().reset_index(name='Count')
    fig = px.bar(hourly, x='Hour', y='Count', title='Tests per Hour')
    return fig


def device_trend(df: pd.DataFrame):
    df['Date'] = df['Timestamp'].dt.date
    trend = df.groupby(['Date', 'Device_ID']).size().reset_index(name='Count')
    fig = px.line(trend, x='Date', y='Count', color='Device_ID', title='Device Usage Trend')
    return fig


def flag_pie(df: pd.DataFrame):
    flag_cols = [
        'RAPID',
        'LOC_CONFLICT',
        'HOURLY',
        'DEVICE_HOP',
        'SHIFT',
        'SHIFT_VIOL',
        'LOAD_DEV',
        'COLOC',
    ]
    counts = df[flag_cols].sum().reset_index()
    counts.columns = ['Flag', 'Count']
    fig = px.pie(counts, names='Flag', values='Count', title='Flag Distribution')
    return fig


def interval_distribution(df: pd.DataFrame):
    df = df.sort_values('Timestamp')
    df['Prev'] = df.groupby('Operator_ID')['Timestamp'].shift(1)
    df['Interval'] = (df['Timestamp'] - df['Prev']).dt.total_seconds()
    intervals = df['Interval'].dropna()
    fig = px.histogram(intervals, nbins=50, title='Time Between Tests (s)')
    return fig


def behaviour_timeline(df: pd.DataFrame, operator: str):
    sub = df[df['Operator_ID'] == operator].sort_values('Timestamp')
    fig = px.scatter(
        sub,
        x='Timestamp',
        y='Device_ID',
        color=sub[['RAPID', 'LOC_CONFLICT', 'COLOC']].any(axis=1).map(
            {True: 'Flagged', False: 'Normal'}
        ),
        title=f'Activity Timeline - {operator}',
    )
    return fig


def operator_heatmap(df: pd.DataFrame):
    """Heatmap of operator activity by hour."""
    df['Hour'] = df['Timestamp'].dt.hour
    heat = df.pivot_table(index='Operator_ID', columns='Hour', values='Event_ID', aggfunc='count', fill_value=0)
    fig = px.imshow(heat, aspect='auto', labels=dict(color='Tests'), title='Operator vs Hour')
    return fig


def device_heatmap(df: pd.DataFrame):
    """Heatmap of device activity by hour."""
    df['Hour'] = df['Timestamp'].dt.hour
    heat = df.pivot_table(index='Device_ID', columns='Hour', values='Event_ID', aggfunc='count', fill_value=0)
    fig = px.imshow(heat, aspect='auto', labels=dict(color='Tests'), title='Device vs Hour')
    return fig


def timeline_plot(df: pd.DataFrame, id_col: str = 'Operator_ID'):
    """Scatter plot timeline for a given identifier column."""
    ids = df[id_col].unique()
    fig = px.scatter(
        df,
        x='Timestamp',
        y=id_col,
        color=df[['RAPID', 'LOC_CONFLICT', 'COLOC']].any(axis=1).map({True: 'Flagged', False: 'Normal'}),
        hover_data=['Device_ID', 'Location'],
        title=f'Timeline by {id_col}',
    )
    fig.update_yaxes(categoryorder='array', categoryarray=sorted(ids))
    return fig


def summary_cards(df: pd.DataFrame):
    """Display high level metrics using Streamlit's columns."""
    import streamlit as st

    total_events = int(len(df))
    flagged_events = int(df['Flagged'].sum())
    unique_ops = df['Operator_ID'].nunique()
    unique_devices = df['Device_ID'].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Total Events', total_events)
    col2.metric('Flagged Events', flagged_events)
    col3.metric('Operators', unique_ops)
    col4.metric('Devices', unique_devices)


def export_buttons(df: pd.DataFrame):
    """Provide download buttons for flagged data and scores."""
    import streamlit as st

    flagged_csv = df[df['Flagged']].to_csv(index=False)
    st.download_button('Download Flags CSV', flagged_csv, file_name='flagged_summary.csv')
    score_csv = compute_scores(df).to_csv(index=False)
    st.download_button('Download Operator Scores', score_csv, file_name='operator_scores.csv')
