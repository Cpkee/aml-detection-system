"""Payment-graph features per account and week since opening (proposal 28 Oct 2026; not part of the store's 28).

Only payments between two accounts of the bank (counterparty `A*`) form links; external ids are drawn afresh for every
account, so no two accounts share an external payer or payee and a shared-counterparty graph would be empty by
construction. The links are directed (who paid whom) and carry money. Laundering adds links along each network's
chain (networks.internal_pieces_share of a networked launderer's pieces go to its next member, who forwards them),
while a normal account sends normal.internal_share_of_transfers of its one-off transfers to a random open account.
EDA section 6: 163 launderer-launderer links vs ~9 by chance, but only 1 exists before both ends start laundering,
so these features can strengthen a burst the account's own features already see, not flag anyone before it.

Same clock and cut-off as the store (week w ends open_day + 7w + 6; only rows with day <= that day), weeks 0-77:

  g_int_in_money_4wk      money in from other accounts of the bank, this week and the three before
  g_int_out_money_4wk     money out to other accounts of the bank, same window
  g_n_int_payers_4wk      distinct accounts of the bank that paid in, same window
  g_int_fwd24h_share_4wk  money paid out (any kind) within 24 h of a payment in that came from an account of the bank
                          (the latest payment in before it), over money in from accounts of the bank, same window:
                          the "receive from the previous chain member, forward on" step
  g_n_nb_cum              distinct accounts of the bank exchanged money with so far (either direction)
  g_n_nb_silent           of those, how many show the bank-closure footprint by the cut-off: a week with no rows at
                          all, ending on or before the cut-off (every open account has a weekly card row). This is
                          public; it also marks ~420 normal account-weeks in months 0-5 that happen to have no rows,
                          so it is a noisy closure signal (CLAUDE.md, closure footprint)

Written to <out>/features/graph_weekly.parquet, with graph_edges.parquet (every internal payment: account_id, nb_id,
day, direction, amount; used by models.graph_nb) and graph_manifest.json (data run, feature store and code hashes).
Reads `accounts` and `transactions` through amldata.public() and the store's n_rows_wk; nothing hidden.

    PYTHONPATH=src python -m features graph --out data/v1_full
"""
from __future__ import annotations
import hashlib
import json
import os

import amldata
from . import manifest
from .weekly import LAST_WEEK

KEY = ["account_id", "weeks_since_open"]
FEATURES = ["g_int_in_money_4wk", "g_int_out_money_4wk", "g_n_int_payers_4wk", "g_int_fwd24h_share_4wk",
            "g_n_nb_cum", "g_n_nb_silent"]
WINDOW = 4
FWD_SECONDS = 86400
GRAPH = "graph_weekly.parquet"
EDGES = "graph_edges.parquet"
MANIFEST = "graph_manifest.json"


def edges_sql(month: int, max_day: int | None = None) -> str:
    """Every payment between the accounts of one opening month and other accounts of the bank, weeks 0-LAST_WEEK."""
    cap = f" AND x.day <= {int(max_day)}" if max_day is not None else ""
    return f"""
    SELECT x.account_id, x.counterparty_id AS nb_id, x.day, x.direction, CAST(x.amount AS DOUBLE) AS amount
    FROM transactions x JOIN (SELECT account_id, open_day FROM accounts WHERE open_month = {month}) a USING (account_id)
    WHERE x.counterparty_id LIKE 'A%' AND x.day <= a.open_day + 7 * {LAST_WEEK} + 6{cap}
    ORDER BY x.account_id, x.day, x.time, x.txn_id"""


