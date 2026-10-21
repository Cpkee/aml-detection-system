"""The weekly feature store: one row per account per week since opening.

Week w of an account runs from open_day + 7w to open_day + 7w + 6 (its cut-off), the clock used by
`amldata.labels(weeks_since_open=w)`. A feature for week w may use only transactions with day <= that cut-off.
The store is written to <out>/features/weekly.parquet with a manifest (see manifest.py).

The feature list is the one fixed at the Phase 1 gate (outputs/modelling/eda/report.md, section 8; phased plan,
"Feature list for Phase 3"). Definitions follow the EDA panel (notebooks/01_eda_train.ipynb, section 3) so the
gate's AUCs can be reproduced from the store:

  volume          rows, payments in / out, money in / out, largest payment in / out, card items (this week);
                  rows, money in, money out (cumulative)
  counterparties  distinct payers (not cash) and payees (not cash, not card), first-time payer share (this week);
                  distinct payers and payees to date (cumulative). "New" means two things here, both kept from
                  the EDA: new_payer_share_wk counts a payer as new at the first contact in either direction,
                  n_payers_cum counts a counterparty at the first time it pays in.
  pass-through    share of this week's money in that leaves this week: min(out, in) / in
  speed           out_1h / out_24h_share_wk: money paid out (any kind) within 1 h / 24 h of the latest payment in
                  (any kind), over this week's money in (can exceed 1); med_in_out_minutes_wk: median minutes from
                  the latest payment in to each payment out. All three are the EDA's definitions. A transfers-only,
                  capped redefinition was tried and dropped (15 Oct 2026): it cannot see laundering through cash
                  (1 h AUC 0.772 vs 0.951 for cash patterns); see outputs/modelling/features/report.md
  self vs past    (this week - median of earlier weeks) / MAD of earlier weeks, for money in, payers and rows;
                  NaN until 4 earlier weeks exist or when the MAD is 0
  peers           this week's money in / median money in of accounts with the same income and age band at the
                  same week since opening; medians from accounts opened in months 0-4 only, frozen in
                  features/peer_medians.parquet (kept instead of income fit: correlation 0.998 at the gate)
  mix             internal (A*) share of money out, cash deposit share of money in, abroad and high-risk
                  country shares of money out, all cumulative (weekly versions carried no signal at the gate)
  clock           weeks_since_open
Dropped at the gate: night share (same hour weights for everyone), weekly cash / abroad / high-risk shares.
"""
from __future__ import annotations
import hashlib
import os
import shutil

import amldata
from . import manifest

KEYS = ["account_id", "weeks_since_open"]
FEATURES = [
    "n_rows_wk", "n_in_wk", "n_out_wk", "money_in_wk", "money_out_wk",
    "n_rows_cum", "money_in_cum", "money_out_cum",
    "max_in_wk", "max_out_wk", "card_items_wk",
    "n_payers_wk", "n_payees_wk", "new_payer_share_wk", "n_payers_cum", "n_payees_cum",
    "passthrough_wk", "out_1h_share_wk", "out_24h_share_wk", "med_in_out_minutes_wk",
    "self_vs_past_money_in", "self_vs_past_payers", "self_vs_past_rows",
    "peer_ratio_money_in",
    "internal_out_share_cum", "cash_in_share_cum", "abroad_out_share_cum", "high_risk_out_share_cum",
]
MONEY = ["money_in_wk", "money_out_wk", "money_in_cum", "money_out_cum", "max_in_wk", "max_out_wk"]  # exact sums, then DOUBLE
PEER_MONTHS = (0, 1, 2, 3, 4)                         # peer medians come from training months only
HIGH_RISK = ("Mexico", "Turkey", "Morocco", "UAE")   # configs/sim.yaml countries.high_risk (SAML-D)
SELF_MIN_WEEKS = 4
PEERS = "peer_medians.parquet"
# weekly totals that are 0 in a week with no rows (the median delay stays NULL: there is no delay to measure)
ZERO_FILL = ["n_rows_wk", "n_in_wk", "n_out_wk", "money_in_wk", "money_out_wk", "max_in_wk", "max_out_wk",
             "card_items_wk", "n_payers_wk", "n_payees_wk", "n_new_payers_wk", "first_seen_payers",
             "first_seen_payees", "cash_in_wk", "internal_out_wk", "abroad_out_wk", "high_risk_out_wk",
             "out_1h", "out_24h"]


