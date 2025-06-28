import pandas as pd
import numpy as np
from datetime import timedelta

def parse_timestamps(df):
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    return df

def apply_flags(df, suspicion_window, share_threshold, rapid_threshold, custom_rules=None):
    # Flag: Barcode used by >share_threshold operators within suspicion_window minutes
    events = []
    flagged = pd.DataFrame()
    for barcode, sub in df.groupby('Barcode'):
        sub = sub.sort_values('Timestamp')
        for idx, row in sub.iterrows():
            window = sub[(sub['Timestamp'] >= row['Timestamp'] - timedelta(minutes=suspicion_window)) &
                         (sub['Timestamp'] <= row['Timestamp'] + timedelta(minutes=suspicion_window))]
            n_operators = window['Operator_ID'].nunique()
            if n_operators >= share_threshold:
                events.append({**row.to_dict(), "Flag": "Shared barcode", "OperatorsInWindow": n_operators})
    flagged = pd.DataFrame(events)
    # Flag: Rapid succession
    df = df.sort_values(['Barcode', 'Timestamp'])
    df['DeltaSec'] = df.groupby('Barcode')['Timestamp'].diff().dt.total_seconds().fillna(np.inf)
    rapid = df[df['DeltaSec'] < rapid_threshold]
    if not rapid.empty:
        rapid = rapid.assign(Flag="Rapid succession")
        flagged = pd.concat([flagged, rapid], ignore_index=True)
    # Custom user rules
    if custom_rules:
        for rule in custom_rules:
            flagged = pd.concat([flagged, rule(df)], ignore_index=True)
    flagged.reset_index(drop=True, inplace=True)
    flagged['Event_ID'] = flagged.index + 1
    return flagged, flagged

def compute_scores(events):
    # Example: Each flag increases suspicion score
    events['Suspicion_Score'] = 10
    events.loc[events['Flag'] == 'Shared barcode', 'Suspicion_Score'] += 40
    events.loc[events['Flag'] == 'Rapid succession', 'Suspicion_Score'] += 20
    return events

def detect_sessions(events):
    # Group by barcode and time windows to create unique session IDs
    events = events.sort_values(['Barcode', 'Timestamp'])
    events['Session_ID'] = (events['Barcode'].astype(str) + "_" +
                            events['Timestamp'].dt.floor('30T').astype(str))
    return events

def filter_events(events, sidebar):
    # Add filters for operator, barcode, flag, date, etc.
    ops = sidebar.multiselect("Filter Operator", options=sorted(events['Operator_ID'].unique()))
    barcodes = sidebar.multiselect("Filter Barcode", options=sorted(events['Barcode'].unique()))
    flags = sidebar.multiselect("Filter Flag", options=sorted(events['Flag'].unique()))
    if ops:
        events = events[events['Operator_ID'].isin(ops)]
    if barcodes:
        events = events[events['Barcode'].isin(barcodes)]
    if flags:
        events = events[events['Flag'].isin(flags)]
    return events

def session_summary(sessions):
    # Summarize sessions for quick review
    return sessions.groupby('Session_ID').agg({
        'Timestamp': ['min', 'max', 'count'],
        'Operator_ID': pd.Series.nunique,
        'Barcode': 'first'
    }).reset_index()