def weekly_sql(month: int, store: str, max_day: int | None = None) -> str:
    """Graph features per account of one opening month and week 0-LAST_WEEK. max_day (tests only) drops every
    transaction after that day, to show that weeks ending on or before it do not change."""
    cap = f" AND x.day <= {int(max_day)}" if max_day is not None else ""
    return f"""
    WITH acc AS (SELECT account_id, open_day FROM accounts WHERE open_month = {month}),
    t AS (
        SELECT x.account_id, x.direction, x.counterparty_id AS cp, CAST(x.amount AS DECIMAL(18, 2)) AS amount,
               x.day, (x.day - a.open_day) // 7 AS w, x.counterparty_id LIKE 'A%' AS internal,
               x.day * 86400 + CAST(substr(x.time, 1, 2) AS INT) * 3600 + CAST(substr(x.time, 4, 2) AS INT) * 60
                   + CAST(substr(x.time, 7, 2) AS INT) AS ts
        FROM transactions x JOIN acc a USING (account_id)
        WHERE x.day <= a.open_day + 7 * {LAST_WEEK} + 6{cap}),
    ins AS (SELECT account_id, ts, internal FROM t WHERE direction = 'in'),
    fwd AS (    -- each payment out, credited when the latest payment in before it came from the bank, within 24 h
        SELECT o.account_id, o.w,
               coalesce(sum(o.amount) FILTER (WHERE i.internal AND o.ts - i.ts <= {FWD_SECONDS}), 0) AS int_fwd
        FROM (SELECT account_id, w, ts, amount FROM t WHERE direction = 'out') o
        ASOF LEFT JOIN ins i ON o.account_id = i.account_id AND o.ts >= i.ts
        GROUP BY 1, 2),
    e AS (SELECT * FROM t WHERE internal),
    wk AS (
        SELECT account_id, w,
               coalesce(sum(amount) FILTER (WHERE direction = 'in'), 0)  AS int_in,
               coalesce(sum(amount) FILTER (WHERE direction = 'out'), 0) AS int_out
        FROM e GROUP BY 1, 2),
    grid AS (SELECT account_id, open_day, unnest(range(0, {LAST_WEEK + 1})) AS w FROM acc),
    payers4 AS (   -- distinct internal payers in weeks w-3..w
        SELECT g.account_id, g.w, count(DISTINCT e.cp) AS n_payers
        FROM grid g JOIN e ON e.account_id = g.account_id AND e.direction = 'in'
                          AND e.w BETWEEN g.w - {WINDOW - 1} AND g.w
        GROUP BY 1, 2),
    pairs AS (SELECT account_id, cp, min(day) AS first_day FROM e GROUP BY 1, 2),
    zero AS (      -- each account's first week with no rows at all, known at the end of that week
        SELECT s.account_id, min(a.open_day + 7 * s.weeks_since_open + 6) AS silent_day
        FROM read_parquet('{store}') s JOIN accounts a USING (account_id)
        WHERE s.n_rows_wk = 0 GROUP BY 1),
    known AS (     -- the focal week from which a neighbour counts (cut-off >= the day it became known)
        SELECT p.account_id,
               greatest(0, CAST(ceil((p.first_day - a.open_day - 6) / 7.0) AS INT)) AS w_nb,
               CASE WHEN z.silent_day IS NOT NULL THEN greatest(0, CAST(ceil(
                   (greatest(p.first_day, z.silent_day) - a.open_day - 6) / 7.0) AS INT)) END AS w_silent
        FROM pairs p JOIN acc a USING (account_id) LEFT JOIN zero z ON z.account_id = p.cp),
    nb AS (SELECT account_id, w_nb AS w, count(*) AS new_nb FROM known GROUP BY 1, 2),
    sil AS (SELECT account_id, w_silent AS w, count(*) AS new_silent FROM known WHERE w_silent IS NOT NULL GROUP BY 1, 2),
    j AS (
        SELECT g.account_id, g.w,
               coalesce(wk.int_in, 0) AS int_in, coalesce(wk.int_out, 0) AS int_out,
               coalesce(fwd.int_fwd, 0) AS int_fwd, coalesce(p4.n_payers, 0) AS n_payers,
               coalesce(nb.new_nb, 0) AS new_nb, coalesce(sil.new_silent, 0) AS new_silent
        FROM grid g LEFT JOIN wk USING (account_id, w) LEFT JOIN fwd USING (account_id, w)
        LEFT JOIN payers4 p4 USING (account_id, w) LEFT JOIN nb USING (account_id, w) LEFT JOIN sil USING (account_id, w))
    SELECT account_id, w AS weeks_since_open,
           CAST(sum(int_in) OVER r4 AS DOUBLE)                                    AS g_int_in_money_4wk,
           CAST(sum(int_out) OVER r4 AS DOUBLE)                                   AS g_int_out_money_4wk,
           n_payers                                                               AS g_n_int_payers_4wk,
           CAST(sum(int_fwd) OVER r4 / nullif(sum(int_in) OVER r4, 0) AS DOUBLE)  AS g_int_fwd24h_share_4wk,
           sum(new_nb) OVER cum                                                   AS g_n_nb_cum,
           sum(new_silent) OVER cum                                               AS g_n_nb_silent
    FROM j
    WINDOW r4 AS (PARTITION BY account_id ORDER BY w ROWS BETWEEN {WINDOW - 1} PRECEDING AND CURRENT ROW),
           cum AS (PARTITION BY account_id ORDER BY w)
    ORDER BY account_id, weeks_since_open"""