def parse_weeks(text: str) -> tuple[int, int]:
    lo, _, hi = text.partition("-")
    lo, hi = int(lo), int(hi or lo)
    if lo < 0 or hi < lo:
        raise ValueError(f"bad week range '{text}'")
    return lo, hi


def base_sql(w_hi: int, month: int) -> str:
    """Per account and week 0..w_hi: the weekly aggregates every feature is built from (accounts of one month)."""
    hr = ", ".join(f"'{c}'" for c in HIGH_RISK)
    return f"""
    WITH acc AS (
        SELECT account_id, open_day, open_month, income, customer_age FROM accounts WHERE open_month = {month}),
    t AS (
        -- money as exact pence (amounts have 2 decimals): sums do not depend on the order DuckDB adds them in
        SELECT x.account_id, x.direction, x.counterparty_id, CAST(x.amount AS DECIMAL(18, 2)) AS amount,
               x.item_count, x.payment_type,
               x.receiver_bank_location, (x.day - a.open_day) // 7 AS w,
               x.day * 86400 + CAST(substr(x.time, 1, 2) AS INT) * 3600 + CAST(substr(x.time, 4, 2) AS INT) * 60
                   + CAST(substr(x.time, 7, 2) AS INT) AS ts,
               row_number() OVER (PARTITION BY x.account_id, x.counterparty_id
                                  ORDER BY x.day, x.time, x.txn_id) AS nth_with_cp,
               row_number() OVER (PARTITION BY x.account_id, x.direction, x.counterparty_id
                                  ORDER BY x.day, x.time, x.txn_id) AS nth_dir_cp
        FROM transactions x JOIN acc a USING (account_id)
        WHERE x.day <= a.open_day + 7 * {w_hi} + 6),
    ins AS (SELECT account_id, ts FROM t WHERE direction = 'in'),
    outs AS (   -- each payment out, with the time since the latest payment in (NULL if none yet)
        SELECT o.account_id, o.w, o.amount, o.ts - i.ts AS delay
        FROM (SELECT account_id, w, ts, amount FROM t WHERE direction = 'out') o
        ASOF LEFT JOIN ins i ON o.account_id = i.account_id AND o.ts >= i.ts),
    speed AS (
        SELECT account_id, w,
               coalesce(sum(amount) FILTER (WHERE delay <= 3600), 0)  AS out_1h,
               coalesce(sum(amount) FILTER (WHERE delay <= 86400), 0) AS out_24h,
               median(delay) / 60.0                                   AS med_in_out_minutes_wk
        FROM outs GROUP BY 1, 2),
    wk AS (
        SELECT account_id, w,
               count(*)                                                                AS n_rows_wk,
               count(*) FILTER (WHERE direction = 'in')                                AS n_in_wk,
               count(*) FILTER (WHERE direction = 'out')                               AS n_out_wk,
               coalesce(sum(amount) FILTER (WHERE direction = 'in'), 0)                AS money_in_wk,
               coalesce(sum(amount) FILTER (WHERE direction = 'out'), 0)               AS money_out_wk,
               coalesce(max(amount) FILTER (WHERE direction = 'in'), 0)                AS max_in_wk,
               coalesce(max(amount) FILTER (WHERE direction = 'out'), 0)               AS max_out_wk,
               coalesce(sum(item_count) FILTER (WHERE counterparty_id = 'CARD_MERCHANTS'), 0) AS card_items_wk,
               count(DISTINCT counterparty_id) FILTER (WHERE direction = 'in' AND counterparty_id <> 'CASH')
                                                                                       AS n_payers_wk,
               count(DISTINCT counterparty_id) FILTER (WHERE direction = 'out'
                                    AND counterparty_id NOT IN ('CASH', 'CARD_MERCHANTS')) AS n_payees_wk,
               count(DISTINCT counterparty_id) FILTER (WHERE direction = 'in' AND counterparty_id <> 'CASH'
                                                       AND nth_with_cp = 1)            AS n_new_payers_wk,
               count(*) FILTER (WHERE direction = 'in' AND counterparty_id <> 'CASH' AND nth_dir_cp = 1)
                                                                                       AS first_seen_payers,
               count(*) FILTER (WHERE direction = 'out' AND counterparty_id NOT IN ('CASH', 'CARD_MERCHANTS')
                                AND nth_dir_cp = 1)                                    AS first_seen_payees,
               coalesce(sum(amount) FILTER (WHERE direction = 'in' AND payment_type = 'Cash Deposit'), 0)
                                                                                       AS cash_in_wk,
               coalesce(sum(amount) FILTER (WHERE direction = 'out' AND counterparty_id LIKE 'A%'), 0)
                                                                                       AS internal_out_wk,
               coalesce(sum(amount) FILTER (WHERE direction = 'out' AND receiver_bank_location <> 'UK'), 0)
                                                                                       AS abroad_out_wk,
               coalesce(sum(amount) FILTER (WHERE direction = 'out' AND receiver_bank_location IN ({hr})), 0)
                                                                                       AS high_risk_out_wk
        FROM t GROUP BY 1, 2),
    grid AS (SELECT account_id, open_month, income, customer_age, unnest(range(0, {w_hi + 1})) AS w FROM acc)
    SELECT g.account_id, g.open_month, g.income, g.customer_age, g.w,
           {", ".join(f"coalesce({c}, 0) AS {c}" for c in ZERO_FILL)}, med_in_out_minutes_wk
    FROM grid g LEFT JOIN wk USING (account_id, w) LEFT JOIN speed USING (account_id, w)"""


