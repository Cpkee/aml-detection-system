"""Robustness checks (plan: outputs/modelling/robustness/PLAN.md, approved 5 Nov 2026).

Reads each run's committed harness output (results/<run>/final_test/launderers.csv) and gives its lead:
mules caught by the model minus mules caught by the rules, weeks 0-26, as a share of the cohort's mules,
with a paired bootstrap over the mules (1,000 resamples, 95% interval).

  PYTHONPATH=src python -m evaluation.robustness            # the plan's 7 runs -> summary.csv
  PYTHONPATH=src python -m evaluation.robustness seed__44 in_window_mix__1   # a subset: printed, not saved

summary.csv is the committed record, so it is written only for the plan's full list (or to --to PATH).
"""
import argparse
import os

import numpy as np
import pandas as pd

RESULTS = "outputs/modelling/results"
OUT = "outputs/modelling/robustness/summary.csv"
HEADLINE = "v1_full"
YARDSTICK = "seed__44"
PLAN_RUNS = ["seed__44", "in_window_mix__1", "bursts_per_launderer__1", "fake_start_days__2", "fake_start_days__1",
             "out_transfer_mean__1", "fake_age_rule__1"]          # the plan's order
HORIZON = 26
MIN_HALF_BAND = 0.05


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


def verdict(lead: float, lead_lo: float, band_lo: float) -> str:
    """The plan's rule: holds = lead inside or above the chance band; shrinks = below it but the interval is
    above 0; fails = the interval includes 0 (which covers the rules catching more)."""
    if lead >= band_lo:
        return "holds"
    return "shrinks" if lead_lo > 0 else "fails"


def check_runs(runs: list[str]) -> None:
    if HEADLINE in runs:
        raise SystemExit(f"{HEADLINE} is the headline and is always included: do not pass it")
    if len(set(runs)) != len(runs):
        raise SystemExit(f"a run is named twice: {runs}")
    for r in [HEADLINE, *runs]:
        f = os.path.join(RESULTS, r, "final_test", "launderers.csv")
        if not os.path.exists(f):
            raise SystemExit(f"no final test for '{r}' ({f} missing)")


def table(runs: list[str]) -> pd.DataFrame:
    """Headline first, then the runs. Band and verdict are added only when the yardstick run is included."""
    check_runs(runs)
    t = pd.DataFrame([lead(r) for r in [HEADLINE, *runs]])
    if YARDSTICK in runs:
        head = t.lead.iloc[0]
        half = max(abs(t.loc[t.run == YARDSTICK, "lead"].iloc[0] - head), MIN_HALF_BAND)
        t["band_lo"], t["band_hi"] = head - half, head + half
        t["verdict"] = ["" if r.run in (HEADLINE, YARDSTICK) else verdict(r.lead, r.lead_lo, r.band_lo)
                        for r in t.itertuples()]
    return t


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="*", default=PLAN_RUNS, help="default: the plan's 7 runs")
    ap.add_argument("--to", help=f"write the table here (default: {OUT}, only for the plan's full list)")
    a = ap.parse_args()
    t = table(a.runs)
    print(t.round(3).to_string(index=False))
    to = a.to or (OUT if a.runs == PLAN_RUNS else None)
    if to:
        t.to_csv(to, index=False)
        print(f"written: {to}")
    else:
        print(f"not written: {OUT} holds the plan's full list only (use --to PATH to save a subset)")


if __name__ == "__main__":
    main()
