"""Markdown report generation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_report(
    path: str | Path,
    summary: dict,
    comparison: pd.DataFrame,
    risk: pd.DataFrame,
    emissions: pd.DataFrame,
    emergency: pd.DataFrame,
    equity: pd.DataFrame,
) -> None:
    """Write a compact synthetic mobility-risk report."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Synthetic Smart City Mobility Risk Digital Twin Report",
        "",
        "> Independent planning simulator output. This report is not official traffic-control guidance, emergency dispatch guidance, or city policy certification.",
        "",
        "## Run summary",
        "",
    ]
    for key, value in summary.items():
        lines.append(f"- **{key}**: {value}")
    lines.extend(["", "## Scenario comparison", "", _to_markdown(comparison.head(12)), "", "## Highest-risk road segments", "", _to_markdown(risk.head(12)), "", "## Highest emissions burden segments", "", _to_markdown(emissions.head(12)), "", "## Emergency-route review", "", _to_markdown(emergency.head(12)), "", "## Transport equity review", "", _to_markdown(equity.head(12)), "", "## Review boundary", "", "All data are fictional synthetic records. Real deployments require calibrated city data, transport-engineering validation, emergency-services review, accessibility review, public participation, privacy review, and governance."])
    output.write_text("\n".join(lines), encoding="utf-8")


def _to_markdown(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "No rows generated."
    return frame.to_markdown(index=False)
