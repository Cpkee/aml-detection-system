"""Candidate weekly features, built on top of the feature store, for trying out before any goes into it.

Each group below turns store columns into new columns per account and week. They only look at the same week and
earlier weeks of the same account, so the cut-off rule of the store (rows with day <= the end of week w) still holds.
Nothing here changes the store, its FEATURES list or its manifest: a group that earns its place is proposed to the
team and then added to weekly.py.

  lag1         last week's value of the main weekly features
  roll2        totals over this week and the one before (a ~2-week laundering burst often crosses a week boundary)
  roll4        the same over this week and the three before
  roll4_core   roll4's three ratios and payments in only (is the smaller set as good?)
  running_max  the largest weekly value so far (a burst stays visible after it ends)
  new_cp4      payers and payees first seen in this week and the three before (from the cumulative counts)
  self4        this week and the three before vs the account's own average 4 weeks before them (money in / out,
               payments in): self-vs-past on a monthly scale, defined when weekly money in is mostly 0
  speed_cum    share of all money in so far paid out within 1 h / 24 h of a payment in (a burst stays visible after
               it ends, while a normal account's one-off fast week is diluted, unlike running_max)
  max_out_hist this week's largest payment out over the largest in any earlier week (insight r01-2: a burst pays
               out more than the account ever did, even with a long normal history)
  internal_out share of this week's (and the last 4 weeks') money out paid to accounts inside the bank, recovered from
               the store's cumulative share (insight r01-4: a long history dilutes the cumulative share)

Evaluated by `python -m models.feature_lab` (see that module); every trial is logged in its ledger. Groups the team
adopts are listed in ADOPTED at the bottom of this file.
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


def roll4_core(df, g):
    """The 4-week ratios plus payments in: roll4 without the totals that move with them (rows, money, payers)."""
    w = _window(df, 4)
    return {c: w[c] for c in ("n_in_4wk", "out_1h_share_4wk", "out_24h_share_4wk", "passthrough_4wk")}


def running_max(df, g):
    # a week with no money in has no share; it counts as 0 so the running max carries on through it
    return {f"{c}_max_so_far": df[c].fillna(0).groupby(df["account_id"].to_numpy(), sort=False).cummax()
            for c in MAX_COLS}


def new_cp4(df, g):
    """Distinct payers (payees) whose first payment in (out) falls in weeks w-3..w: the growth of the store's
    cumulative counts over 4 weeks. Unlike n_payers_4wk, a payer who pays every week counts once, and only if new."""
    return {f"new_{c}_4wk": df[f"n_{c}_cum"] - g[f"n_{c}_cum"].shift(4).fillna(0) for c in ("payers", "payees")}


SELF4_COLS = ["money_in_wk", "money_out_wk", "n_in_wk"]


def self4(df, g):
    """Sum over weeks w-3..w / (4 x mean weekly value over weeks 0..w-4). NaN until 4 earlier weeks exist (as the
    store's self_vs_past, SELF_MIN_WEEKS) or when the earlier weeks hold nothing. A salary paid monthly leaves most
    weeks at 0, so the store's median/MAD version is often NaN; a 4-week window holds about one pay day."""
    acc = df["account_id"].to_numpy()
    n_past = (df["weeks_since_open"] - 3).where(df["weeks_since_open"] >= 7)       # weeks 0..w-4, at least 4
    out = {}
    for c in SELF4_COLS:
        cum = df[c].groupby(acc, sort=False).cumsum()
        past = cum.groupby(acc, sort=False).shift(4)                                 # total of weeks 0..w-4
        usual = 4 * past / n_past
        out[f"self4_{c.removesuffix('_wk')}"] = (cum - past) / usual.where(usual > 0)
    return out


def speed_cum(df, g):
    """Money paid out within 1 h / 24 h of the latest payment in, summed over weeks 0..w, over money in summed over
    weeks 0..w (the weekly shares weighted by the week's money in, as roll4 does over 4 weeks). NaN until money in."""
    acc = df["account_id"].to_numpy()
    money_in = df["money_in_wk"].groupby(acc, sort=False).cumsum()
    return {f"{c}_share_cum": (df[f"{c}_share_wk"].fillna(0) * df["money_in_wk"]).groupby(acc, sort=False).cumsum()
            / money_in.where(money_in > 0) for c in ("out_1h", "out_24h")}


def max_out_hist(df, g):
    """max_out_wk / the largest max_out_wk in weeks 0..w-1. NaN until an earlier week has money out; 0 in a week with
    none. Store version: max_out_wk includes the weekly card row (insight r01-2's raw version leaves it out)."""
    before = g["max_out_wk"].cummax().groupby(df["account_id"].to_numpy(), sort=False).shift(1)
    return {"max_out_vs_hist": df["max_out_wk"] / before.where(before > 0)}


def internal_out(df, g):
    """Money out to accounts inside the bank (A*) over weeks w-k+1..w, k = 1 and 4, over money out in those weeks.
    The internal money so far is internal_out_share_cum x money_out_cum (the share is NaN, i.e. 0 money, until money
    goes out); its growth over k weeks is rounded to pence, as the amounts are, so float error cannot leave a tiny
    non-zero share. NaN when no money goes out in the window."""
    so_far = df["internal_out_share_cum"].fillna(0) * df["money_out_cum"]
    out = {}
    for k in (1, 4):
        internal = (so_far - so_far.groupby(df["account_id"].to_numpy(), sort=False).shift(k).fillna(0)).round(2)
        money = df["money_out_wk"] + sum(g["money_out_wk"].shift(j).fillna(0) for j in range(1, k))
        out["internal_out_share_wk" if k == 1 else f"internal_out_share_{k}wk"] = internal / money.where(money > 0)
    return out


GROUPS = {"lag1": lag1, "roll2": roll2, "roll4": roll4, "roll4_core": roll4_core, "running_max": running_max,
          "new_cp4": new_cp4, "self4": self4, "speed_cum": speed_cum, "max_out_hist": max_out_hist,
          "internal_out": internal_out}

# Adopted into the model inputs (decision 26 Oct 2026, Kee Chee Pheng, lead; feature lab trials
# item1-history-tuned-measure and roll4-core-vs-full). Computed at load time by models.lgbm_baseline.load_table(...,
# adopted=True), not stored: they are sums of store columns. Moving them into weekly.py is optional tidying.
ADOPTED_GROUP = "roll4"
ADOPTED = ["n_rows_4wk", "n_in_4wk", "money_in_4wk", "money_out_4wk", "n_payers_4wk",
           "out_1h_share_4wk", "out_24h_share_4wk", "passthrough_4wk"]


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
