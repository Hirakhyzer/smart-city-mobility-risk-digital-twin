"""Shared configuration utilities."""

from __future__ import annotations

from pathlib import Path
import random

import numpy as np


def set_seed(seed: int) -> None:
    """Set deterministic seeds for reproducible synthetic experiments."""
    random.seed(seed)
    np.random.seed(seed)


def ensure_output_dirs(root: str | Path = "outputs") -> dict[str, Path]:
    """Create standard output directories and return their paths."""
    root_path = Path(root)
    dirs = {
        "root": root_path,
        "results": root_path / "results",
        "figures": root_path / "figures",
        "reports": root_path / "reports",
        "audit": root_path / "audit",
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return dirs
