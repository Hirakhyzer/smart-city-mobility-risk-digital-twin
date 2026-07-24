# Synthetic Lab Guide

Run the default experiment:

```bash
python scripts/run_synthetic_mobility_lab.py
```

Run a smaller smoke experiment:

```bash
python scripts/run_synthetic_mobility_lab.py --zones 8 --segments 14 --time-steps 12 --seed 7 --output-dir outputs_ci
```

Run a larger scenario experiment:

```bash
python scripts/run_synthetic_mobility_lab.py --zones 24 --segments 72 --time-steps 168 --seed 42
```

The lab writes CSV tables, figures, a Markdown report, a JSON summary, and a hash-chained audit ledger. All generated records are fictional.
