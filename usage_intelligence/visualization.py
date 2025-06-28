import pandas as pd
import plotly.express as px


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
