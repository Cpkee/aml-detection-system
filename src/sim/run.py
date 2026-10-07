"""Command line for the simulator.

  PYTHONPATH=src python -m sim.run accounts  --baf PATH     # steps 1-3
  PYTHONPATH=src python -m sim.run normal    --batches 0-9  # step 4, in batches
  PYTHONPATH=src python -m sim.run laundering               # step 5
  PYTHONPATH=src python -m sim.run finalize                 # merge into the 6 files
  PYTHONPATH=src python -m sim.run all       --baf PATH     # everything
  PYTHONPATH=src python -m sim.run rules                    # step 6: tune the bank's rules, find closures
  (finalize then removes activity after closure and writes the alert files)

Override settings for one run without editing configs/sim.yaml (repeatable, value read as YAML):
  PYTHONPATH=src python -m sim.run all --out data/v1_full --set size.n_accounts=244000
The first step records the overrides in <out>/run_manifest.json; later steps must pass the same --set values.
"""
from __future__ import annotations
import argparse
import glob
import subprocess
import sys
import json
import os
import tempfile
import time

import duckdb
import numpy as np
import pandas as pd

from .config import Cfg, check_manifest, write_manifest
from .accounts import load_baf, build_accounts
from .normal import generate_normal
from .laundering import generate_laundering
from .common import to_output
from .rules import RULES, weekly_features, hits, decide, tune


def _paths(out):
    return {k: os.path.join(out, f) for k, f in {
        "accounts": "accounts.parquet", "truth": "accounts_truth.parquet",
        "tx": "transactions.parquet", "txtruth": "transactions_truth.parquet",
        "alerts": "aml_alerts.parquet", "outcomes": "aml_outcomes.parquet",
        "internal": "_internal/accounts_internal.parquet", "parts": "_internal/parts"}.items()}


def step_accounts(cfg, out, baf_path):
    p = _paths(out)
    os.makedirs(p["parts"], exist_ok=True)
    rng = np.random.default_rng(cfg.get("meta.seed"))
    accounts, truth, internal = build_accounts(cfg, load_baf(baf_path), rng)
    accounts.to_parquet(p["accounts"], index=False)
    truth.to_parquet(p["truth"], index=False)
    internal.to_parquet(p["internal"], index=False)
    print(f"accounts: {len(accounts):,}  launderers: {truth.is_launderer.sum()}  "
          f"profiles: {truth.profile.value_counts().to_dict()}")


def step_normal(cfg, out, batches):
    p = _paths(out)
    acc = pd.read_parquet(p["accounts"], columns=["account_id", "open_day", "income"])
    ids = acc["account_id"].to_numpy()
    all_open = acc["open_day"].to_numpy()
    bs = cfg.get("size.batch_size")
    n_batches = int(np.ceil(len(acc) / bs))
    for b in batches:
        if b >= n_batches:
            continue
        t = time.time()
        rng = np.random.default_rng([cfg.get("meta.seed"), 1, b])
        batch = acc.iloc[b * bs:(b + 1) * bs].copy()
        batch["acct"] = np.arange(b * bs, b * bs + len(batch))
        batch.attrs["pair_base"] = b * 10_000_000
        rows = generate_normal(cfg, batch, all_open, rng).frame()
        tx, truth = to_output(rows, ids, prefix=f"N{b:03d}_")
        tx.attrs = {}
        tx.to_parquet(os.path.join(p["parts"], f"tx_normal_{b:03d}.parquet"), index=False)
        truth.to_parquet(os.path.join(p["parts"], f"truth_normal_{b:03d}.parquet"), index=False)
        print(f"batch {b}: {len(tx):,} rows in {time.time() - t:.1f}s")


def step_laundering(cfg, out):
    p = _paths(out)
    acc = pd.read_parquet(p["accounts"], columns=["account_id", "open_day"])
    truth = pd.read_parquet(p["truth"])
    internal = pd.read_parquet(p["internal"])
    rng = np.random.default_rng([cfg.get("meta.seed"), 2])
    rows, shape_of = generate_laundering(cfg, truth, internal, acc["open_day"].to_numpy(), rng,
                                         pair_base=9_000_000_000)
    rows = rows.frame()
    shapes = pd.DataFrame({"account_id": acc["account_id"].to_numpy()[list(shape_of)], "shape": list(shape_of.values())})
    shapes.to_parquet(os.path.join(out, "_internal/launderer_shapes.parquet"), index=False)
    print(shapes["shape"].value_counts().to_string())
    ids = acc["account_id"].to_numpy()
    tx, ttruth = to_output(rows, ids, prefix="L_")
    tx.attrs["links"].to_parquet(os.path.join(out, "_internal/forward_links.parquet"), index=False)
    tx.attrs = {}
    tx.to_parquet(os.path.join(p["parts"], "tx_laundering.parquet"), index=False)
    ttruth.to_parquet(os.path.join(p["parts"], "truth_laundering.parquet"), index=False)
    sums = tx.groupby(["account_id", "direction"])["amount"].sum().unstack(fill_value=0.0)
    truth["laundered_in"] = truth["account_id"].map(sums.get("in", pd.Series(dtype=float))).fillna(0.0).round(2)
    truth["laundered_out"] = truth["account_id"].map(sums.get("out", pd.Series(dtype=float))).fillna(0.0).round(2)
    truth.to_parquet(p["truth"], index=False)
    print(f"laundering rows: {len(tx):,}  money in: {truth.laundered_in.sum():,.0f}  out: {truth.laundered_out.sum():,.0f}")


