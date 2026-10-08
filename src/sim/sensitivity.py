"""Sensitivity runs: one simulator run per `test` value in configs/sim.yaml, with the bank's rules frozen.

  PYTHONPATH=src python -m sim.sensitivity --list                    # the planned runs
  PYTHONPATH=src python -m sim.sensitivity --run [--only NAME ...]   # run them (finished runs are skipped)
  PYTHONPATH=src python -m sim.sensitivity --summarise               # rebuild the summary table only

Every run uses the main settings plus ONE change (team decisions 7 Oct 2026):
  - 244,000 accounts, seed 42, BAF Base; rules frozen at the scale tuned on the main full-size run
    (read from data/v1_full/_internal/rules_state.json, or pass --scale);
  - one `test` value of one setting; plus seeds 43 and 44 (the chance yardstick) and the prevalence runs
    (0.1% at 732,000 accounts so the test months keep ~180 launderers; 1% at 244,000).
Output: data/sensitivity/<name>/ (large transaction files deleted after the checks; every run can be rebuilt
exactly from its run_manifest.json; seed runs are kept whole) and outputs/sensitivity/:
runs/<name>/ (summary.json, data_card.md, run_manifest.json) and summary.csv (one row per run + the main run).
"""
from __future__ import annotations
import argparse
import json
import os
import shutil
import subprocess
import sys

import duckdb
import pandas as pd
import yaml

from .config import NOT_READ

CONFIG = "configs/sim.yaml"
BAF = "data/raw/BAF_Base.csv"
MAIN = "data/v1_full"
DATA_ROOT = "data/sensitivity"
OUT_ROOT = "outputs/sensitivity"
N_MAIN = 244_000
# settings whose `test` values are handled as special runs below, or not runnable as a one-setting change yet
SPECIAL = {
    "size.n_accounts": "the full-size main run itself",
    "profiles.launderer_share": "prevalence runs (special sizes, below)",
}


def _settings(node, path=()):
    if isinstance(node, dict) and "value" not in node:
        for k, v in node.items():
            yield from _settings(v, path + (k,))
    elif isinstance(node, dict):
        yield ".".join(path), node


def planned_runs(config=CONFIG) -> list[dict]:
    """Every run: name, the --set values it adds to the main settings, and whether to keep its large files."""
    cfg = yaml.safe_load(open(config))
    runs = []
    for key, node in _settings(cfg):
        if "test" not in node or key in SPECIAL or key in NOT_READ:
            continue
        for i, val in enumerate(node["test"], 1):
            runs.append({"name": f"{key.split('.')[-1]}__{i}", "setting": key, "test_value": val,
                         "set": [f"{key}={json.dumps(val)}"], "n_accounts": N_MAIN, "keep": False})
    for seed in (43, 44):
        runs.append({"name": f"seed__{seed}", "setting": "meta.seed", "test_value": seed,
                     "set": [f"meta.seed={seed}"], "n_accounts": N_MAIN, "keep": True})
    runs.append({"name": "prevalence__0.1pct", "setting": "profiles.launderer_share", "test_value": 0.001,
                 "set": ["profiles.launderer_share=0.001"], "n_accounts": 732_000, "keep": False})
    runs.append({"name": "prevalence__1pct", "setting": "profiles.launderer_share", "test_value": 0.01,
                 "set": ["profiles.launderer_share=0.01"], "n_accounts": N_MAIN, "keep": False})
    return runs


def frozen_scale(arg: float | None) -> float:
    if arg is not None:
        return arg
    with open(os.path.join(MAIN, "_internal/rules_state.json")) as fh:
        return float(json.load(fh)["scale"])


def summarise_run(out: str) -> dict:
    """Headline numbers of one finished run (same definitions as the data card)."""
    con = duckdb.connect()
    con.execute("PRAGMA memory_limit='2GB'")
    for f in ["accounts", "accounts_truth", "aml_alerts", "aml_outcomes"]:
        con.execute(f"CREATE VIEW {f} AS SELECT * FROM read_parquet('{os.path.join(out, f + '.parquet')}')")
    q = lambda s: con.execute(s).fetchone()[0]
    s = {
        "accounts": q("SELECT count(*) FROM accounts"),
        "launderers": int(q("SELECT sum(is_launderer) FROM accounts_truth")),
        "test_launderers": int(q("""SELECT sum(t.is_launderer) FROM accounts a JOIN accounts_truth t USING (account_id)
                                   WHERE a.open_month >= 6""")),
        "alerts": q("SELECT count(*) FROM aml_alerts"),
    }
    tru = """SELECT a.* FROM aml_alerts a JOIN accounts_truth t USING (account_id)
             WHERE t.is_launderer = 1 AND t.launder_start_day <= a.alert_day"""
    s["true_alerts"] = q(f"SELECT count(*) FROM ({tru})")
    s["false_alarm_share"] = round(1 - s["true_alerts"] / max(s["alerts"], 1), 4)
    caught = q(f"SELECT count(DISTINCT account_id) FROM ({tru})")
    s["launderers_caught_share"] = round(caught / max(s["launderers"], 1), 4)
    s["median_days_to_catch"] = q(f"""SELECT median(d - t.launder_start_day) FROM
        (SELECT account_id, min(alert_day) d FROM ({tru}) GROUP BY 1) JOIN accounts_truth t USING (account_id)""")
    s["weekly_budget_mean"] = round(q("SELECT avg(c) FROM (SELECT alert_day // 7, count(*) c FROM aml_alerts GROUP BY 1)") or 0, 1)
    s["closures"] = q("SELECT count(aml_exit_day) FROM aml_outcomes")
    for r in ["R1", "R2", "R3", "R4", "R5", "R6"]:
        s[f"alerts_{r}"] = q(f"SELECT count(*) FROM aml_alerts WHERE rules_fired LIKE '%{r}%'")
    card = open(os.path.join(out, "data_card.md")).read() if os.path.exists(os.path.join(out, "data_card.md")) else ""
    for line in card.splitlines():
        if line.startswith("- Activity model AUC:"):
            s["activity_auc"] = float(line.split(":")[1].split()[0])
        if line.startswith("- Application-only logistic AUC:"):
            s["application_auc"] = float(line.split(":")[1].split()[0])
    return s


