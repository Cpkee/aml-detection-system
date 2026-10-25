"""Candidate weekly features, built on top of the feature store, for trying out before any goes into it.

Each group below turns store columns into new columns per account and week. They only look at the same week and
earlier weeks of the same account, so the cut-off rule of the store (rows with day <= the end of week w) still holds.
Nothing here changes the store, its FEATURES list or its manifest: a group that earns its place is proposed to the
team and then added to weekly.py.

  lag1         last week's value of the main weekly features
  roll2        totals over this week and the one before (a ~2-week laundering burst often crosses a week boundary)
  roll4        the same over this week and the three before
  running_max  the largest weekly value so far (a burst stays visible after it ends)

Evaluated by `python -m models.feature_lab` (see that module); every trial is logged in its ledger.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

KEY = ["account_id", "weeks_since_open"]
LAG_COLS = ["n_rows_wk", "n_in_wk", "money_in_wk", "money_out_wk", "n_payers_wk", "out_1h_share_wk",
            "out_24h_share_wk", "passthrough_wk"]
ROLL_COLS = ["n_rows_wk", "n_in_wk", "money_in_wk", "money_out_wk", "n_payers_wk"]
MAX_COLS = ["out_1h_share_wk", "out_24h_share_wk", "n_payers_wk", "money_in_wk"]


def _check(df: pd.DataFrame) -> pd.core.groupby.DataFrameGroupBy:
    """Rows must be sorted by account and week, each account starting at week 0 with no gap: then `shift(k)` within
    an account is exactly week w - k. (Weeks the bank closed are dropped from the end only, so they leave no gap.)"""
    g = df.groupby("account_id", sort=False)
    if not (df["weeks_since_open"].to_numpy() == g.cumcount().to_numpy()).all():
        raise ValueError("rows must be sorted by account and week, every account from week 0 with no gap")
    return g


def _window(df, k: int) -> dict[str, pd.Series]:
    """Sums over this week and the k - 1 before it (fewer at the start of an account's life). n_payers_<k>wk adds
    the weekly distinct counts, so a payer seen in two of the weeks counts twice."""
    speed = {c: df[f"{c}_share_wk"].fillna(0) * df["money_in_wk"] for c in ("out_1h", "out_24h")}   # money, not share
    tmp = pd.DataFrame({**{c: df[c] for c in ROLL_COLS}, **speed})
    tg = tmp.groupby(df["account_id"].to_numpy(), sort=False)
    total = {c: tmp[c] + sum(tg[c].shift(j).fillna(0) for j in range(1, k)) for c in tmp.columns}
    out = {f"{c.removesuffix('_wk')}_{k}wk": total[c] for c in ROLL_COLS}
    money_in = total["money_in_wk"].replace(0, np.nan)
    out[f"out_1h_share_{k}wk"] = total["out_1h"] / money_in
    out[f"out_24h_share_{k}wk"] = total["out_24h"] / money_in
    out[f"passthrough_{k}wk"] = np.minimum(total["money_out_wk"], total["money_in_wk"]) / money_in
    return out


def lag1(df, g):
    return {f"{c}_lag1": g[c].shift(1) for c in LAG_COLS}


def roll2(df, g):
    return _window(df, 2)


def roll4(df, g):
    return _window(df, 4)


def running_max(df, g):
    # a week with no money in has no share; it counts as 0 so the running max carries on through it
    return {f"{c}_max_so_far": df[c].fillna(0).groupby(df["account_id"].to_numpy(), sort=False).cummax()
            for c in MAX_COLS}


GROUPS = {"lag1": lag1, "roll2": roll2, "roll4": roll4, "running_max": running_max}


def add(df: pd.DataFrame, groups: list[str]) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    """df with the candidate columns of `groups` added (float32), and the new column names per group."""
    unknown = set(groups) - set(GROUPS)
    if unknown:
        raise ValueError(f"unknown groups {sorted(unknown)}; known: {sorted(GROUPS)}")
    g = _check(df)
    new, names = {}, {}
    for name in groups:
        cols = {k: v.astype("float32") for k, v in GROUPS[name](df, g).items()}
        clash = set(cols) & (set(df.columns) | set(new))
        if clash:
            raise ValueError(f"group {name} would overwrite {sorted(clash)}")
        new.update(cols)
        names[name] = list(cols)
    return pd.concat([df, pd.DataFrame(new, index=df.index)], axis=1), names