def _con():
    con = duckdb.connect()
    con.execute("PRAGMA memory_limit='1500MB'")
    con.execute(f"PRAGMA temp_directory='{tempfile.gettempdir()}/sim_duckdb_{os.getpid()}'")
    con.execute("PRAGMA preserve_insertion_order=false")
    return con


def _truth_arrays(p):
    tr = pd.read_parquet(p["truth"], columns=["is_launderer", "launder_start_day"])
    return tr["launder_start_day"].fillna(-1).to_numpy().astype(int), tr["is_launderer"].to_numpy()


def step_rules(cfg, out):
    """Tune R3-R6 on the full simulated data (or use rules.fixed_scale), then record which accounts the bank closes."""
    p = _paths(out)
    con = _con()
    tx_rel = f"read_parquet('{os.path.join(p['parts'], 'tx_*.parquet')}')"
    f = weekly_features(con, tx_rel, p["accounts"], cfg)
    start, is_l = _truth_arrays(p)
    seed = cfg.get("meta.seed")
    fixed = cfg.get("rules.fixed_scale")
    if fixed is None:
        scale, table = tune(f, cfg, start, is_l, seed)
        table.to_csv(os.path.join(out, "_internal/rules_tuning.csv"), index=False)
        print(table.to_string(index=False))
    else:   # frozen rules: thresholds set elsewhere, never tuned on this run's labels
        scale = float(fixed)
        print(f"rules frozen at scale {scale} (rules.fixed_scale): not tuned on this run")
    _, exits = decide(hits(f, cfg, scale), cfg, start, is_l, seed)
    ids = pd.read_parquet(p["accounts"], columns=["account_id"])["account_id"].to_numpy()
    pd.DataFrame({"account_id": ids[list(exits)], "exit_day": list(exits.values())}).to_parquet(
        os.path.join(out, "_internal/exits.parquet"), index=False)
    with open(os.path.join(out, "_internal/rules_state.json"), "w") as fh:
        json.dump({"scale": scale, "frozen": fixed is not None}, fh)
    print(f"{'frozen' if fixed is not None else 'chosen'} scale {scale}: closures {len(exits)}")


def _write_final(con, p, exits_path, seed):
    tx_parts = os.path.join(p["parts"], "tx_*.parquet")
    tr_parts = os.path.join(p["parts"], "truth_*.parquet")
    con.execute(f"""CREATE OR REPLACE TEMP TABLE removed AS
        SELECT DISTINCT t.txn_id FROM read_parquet('{tx_parts}') t
        JOIN read_parquet('{exits_path}') e USING (account_id) WHERE t.day > e.exit_day""")
    links = os.path.join(os.path.dirname(exits_path), "forward_links.parquet")
    if os.path.exists(links):   # money that never arrived can't be forwarded on
        con.execute(f"""INSERT INTO removed SELECT DISTINCT l.txn_id FROM read_parquet('{links}') l
                        JOIN removed r ON r.txn_id = l.hop_txn_id ANTI JOIN removed r2 ON r2.txn_id = l.txn_id""")
    # Part files use provisional ids ('N003_17', 'L_5') that reveal which generator made a row.
    # Public ids are 'T' + 16 hex digits of md5(provisional id + seed): random-looking, the same for both rows
    # of a transfer, and no lookup table needed. Rows are sorted by time, so neither the id nor the row's
    # position in the file says anything about laundering. (A duplicate id would fail check 1.)
    new_id = f"'T' || substr(md5(txn_id || ':{seed}'), 1, 16)"
    con.execute(f"""COPY (SELECT * FROM (SELECT {new_id} AS txn_id, * EXCLUDE (txn_id) FROM read_parquet('{tx_parts}')
                                         ANTI JOIN removed USING (txn_id))
                          ORDER BY day, time, txn_id, account_id)
                    TO '{p['tx']}' (FORMAT PARQUET)""")
    con.execute(f"""COPY (SELECT {new_id} AS txn_id, * EXCLUDE (txn_id) FROM read_parquet('{tr_parts}')
                          ANTI JOIN removed USING (txn_id)) TO '{p['txtruth']}' (FORMAT PARQUET)""")
    return con.execute("SELECT count(*) FROM removed").fetchone()[0]


