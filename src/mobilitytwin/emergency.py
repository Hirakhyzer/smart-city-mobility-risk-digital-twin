"""Emergency route delay audit for the synthetic city network."""

from __future__ import annotations

import numpy as np
import pandas as pd


def emergency_route_audit(zones: pd.DataFrame, roads: pd.DataFrame, facilities: pd.DataFrame, simulated: pd.DataFrame) -> pd.DataFrame:
    """Estimate emergency response delay pressure by origin zone and scenario."""
    if simulated.empty:
        return pd.DataFrame(columns=["scenario", "zone_id", "estimated_response_delay_min", "emergency_route_risk"])
    facility_counts = facilities.groupby("zone_id").size().rename("facility_count").reset_index()
    emergency_facility_counts = facilities.loc[facilities["facility_type"].isin(["hospital", "fire_station", "ambulance_depot"])].groupby("zone_id").size().rename("emergency_facility_count").reset_index()
    enriched_zones = zones.merge(facility_counts, on="zone_id", how="left").merge(emergency_facility_counts, on="zone_id", how="left")
    enriched_zones[["facility_count", "emergency_facility_count"]] = enriched_zones[["facility_count", "emergency_facility_count"]].fillna(0)

    grouped = simulated.groupby(["scenario", "from_zone"], as_index=False).agg(
        mean_speed_kph=("avg_speed_kph", "mean"),
        p10_speed_kph=("avg_speed_kph", lambda s: float(np.percentile(s, 10))),
        mean_vcr=("volume_capacity_ratio", "mean"),
        incident_rate=("incident_flag", "mean"),
        emergency_request_count=("emergency_request_count", "sum"),
        emergency_corridor_share=("emergency_corridor", "mean"),
        mean_length_km=("length_km", "mean"),
    ).rename(columns={"from_zone": "zone_id"})
    out = grouped.merge(enriched_zones[["zone_id", "income_index", "transit_access_index", "equity_priority_score", "emergency_facility_count"]], on="zone_id", how="left")
    base_travel = (out["mean_length_km"] / out["p10_speed_kph"].clip(lower=5)) * 60
    congestion_penalty = 1 + 0.65 * out["mean_vcr"].clip(0, 1.8) + 0.70 * out["incident_rate"].clip(0, 1)
    facility_relief = 1 - 0.10 * out["emergency_facility_count"].clip(0, 3)
    corridor_relief = 1 - 0.18 * out["emergency_corridor_share"].clip(0, 1)
    out["estimated_response_delay_min"] = (base_travel * congestion_penalty * facility_relief * corridor_relief).clip(lower=1.0)
    out["emergency_route_risk"] = np.clip(
        0.43 * (out["estimated_response_delay_min"] / 18)
        + 0.25 * out["incident_rate"].clip(0, 1)
        + 0.20 * out["equity_priority_score"].fillna(0)
        + 0.12 * (out["emergency_request_count"] > 0).astype(float),
        0,
        1,
    )
    out["emergency_risk_class"] = out["emergency_route_risk"].map(_risk_class)
    numeric_cols = ["mean_speed_kph", "p10_speed_kph", "mean_vcr", "incident_rate", "estimated_response_delay_min", "emergency_route_risk"]
    out[numeric_cols] = out[numeric_cols].round(4)
    return out.sort_values(["emergency_route_risk", "estimated_response_delay_min"], ascending=[False, False]).reset_index(drop=True)


def _risk_class(score: float) -> str:
    if score >= 0.75:
        return "critical"
    if score >= 0.55:
        return "high"
    if score >= 0.32:
        return "medium"
    return "low"
