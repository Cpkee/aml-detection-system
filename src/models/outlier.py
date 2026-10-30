"""Outlier detection, report appendix (plan: outputs/modelling/outlier/PLAN.md; D1-D3 decided 30 Oct 2026).

Two label-free scores for every account-week, fitted on the training months only:

  rarity   (M3) for each input, how rare the value is among training weeks of the same week band, on either side
           (ECOD-style: Li et al. 2022, "ECOD: Unsupervised Outlier Detection Using Empirical Cumulative
           Distribution Functions"); rarity = -log10(tail share), score = mean of the 3 rarest inputs
  iforest  (M4) scikit-learn Isolation Forest per week band, on each input's rank within the band (0-1)

Why ranks, not raw values or z-scores (label-free check, 30 Oct 2026, v1_full months 0-4): 9 of the 19 inputs have
a median absolute deviation of 0 in at least one band (out_1h_share_wk among them), and the tails reach thousands
of MADs (self_vs_past_money_in; out_24h_share_wk up to 10), so z-scores would skip the speed shares and be ruled by
the longest tail. A rank needs no scale: a value most weeks share is not rare, however large it is.

A missing value (no payment out that week, fewer than 4 past weeks) counts as no evidence: rarity 0, rank 0.5.
No label is read here; fitting drops the weeks after the bank closed an account (`open_by_day`: the bank knows
what it closed). The harness compares accounts within the same week since opening, so scores need not be
comparable across bands.

    PYTHONPATH=src python -m models outlier --out data/v1_full --method rarity --months 5
    -> <out>/scores/outlier_<method>_m<months>.parquet (account_id, weeks_since_open, score)
       for `python -m evaluation.score --scores PATH --horizons 26`
"""
from __future__ import annotations
import argparse
import os

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

import amldata
from models import train as trainer

INPUTS = ["passthrough_wk", "out_1h_share_wk", "out_24h_share_wk", "med_in_out_minutes_wk", "n_payers_wk",
          "n_payees_wk", "new_payer_share_wk", "self_vs_past_money_in", "self_vs_past_payers", "self_vs_past_rows",
          "peer_ratio_money_in", "internal_out_share_cum", "cash_in_share_cum", "abroad_out_share_cum",
          "high_risk_out_share_cum", "out_1h_share_4wk", "out_24h_share_4wk", "passthrough_4wk", "n_payers_4wk"]
KEY = ["account_id", "weeks_since_open"]
BANDS = ((0, 3), (4, 12), (13, 26))           # new accounts behave differently: each band its own reference
WEEKS = (BANDS[0][0], BANDS[-1][1])
TRAIN_MONTHS = (0, 1, 2, 3, 4)
SCORE_MONTHS = (5,)                           # D1: the one look is on month 5; test months 6-7 are never scored
TOP_K = 3
IFOREST = {"n_estimators": 300, "max_samples": 256, "random_state": 42}
METHODS = ("rarity", "iforest")


def settings() -> dict:
    """Everything that decides the scores, for the settings file committed before the one look."""
    return {"inputs": INPUTS, "bands": [list(b) for b in BANDS], "train_months": list(TRAIN_MONTHS),
            "weeks": list(WEEKS), "top_k": TOP_K, "iforest": IFOREST, "missing": "rarity 0, rank 0.5"}


def band(weeks) -> np.ndarray:
    """Index of each week's band in BANDS (-1 outside weeks 0-26)."""
    w = np.asarray(weeks)
    out = np.full(len(w), -1)
    for i, (lo, hi) in enumerate(BANDS):
        out[(w >= lo) & (w <= hi)] = i
    return out