def run_one(r: dict, scale: float) -> None:
    out = os.path.join(DATA_ROOT, r["name"])
    keep_dir = os.path.join(OUT_ROOT, "runs", r["name"])
    if os.path.exists(os.path.join(keep_dir, "summary.json")):
        print(f"skip {r['name']} (done)")
        return
    sets = [f"size.n_accounts={r['n_accounts']}", f"rules.fixed_scale={scale}"] + r["set"]
    env = {**os.environ, "PYTHONPATH": "src"}
    cmd = [sys.executable, "-m", "sim.run", "all", "--config", CONFIG, "--baf", BAF, "--out", out]
    for s in sets:
        cmd += ["--set", s]
    print(f"=== {r['name']}: --set {' --set '.join(sets)}", flush=True)
    subprocess.run(cmd, check=True, env=env, stdout=subprocess.DEVNULL)
    chk = subprocess.run([sys.executable, "-m", "sim.checks", "--config", CONFIG, "--out", out, "--baf", BAF],
                         env=env, capture_output=True, text=True)
    passed = sum(line.startswith("PASS") for line in chk.stdout.splitlines())
    failed = [line for line in chk.stdout.splitlines() if line.startswith("FAIL")]
    s = {"name": r["name"], "setting": r["setting"], "test_value": json.dumps(r["test_value"]),
         "checks_passed": passed, "checks_failed": "; ".join(failed), **summarise_run(out)}
    os.makedirs(keep_dir, exist_ok=True)
    for f in ["data_card.md", "run_manifest.json"]:
        shutil.copy(os.path.join(out, f), keep_dir)
    if not r["keep"]:   # rebuildable exactly from run_manifest.json
        for f in ["transactions.parquet", "transactions_truth.parquet"]:
            os.remove(os.path.join(out, f))
        shutil.rmtree(os.path.join(out, "_internal", "parts"), ignore_errors=True)
    with open(os.path.join(keep_dir, "summary.json"), "w") as fh:
        json.dump(s, fh, indent=2, default=str)
    print(f"    checks {passed}/10, false alarms {s['false_alarm_share']:.1%}, caught {s['launderers_caught_share']:.0%}",
          flush=True)


def write_summary() -> pd.DataFrame:
    rows = []
    if os.path.exists(os.path.join(MAIN, "aml_alerts.parquet")):
        rows.append({"name": "main", "setting": "", "test_value": "", **summarise_run(MAIN)})
    runs_dir = os.path.join(OUT_ROOT, "runs")
    for name in sorted(os.listdir(runs_dir)) if os.path.isdir(runs_dir) else []:
        p = os.path.join(runs_dir, name, "summary.json")
        if os.path.exists(p):
            rows.append(json.load(open(p)))
    df = pd.DataFrame(rows)
    os.makedirs(OUT_ROOT, exist_ok=True)
    df.to_csv(os.path.join(OUT_ROOT, "summary.csv"), index=False)
    return df


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", action="store_true")
    g.add_argument("--run", action="store_true")
    g.add_argument("--summarise", action="store_true")
    ap.add_argument("--only", nargs="*", help="run only these names")
    ap.add_argument("--scale", type=float, help="frozen R3-R6 scale (default: the main full-size run's)")
    a = ap.parse_args()
    runs = planned_runs()
    if a.only:
        runs = [r for r in runs if r["name"] in a.only]
    if a.list:
        for r in runs:
            print(f"{r['name']:34s} {r['n_accounts']:>8,}  --set {' '.join(r['set'])}")
        print(f"{len(runs)} runs. Not run as one-setting changes: " + "; ".join(f"{k} ({v})" for k, v in SPECIAL.items()))
        return
    if a.run:
        scale = frozen_scale(a.scale)
        print(f"rules frozen at scale {scale}")
        for r in runs:
            run_one(r, scale)
    print(write_summary().to_string(index=False))


if __name__ == "__main__":
    main()
