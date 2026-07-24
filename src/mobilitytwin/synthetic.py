"""Deterministic synthetic smart-city mobility data.

All zones, roads, facilities, stops, trips, and traffic readings are fictional.
The generator is designed for repeatable research on congestion, safety,
emissions, emergency routing, and transport equity without real city data.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

ZONE_TYPES = ["residential", "commercial", "industrial", "mixed_use", "suburban", "civic"]
ROAD_CLASSES = ["arterial", "collector", "local", "expressway"]


@dataclass(frozen=True)
class SyntheticMobilityConfig:
    zones: int = 16
    segments: int = 46
    time_steps: int = 96
    seed: int = 42

    def __post_init__(self) -> None:
        if self.zones < 6:
            raise ValueError("Use at least 6 city zones for equity and routing analysis.")
        if self.segments < self.zones:
            raise ValueError("Use at least as many road segments as city zones.")
        if self.time_steps < 12:
            raise ValueError("Use at least 12 time steps for temporal mobility analysis.")


def generate_synthetic_mobility_data(config: SyntheticMobilityConfig | None = None) -> dict[str, pd.DataFrame]:
    """Generate fictional city zones, road network, transit stops, facilities, and traffic traces."""
    cfg = config or SyntheticMobilityConfig()
    rng = np.random.default_rng(cfg.seed)
    zones = _zones(cfg, rng)
    roads = _roads(cfg, zones, rng)
    facilities = _facilities(zones, rng)
    transit = _transit_stops(zones, rng)
    traces = _traffic_traces(cfg, zones, roads, transit, rng)
    return {"zones": zones, "roads": roads, "facilities": facilities, "transit_stops": transit, "traffic_traces": traces}


def _zones(cfg: SyntheticMobilityConfig, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for idx in range(cfg.zones):
        angle = 2 * np.pi * idx / cfg.zones
        radius = 4.0 + 1.4 * (idx % 3) + rng.normal(0, 0.25)
        zone_type = ZONE_TYPES[idx % len(ZONE_TYPES)]
        income = float(np.clip(rng.normal(0.55 - 0.12 * (idx % 4 == 0), 0.18), 0.08, 0.98))
        transit_access = float(np.clip(rng.normal(0.55 + 0.15 * (zone_type in {"commercial", "civic"}), 0.20), 0.05, 0.98))
        car_ownership = float(np.clip(0.78 - 0.40 * transit_access + 0.22 * income + rng.normal(0, 0.08), 0.08, 0.98))
        vulnerable_share = float(np.clip(rng.normal(0.22 + 0.18 * (income < 0.40), 0.08), 0.03, 0.65))
        equity_priority = float(np.clip(0.45 * (1 - income) + 0.35 * vulnerable_share + 0.20 * (1 - transit_access), 0, 1))
        rows.append({
            "zone_id": f"Z-{idx+1:03d}",
            "zone_name": f"Synthetic Zone {idx+1}",
            "zone_type": zone_type,
            "population": int(rng.integers(3500, 34000)),
            "income_index": round(income, 3),
            "car_ownership_rate": round(car_ownership, 3),
            "transit_access_index": round(transit_access, 3),
            "vulnerable_population_share": round(vulnerable_share, 3),
            "equity_priority_score": round(equity_priority, 3),
            "centroid_x": round(float(radius * np.cos(angle)), 3),
            "centroid_y": round(float(radius * np.sin(angle)), 3),
        })
    return pd.DataFrame(rows)


def _roads(cfg: SyntheticMobilityConfig, zones: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    zone_ids = zones["zone_id"].tolist()
    zone_lookup = zones.set_index("zone_id")
    rows = []
    pairs: set[tuple[str, str]] = set()

    # Ring backbone for connectivity.
    for idx, zone_id in enumerate(zone_ids):
        pairs.add((zone_id, zone_ids[(idx + 1) % len(zone_ids)]))
    # Extra cross-city connectors.
    while len(pairs) < cfg.segments:
        a, b = rng.choice(zone_ids, size=2, replace=False)
        pair = (str(a), str(b))
        reverse = (str(b), str(a))
        if pair not in pairs and reverse not in pairs:
            pairs.add(pair)

    for idx, (from_zone, to_zone) in enumerate(sorted(pairs)):
        f = zone_lookup.loc[from_zone]
        t = zone_lookup.loc[to_zone]
        dist = float(np.hypot(f.centroid_x - t.centroid_x, f.centroid_y - t.centroid_y))
        road_class = ROAD_CLASSES[(idx + int(dist * 10)) % len(ROAD_CLASSES)]
        lanes = int({"local": 1, "collector": 2, "arterial": 3, "expressway": 4}[road_class])
        speed = float({"local": 32, "collector": 45, "arterial": 58, "expressway": 78}[road_class] + rng.normal(0, 4))
        capacity = int(max(250, lanes * speed * 18))
        rows.append({
            "segment_id": f"R-{idx+1:04d}",
            "from_zone": from_zone,
            "to_zone": to_zone,
            "road_class": road_class,
            "length_km": round(max(0.35, dist + rng.normal(0, 0.20)), 3),
            "lanes": lanes,
            "speed_limit_kph": round(max(25, speed), 1),
            "baseline_capacity": capacity,
            "bike_lane": int(rng.random() < 0.30),
            "bus_priority": int(rng.random() < 0.25),
            "emergency_corridor": int((idx % 7 == 0) or (road_class in {"arterial", "expressway"} and rng.random() < 0.18)),
        })
    return pd.DataFrame(rows)


def _facilities(zones: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    zone_ids = zones["zone_id"].tolist()
    facility_types = ["hospital", "fire_station", "ambulance_depot", "mobility_control_center"]
    for idx, facility_type in enumerate(facility_types * 3):
        zone_id = str(rng.choice(zone_ids))
        rows.append({
            "facility_id": f"F-{idx+1:03d}",
            "facility_type": facility_type,
            "zone_id": zone_id,
            "response_capacity": int(rng.integers(2, 11)),
        })
    return pd.DataFrame(rows)


def _transit_stops(zones: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    stop_idx = 1
    for zone in zones.itertuples(index=False):
        stop_count = int(np.clip(round(zone.transit_access_index * 4 + rng.normal(0, 0.8)), 0, 5))
        for _ in range(stop_count):
            rows.append({
                "stop_id": f"T-{stop_idx:04d}",
                "zone_id": zone.zone_id,
                "service_frequency_per_hour": round(float(np.clip(rng.normal(4 + 8 * zone.transit_access_index, 2.0), 1, 18)), 2),
                "accessible_stop": int(rng.random() < 0.82),
            })
            stop_idx += 1
    return pd.DataFrame(rows, columns=["stop_id", "zone_id", "service_frequency_per_hour", "accessible_stop"])


def _traffic_traces(cfg: SyntheticMobilityConfig, zones: pd.DataFrame, roads: pd.DataFrame, transit: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    zone_lookup = zones.set_index("zone_id")
    transit_counts = transit.groupby("zone_id").size().to_dict() if not transit.empty else {}
    rows = []
    for step in range(cfg.time_steps):
        hour = step % 24
        morning_peak = np.exp(-((hour - 8) ** 2) / 9)
        evening_peak = np.exp(-((hour - 17) ** 2) / 10)
        peak_factor = 1.0 + 0.85 * morning_peak + 0.95 * evening_peak
        rain = float(np.clip(rng.beta(1.4, 7.0) + 0.45 * (rng.random() < 0.08), 0, 1))
        for road in roads.itertuples(index=False):
            origin = zone_lookup.loc[road.from_zone]
            destination = zone_lookup.loc[road.to_zone]
            socio_demand = 0.55 * origin.population / 18000 + 0.35 * origin.car_ownership_rate + 0.20 * (destination.zone_type in {"commercial", "civic"})
            vehicles = int(max(10, rng.normal(road.baseline_capacity * 0.34 * peak_factor * socio_demand, road.baseline_capacity * 0.08)))
            incident = int(rng.random() < (0.012 + 0.030 * rain + 0.015 * morning_peak + 0.012 * evening_peak))
            load_ratio = vehicles / max(road.baseline_capacity, 1)
            speed_factor = np.clip(1.06 - 0.62 * load_ratio - 0.18 * rain - 0.20 * incident, 0.12, 1.05)
            avg_speed = float(max(5, road.speed_limit_kph * speed_factor))
            emergency_requests = int(rng.poisson(0.05 + 0.18 * incident + 0.06 * (origin.equity_priority_score > 0.55)))
            rows.append({
                "time_step": step,
                "hour": hour,
                "segment_id": road.segment_id,
                "from_zone": road.from_zone,
                "to_zone": road.to_zone,
                "vehicles": vehicles,
                "flow_capacity": int(road.baseline_capacity),
                "avg_speed_kph": round(avg_speed, 3),
                "speed_limit_kph": road.speed_limit_kph,
                "rain_intensity": round(rain, 3),
                "incident_flag": incident,
                "heavy_vehicle_share": round(float(np.clip(rng.normal(0.12 + 0.06 * (road.road_class == "arterial"), 0.04), 0.02, 0.35)), 3),
                "transit_stop_count_origin": int(transit_counts.get(road.from_zone, 0)),
                "emergency_request_count": emergency_requests,
            })
    return pd.DataFrame(rows)
