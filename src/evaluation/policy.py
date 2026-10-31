"""A secondary flagging policy for the harness: spend the rules' weekly budget only on high scores, carry the rest.

Background (review of the harness, 28 Oct 2026). With the agreed main policy (score.permanent_flags: each week since
opening the model flags as many new accounts as the rules raised alerts that week), the flags of weeks 1-7 land on
almost no mules, because laundering has barely started; in burst weeks nearly every flag hits and the budget is the
limit. The idea tested here: flag only accounts whose score reaches a threshold tau, and let the unused budget carry
forward to later weeks.

  carry_forward_flags  each week w, in order, among accounts not flagged before: flag those with score >= tau,
                       highest first (ties: account id, as score.permanent_flags), as long as the model's cumulative
                       flags never exceed the rules' cumulative alerts up to week w. Optional cap: at most
                       cap x that week's budget in any single week (a week with no rule alerts then gets no flags)

It stays fair to the rules: at the end of every week the model has used no more reviews than the rules. It is a
secondary result beside the agreed main policy (decision 9 Oct 2026), never a replacement.

  quantile_tau         tau expressed as a quantile of a cohort's account-week scores (pre-registered grid QUANTILES)
  choose_quantile      the pre-registered choice: most mules caught over the selection folds (1 + 2) combined
  policy_verdict       the pre-registered verdict on the held-back fold (3) and the selection folds

Pure functions on hand-made inputs (tests/test_policy.py); the notebook 11_policy_drift feeds them out-of-fold scores
of the tuned model on months 0-4 and scores the flags with score.measures.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

QUANTILES = (0.99, 0.995, 0.998, 0.999, 0.9995)     # pre-registered tau grid (29 Oct 2026)
CAP = 2                                             # optional weekly cap: 2 x that week's budget


def carry_forward_flags(scores: pd.DataFrame, k: dict[int, int], tau: float, cap: float | None = None) -> pd.Series:
    """First flag week per account (same form as score.permanent_flags) under the carry-forward policy.

    scores: account_id, weeks_since_open, score of open account-weeks; k: the rules' alerts per week since opening;
    tau: score threshold; cap: if given, at most cap * k[w] flags in week w."""
    weeks = sorted(set(int(w) for w in k) | set(int(w) for w in scores["weeks_since_open"].unique()))
    by_week = dict(tuple(scores[scores["score"] >= tau]
                         .sort_values(["weeks_since_open", "score", "account_id"], ascending=[True, False, True],
                                      kind="stable").groupby("weeks_since_open", sort=True)))
    first: dict[str, int] = {}
    allowed = 0                                     # the rules' alerts up to and including week w
    for w in weeks:
        allowed += int(k.get(w, 0))
        room = allowed - len(first)
        if cap is not None:
            room = min(room, int(np.floor(cap * int(k.get(w, 0)))))
        g = by_week.get(w)
        if room <= 0 or g is None:
            continue
        pool = g[~g["account_id"].isin(first.keys())]["account_id"].head(room)
        first.update({a: w for a in pool})
    return pd.Series(first, dtype=float)


def within_budget(first: pd.Series, k: dict[int, int]) -> bool:
    """True if at the end of every week the flags so far are no more than the rules' alerts so far."""
    weeks = sorted(set(int(w) for w in k) | set(int(w) for w in first.to_numpy()))
    used = first.value_counts()
    cum_flags = np.cumsum([int(used.get(w, 0)) for w in weeks])
    cum_budget = np.cumsum([int(k.get(w, 0)) for w in weeks])
    return bool((cum_flags <= cum_budget).all())


def quantile_tau(scores: pd.DataFrame, q: float) -> float:
    """The score at quantile q of all account-weeks in `scores` (so tau is set per cohort as a share, not a raw score)."""
    return float(np.quantile(scores["score"].to_numpy(), q))


def choose_quantile(summary: pd.DataFrame, folds=(1, 2)) -> float:
    """Pre-registered choice: the quantile with the most mules caught over `folds` combined. summary: one row per
    fold and quantile with columns fold, quantile, caught. Ties: the higher quantile (fewer, surer flags)."""
    s = summary[summary["fold"].isin(folds)].groupby("quantile")["caught"].sum()
    best = s.max()
    return float(max(q for q, c in s.items() if c == best))


def policy_verdict(policy: pd.DataFrame, topk: pd.DataFrame, test_fold: int = 3, select=(1, 2)) -> str:
    """Pre-registered verdict. policy / topk: one row per fold with caught and median_days_from_start.

    'holds up' if on the test fold the policy catches at least as many mules as weekly top-k AND its median days from
    start to first flag is no later; 'better' if it also catches more on each selection fold; else 'does not hold up'."""
    p, t = policy.set_index("fold"), topk.set_index("fold")
    holds = (p.loc[test_fold, "caught"] >= t.loc[test_fold, "caught"]
             and p.loc[test_fold, "median_days_from_start"] <= t.loc[test_fold, "median_days_from_start"])
    if not holds:
        return "does not hold up"
    if all(p.loc[f, "caught"] > t.loc[f, "caught"] for f in select):
        return "better"
    return "holds up"


def caught_by_start_week(truth: pd.DataFrame, first: pd.Series, mules) -> int:
    """Mules (ids in `mules`) whose first flag comes no later than the end of their laundering start week (a flag
    before the start counts: it is earlier still). Mules with no start inside the data count as not caught here."""
    t = truth.set_index("account_id").loc[list(mules)]
    start_week = (t["start_day"] - t["open_day"]) // 7
    f = first.reindex(t.index)
    return int((f <= start_week).sum())