def peer_sql(parts: str) -> str:
    """Median money in per income band, age band and week since opening, over accounts opened in months 0-4."""
    months = ", ".join(map(str, PEER_MONTHS))
    return f"""
    SELECT income, customer_age, w, median(CAST(money_in_wk AS DOUBLE)) AS peer_median_money_in
    FROM read_parquet('{parts}') WHERE open_month IN ({months})
    GROUP BY 1, 2, 3 ORDER BY 1, 2, 3"""


def final_sql(parts: str, peers: str, w_lo: int, w_hi: int) -> str:
    self_vs_past = []
    for name, col in [("money_in", "money_in_wk"), ("payers", "n_payers_wk"), ("rows", "n_rows_wk")]:
        self_vs_past.append(
            # medians of DECIMAL round to 2 places in DuckDB, so take them on DOUBLE
            f"CASE WHEN count(*) OVER past >= {SELF_MIN_WEEKS} THEN (CAST({col} AS DOUBLE) - median(CAST({col} AS DOUBLE))"
            f" OVER past) / nullif(mad(CAST({col} AS DOUBLE)) OVER past, 0) END AS self_vs_past_{name}")
    cols = [f"CAST({c} AS DOUBLE) AS {c}" if c in MONEY else c for c in KEYS + FEATURES]
    return f"""
    SELECT {", ".join(cols)} FROM (
        SELECT b.account_id, b.w AS weeks_since_open,
               n_rows_wk, n_in_wk, n_out_wk, money_in_wk, money_out_wk,
               sum(n_rows_wk)    OVER cum AS n_rows_cum,
               sum(money_in_wk)  OVER cum AS money_in_cum,
               sum(money_out_wk) OVER cum AS money_out_cum,
               max_in_wk, max_out_wk, card_items_wk,
               n_payers_wk, n_payees_wk,
               n_new_payers_wk / nullif(n_payers_wk, 0)                    AS new_payer_share_wk,
               sum(first_seen_payers) OVER cum                             AS n_payers_cum,
               sum(first_seen_payees) OVER cum                             AS n_payees_cum,
               least(money_out_wk, money_in_wk) / nullif(money_in_wk, 0)   AS passthrough_wk,
               out_1h / nullif(money_in_wk, 0)                             AS out_1h_share_wk,
               out_24h / nullif(money_in_wk, 0)                            AS out_24h_share_wk,
               med_in_out_minutes_wk,
               {", ".join(self_vs_past)},
               CAST(money_in_wk AS DOUBLE) / nullif(p.peer_median_money_in, 0) AS peer_ratio_money_in,
               sum(internal_out_wk)  OVER cum / nullif(sum(money_out_wk) OVER cum, 0) AS internal_out_share_cum,
               sum(cash_in_wk)       OVER cum / nullif(sum(money_in_wk)  OVER cum, 0) AS cash_in_share_cum,
               sum(abroad_out_wk)    OVER cum / nullif(sum(money_out_wk) OVER cum, 0) AS abroad_out_share_cum,
               sum(high_risk_out_wk) OVER cum / nullif(sum(money_out_wk) OVER cum, 0) AS high_risk_out_share_cum
        FROM read_parquet('{parts}') b
        LEFT JOIN read_parquet('{peers}') p USING (income, customer_age, w)
        WINDOW cum  AS (PARTITION BY b.account_id ORDER BY b.w),
               past AS (PARTITION BY b.account_id ORDER BY b.w ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING))
    WHERE weeks_since_open BETWEEN {w_lo} AND {w_hi}
    ORDER BY account_id, weeks_since_open"""