def step_finalize(cfg, out):
    """Merge batches, remove activity after closure, run the rules on the final data, write all 6 files."""
    p = _paths(out)
    con = _con()
    exits_path = os.path.join(out, "_internal/exits.parquet")
    with open(os.path.join(out, "_internal/rules_state.json")) as fh:
        scale = json.load(fh)["scale"]
    start, is_l = _truth_arrays(p)
    ids = pd.read_parquet(p["accounts"], columns=["account_id"])["account_id"].to_numpy()
    seed = cfg.get("meta.seed")
    for it in range(4):
        removed = _write_final(con, p, exits_path, seed)
        f = weekly_features(con, f"read_parquet('{p['tx']}')", p["accounts"], cfg)
        al, exits = decide(hits(f, cfg, scale), cfg, start, is_l, seed)
        old = pd.read_parquet(exits_path)
        new = pd.DataFrame({"account_id": ids[list(exits)], "exit_day": list(exits.values())})
        same = old.sort_values("account_id").reset_index(drop=True).equals(new.sort_values("account_id").reset_index(drop=True))
        print(f"pass {it + 1}: removed {removed:,} transfers after closure; closures {len(new)}; stable {same}")
        if same:
            break
        new.to_parquet(exits_path, index=False)
    rules_fired = al[RULES].apply(lambda r: ";".join(k for k in RULES if r[k]), axis=1)
    alerts = pd.DataFrame({"alert_id": [f"AL{i:07d}" for i in range(1, len(al) + 1)],
                           "account_id": ids[al["acct"].to_numpy()], "alert_day": al["alert_day"].to_numpy(),
                           "rules_fired": rules_fired.to_numpy(), "review_days": al["review_days"].to_numpy(),
                           "confirmed": al["confirmed"].to_numpy()})
    alerts.to_parquet(p["alerts"], index=False)
    first = alerts.groupby("account_id")["alert_day"].min()
    outcomes = pd.DataFrame({"account_id": ids})
    outcomes["aml_alert_day"] = pd.array(outcomes["account_id"].map(first), dtype="Int64")
    outcomes["aml_exit_day"] = pd.array(outcomes["account_id"].map(new.set_index("account_id")["exit_day"]), dtype="Int64")
    outcomes.to_parquet(p["outcomes"], index=False)
    # laundered money after removal
    lt = con.execute(f"""SELECT t.account_id, t.direction, sum(t.amount) s FROM read_parquet('{p['tx']}') t
                         JOIN read_parquet('{p['txtruth']}') r USING (txn_id) WHERE r.is_laundering = 1 GROUP BY 1, 2""").df()
    piv = lt.pivot_table(index="account_id", columns="direction", values="s", fill_value=0.0)
    truth = pd.read_parquet(p["truth"])
    truth["laundered_in"] = truth["account_id"].map(piv.get("in", pd.Series(dtype=float))).fillna(0.0).round(2)
    truth["laundered_out"] = truth["account_id"].map(piv.get("out", pd.Series(dtype=float))).fillna(0.0).round(2)
    truth.to_parquet(p["truth"], index=False)
    n = con.execute(f"SELECT count(*) FROM read_parquet('{p['tx']}')").fetchone()[0]
    print(f"transactions: {n:,} rows; alerts: {len(alerts):,} (confirmed {alerts.confirmed.sum()}); closures: {len(new)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["accounts", "normal", "laundering", "rules", "finalize", "all"])
    ap.add_argument("--config", default="configs/sim.yaml")
    ap.add_argument("--baf")
    ap.add_argument("--out")
    ap.add_argument("--batches", default="all")
    ap.add_argument("--in-process", action="store_true", help="run all normal batches in this process (needs more memory)")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                    help="override a setting for this run only, e.g. --set size.n_accounts=244000 (repeatable; "
                         "value read as YAML). Recorded in <out>/run_manifest.json")
    a = ap.parse_args()
    cfg = Cfg(a.config, set_args=a.set)
    out = a.out or cfg.get("paths.out_dir")
    baf = a.baf or cfg.get("paths.baf_file")
    if a.step in ("accounts", "all"):
        write_manifest(cfg, out, baf)
        if cfg.overrides:
            print(f"overrides: {cfg.overrides}")
    else:
        check_manifest(cfg, out)
    if a.batches == "all":
        n_b = int(np.ceil(cfg.get("size.n_accounts") / cfg.get("size.batch_size")))
        batches = range(n_b)
    else:
        lo, hi = map(int, a.batches.split("-"))
        batches = range(lo, hi + 1)
    if a.step in ("accounts", "all"):
        step_accounts(cfg, out, baf)
    if a.step in ("normal", "all"):
        if len(batches) > 1 and not a.in_process:
            # one process per batch: memory is fully released between batches (~2.7 GB peak per 5,000 accounts)
            for b in batches:
                cmd = [sys.executable, "-m", "sim.run", "normal", "--config", a.config, "--out", out,
                       "--batches", f"{b}-{b}"] + [x for s in a.set for x in ("--set", s)]
                subprocess.run(cmd, check=True, env={**os.environ, "PYTHONPATH": os.pathsep.join(sys.path)})
        else:
            step_normal(cfg, out, batches)
    if a.step in ("laundering", "all"):
        step_laundering(cfg, out)
    if a.step in ("rules", "all"):
        step_rules(cfg, out)
    if a.step in ("finalize", "all"):
        step_finalize(cfg, out)


if __name__ == "__main__":
    main()
