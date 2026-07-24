from mobilitytwin.emergency import emergency_route_audit
from mobilitytwin.emissions import estimate_emissions
from mobilitytwin.equity import transport_equity_audit
from mobilitytwin.risk import score_mobility_risks
from mobilitytwin.scenarios import scenario_comparison
from mobilitytwin.synthetic import SyntheticMobilityConfig, generate_synthetic_mobility_data
from mobilitytwin.traffic import SCENARIOS, simulate_scenarios


def _sample():
    data = generate_synthetic_mobility_data(SyntheticMobilityConfig(zones=8, segments=14, time_steps=12, seed=5))
    simulated = simulate_scenarios(data["zones"], data["roads"], data["traffic_traces"])
    return data, simulated


def test_all_scenarios_generated():
    _, simulated = _sample()
    assert set(simulated["scenario"].unique()) == set(SCENARIOS)
    assert {"volume_capacity_ratio", "scenario_rationale"}.issubset(simulated.columns)


def test_risk_emissions_emergency_equity_outputs():
    data, simulated = _sample()
    risk = score_mobility_risks(simulated)
    emissions = estimate_emissions(simulated)
    emergency = emergency_route_audit(data["zones"], data["roads"], data["facilities"], simulated)
    equity = transport_equity_audit(data["zones"], data["transit_stops"], risk, emissions, emergency)
    comparison = scenario_comparison(risk, emissions, emergency, equity)
    assert not risk.empty
    assert not emissions.empty
    assert not emergency.empty
    assert not equity.empty
    assert not comparison.empty
    assert {"scenario", "planning_score"}.issubset(comparison.columns)
