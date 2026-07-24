"""Run the independent synthetic smart city mobility risk digital twin.

The command uses only fictional zones, roads, vehicles, transit stops, emergency
facilities, and traffic traces. It demonstrates traffic scenario simulation,
congestion and accident-risk scoring, emissions burden estimation, emergency
route-delay analysis, transport-equity auditing, reporting, figures, and a
hash-chained audit log.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mobilitytwin.audit import append_record, verify_log
from mobilitytwin.config import ensure_output_dirs, set_seed
from mobilitytwin.emergency import emergency_route_audit
from mobilitytwin.emissions import estimate_emissions
from mobilitytwin.equity import transport_equity_audit
from mobilitytwin.reporting import write_report
from mobilitytwin.risk import score_mobility_risks
from mobilitytwin.scenarios import scenario_comparison, summary_metrics
from mobilitytwin.synthetic import SyntheticMobilityConfig, generate_synthetic_mobility_data
from mobilitytwin.traffic import simulate_scenarios
from mobilitytwin.visualization import (
    plot_accident_risk,
    plot_congestion_risk,
    plot_emergency_delay,
    plot_emissions,
    plot_scenario_comparison,
    plot_transport_equity,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a synthetic smart city mobility risk digital twin.")
    parser.add_argument("--zones", type=int, default=16)
    parser.add_argument("--segments", type=int, default=46)
    parser.add_argument("--time-steps", type=int, default=96)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    set_seed(args.seed)
    outputs = ensure_output_dirs(args.output_dir)
    data = generate_synthetic_mobility_data(SyntheticMobilityConfig(
        zones=args.zones,
        segments=args.segments,
        time_steps=args.time_steps,
        seed=args.seed,
    ))
    zones = data["zones"]
    roads = data["roads"]
    facilities = data["facilities"]
    transit = data["transit_stops"]
    traces = data["traffic_traces"]

    simulated = simulate_scenarios(zones, roads, traces)
    risk = score_mobility_risks(simulated)
    emissions = estimate_emissions(simulated)
    emergency = emergency_route_audit(zones, roads, facilities, simulated)
    equity = transport_equity_audit(zones, transit, risk, emissions, emergency)
    comparison = scenario_comparison(risk, emissions, emergency, equity)

    summary = summary_metrics(comparison, risk, emissions, emergency, equity)
    summary.update({
        "seed": args.seed,
        "zone_count": int(len(zones)),
        "road_segment_count": int(len(roads)),
        "traffic_trace_count": int(len(traces)),
        "scenario_trace_count": int(len(simulated)),
        "transit_stop_count": int(len(transit)),
        "facility_count": int(len(facilities)),
    })

    zones.to_csv(outputs["results"] / "synthetic_city_zones.csv", index=False)
    roads.to_csv(outputs["results"] / "synthetic_road_network.csv", index=False)
    facilities.to_csv(outputs["results"] / "synthetic_emergency_facilities.csv", index=False)
    transit.to_csv(outputs["results"] / "synthetic_transit_stops.csv", index=False)
    traces.to_csv(outputs["results"] / "synthetic_traffic_traces.csv", index=False)
    simulated.to_csv(outputs["results"] / "synthetic_scenario_traces.csv", index=False)
    risk.to_csv(outputs["results"] / "synthetic_congestion_accident_risk.csv", index=False)
    emissions.to_csv(outputs["results"] / "synthetic_emissions_estimate.csv", index=False)
    emergency.to_csv(outputs["results"] / "synthetic_emergency_route_audit.csv", index=False)
    equity.to_csv(outputs["results"] / "synthetic_transport_equity_audit.csv", index=False)
    comparison.to_csv(outputs["results"] / "synthetic_scenario_comparison.csv", index=False)

    audit_path = outputs["audit"] / "mobility_risk_audit_log.jsonl"
    append_record(audit_path, {**summary, "boundary": "independent synthetic mobility planning simulator only"})
    summary["audit_log"] = verify_log(audit_path)
    (outputs["results"] / "synthetic_mobility_risk_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    write_report(outputs["reports"] / "synthetic_mobility_risk_report.md", summary, comparison, risk, emissions, emergency, equity)
    plot_congestion_risk(risk, outputs["figures"] / "synthetic_congestion_risk.png")
    plot_accident_risk(risk, outputs["figures"] / "synthetic_accident_risk.png")
    plot_emissions(emissions, outputs["figures"] / "synthetic_emissions_burden.png")
    plot_emergency_delay(emergency, outputs["figures"] / "synthetic_emergency_delay.png")
    plot_transport_equity(equity, outputs["figures"] / "synthetic_transport_equity.png")
    plot_scenario_comparison(comparison, outputs["figures"] / "synthetic_scenario_comparison.png")

    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
