import json
import subprocess
import sys
from pathlib import Path


def test_synthetic_pipeline_smoke(tmp_path):
    output_dir = tmp_path / "outputs"
    cmd = [
        sys.executable,
        "scripts/run_synthetic_mobility_lab.py",
        "--zones",
        "8",
        "--segments",
        "14",
        "--time-steps",
        "12",
        "--seed",
        "11",
        "--output-dir",
        str(output_dir),
    ]
    subprocess.run(cmd, check=True)
    summary_path = output_dir / "results" / "synthetic_mobility_risk_summary.json"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["zone_count"] == 8
    assert summary["road_segment_count"] == 14
    assert summary["scenario_count"] >= 4
    assert summary["audit_log"]["valid"] is True
    assert (output_dir / "reports" / "synthetic_mobility_risk_report.md").exists()
