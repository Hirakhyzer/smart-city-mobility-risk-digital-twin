"""Scenario comparison and summary metrics."""

from __future__ import annotations

import pandas as pd


def scenario_comparison(risk: pd.DataFrame, emissions: pd.DataFrame, emergency: pd.DataFrame, equity: pd.DataFrame) -> pd.DataFrame:
    """Aggregate scenario-level mobility, safety, emissions, emergency, and equity metrics."""
    risk_summary = risk.groupby("scenario", as_index=False).agg(
        mean_congestion_score=("congestion_score", "mean"),
        mean_accident_risk_score=("accident_risk_score", "mean"),
        mean_road_vulnerability_score=("road_vulnerability_score", "mean"),
        high_or_critical_segments=("mobility_risk_class", lambda s: int(s.isin(["high", "critical"]).sum())),
    )
    emissions_summary = emissions.groupby("scenario", as_index=False).agg(
        total_emissions_kg_co2e=("emissions_kg_co2e", "sum"),
        mean_emissions_burden_score=("emissions_burden_score", "mean"),
    )
    emergency_summary = emergency.groupby("scenario", as_index=False).agg(
        mean_response_delay_min=("estimated_response_delay_min", "mean"),
        mean_emergency_route_risk=("emergency_route_risk", "mean"),
        high_emergency_risk_zones=("emergency_risk_class", lambda s: int(s.isin(["high", "critical"]).sum())),
    )
    equity_summary = equity.groupby("scenario", as_index=False).agg(
        mean_transport_equity_burden_score=("transport_equity_burden_score", "mean"),
        equity_review_zone_count=("equity_review_flag", "sum"),
        max_equity_gap_vs_city_mean=("equity_gap_vs_city_mean", "max"),
    )
    out = risk_summary.merge(emissions_summary, on="scenario", how="left").merge(emergency_summary, on="scenario", how="left").merge(equity_summary, on="scenario", how="left")
    out["planning_score"] = (
        1
        - 0.24 * out["mean_congestion_score"]
        - 0.20 * out["mean_accident_risk_score"]
        - 0.18 * out["mean_emissions_burden_score"]
        - 0.20 * out["mean_emergency_route_risk"]
        - 0.18 * out["mean_transport_equity_burden_score"]
    ).clip(0, 1)
    numeric_cols = [col for col in out.columns if col != "scenario"]
    out[numeric_cols] = out[numeric_cols].round(4)
    return out.sort_values("planning_score", ascending=False).reset_index(drop=True)


def summary_metrics(comparison: pd.DataFrame, risk: pd.DataFrame, emissions: pd.DataFrame, emergency: pd.DataFrame, equity: pd.DataFrame) -> dict[str, float | int | str]:
    """Compact experiment summary for JSON and reports."""
    return {
        "scenario_count": int(comparison["scenario"].nunique()) if len(comparison) else 0,
        "best_planning_score_scenario": str(comparison.sort_values("planning_score", ascending=False)["scenario"].iloc[0]) if len(comparison) else "none",
        "lowest_congestion_scenario": str(comparison.sort_values("mean_congestion_score")["scenario"].iloc[0]) if len(comparison) else "none",
        "lowest_emissions_scenario": str(comparison.sort_values("total_emissions_kg_co2e")["scenario"].iloc[0]) if len(comparison) else "none",
        "high_or_critical_segment_count": int(risk["mobility_risk_class"].isin(["high", "critical"]).sum()) if len(risk) else 0,
        "total_emissions_kg_co2e": float(emissions["emissions_kg_co2e"].sum()) if len(emissions) else 0.0,
        "mean_response_delay_min": float(emergency["estimated_response_delay_min"].mean()) if len(emergency) else 0.0,
        "equity_review_zone_count": int(equity["equity_review_flag"].sum()) if len(equity) else 0,
        "data_origin": "synthetic fictional city mobility records",
        "decision_boundary": "independent planning simulator only; not official traffic control or emergency dispatch",
    }
