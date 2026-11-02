"""F2 of the methods comparison: the bank's rules and a model share each week's alert budget
(plan: outputs/modelling/comparison/PLAN.md, 2 Nov 2026).

Week w since opening has budget k_w (the rules' alerts that week). With model share s, the rules get
floor(k_w x (1 - s)) slots: that week's alerts in arrival order (alert day, then alert id), skipping accounts already
flagged. The model gets the remaining slots, including rule slots left unused, filled with its top-scoring accounts
not yet flagged. Every slot flags a different account, as the model alone does (feature_lab.first_flag_weeks).

s = 1 is the model alone; s = 0 is the rules' own first alerts, plus model flags only where a week's alerts fall on
accounts already alerted. Reads the hidden alerts table, so it lives here (test_hidden_files); months 0-5 only.
"""
from __future__ import annotations

import math

import pandas as pd

import amldata
from evaluation import budget

SHARES = (0.0, 0.25, 0.5, 0.75, 1.0)
MAIN_SHARE = 0.5                               # the pre-registered point


def rules_alerts(out: str, months, weeks: tuple[int, int]) -> pd.DataFrame:
    """open_month, week, account_id of every rule alert inside `weeks`, in arrival order (alert day, then alert id)."""
    m = budget._months(months)
    return amldata.evaluation(out).execute(f"""
        WITH a AS (SELECT account_id, open_month, open_day FROM accounts WHERE open_month IN ({m}))
        SELECT a.open_month, (x.alert_day - a.open_day) // 7 AS week, x.account_id
        FROM aml_alerts x JOIN a USING (account_id)
        WHERE (x.alert_day - a.open_day) // 7 BETWEEN {int(weeks[0])} AND {int(weeks[1])}
        ORDER BY x.alert_day, x.alert_id""").df()


def split_flags(v: pd.DataFrame, alerts: pd.DataFrame, k: dict[int, int], share: float) -> pd.Series:
    """First flag week per account when the rules and the model share each week's budget.

    v: one cohort's account_id, weeks_since_open, score rows (open accounts); alerts: that cohort's week, account_id
    rows in arrival order; k: budget per week; share: the model's share s."""
    first: dict[str, int] = {}
    by_week = {w: g["account_id"].tolist() for w, g in alerts.groupby("week", sort=False)}
    for w, g in v.groupby("weeks_since_open"):
        n = int(k.get(int(w), 0))
        n_rules = math.floor(n * (1 - share))
        for a in by_week.get(int(w), []):
            if n_rules == 0:
                break
            if a not in first:
                first[a] = w
                n_rules -= 1
        n_model = n - sum(1 for x in first.values() if x == w)
        pool = g[~g["account_id"].isin(first.keys())]
        for a in pool.sort_values("score", ascending=False, kind="stable")["account_id"].head(n_model):
            first[a] = w
    return pd.Series(first, dtype=float)
