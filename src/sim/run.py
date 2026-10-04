"""Command line for the simulator.

  PYTHONPATH=src python -m sim.run accounts  --baf PATH     # steps 1-3
  PYTHONPATH=src python -m sim.run normal    --batches 0-9  # step 4, in batches
  PYTHONPATH=src python -m sim.run laundering               # step 5
  PYTHONPATH=src python -m sim.run finalize                 # merge into the 6 files
  PYTHONPATH=src python -m sim.run all       --baf PATH     # everything
Step 6 (the bank's 6 rules) is a separate module; until it exists the two aml files are written empty.
"""
from __future__ import annotations
import argparse
import glob
import os
import tempfile
import time

import duckdb
import numpy as np
import pandas as pd

from .config import Cfg
from .accounts import load_baf, build_accounts
from .normal import generate_normal
from .laundering import generate_laundering
from .common import to_output


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
        tx.to_parquet(os.path.join(p["parts"], f"tx_normal_{b:03d}.parquet"), index=False)
        truth.to_parquet(os.path.join(p["parts"], f"truth_normal_{b:03d}.parquet"), index=False)
        print(f"batch {b}: {len(tx):,} rows in {time.time() - t:.1f}s")


def step_laundering(cfg, out):
    p = _paths(out)
    acc = pd.read_parquet(p["accounts"], columns=["account_id", "open_day"])
    truth = pd.read_parquet(p["truth"])
    internal = pd.read_parquet(p["internal"])
    rng = np.random.default_rng([cfg.get("meta.seed"), 2])
    rows = generate_laundering(cfg, truth, internal, acc["open_day"].to_numpy(), rng,
                               pair_base=9_000_000_000).frame()
    ids = acc["account_id"].to_numpy()
    tx, ttruth = to_output(rows, ids, prefix="L_")
    tx.to_parquet(os.path.join(p["parts"], "tx_laundering.parquet"), index=False)
    ttruth.to_parquet(os.path.join(p["parts"], "truth_laundering.parquet"), index=False)
    sums = tx.groupby(["account_id", "direction"])["amount"].sum().unstack(fill_value=0.0)
    truth["laundered_in"] = truth["account_id"].map(sums.get("in", pd.Series(dtype=float))).fillna(0.0).round(2)
    truth["laundered_out"] = truth["account_id"].map(sums.get("out", pd.Series(dtype=float))).fillna(0.0).round(2)
    truth.to_parquet(p["truth"], index=False)
    print(f"laundering rows: {len(tx):,}  money in: {truth.laundered_in.sum():,.0f}  out: {truth.laundered_out.sum():,.0f}")


def step_finalize(out):
    p = _paths(out)
    con = duckdb.connect()
    con.execute("PRAGMA memory_limit='1500MB'")
    con.execute(f"PRAGMA temp_directory='{tempfile.gettempdir()}/sim_duckdb'")
    con.execute("PRAGMA preserve_insertion_order=false")
    tx_parts = os.path.join(p["parts"], "tx_*.parquet")
    tr_parts = os.path.join(p["parts"], "truth_*.parquet")
    con.execute(f"COPY (SELECT * FROM read_parquet('{tx_parts}')) TO '{p['tx']}' (FORMAT PARQUET)")
    con.execute(f"COPY (SELECT * FROM read_parquet('{tr_parts}')) TO '{p['txtruth']}' (FORMAT PARQUET)")
    pd.DataFrame({"alert_id": pd.Series(dtype=str), "account_id": pd.Series(dtype=str),
                  "alert_day": pd.Series(dtype="Int64"), "rules_fired": pd.Series(dtype=str),
                  "review_days": pd.Series(dtype="Int64"), "confirmed": pd.Series(dtype="Int64")}).to_parquet(p["alerts"], index=False)
    acc = pd.read_parquet(p["accounts"], columns=["account_id"])
    pd.DataFrame({"account_id": acc["account_id"], "aml_alert_day": pd.array([pd.NA] * len(acc), dtype="Int64"),
                  "aml_exit_day": pd.array([pd.NA] * len(acc), dtype="Int64")}).to_parquet(p["outcomes"], index=False)
    n = con.execute(f"SELECT count(*) FROM read_parquet('{p['tx']}')").fetchone()[0]
    print(f"transactions: {n:,} rows written")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["accounts", "normal", "laundering", "finalize", "all"])
    ap.add_argument("--config", default="configs/sim.yaml")
    ap.add_argument("--baf")
    ap.add_argument("--out")
    ap.add_argument("--batches", default="all")
    a = ap.parse_args()
    cfg = Cfg(a.config)
    out = a.out or cfg.get("paths.out_dir")
    baf = a.baf or cfg.get("paths.baf_file")
    if a.batches == "all":
        n_b = int(np.ceil(cfg.get("size.n_accounts") / cfg.get("size.batch_size")))
        batches = range(n_b)
    else:
        lo, hi = map(int, a.batches.split("-"))
        batches = range(lo, hi + 1)
    if a.step in ("accounts", "all"):
        step_accounts(cfg, out, baf)
    if a.step in ("normal", "all"):
        step_normal(cfg, out, batches)
    if a.step in ("laundering", "all"):
        step_laundering(cfg, out)
    if a.step in ("finalize", "all"):
        step_finalize(out)


if __name__ == "__main__":
    main()