def code_sha256() -> str:
    """Fingerprint of the feature SQL, stored in the manifest: a store built by different feature code is refused.
    Built with fixed placeholder inputs, so it changes with the SQL (and the constants inside it), not with comments
    in this file or with the weeks asked for."""
    sql = base_sql(0, 0) + peer_sql("PARTS") + final_sql("PARTS", "PEERS", 0, 0)
    return hashlib.sha256(sql.encode()).hexdigest()


def build(out: str = amldata.DEFAULT_OUT, weeks: tuple[int, int] = (0, 78), force: bool = False):
    """Write <out>/features/weekly.parquet (+ peer medians and manifest). Returns (path, rows).

    Accounts are processed one opening month at a time to bound memory (~13M transaction rows per month at
    244k accounts); weeks before `weeks[0]` are still computed because cumulative and self-vs-past features
    need them, then left out of the store."""
    folder = os.path.join(out, "features")
    path = os.path.join(folder, "weekly.parquet")
    if os.path.exists(path) and not force:
        try:
            manifest.check(out, FEATURES, weeks)
            n = amldata.public(out).execute(f"SELECT count(*) FROM read_parquet('{path}')").fetchone()[0]
            return path, n
        except (ValueError, FileNotFoundError):
            pass
    os.makedirs(folder, exist_ok=True)
    work = os.path.join(folder, "_build")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    con = amldata.public(out)                       # only the `accounts` and `transactions` views exist here
    con.execute(f"PRAGMA memory_limit='{os.environ.get('FEATURES_DUCKDB_MEMORY', '4GB')}'")
    con.execute(f"PRAGMA temp_directory='{os.path.join(work, 'duckdb_tmp')}'")
    months = [r[0] for r in con.execute("SELECT DISTINCT open_month FROM accounts ORDER BY 1").fetchall()]
    for m in months:
        con.execute(f"COPY ({base_sql(weeks[1], m)}) TO '{os.path.join(work, f'base_{m}.parquet')}' (FORMAT PARQUET)")
    parts = os.path.join(work, "base_*.parquet")
    peers = os.path.join(folder, PEERS)
    con.execute(f"COPY ({peer_sql(parts)}) TO '{peers}' (FORMAT PARQUET)")
    tmp = path + ".tmp"
    con.execute(f"COPY ({final_sql(parts, peers, *weeks)}) TO '{tmp}' (FORMAT PARQUET)")
    os.replace(tmp, path)
    n = con.execute(f"SELECT count(*) FROM read_parquet('{path}')").fetchone()[0]
    con.close()
    shutil.rmtree(work, ignore_errors=True)
    manifest.write(out, FEATURES, weeks, {"rows": int(n), "peer_months": list(PEER_MONTHS),
                                         "peer_medians_sha256": manifest._sha256(peers), "code_sha256": code_sha256()})
    return path, n


def load(out: str = amldata.DEFAULT_OUT, weeks: tuple[int, int] | None = None,
         months: tuple[int, ...] | None = None, columns: list[str] | None = None):
    """DataFrame of the store, after checking its manifest against the data run, the feature code and FEATURES.

    weeks: weeks since opening to keep (inclusive); months: opening months of the accounts to keep; columns: features
    to return besides the two keys. Rows come sorted by account and week."""
    manifest.check(out, FEATURES, weeks)
    con = amldata.public(out)                       # `accounts` gives each account's opening month
    cols = ", ".join(KEYS + list(columns)) if columns else "*"
    where = []
    if weeks:
        where.append(f"weeks_since_open BETWEEN {weeks[0]} AND {weeks[1]}")
    if months:
        where.append(f"account_id IN (SELECT account_id FROM accounts WHERE open_month IN ({', '.join(map(str, months))}))")
    return con.execute(f"""SELECT {cols} FROM read_parquet('{os.path.join(out, 'features', 'weekly.parquet')}')
                           {'WHERE ' + ' AND '.join(where) if where else ''} ORDER BY account_id, weeks_since_open""").df()
