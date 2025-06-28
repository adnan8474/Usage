from __future__ import annotations

"""Core analytics for the POCTIFY Usage Intelligence dashboard."""

from datetime import timedelta
from typing import Iterable

import pandas as pd

FLAG_COLUMNS = ["RAPID", "LOC_CONFLICT", "DEVICE_HOP"]


def parse_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """Parse the ``Timestamp`` column and report any failures."""
    parsed = pd.to_datetime(df["Timestamp"], errors="coerce")
    if parsed.isna().any():
        bad_rows = (parsed.isna()).nonzero()[0].tolist()
        raise ValueError(f"Invalid timestamps at rows: {bad_rows}")
    df["Timestamp"] = parsed
    return df


def ensure_unique_event_id(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure the dataframe has a unique ``Event_ID`` column."""
    if "Event_ID" not in df.columns or df["Event_ID"].duplicated().any():
        df = df.reset_index(drop=True)
        df["Event_ID"] = range(1, len(df) + 1)
    return df


def _flag_rapid(df: pd.DataFrame, threshold: int) -> pd.Series:
    diff = df.groupby("Operator_ID")["Timestamp"].diff().dt.total_seconds()
    return diff.notna() & (diff < threshold)


def _flag_loc_conflict(df: pd.DataFrame, window: int) -> pd.Series:
    prev_loc = df.groupby("Operator_ID")["Location"].shift()
    prev_time = df.groupby("Operator_ID")["Timestamp"].shift()
    time_delta = (df["Timestamp"] - prev_time).dt.total_seconds() / 60
    return (
        prev_loc.notna()
        & (prev_loc != df["Location"])
        & (time_delta.abs() <= window)
    )


def _flag_device_hop(df: pd.DataFrame, threshold: int, window: int) -> pd.Series:
    flags = pd.Series(False, index=df.index)
    for op, sub in df.groupby("Operator_ID"):
        idx = sub.index
        times = sub["Timestamp"]
        for i, t in enumerate(times):
            start = t - timedelta(minutes=window)
            end = t + timedelta(minutes=window)
            window_devices = sub.loc[(times >= start) & (times <= end), "Device_ID"].nunique()
            if window_devices >= threshold:
                flags.loc[idx[i]] = True
    return flags


def compute_all_flags(
    df: pd.DataFrame,
    *,
    rapid_th: int = 60,
    hop_threshold: int = 3,
    window_minutes: int = 5,
) -> pd.DataFrame:
    """Compute all misuse flags and return the annotated dataframe."""
    data = df.copy()
    data = ensure_unique_event_id(data)
    data = data.sort_values("Timestamp")

    data["RAPID"] = _flag_rapid(data, rapid_th)
    data["LOC_CONFLICT"] = _flag_loc_conflict(data, window_minutes)
    data["DEVICE_HOP"] = _flag_device_hop(data, hop_threshold, window_minutes)
    data["Flagged"] = data[FLAG_COLUMNS].any(axis=1)
    return data


def compute_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate a suspicion score for each operator."""
    grouped = df.groupby("Operator_ID").agg(
        Flagged_Count=("Flagged", "sum"),
        RAPID=("RAPID", "sum"),
        LOC_CONFLICT=("LOC_CONFLICT", "sum"),
        DEVICE_HOP=("DEVICE_HOP", "sum"),
    )
    grouped["Suspicion_Score"] = (
        grouped["Flagged_Count"] * 2
        + grouped["RAPID"] * 1.5
        + grouped["LOC_CONFLICT"] * 1.25
        + grouped["DEVICE_HOP"] * 1
    )

    def risk(score: float) -> str:
        if score >= 75:
            return "High"
        if score >= 40:
            return "Medium"
        return "Low"

    grouped["Risk_Level"] = grouped["Suspicion_Score"].apply(risk)
    return grouped.reset_index()


# ---------------------------------------------------------------------------
# Legacy helper functions retained for potential extensions
# ---------------------------------------------------------------------------

def apply_flags(
    df: pd.DataFrame,
    suspicion_window: int,
    share_threshold: int,
    rapid_threshold: int,
    custom_rules: Iterable | None = None,
):
    """Backwards compatible flagging helper."""
    events = []
    flagged = pd.DataFrame()
    for barcode, sub in df.groupby("Barcode"):
        sub = sub.sort_values("Timestamp")
        for _, row in sub.iterrows():
            window = sub[
                (sub["Timestamp"] >= row["Timestamp"] - timedelta(minutes=suspicion_window))
                & (sub["Timestamp"] <= row["Timestamp"] + timedelta(minutes=suspicion_window))
            ]
            n_operators = window["Operator_ID"].nunique()
            if n_operators >= share_threshold:
                events.append({**row.to_dict(), "Flag": "Shared barcode", "OperatorsInWindow": n_operators})
    flagged = pd.DataFrame(events)
    df = df.sort_values(["Barcode", "Timestamp"])
    df["DeltaSec"] = df.groupby("Barcode")["Timestamp"].diff().dt.total_seconds().fillna(float("inf"))
    rapid = df[df["DeltaSec"] < rapid_threshold]
    if not rapid.empty:
        rapid = rapid.assign(Flag="Rapid succession")
        flagged = pd.concat([flagged, rapid], ignore_index=True)
    if custom_rules:
        for rule in custom_rules:
            flagged = pd.concat([flagged, rule(df)], ignore_index=True)
    flagged.reset_index(drop=True, inplace=True)
    flagged["Event_ID"] = flagged.index + 1
    return flagged, flagged


def detect_sessions(events: pd.DataFrame) -> pd.DataFrame:
    events = events.sort_values(["Barcode", "Timestamp"])
    events["Session_ID"] = events["Barcode"].astype(str) + "_" + events["Timestamp"].dt.floor("30T").astype(str)
    return events


def filter_events(events: pd.DataFrame, sidebar) -> pd.DataFrame:
    ops = sidebar.multiselect("Filter Operator", options=sorted(events["Operator_ID"].unique()))
    barcodes = sidebar.multiselect("Filter Barcode", options=sorted(events["Barcode"].unique()))
    flags = sidebar.multiselect("Filter Flag", options=sorted(events["Flag"].unique()))
    if ops:
        events = events[events["Operator_ID"].isin(ops)]
    if barcodes:
        events = events[events["Barcode"].isin(barcodes)]
    if flags:
        events = events[events["Flag"].isin(flags)]
    return events


def session_summary(sessions: pd.DataFrame) -> pd.DataFrame:
    return (
        sessions.groupby("Session_ID").agg(
            Timestamp=["min", "max", "count"],
            Operator_ID=pd.Series.nunique,
            Barcode="first",
        ).reset_index()
    )
