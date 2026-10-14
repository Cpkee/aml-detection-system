"""The weekly feature store: one row per account per week since opening.

Week w of an account runs from open_day + 7w to open_day + 7w + 6 (its cut-off), the clock used by
`amldata.labels(weeks_since_open=w)`. A feature for week w may use only transactions with day <= that cut-off.
The store is written to <out>/features/weekly.parquet with a manifest (see manifest.py).

Phase 0 builds the skeleton with a handful of volume features so the leak tests are real; Phase 3 adds the
feature groups in the modelling plan (speed, counterparties, mix, self vs past, peers, income fit).
"""
from __future__ import annotations
import os

import amldata
from amldata.loaders import _connect
from . import manifest

# this week = rows in [open_day + 7w, open_day + 7w + 6]; cumulative = rows with day <= open_day + 7w + 6
FEATURES = ["n_rows_wk", "n_in_wk", "n_out_wk", "money_in_wk", "money_out_wk",
            "n_rows_cum", "money_in_cum", "money_out_cum"]
KEYS = ["account_id", "weeks_since_open"]


def parse_weeks(text: str) -> tuple[int, int]:
    lo, _, hi = text.partition("-")
    lo, hi = int(lo), int(hi or lo)
    if lo < 0 or hi < lo:
        raise ValueError(f"bad week range '{text}'")
    return lo, hi


def sql(w_lo: int, w_hi: int) -> str:
    """Features for every account and week in [w_lo, w_hi], from the `accounts` and `transactions` views."""
    return f"""
    WITH grid AS (
        SELECT account_id, open_day, unnest(range({w_lo}, {w_hi + 1})) AS w FROM accounts),
    wk AS (
        SELECT g.account_id, g.w,
               count(t.account_id)                                            AS n_rows_wk,
               count(t.account_id) FILTER (WHERE t.direction = 'in')          AS n_in_wk,
               count(t.account_id) FILTER (WHERE t.direction = 'out')         AS n_out_wk,
               coalesce(sum(t.amount) FILTER (WHERE t.direction = 'in'), 0)   AS money_in_wk,
               coalesce(sum(t.amount) FILTER (WHERE t.direction = 'out'), 0)  AS money_out_wk
        FROM grid g LEFT JOIN transactions t
          ON t.account_id = g.account_id AND t.day BETWEEN g.open_day + 7 * g.w AND g.open_day + 7 * g.w + 6
        GROUP BY 1, 2)
    SELECT account_id, w AS weeks_since_open, n_rows_wk, n_in_wk, n_out_wk, money_in_wk, money_out_wk,
           sum(n_rows_wk)   OVER (PARTITION BY account_id ORDER BY w) AS n_rows_cum,
           sum(money_in_wk)  OVER (PARTITION BY account_id ORDER BY w) AS money_in_cum,
           sum(money_out_wk) OVER (PARTITION BY account_id ORDER BY w) AS money_out_cum
    FROM wk ORDER BY account_id, w"""


def build(out: str = amldata.DEFAULT_OUT, weeks: tuple[int, int] = (0, 78), force: bool = False):
    """Write <out>/features/weekly.parquet (+ manifest). Returns (path, rows)."""
    folder = os.path.join(out, "features")
    path = os.path.join(folder, "weekly.parquet")
    if os.path.exists(path) and not force:
        try:
            manifest.check(out, FEATURES, weeks)
            con = _connect()
            n = con.execute(f"SELECT count(*) FROM read_parquet('{path}')").fetchone()[0]
            return path, n
        except (ValueError, FileNotFoundError):
            pass
    os.makedirs(folder, exist_ok=True)
    con = amldata.public(out)                       # only the `accounts` and `transactions` views exist here
    tmp = path + ".tmp"
    con.execute(f"COPY ({sql(*weeks)}) TO '{tmp}' (FORMAT PARQUET)")
    os.replace(tmp, path)
    n = con.execute(f"SELECT count(*) FROM read_parquet('{path}')").fetchone()[0]
    manifest.write(out, FEATURES, weeks, {"rows": int(n)})
    return path, n


def load(out: str = amldata.DEFAULT_OUT, weeks: tuple[int, int] | None = None):
    """DataFrame of the store, after checking its manifest against the data run and FEATURES."""
    manifest.check(out, FEATURES, weeks)
    con = _connect()
    where = f"WHERE weeks_since_open BETWEEN {weeks[0]} AND {weeks[1]}" if weeks else ""
    return con.execute(f"SELECT * FROM read_parquet('{os.path.join(out, 'features', 'weekly.parquet')}') {where}").df()
