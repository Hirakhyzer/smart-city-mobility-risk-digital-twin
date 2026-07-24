"""Traffic scenario simulation for the synthetic mobility digital twin."""

from __future__ import annotations

import numpy as np
import pandas as pd

SCENARIOS = [
    "baseline",
    "congestion_pricing",
    "emergency_lane_priority",
    "transit_priority_corridor",
    "low_emission_routing",
    "equity_aware_mobility",
]


def simulate_scenarios(zones: pd.DataFrame, roads: pd.DataFrame, traces: pd.DataFrame) -> pd.DataFrame:
    """Apply transparent planning scenarios to traffic traces."""
    zone_cols = ["zone_id", "income_index", "transit_access_index", "equity_priority_score", "vulnerable_population_share"]
    enriched = traces.merge(roads[["segment_id", "road_class", "lanes", "length_km", "bike_lane", "bus_priority", "emergency_corridor"]], on="segment_id", how="left")
    enriched = enriched.merge(zones[zone_cols].rename(columns={"zone_id": "from_zone"}), on="from_zone", how="left")
    rows = []
    for scenario in SCENARIOS:
        frame = enriched.copy()
        frame["scenario"] = scenario
        frame["scenario_rationale"] = _scenario_rationale(scenario)
        if scenario == "congestion_pricing":
            peak = frame["hour"].between(7, 9) | frame["hour"].between(16, 18)
            frame.loc[peak, "vehicles"] = frame.loc[peak, "vehicles"] * 0.88
            frame.loc[~peak, "vehicles"] = frame.loc[~peak, "vehicles"] * 0.97
        elif scenario == "emergency_lane_priority":
            boost = (frame["emergency_corridor"] == 1) | (frame["emergency_request_count"] > 0)
            frame.loc[boost, "flow_capacity"] = frame.loc[boost, "flow_capacity"] * 1.16
            frame.loc[boost, "avg_speed_kph"] = frame.loc[boost, "avg_speed_kph"] * 1.10
        elif scenario == "transit_priority_corridor":
            transit = (frame["bus_priority"] == 1) | (frame["transit_stop_count_origin"] >= 2)
            frame.loc[transit, "vehicles"] = frame.loc[transit, "vehicles"] * 0.90
            frame.loc[transit, "flow_capacity"] = frame.loc[transit, "flow_capacity"] * 1.06
            frame.loc[transit, "avg_speed_kph"] = frame.loc[transit, "avg_speed_kph"] * 1.05
        elif scenario == "low_emission_routing":
            frame["vehicles"] = frame["vehicles"] * np.where(frame["heavy_vehicle_share"] > 0.16, 0.91, 0.98)
            frame["heavy_vehicle_share"] = frame["heavy_vehicle_share"] * 0.82
            frame["avg_speed_kph"] = frame["avg_speed_kph"] * 1.03
        elif scenario == "equity_aware_mobility":
            priority = frame["equity_priority_score"].fillna(0) >= 0.50
            frame.loc[priority, "flow_capacity"] = frame.loc[priority, "flow_capacity"] * 1.11
            frame.loc[priority, "avg_speed_kph"] = frame.loc[priority, "avg_speed_kph"] * 1.08
            frame.loc[priority, "vehicles"] = frame.loc[priority, "vehicles"] * 0.94
        frame["vehicles"] = frame["vehicles"].round().clip(lower=0).astype(int)
        frame["flow_capacity"] = frame["flow_capacity"].round().clip(lower=1).astype(int)
        frame["avg_speed_kph"] = frame["avg_speed_kph"].clip(lower=3, upper=frame["speed_limit_kph"] * 1.15).round(3)
        frame["volume_capacity_ratio"] = (frame["vehicles"] / frame["flow_capacity"].clip(lower=1)).round(4)
        rows.append(frame)
    return pd.concat(rows, ignore_index=True)


def _scenario_rationale(scenario: str) -> str:
    rationales = {
        "baseline": "no intervention synthetic baseline",
        "congestion_pricing": "peak-period demand reduction proxy",
        "emergency_lane_priority": "priority capacity for emergency corridors and active requests",
        "transit_priority_corridor": "bus and transit corridor capacity improvement proxy",
        "low_emission_routing": "heavy-vehicle and stop-start traffic reduction proxy",
        "equity_aware_mobility": "targeted mobility improvement in high-priority zones",
    }
    return rationales.get(scenario, "scenario review")
