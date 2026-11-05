"""Robustness checks (plan: outputs/modelling/robustness/PLAN.md, approved 5 Nov 2026).

Reads each run's committed harness output (results/<run>/final_test/launderers.csv) and gives its lead:
mules caught by the model minus mules caught by the rules, weeks 0-26, as a share of the cohort's mules,
with a paired bootstrap over the mules (1,000 resamples, 95% interval).

  PYTHONPATH=src python -m evaluation.robustness seed__44 [in_window_mix__1 ...]
"""
import argparse
import os

import numpy as np
import pandas as pd

RESULTS = "outputs/modelling/results"
OUT = "outputs/modelling/robustness/summary.csv"
HEADLINE = "v1_full"
HORIZON = 26


def mules(run: str, horizon: int = HORIZON) -> pd.DataFrame:
    """One row per cohort mule by the horizon (fakes count from opening, real customers from their start), with
    0/1 caught by the model and by the rules (first alert by the horizon), as the harness counts them."""
    d = pd.read_csv(os.path.join(RESULTS, run, "final_test", "launderers.csv"))
    m = d[(d.profile == "fake") | (d.start_week <= horizon)].copy()
    m["model"] = m[f"model_flag_week_w{horizon}"].notna().astype(int)
    m["rules"] = (m.rules_first_alert_week <= horizon).astype(int)
    return m


def lead(run: str, n_boot: int = 1000, seed: int = 0) -> dict:
    m = mules(run)
    diff = (m.model - m.rules).to_numpy()
    rng = np.random.default_rng(seed)
    boot = diff[rng.integers(0, len(diff), (n_boot, len(diff)))].mean(axis=1)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return {"run": run, "mules": len(m), "model_caught": int(m.model.sum()), "rules_caught": int(m.rules.sum()),
            "lead": diff.mean(), "lead_lo": lo, "lead_hi": hi}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="+")
    a = ap.parse_args()
    rows = [lead(r) for r in [HEADLINE, *a.runs]]
    t = pd.DataFrame(rows)
    gap = abs(t.loc[t.run == "seed__44", "lead"].iloc[0] - t.lead.iloc[0]) if "seed__44" in t.run.values else None
    if gap is not None:
        half = max(gap, 0.05)
        band = (t.lead.iloc[0] - half, t.lead.iloc[0] + half)
        t["band_lo"], t["band_hi"] = band
        t["verdict"] = np.where(t.run.isin([HEADLINE, "seed__44"]), "",
                       np.where(t.lead >= band[0], "holds", np.where(t.lead_lo > 0, "shrinks", "fails")))
    t.to_csv(OUT, index=False)
    print(t.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
