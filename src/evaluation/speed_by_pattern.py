"""Why the store keeps the EDA's speed shares: AUC of each definition by laundering pattern (decision 15 Oct 2026).

Phase 3 tried a transfers-only, capped redefinition of the 1 h / 24 h speed shares and dropped it. Its weakness only
shows by laundering pattern, which is a hidden label, so the breakdown lives here (src/evaluation may read hidden
files). Training months 0-4 only; each launderer's first laundering week (weeks 0-26 since opening) against the open
account-weeks of 20,000 seeded normal accounts.

  PYTHONPATH=src python -m evaluation.speed_by_pattern --out data/v1_full   # -> outputs/modelling/features/speed_by_pattern.csv
"""
from __future__ import annotations
import argparse
import os

import numpy as np
import pandas as pd

import amldata
from features import weekly

TRAIN = (0, 1, 2, 3, 4)
HORIZON = 26
CASH_PATTERNS = {"Deposit-Send": "cash in (half), transfers out", "Cash_Withdrawal": "transfers in, cash out",
                 "Smurfing": "many cash deposits, transfers out"}


def tried_sql(months: str, horizon: int) -> str:
    """The dropped definition: transfers out within 1 h / 24 h of the latest transfer in, each inflow passed on once."""
    return f"""
    WITH acc AS (SELECT account_id, open_day FROM accounts WHERE open_month IN ({months})),
    t AS (SELECT x.account_id, x.direction, x.payment_type, CAST(x.amount AS DECIMAL(18, 2)) AS amount,
                 (x.day - a.open_day) // 7 AS w,
                 x.day * 86400 + CAST(substr(x.time, 1, 2) AS INT) * 3600 + CAST(substr(x.time, 4, 2) AS INT) * 60
                     + CAST(substr(x.time, 7, 2) AS INT) AS ts
          FROM transactions x JOIN acc a USING (account_id) WHERE x.day <= a.open_day + 7 * {horizon} + 6),
    tin AS (SELECT account_id, ts, amount AS in_amt, row_number() OVER (PARTITION BY account_id ORDER BY ts, amount) AS in_id
            FROM t WHERE direction = 'in' AND payment_type = 'ACH'),
    fo AS (SELECT o.account_id, o.w, o.ts, o.amount, i.in_id, i.in_amt, o.ts - i.ts AS delay
           FROM (SELECT * FROM t WHERE direction = 'out' AND payment_type IN ('ACH', 'Cross-border')) o
           ASOF JOIN tin i ON o.account_id = i.account_id AND o.ts >= i.ts),
    fc AS (SELECT account_id, w,
                  CASE WHEN delay <= 3600 THEN greatest(0, least(amount, in_amt
                       - coalesce(sum(amount) FILTER (WHERE delay <= 3600) OVER bf, 0))) ELSE 0 END AS f1h
           FROM fo WINDOW bf AS (PARTITION BY account_id, in_id ORDER BY ts, amount
                                 ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)),
    fwd AS (SELECT account_id, w, sum(f1h) AS f1h FROM fc GROUP BY 1, 2),
    tin_wk AS (SELECT account_id, w, sum(amount) AS transfer_in FROM t WHERE direction = 'in' AND payment_type = 'ACH' GROUP BY 1, 2)
    SELECT account_id, w AS weeks_since_open, least(1.0, coalesce(f1h, 0) / transfer_in) AS tried_1h
    FROM tin_wk LEFT JOIN fwd USING (account_id, w) WHERE transfer_in > 0"""


def auc(pos: np.ndarray, neg: np.ndarray) -> float:
    """Rank AUC; NaN ranked lowest (as in the EDA)."""
    x = np.where(np.isnan(np.r_[pos, neg]), -np.inf, np.r_[pos, neg])
    y = np.r_[np.ones(len(pos), bool), np.zeros(len(neg), bool)]
    r = pd.Series(x).rank().to_numpy()
    return float((r[y].sum() - y.sum() * (y.sum() + 1) / 2) / (y.sum() * (~y).sum()))


