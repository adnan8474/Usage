import pandas as pd
import numpy as np
from scipy import stats
from typing import List, Dict

FLAG_WEIGHTS = {
    'RAPID': 30,
    'LOC_CONFLICT': 30,
    'HOURLY': 20,
    'DEVICE_HOP': 10,
    'SHIFT': 10,
}


def parse_timestamps(df: pd.DataFrame, column: str = 'Timestamp') -> pd.DataFrame:
    """Parse timestamps using multiple formats."""
    df = df.copy()
    df[column] = pd.to_datetime(df[column], errors='coerce', dayfirst=True, utc=True)
    if df[column].isna().any():
        raise ValueError('Invalid timestamps detected. Please use DD/MM/YYYY HH:MM or ISO formats.')
    return df


def rapid_succession(df: pd.DataFrame, threshold: int = 60) -> pd.DataFrame:
    df = df.sort_values('Timestamp')
    df['Prev_Time'] = df.groupby('Operator_ID')['Timestamp'].shift(1)
    df['Diff'] = (df['Timestamp'] - df['Prev_Time']).dt.total_seconds()
    df['RAPID'] = df['Diff'] < threshold
    return df.drop(columns=['Prev_Time', 'Diff'])


def location_conflict(df: pd.DataFrame, travel_threshold: int = 300) -> pd.DataFrame:
    df = df.sort_values('Timestamp')
    df['Prev_Time'] = df.groupby('Operator_ID')['Timestamp'].shift(1)
    df['Prev_Location'] = df.groupby('Operator_ID')['Location'].shift(1)
    df['Time_Diff'] = (df['Timestamp'] - df['Prev_Time']).dt.total_seconds()
    df['LOC_CONFLICT'] = (df['Location'] != df['Prev_Location']) & (df['Time_Diff'] < travel_threshold)
    return df.drop(columns=['Prev_Time', 'Prev_Location', 'Time_Diff'])


def hourly_density(df: pd.DataFrame) -> pd.DataFrame:
    df['Hour'] = df['Timestamp'].dt.hour
    hourly = df.groupby(['Operator_ID', 'Hour']).size().reset_index(name='Count')
    hourly['Z'] = hourly.groupby('Operator_ID')['Count'].transform(lambda x: stats.zscore(x, nan_policy='omit'))
    hourly['HOURLY'] = hourly['Z'] > 2
    df = df.merge(hourly[['Operator_ID', 'Hour', 'HOURLY']], on=['Operator_ID', 'Hour'], how='left')
    return df.drop(columns=['Hour'])


def device_hopping(df: pd.DataFrame, hop_threshold: int = 3, window_minutes: int = 5) -> pd.DataFrame:
    df = df.sort_values('Timestamp')
    windows = []
    for op, group in df.groupby('Operator_ID'):
        times = group['Timestamp']
        devices = group['Device_ID']
        counts = []
        for idx, ts in enumerate(times):
            start = ts - pd.Timedelta(minutes=window_minutes)
            mask = (times >= start) & (times <= ts)
            counts.append(devices[mask].nunique())
        windows.extend(counts)
    df['DEVICES_WINDOW'] = windows
    df['DEVICE_HOP'] = df['DEVICES_WINDOW'] > hop_threshold
    return df.drop(columns=['DEVICES_WINDOW'])


def shift_consistency(df: pd.DataFrame) -> pd.DataFrame:
    df['Shift'] = df['Timestamp'].dt.floor('8H')
    shift_counts = df.groupby(['Operator_ID', 'Shift']).size().reset_index(name='Shift_Count')
    median_shift = shift_counts.groupby('Operator_ID')['Shift_Count'].median()
    shift_counts = shift_counts.join(median_shift, on='Operator_ID', rsuffix='_MED')
    shift_counts['SHIFT'] = abs(shift_counts['Shift_Count'] - shift_counts['Shift_Count_MED']) > 3
    df = df.merge(shift_counts[['Operator_ID', 'Shift', 'SHIFT']], on=['Operator_ID', 'Shift'], how='left')
    return df.drop(columns=['Shift'])


def apply_flags(df: pd.DataFrame, rapid_th: int = 60) -> pd.DataFrame:
    df = rapid_succession(df, rapid_th)
    df = location_conflict(df)
    df = hourly_density(df)
    df = device_hopping(df)
    df = shift_consistency(df)
    return df


def compute_scores(df: pd.DataFrame) -> pd.DataFrame:
    flags = ['RAPID', 'LOC_CONFLICT', 'HOURLY', 'DEVICE_HOP', 'SHIFT']
    score_df = df.groupby('Operator_ID')[flags].sum().reset_index()
    for f in flags:
        score_df[f] = score_df[f] * FLAG_WEIGHTS[f]
    score_df['Suspicion_Score'] = score_df[flags].sum(axis=1)
    score_df['Total_Tests'] = df.groupby('Operator_ID').size().values
    score_df = score_df.sort_values('Suspicion_Score', ascending=False)
    return score_df
