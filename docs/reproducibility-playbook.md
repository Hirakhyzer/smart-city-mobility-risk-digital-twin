# Reproducibility Playbook

This playbook defines how to run, document, and report experiments from the **Smart City Mobility Risk Digital Twin** so another researcher can inspect the workflow.

## 1. Minimum run record

Every experiment should record:

| Field | Example |
|---|---|
| Run name | `mobility_risk_seed_42_zones_18` |
| Dataset type | synthetic fictional city mobility traces |
| Number of zones | `18` |
| Number of road segments | `54` |
| Time steps | `120` |
| Random seed | `42` |
| Scenario set | baseline, congestion pricing, emergency lane priority, transit priority corridor, low-emission routing, equity-aware mobility |
| Risk models | congestion, accident, emissions, emergency delay, equity burden |
| Output directory | `outputs/` |
| Boundary statement | synthetic planning simulator only, not official city performance or policy certification |

## 2. Recommended command

```bash
python scripts/run_synthetic_mobility_lab.py --zones 18 --segments 54 --time-steps 120 --seed 42
```

## 3. Evidence bundle

A complete run should include:

```text
outputs/results/synthetic_city_zones.csv
outputs/results/synthetic_road_network.csv
outputs/results/synthetic_emergency_facilities.csv
outputs/results/synthetic_transit_stops.csv
outputs/results/synthetic_traffic_traces.csv
outputs/results/synthetic_scenario_traces.csv
outputs/results/synthetic_congestion_accident_risk.csv
outputs/results/synthetic_emissions_estimate.csv
outputs/results/synthetic_emergency_route_audit.csv
outputs/results/synthetic_transport_equity_audit.csv
outputs/results/synthetic_scenario_comparison.csv
outputs/results/synthetic_mobility_risk_summary.json
outputs/reports/synthetic_mobility_risk_report.md
outputs/audit/mobility_risk_audit_log.jsonl
outputs/figures/
```

## 4. Interpretation rules

- Report each scenario against the baseline.
- Report congestion, accident risk, emissions, emergency delay, and equity together.
- Do not claim real-world city performance from synthetic traces.
- Treat emergency-delay estimates as review prompts, not dispatch guidance.
- State whether any scenario targets equity, emissions, or emergency response.
- Preserve the hash-chained audit log when sharing results.

## 5. Checklist before sharing results

- [ ] Seed and configuration recorded.
- [ ] Synthetic-data boundary stated clearly.
- [ ] Scenario assumptions documented.
- [ ] Risk and equity metrics reported together.
- [ ] Emergency-service limitations stated.
- [ ] Figures and generated report included.
- [ ] No official city policy or traffic-control claim is made.