def _counts(ref: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Reference values below x and at or below x."""
    return np.searchsorted(ref, x, side="left"), np.searchsorted(ref, x, side="right")


def rarity(ref: np.ndarray, x: np.ndarray) -> np.ndarray:
    """-log10 of the smaller tail share (values at or below x, at or above x; +1 smoothed); 0 where x is missing."""
    n = len(ref)
    if n == 0:
        return np.zeros(len(x))
    below, upto = _counts(ref, x)
    p = np.minimum(upto + 1, n - below + 1) / (n + 1)
    return np.where(np.isnan(x), 0.0, -np.log10(p))


def rank(ref: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Mid-rank of x in the reference (0-1); 0.5 where x is missing or the reference is empty."""
    n = len(ref)
    if n == 0:
        return np.full(len(x), 0.5)
    below, upto = _counts(ref, x)
    return np.where(np.isnan(x), 0.5, (below + upto) / (2 * n))


def _values(rows: pd.DataFrame, c: str) -> np.ndarray:
    return rows[c].to_numpy(dtype="float32")


def _ranks(refs: dict, rows: pd.DataFrame) -> np.ndarray:
    return np.column_stack([rank(refs[c], _values(rows, c)) for c in INPUTS])


def fit(train: pd.DataFrame, method: str) -> list[dict]:
    """Per week band: each input's sorted training values, and for iforest the forest fitted on their ranks."""
    if method not in METHODS:
        raise ValueError(f"method must be one of {METHODS}")
    b = band(train["weeks_since_open"])
    fitted = []
    for i in range(len(BANDS)):
        rows = train[b == i]
        refs = {c: np.sort(v[~np.isnan(v)]) for c in INPUTS for v in [_values(rows, c)]}
        f = {"refs": refs}
        if method == "iforest":
            f["forest"] = IsolationForest(**IFOREST).fit(_ranks(refs, rows))
        fitted.append(f)
    return fitted


def score(df: pd.DataFrame, fitted: list[dict], method: str) -> np.ndarray:
    """Outlier score per row (higher = more unusual); NaN for weeks outside 0-26."""
    b = band(df["weeks_since_open"])
    s = np.full(len(df), np.nan)
    for i, f in enumerate(fitted):
        rows = df[b == i]
        if method == "rarity":
            r = np.column_stack([rarity(f["refs"][c], _values(rows, c)) for c in INPUTS])
            s[b == i] = -np.sort(-r, axis=1)[:, :TOP_K].mean(axis=1)
        else:
            s[b == i] = -f["forest"].score_samples(_ranks(f["refs"], rows))
    return s


def load(out: str, months, open_only: bool) -> pd.DataFrame:
    """Account-weeks 0-26 of accounts opened in `months`: keys + INPUTS (public store only). open_only drops the
    weeks after the bank closed the account; only `open_by_day` is kept from amldata.labels."""
    x = trainer.feature_table(out, months, WEEKS)[KEY + INPUTS]
    if open_only:
        shut = pd.concat([amldata.labels(out, months=tuple(months), weeks_since_open=w)
                          .loc[lambda y: y["open_by_day"] == 0, ["account_id"]].assign(weeks_since_open=w)
                          for w in range(WEEKS[0], WEEKS[1] + 1)], ignore_index=True)
        x = x.merge(shut, on=KEY, how="left", indicator=True)
        x = x[x.pop("_merge") == "left_only"].reset_index(drop=True)
    return x


def run(out: str, method: str, months=SCORE_MONTHS) -> pd.DataFrame:
    """Fit on the training months, score `months` (training months: in-sample, for the label-free checks only)."""
    bad = set(months) - set(TRAIN_MONTHS) - set(SCORE_MONTHS)
    if bad:
        raise ValueError(f"months {sorted(bad)} are not scored here (decision D1: month 5 only, never 6-7)")
    fitted = fit(load(out, TRAIN_MONTHS, open_only=True), method)
    x = load(out, months, open_only=False)                 # the harness decides which weeks are open
    return x[KEY].assign(score=score(x, fitted, method))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m models outlier", description="write label-free outlier scores")
    ap.add_argument("--out", default=amldata.DEFAULT_OUT)
    ap.add_argument("--method", choices=METHODS, required=True)
    ap.add_argument("--months", nargs="+", type=int, default=list(SCORE_MONTHS))
    ap.add_argument("--to", default=None, help="output file (default <out>/scores/outlier_<method>_m<months>.parquet)")
    a = ap.parse_args(argv)
    path = a.to or os.path.join(a.out, "scores", f"outlier_{a.method}_m{''.join(map(str, a.months))}.parquet")
    s = run(a.out, a.method, a.months)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    s.to_parquet(path, index=False)
    print(f"{len(s):,} account-weeks of {s['account_id'].nunique():,} accounts scored by {a.method} -> {path}")
