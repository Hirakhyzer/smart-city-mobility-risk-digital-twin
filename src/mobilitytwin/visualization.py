"""Local matplotlib visualizations for synthetic smart-city mobility runs."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _save(fig, path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)


def plot_congestion_risk(risk: pd.DataFrame, path: str | Path) -> None:
    summary = risk.groupby("scenario")["congestion_score"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    summary.plot(kind="bar", ax=ax)
    ax.set_title("Mean congestion risk by scenario")
    ax.set_ylabel("Congestion score")
    ax.set_xlabel("Scenario")
    ax.tick_params(axis="x", rotation=35)
    _save(fig, path)


def plot_accident_risk(risk: pd.DataFrame, path: str | Path) -> None:
    summary = risk.groupby("scenario")["accident_risk_score"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    summary.plot(kind="bar", ax=ax)
    ax.set_title("Mean accident-risk score by scenario")
    ax.set_ylabel("Accident-risk score")
    ax.set_xlabel("Scenario")
    ax.tick_params(axis="x", rotation=35)
    _save(fig, path)


def plot_emissions(emissions: pd.DataFrame, path: str | Path) -> None:
    summary = emissions.groupby("scenario")["emissions_kg_co2e"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    summary.plot(kind="bar", ax=ax)
    ax.set_title("Synthetic emissions burden by scenario")
    ax.set_ylabel("Estimated kg CO2e")
    ax.set_xlabel("Scenario")
    ax.tick_params(axis="x", rotation=35)
    _save(fig, path)


def plot_emergency_delay(emergency: pd.DataFrame, path: str | Path) -> None:
    summary = emergency.groupby("scenario")["estimated_response_delay_min"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    summary.plot(kind="bar", ax=ax)
    ax.set_title("Mean estimated emergency response delay")
    ax.set_ylabel("Minutes")
    ax.set_xlabel("Scenario")
    ax.tick_params(axis="x", rotation=35)
    _save(fig, path)


def plot_transport_equity(equity: pd.DataFrame, path: str | Path) -> None:
    summary = equity.groupby("scenario")["transport_equity_burden_score"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    summary.plot(kind="bar", ax=ax)
    ax.set_title("Mean transport-equity burden by scenario")
    ax.set_ylabel("Equity burden score")
    ax.set_xlabel("Scenario")
    ax.tick_params(axis="x", rotation=35)
    _save(fig, path)


def plot_scenario_comparison(comparison: pd.DataFrame, path: str | Path) -> None:
    summary = comparison.set_index("scenario")["planning_score"].sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    summary.plot(kind="bar", ax=ax)
    ax.set_title("Composite mobility planning score")
    ax.set_ylabel("Planning score")
    ax.set_xlabel("Scenario")
    ax.tick_params(axis="x", rotation=35)
    _save(fig, path)
