# Notebook Guidance

This repository is designed to run from scripts first so results are reproducible in CI.

Suggested notebook workflow:

1. Run `python scripts/run_synthetic_mobility_lab.py`.
2. Load CSV outputs from `outputs/results/`.
3. Explore scenario trade-offs, highest-risk segments, emergency delays, emissions burden, and equity gaps.
4. Keep notebooks free of real GPS traces, camera data, license-plate data, dispatch records, or personally identifiable mobility data.
