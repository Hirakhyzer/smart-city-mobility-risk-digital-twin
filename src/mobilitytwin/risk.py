"""Congestion and accident-risk scoring."""

from __future__ import annotations

import numpy as np
import pandas as pd


def score_mobility_risks(simulated: pd.DataFrame) -> pd.DataFrame:
    """Score congestion, accident, and road-vulnerability risk by scenario and road segment."""
    if simulated.empty:
        return _empty_risk_table()
    grouped = simulated.groupby(["scenario", "segment_id", "from_zone", "to_zone", "road_class"], as_index=False).agg(
        mean_vehicles=("vehicles", "mean"),
        p95_vehicles=("vehicles", lambda s: float(np.percentile(s, 95))),
        mean_speed_kph=("avg_speed_kph", "mean"),
        speed_limit_kph=("speed_limit_kph", "mean"),
        mean_volume_capacity_ratio=("volume_capacity_ratio", "mean"),
        p95_volume_capacity_ratio=("volume_capacity_ratio", lambda s: float(np.percentile(s, 95))),
        incident_rate=("incident_flag", "mean"),
        mean_rain_intensity=("rain_intensity", "mean"),
        mean_heavy_vehicle_share=("heavy_vehicle_share", "mean"),
        emergency_request_count=("emergency_request_count", "sum"),
        length_km=("length_km", "mean"),
        lanes=("lanes", "mean"),
        equity_priority_score=("equity_priority_score", "mean"),
    )
    speed_drop = 1 - (grouped["mean_speed_kph"] / grouped["speed_limit_kph"].replace(0, np.nan)).fillna(0).clip(0, 1.2)
    grouped["congestion_score"] = np.clip(
        0.52 * (grouped["p95_volume_capacity_ratio"] / 1.35)
        + 0.30 * speed_drop
        + 0.18 * grouped["mean_volume_capacity_ratio"].clip(0, 1.5),
        0,
        1,
    )
    grouped["accident_risk_score"] = np.clip(
        0.34 * grouped["incident_rate"].clip(0, 1)
        + 0.24 * grouped["mean_rain_intensity"].clip(0, 1)
        + 0.20 * grouped["mean_heavy_vehicle_share"].clip(0, 0.4) / 0.4
        + 0.14 * grouped["congestion_score"]
        + 0.08 * (grouped["road_class"].isin(["arterial", "expressway"]).astype(float)),
        0,
        1,
    )
    grouped["road_vulnerability_score"] = np.clip(
        0.40 * grouped["congestion_score"]
        + 0.32 * grouped["accident_risk_score"]
        + 0.18 * grouped["equity_priority_score"].fillna(0)
        + 0.10 * (grouped["emergency_request_count"] > 0).astype(float),
        0,
        1,
    )
    grouped["mobility_risk_class"] = grouped["road_vulnerability_score"].map(_risk_class)
    grouped["risk_drivers"] = grouped.apply(_risk_drivers, axis=1)
    numeric_cols = ["mean_vehicles", "p95_vehicles", "mean_speed_kph", "mean_volume_capacity_ratio", "p95_volume_capacity_ratio", "incident_rate", "mean_rain_intensity", "mean_heavy_vehicle_share", "congestion_score", "accident_risk_score", "road_vulnerability_score"]
    grouped[numeric_cols] = grouped[numeric_cols].round(4)
    return grouped.sort_values(["road_vulnerability_score", "congestion_score"], ascending=[False, False]).reset_index(drop=True)


def _risk_class(score: float) -> str:
    if score >= 0.75:
        return "critical"
    if score >= 0.55:
        return "high"
    if score >= 0.32:
        return "medium"
    return "low"


def _risk_drivers(row: pd.Series) -> str:
    drivers = []
    if row.congestion_score >= 0.55:
        drivers.append("congestion_hotspot")
    if row.accident_risk_score >= 0.35:
        drivers.append("accident_risk")
    if row.mean_heavy_vehicle_share >= 0.16:
        drivers.append("heavy_vehicle_burden")
    if row.emergency_request_count > 0:
        drivers.append("emergency_route_pressure")
    if row.equity_priority_score >= 0.55:
        drivers.append("equity_priority_zone")
    return "|".join(drivers) if drivers else "normal_operating_range"


def _empty_risk_table() -> pd.DataFrame:
    return pd.DataFrame(columns=["scenario", "segment_id", "from_zone", "to_zone", "congestion_score", "accident_risk_score", "road_vulnerability_score", "mobility_risk_class"])
