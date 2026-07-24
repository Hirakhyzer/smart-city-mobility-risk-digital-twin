"""Synthetic vehicle-emissions burden estimation."""

from __future__ import annotations

import numpy as np
import pandas as pd


def estimate_emissions(simulated: pd.DataFrame) -> pd.DataFrame:
    """Estimate synthetic CO2e burden by scenario and road segment.

    Values are planning proxies only, not regulatory emissions inventories.
    """
    if simulated.empty:
        return pd.DataFrame(columns=["scenario", "segment_id", "from_zone", "emissions_kg_co2e", "emissions_burden_score"])
    frame = simulated.copy()
    low_speed_penalty = np.clip((35 - frame["avg_speed_kph"]) / 35, 0, 1)
    high_speed_penalty = np.clip((frame["avg_speed_kph"] - 80) / 70, 0, 1)
    emission_factor = 0.185 * (1 + 0.55 * low_speed_penalty + 0.18 * high_speed_penalty + 1.35 * frame["heavy_vehicle_share"])
    frame["emissions_kg_co2e"] = frame["vehicles"] * frame["length_km"] * emission_factor
    grouped = frame.groupby(["scenario", "segment_id", "from_zone", "to_zone"], as_index=False).agg(
        emissions_kg_co2e=("emissions_kg_co2e", "sum"),
        mean_emissions_kg_co2e=("emissions_kg_co2e", "mean"),
        mean_vehicle_count=("vehicles", "mean"),
        mean_speed_kph=("avg_speed_kph", "mean"),
        mean_heavy_vehicle_share=("heavy_vehicle_share", "mean"),
        equity_priority_score=("equity_priority_score", "mean"),
    )
    max_emissions = max(float(grouped["emissions_kg_co2e"].max()), 1.0)
    grouped["emissions_burden_score"] = np.clip(0.75 * grouped["emissions_kg_co2e"] / max_emissions + 0.25 * grouped["equity_priority_score"].fillna(0), 0, 1)
    numeric_cols = ["emissions_kg_co2e", "mean_emissions_kg_co2e", "mean_vehicle_count", "mean_speed_kph", "mean_heavy_vehicle_share", "emissions_burden_score"]
    grouped[numeric_cols] = grouped[numeric_cols].round(4)
    return grouped.sort_values(["emissions_burden_score", "emissions_kg_co2e"], ascending=[False, False]).reset_index(drop=True)
