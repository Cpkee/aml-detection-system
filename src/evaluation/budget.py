"""The bank's rules as a review budget and a yardstick, for judging models on training months (proposal 28 Oct 2026).

The project compares the model with the rules at the rules' own weekly alert count (decision 8 Oct 2026). The feature
lab's top 1% of open accounts per week is about 60x that (rules: ~0.02% of accounts per week in weeks 0-26 since
opening), so with a permanent flag it can flag about a quarter of all accounts in 27 weeks and its measures saturate.
This module gives the lab two things, both read from the hidden alerts table and both for months 0-4 only:

  weekly_budget(out, months, weeks)   number of rule alerts per opening month and week since opening: how many
                                      accounts a model may flag that week (an account alerted twice counts twice,
                                      as in the fixed-cohort budget)
  rules_first_alert(out, months, weeks) each account's first alert week since opening, if any inside `weeks`: the
                                      rules' own catch curve, so the lab can show model and rules on one scale

Nothing per account goes into a model: the budget is a count, and the rules' first alerts are only compared with the
model's flags.
"""
from __future__ import annotations

import pandas as pd

import amldata

ALLOWED_MONTHS = (0, 1, 2, 3, 4)      # training months: month 5 stays for calibration, 6-7 for the test


def _months(months) -> str:
    months = tuple(int(m) for m in months)
    if not set(months) <= set(ALLOWED_MONTHS):
        raise ValueError(f"the lab's rules budget is for training months {ALLOWED_MONTHS} only, got {months}")
    return ", ".join(map(str, months))


def weekly_budget(out: str, months, weeks: tuple[int, int]) -> pd.DataFrame:
    """open_month, week, alerts: rule alerts raised in each week since opening on the accounts of each month."""
    m = _months(months)
    df = amldata.evaluation(out).execute(f"""
        WITH a AS (SELECT account_id, open_month, open_day FROM accounts WHERE open_month IN ({m}))
        SELECT a.open_month, (x.alert_day - a.open_day) // 7 AS week, count(*) AS alerts
        FROM aml_alerts x JOIN a USING (account_id)
        WHERE (x.alert_day - a.open_day) // 7 BETWEEN {int(weeks[0])} AND {int(weeks[1])}
        GROUP BY 1, 2""").df()
    grid = pd.MultiIndex.from_product([sorted(int(x) for x in m.split(", ")), range(weeks[0], weeks[1] + 1)],
                                      names=["open_month", "week"])
    return (df.set_index(["open_month", "week"])["alerts"].reindex(grid, fill_value=0).astype(int).reset_index())


def rules_first_alert(out: str, months, weeks: tuple[int, int]) -> pd.Series:
    """First rule alert week since opening per account, for accounts alerted inside `weeks` (others absent)."""
    m = _months(months)
    df = amldata.evaluation(out).execute(f"""
        WITH a AS (SELECT account_id, open_day FROM accounts WHERE open_month IN ({m}))
        SELECT account_id, min((x.alert_day - a.open_day) // 7) AS week
        FROM aml_alerts x JOIN a USING (account_id)
        WHERE (x.alert_day - a.open_day) // 7 BETWEEN {int(weeks[0])} AND {int(weeks[1])}
        GROUP BY 1""").df()
    return df.set_index("account_id")["week"].astype(float)
