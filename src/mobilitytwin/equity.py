"""Transport equity audit for synthetic mobility scenarios."""

from __future__ import annotations

import numpy as np
import pandas as pd


def transport_equity_audit(
    zones: pd.DataFrame,
    transit_stops: pd.DataFrame,
    risk: pd.DataFrame,
    emissions: pd.DataFrame,
    emergency: pd.DataFrame,
) -> pd.DataFrame:
    """Measure whether mobility burden is concentrated in high-priority zones."""
    transit = transit_stops.groupby("zone_id", as_index=False).agg(
        transit_stop_count=("stop_id", "count"),
        mean_service_frequency=("service_frequency_per_hour", "mean"),
        accessible_stop_share=("accessible_stop", "mean"),
    ) if not transit_stops.empty else pd.DataFrame(columns=["zone_id", "transit_stop_count", "mean_service_frequency", "accessible_stop_share"])
    zone_base = zones.merge(transit, on="zone_id", how="left")
    zone_base[["transit_stop_count", "mean_service_frequency", "accessible_stop_share"]] = zone_base[["transit_stop_count", "mean_service_frequency", "accessible_stop_share"]].fillna(0)

    risk_zone = risk.groupby(["scenario", "from_zone"], as_index=False).agg(
        mean_congestion_score=("congestion_score", "mean"),
        mean_accident_risk_score=("accident_risk_score", "mean"),
        mean_road_vulnerability_score=("road_vulnerability_score", "mean"),
        high_risk_segment_count=("mobility_risk_class", lambda s: int(s.isin(["high", "critical"]).sum())),
    ).rename(columns={"from_zone": "zone_id"})
    emissions_zone = emissions.groupby(["scenario", "from_zone"], as_index=False).agg(
        total_emissions_kg_co2e=("emissions_kg_co2e", "sum"),
        mean_emissions_burden_score=("emissions_burden_score", "mean"),
    ).rename(columns={"from_zone": "zone_id"})
    emergency_zone = emergency[["scenario", "zone_id", "estimated_response_delay_min", "emergency_route_risk"]]

    out = risk_zone.merge(emissions_zone, on=["scenario", "zone_id"], how="left").merge(emergency_zone, on=["scenario", "zone_id"], how="left").merge(zone_base, on="zone_id", how="left")
    for col in ["mean_emissions_burden_score", "emergency_route_risk", "estimated_response_delay_min"]:
        out[col] = out[col].fillna(0.0)
    transit_gap = np.clip(1 - out["transit_access_index"].fillna(0), 0, 1)
    out["transport_equity_burden_score"] = np.clip(
        0.25 * out["mean_congestion_score"].fillna(0)
        + 0.20 * out["mean_accident_risk_score"].fillna(0)
        + 0.18 * out["mean_emissions_burden_score"].fillna(0)
        + 0.18 * out["emergency_route_risk"].fillna(0)
        + 0.19 * transit_gap,
        0,
        1,
    )
    city_avg = out.groupby("scenario")["transport_equity_burden_score"].transform("mean")
    out["equity_gap_vs_city_mean"] = out["transport_equity_burden_score"] - city_avg
    out["equity_review_flag"] = ((out["equity_priority_score"].fillna(0) >= 0.50) & (out["equity_gap_vs_city_mean"] > 0.03)).astype(int)
    out["equity_risk_class"] = out["transport_equity_burden_score"].map(_risk_class)
    numeric_cols = ["mean_congestion_score", "mean_accident_risk_score", "mean_road_vulnerability_score", "total_emissions_kg_co2e", "mean_emissions_burden_score", "estimated_response_delay_min", "emergency_route_risk", "transport_equity_burden_score", "equity_gap_vs_city_mean"]
    out[numeric_cols] = out[numeric_cols].round(4)
    return out.sort_values(["equity_review_flag", "transport_equity_burden_score"], ascending=[False, False]).reset_index(drop=True)


def _risk_class(score: float) -> str:
    if score >= 0.75:
        return "critical"
    if score >= 0.55:
        return "high"
    if score >= 0.32:
        return "medium"
    return "low"