def run(out: str = amldata.DEFAULT_OUT, seed: int = 20261015) -> pd.DataFrame:
    ev = amldata.evaluation(out)
    ev.execute(f"PRAGMA memory_limit='{os.environ.get('EVAL_DUCKDB_MEMORY', '6GB')}'")
    months = ", ".join(map(str, TRAIN))
    pattern = ev.execute(f"""SELECT t.account_id, any_value(r.laundering_type) AS pattern
                             FROM transactions t JOIN transactions_truth r USING (txn_id) JOIN accounts a USING (account_id)
                             WHERE r.is_laundering = 1 AND a.open_month IN ({months}) GROUP BY 1""").df()
    tried = ev.execute(tried_sql(months, HORIZON)).df()
    store = weekly.load(out, (0, HORIZON))[["account_id", "weeks_since_open", "out_1h_share_wk"]]
    labs = []
    for w in range(HORIZON + 1):
        l = amldata.labels(out, months=TRAIN, weeks_since_open=w)[["account_id", "is_launderer", "started_by_day", "open_by_day"]]
        l["weeks_since_open"] = w
        labs.append(l)
    d = store.merge(pd.concat(labs), on=["account_id", "weeks_since_open"]).merge(
        tried, on=["account_id", "weeks_since_open"], how="left")
    d = d[d.open_by_day == 1]
    first = d[d.started_by_day == 1].groupby("account_id").weeks_since_open.min()
    pos = d[d.account_id.isin(first.index) & (d.weeks_since_open == d.account_id.map(first))].merge(pattern, on="account_id")
    rng = np.random.default_rng(seed)
    normal_ids = d.loc[d.is_launderer == 0, "account_id"].unique()
    neg = d[d.account_id.isin(rng.choice(normal_ids, min(20_000, len(normal_ids)), replace=False)) & (d.is_launderer == 0)]
    pos["group"] = np.where(pos["pattern"].isin(CASH_PATTERNS), "uses cash", "transfers only")
    rows = []
    parts = [("all launderers", pos)] + list(pos.groupby("group")) + list(pos[pos["pattern"].isin(CASH_PATTERNS)].groupby("pattern"))
    for name, p in parts:
        rows.append({"launderers": name, "how": CASH_PATTERNS.get(name, ""), "n": len(p),
                     "auc_kept_out_1h": auc(p.out_1h_share_wk.to_numpy(float), neg.out_1h_share_wk.to_numpy(float)),
                     "auc_dropped_tried_1h": auc(p.tried_1h.to_numpy(float), neg.tried_1h.to_numpy(float)),
                     "mean_kept": p.out_1h_share_wk.mean(), "mean_dropped": p.tried_1h.mean(),
                     "dropped_reads_0_or_blank": float((p.tried_1h.fillna(0) == 0).mean())})
    rows.append({"launderers": "normal account-weeks", "how": "", "n": len(neg), "auc_kept_out_1h": np.nan,
                 "auc_dropped_tried_1h": np.nan, "mean_kept": neg.out_1h_share_wk.mean(), "mean_dropped": neg.tried_1h.mean(),
                 "dropped_reads_0_or_blank": float((neg.tried_1h.fillna(0) == 0).mean())})
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m evaluation.speed_by_pattern", description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=amldata.DEFAULT_OUT)
    ap.add_argument("--report", default=None, help="default outputs/modelling/features[/<data folder name>]")
    a = ap.parse_args(argv)
    name = os.path.basename(os.path.normpath(a.out))
    report = a.report or "outputs/modelling/features" + ("" if name == "v1_full" else f"/{name}")
    os.makedirs(report, exist_ok=True)
    res = run(a.out)
    res.to_csv(os.path.join(report, "speed_by_pattern.csv"), index=False)
    print(res.round(3).to_string(index=False))
    print(f"-> {os.path.join(report, 'speed_by_pattern.csv')}")


if __name__ == "__main__":
    main()