def code_sha256() -> str:
    return hashlib.sha256((edges_sql(0) + weekly_sql(0, "STORE")).encode()).hexdigest()


def _paths(out: str) -> dict[str, str]:
    folder = os.path.join(out, "features")
    return {"graph": os.path.join(folder, GRAPH), "edges": os.path.join(folder, EDGES),
            "manifest": os.path.join(folder, MANIFEST), "store": os.path.join(folder, "weekly.parquet")}


def _expected(out: str) -> dict:
    store = manifest.check(out)                      # the weekly store must be current (silent footprint uses it)
    return {"features": FEATURES, "weeks": [0, LAST_WEEK], "cutoff_rule": manifest.CUTOFF_RULE,
            "run_manifest_sha256": manifest._sha256(os.path.join(out, "run_manifest.json")),
            "store_code_sha256": store.get("code_sha256"), "code_sha256": code_sha256()}


def check(out: str) -> dict:
    p = _paths(out)
    if not os.path.exists(p["manifest"]):
        raise FileNotFoundError(f"{p['manifest']} not found - run `python -m features graph --out {out}`")
    with open(p["manifest"]) as f:
        m = json.load(f)
    exp = _expected(out)
    bad = [k for k in exp if m.get(k) != exp[k]]
    if bad:
        raise ValueError(f"{out}/features graph store is stale ({', '.join(bad)} differ). Rebuild with --force.")
    return m


def build(out: str = amldata.DEFAULT_OUT, force: bool = False) -> tuple[str, int]:
    p = _paths(out)
    if os.path.exists(p["graph"]) and not force:
        try:
            check(out)
            return p["graph"], amldata.public(out).execute(f"SELECT count(*) FROM read_parquet('{p['graph']}')").fetchone()[0]
        except (ValueError, FileNotFoundError):
            pass
    exp = _expected(out)
    work = os.path.join(os.path.dirname(p["graph"]), "_graph_build")
    os.makedirs(work, exist_ok=True)
    con = amldata.public(out)
    con.execute(f"PRAGMA memory_limit='{os.environ.get('FEATURES_DUCKDB_MEMORY', '4GB')}'")
    con.execute(f"PRAGMA temp_directory='{os.path.join(work, 'duckdb_tmp')}'")
    months = [r[0] for r in con.execute("SELECT DISTINCT open_month FROM accounts ORDER BY 1").fetchall()]
    for m in months:
        con.execute(f"COPY ({weekly_sql(m, p['store'])}) TO '{os.path.join(work, f'g_{m}.parquet')}' (FORMAT PARQUET)")
        con.execute(f"COPY ({edges_sql(m)}) TO '{os.path.join(work, f'e_{m}.parquet')}' (FORMAT PARQUET)")
    for kind, dest in (("g", p["graph"]), ("e", p["edges"])):
        con.execute(f"COPY (SELECT * FROM read_parquet('{os.path.join(work, kind + '_*.parquet')}') "
                    f"ORDER BY account_id{', weeks_since_open' if kind == 'g' else ', day'}) TO '{dest}.tmp' (FORMAT PARQUET)")
        os.replace(dest + ".tmp", dest)
    n = con.execute(f"SELECT count(*) FROM read_parquet('{p['graph']}')").fetchone()[0]
    con.close()
    import shutil
    shutil.rmtree(work, ignore_errors=True)
    exp |= {"rows": int(n), "git_commit": manifest._git("rev-parse", "HEAD"),
            "git_uncommitted_changes": bool(manifest._git("status", "--porcelain", "--untracked-files=no"))}
    with open(p["manifest"], "w") as f:
        json.dump(exp, f, indent=2)
    return p["graph"], n


def load(out: str = amldata.DEFAULT_OUT, weeks: tuple[int, int] | None = None, months=None):
    """DataFrame KEY + FEATURES (float32) after checking the manifest; rows sorted by account and week."""
    check(out)
    con = amldata.public(out)
    where = []
    if weeks:
        where.append(f"weeks_since_open BETWEEN {weeks[0]} AND {weeks[1]}")
    if months:
        where.append(f"account_id IN (SELECT account_id FROM accounts WHERE open_month IN ({', '.join(map(str, months))}))")
    df = con.execute(f"SELECT * FROM read_parquet('{_paths(out)['graph']}') "
                     f"{'WHERE ' + ' AND '.join(where) if where else ''} ORDER BY account_id, weeks_since_open").df()
    for c in FEATURES:
        df[c] = df[c].astype("float32")
    return df


def edges(out: str = amldata.DEFAULT_OUT):
    check(out)
    return _paths(out)["edges"]
