"""A stronger rule set as a second benchmark, report appendix (plan: outputs/modelling/scorecard/PLAN.md).

The bank's six rules (R1-R6) are a small benchmark. This module scores every account-week with three more standard
monitoring scenarios, hand-written from the weekly feature store, so the harness can rank accounts at the rules' own
weekly budget (`python -m evaluation.score --scores`). No model is fitted and no label is read here.

A scenario fires when every one of its conditions holds. A fired scenario adds points: how far its main measure is
over its threshold (measure / threshold), capped at CAP so one extreme value cannot outrank two fired scenarios by
much. An account-week where nothing fires scores 0. A missing value (no money in that week) never fires.

  S1 fast forwarding   most of the week's money in is paid out within 24 hours of the latest payment in
  S2 new payers        several payers in one week, most of them never seen before
  S3 pass-through      most of the week's money in leaves in the same week

Two more were drafted and dropped after a label-free count on months 0-4 (18 Nov 2026, plan, "Dropped"): money in
far above similar accounts (`peer_ratio_money_in` >= 5) fired on 26% of account-weeks and money in far above the
account's own past (`self_vs_past_money_in` >= 10) on 6%, because most people are paid monthly, so every payday week
is far above a typical week. R6 already covers sudden change with an 8-week baseline.

Thresholds that are amounts, counts or multiples are multiplied by one common `scale` (as R3-R6 are in
src/sim/rules.py); shares are not. The scale is chosen on months 0-4 and then frozen (plan, "Choosing the scale").
These scenarios were written after the model's results were known (it leans on forwarding speed), so this benchmark
is generous to the rules; the report says so.

    PYTHONPATH=src python -m models scorecard --out data/v1_full --months 5 [--scale 1.0]
    -> <out>/scores/scorecard_m<months>.parquet (account_id, weeks_since_open, score)
       for `python -m evaluation.score --scores PATH --horizons 26`
"""
from __future__ import annotations
import argparse
import os

import numpy as np
import pandas as pd

import amldata
from features import weekly

KEY = ["account_id", "weeks_since_open"]
WEEKS = (0, 26)                       # the main horizon; the harness is run with --horizons 26
ALLOWED_MONTHS = (0, 1, 2, 3, 4, 5)   # months 0-4 to choose the scale, month 5 for the one result; never 6-7
CAP = 3.0                             # most points one scenario can add
# name -> (main measure, its threshold, is the threshold scaled?, other conditions as (feature, minimum, scaled?))
# Starting values are ours (round numbers, written before any label was read); the behaviours follow the FFIEC
# red flags the six rules already cite. See the plan for each one's reason.
SCENARIOS = {
    "S1_fast_forwarding": ("out_24h_share_wk", 0.8, False, [("money_in_wk", 1000.0, True)]),
    "S2_new_payers": ("n_payers_wk", 5.0, True, [("new_payer_share_wk", 0.8, False)]),
    "S3_pass_through": ("passthrough_wk", 0.8, False, [("money_in_wk", 2000.0, True)]),
}
INPUTS = sorted({f for main, _, _, more in SCENARIOS.values() for f in [main] + [m[0] for m in more]})


def settings(scale: float) -> dict:
    """Everything that decides the scores, for the settings file committed before the month-5 run."""
    return {"scenarios": {k: {"measure": v[0], "threshold": v[1], "scaled": v[2],
                              "also": [list(c) for c in v[3]]} for k, v in SCENARIOS.items()},
            "scale": scale, "cap": CAP, "weeks": list(WEEKS), "missing": "never fires"}


def fired(df: pd.DataFrame, scale: float = 1.0) -> pd.DataFrame:
    """One True/False column per scenario: does it fire in this account-week? (NaN never fires.)"""
    out = {}
    for name, (main, thr, scaled, more) in SCENARIOS.items():
        hit = df[main].to_numpy(dtype=float) >= thr * (scale if scaled else 1.0)
        for feature, minimum, m_scaled in more:
            hit &= df[feature].to_numpy(dtype=float) >= minimum * (scale if m_scaled else 1.0)
        out[name] = hit
    return pd.DataFrame(out, index=df.index)


def score(df: pd.DataFrame, scale: float = 1.0) -> np.ndarray:
    """Points per account-week: for each fired scenario, measure / threshold capped at CAP; 0 if none fires."""
    if scale <= 0:
        raise ValueError("scale must be positive")
    hit = fired(df, scale)
    total = np.zeros(len(df))
    for name, (main, thr, scaled, _) in SCENARIOS.items():
        ratio = df[main].to_numpy(dtype=float) / (thr * (scale if scaled else 1.0))
        total += np.where(hit[name].to_numpy(), np.minimum(ratio, CAP), 0.0)
    return total


def run(out: str, months, scale: float = 1.0) -> pd.DataFrame:
    """account_id, weeks_since_open, score for every account-week 0-26 of accounts opened in `months`."""
    bad = set(months) - set(ALLOWED_MONTHS)
    if bad:
        raise ValueError(f"months {sorted(bad)} are not scored here (plan: months 0-5 only, never test months 6-7)")
    x = weekly.load(out, weeks=WEEKS, months=tuple(months), columns=INPUTS)
    return x[KEY].assign(score=score(x, scale))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m models scorecard", description="write rule-scorecard scores")
    ap.add_argument("--out", default=amldata.DEFAULT_OUT)
    ap.add_argument("--months", nargs="+", type=int, default=[5])
    ap.add_argument("--scale", type=float, default=1.0, help="common multiplier of the scaled thresholds")
    ap.add_argument("--to", default=None, help="output file (default <out>/scores/scorecard_m<months>.parquet)")
    a = ap.parse_args(argv)
    path = a.to or os.path.join(a.out, "scores", f"scorecard_m{''.join(map(str, a.months))}.parquet")
    s = run(a.out, a.months, a.scale)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    s.to_parquet(path, index=False)
    print(f"{len(s):,} account-weeks of {s['account_id'].nunique():,} accounts scored at scale {a.scale}; "
          f"{int((s['score'] > 0).sum()):,} with at least one scenario fired -> {path}")
