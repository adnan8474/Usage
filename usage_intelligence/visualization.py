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
    flag_cols = ['RAPID', 'LOC_CONFLICT', 'HOURLY', 'DEVICE_HOP', 'SHIFT']
    counts = df[flag_cols].sum().reset_index()
    counts.columns = ['Flag', 'Count']
    fig = px.pie(counts, names='Flag', values='Count', title='Flag Distribution')
    return fig
