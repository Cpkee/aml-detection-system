"""Outlier appendix (outputs/modelling/outlier/PLAN.md), evaluation items 2-5: who each method catches, on one cohort
month (month 5, decision D1), weeks 0-26, at the rules' weekly budget with permanent flags (the harness's own
functions in evaluation.score, so the counts match its report).

  hidden     mules (by the end of week 26) split into bank-confirmed (closed by the bank at any time in the window)
             and never confirmed; caught per method in each group
  pattern    caught per laundering pattern; each mule counts once, under its main pattern (the SAML-D type of most of
             its laundering transactions: money forwarded through a network keeps the sender's type, so an account
             can carry several)
  alarms     the normal accounts each method flags with the highest scores, with the outlier inputs of that week
  bootstrap  paired difference in mules caught for every pair of methods: 1,000 resamples of the mules (account
             level), 95% interval; `clear` when it excludes 0

    PYTHONPATH=src python -m evaluation.hidden_mules --out data/v1_full \\
        --scores frozen_tuned=data/v1_full/scores/frozen_tuned_m5.parquet rarity=data/v1_full/scores/outlier_rarity_m5.parquet

Scoring code: it reads hidden tables (amldata.evaluation); nothing it reads goes back into a model.
"""
from __future__ import annotations
import argparse
import itertools
import json
import os

import numpy as np
import pandas as pd

import amldata
from evaluation import budget as rules_budget
from evaluation import score as harness
from features import manifest

HORIZON = 26
N_BOOT = 1000
N_ALARMS = 20
REPORT = "outputs/modelling/outlier"


def flags(truth: pd.DataFrame, scores: pd.DataFrame, k: dict[int, int]) -> pd.Series:
    """First flag week per account, exactly as the harness flags (open weeks only, permanent, weekly budget k)."""
    live = harness.open_rows(scores, truth)
    return harness.permanent_flags(live[live["weeks_since_open"] <= HORIZON], k)


def main_pattern(out: str, ids) -> pd.Series:
    """Laundering pattern with most of each account's laundering transactions (ties: alphabetical), by account_id."""
    con = amldata.evaluation(out)
    con.register("ids", pd.DataFrame({"account_id": list(ids)}))
    df = con.execute("""
        SELECT t.account_id, tt.laundering_type AS pattern, count(*) AS n
        FROM transactions t JOIN transactions_truth tt USING (txn_id) JOIN ids USING (account_id)
        WHERE tt.is_laundering = 1 GROUP BY 1, 2""").df()
    df = df.sort_values(["account_id", "n", "pattern"], ascending=[True, False, True])
    return df.drop_duplicates("account_id").set_index("account_id")["pattern"]


def caught_by(groups: pd.Series, caught: dict[str, set]) -> pd.DataFrame:
    """Mules per group and caught per method (groups: group name by mule account_id)."""
    rows = []
    for g, ids in groups.groupby(groups).groups.items():
        rows.append({"group": g, "mules": len(ids), **{m: len(set(ids) & c) for m, c in caught.items()}})
    return pd.DataFrame(rows).sort_values("mules", ascending=False, kind="stable").reset_index(drop=True)


def bootstrap(mules: list, caught: dict[str, set], n: int = N_BOOT, seed: int = 42) -> pd.DataFrame:
    """Paired difference in mules caught (a - b) for every pair, with a 95% interval over resampled mules."""
    idx = np.random.default_rng(seed).integers(0, len(mules), (n, len(mules)))
    hit = {m: np.array([a in c for a in mules], dtype=int) for m, c in caught.items()}
    rows = []
    for a, b in itertools.combinations(caught, 2):
        d = hit[a] - hit[b]
        lo, hi = np.percentile(d[idx].sum(axis=1), [2.5, 97.5])
        rows.append({"a": a, "b": b, "caught_a": int(hit[a].sum()), "caught_b": int(hit[b].sum()),
                     "difference": int(d.sum()), "low_95": lo, "high_95": hi, "clear": bool(lo > 0 or hi < 0)})
    return pd.DataFrame(rows)


def false_alarms(out: str, months, truth: pd.DataFrame, scores: dict[str, pd.DataFrame],
                 first: dict[str, pd.Series]) -> pd.DataFrame:
    """Per method, the N_ALARMS normal accounts it flags with the highest scores at their flag week, and the
    outlier inputs of that account-week (public store)."""
    from models import outlier
    x = outlier.load(out, months, open_only=False)
    normal = set(truth.loc[truth["is_launderer"] == 0, "account_id"])
    rows = []
    for m, f in first.items():
        f = f[f.index.isin(normal)]
        at = pd.DataFrame({"account_id": f.index, "weeks_since_open": f.to_numpy().astype(int)})
        top = at.merge(scores[m], on=outlier.KEY).nlargest(N_ALARMS, "score")
        rows.append(top.merge(x, on=outlier.KEY, how="left").assign(method=m))
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def run(out: str, months, scores_paths: dict[str, str], report: str) -> dict:
    months = tuple(int(m) for m in months)
    if set(months) & set(amldata.TEST_MONTHS):
        raise SystemExit("test months 6-7 are never used here (decision D1: month 5 only)")
    truth = harness.cohort_truth(out, months)
    k = {int(w): int(n) for w, n in rules_budget.weekly_budget(out, months, (0, HORIZON))
         .groupby("week")["alerts"].sum().items()}
    scores = {m: harness.load_scores(p, truth["account_id"], HORIZON) for m, p in scores_paths.items()}
    first = {m: flags(truth, s, k) for m, s in scores.items()}
    first_all = {"rules": harness.rules_flags(truth, HORIZON), **first}

    mules = truth.loc[harness.mule_at(truth, HORIZON).to_numpy(), "account_id"].tolist()
    caught = {m: set(f.index) & set(mules) for m, f in first_all.items()}
    t = truth.set_index("account_id").loc[mules]
    confirmed = pd.Series(np.where(t["exit_day"].notna(), "bank_confirmed", "never_confirmed"), index=t.index)
    res = {"hidden": caught_by(confirmed, caught),
           "type": caught_by(t["profile"], caught),
           "pattern": caught_by(main_pattern(out, mules).reindex(mules).fillna("none"), caught),
           "bootstrap": bootstrap(mules, caught),
           "alarms": false_alarms(out, months, truth, scores, first)}

    os.makedirs(report, exist_ok=True)
    for name, df in res.items():
        df.to_csv(os.path.join(report, f"{name}.csv"), index=False)
    settings = {"data": out, "cohort_months": list(months), "horizon": HORIZON, "mules": len(mules),
                "budget": int(sum(n for w, n in k.items() if w <= HORIZON)),
                "scores": {m: {"path": p, "sha256": manifest._sha256(p)} for m, p in scores_paths.items()},
                "run_manifest_sha256": manifest._sha256(os.path.join(out, "run_manifest.json")),
                "git_commit": manifest._git("rev-parse", "HEAD"),
                "git_uncommitted_changes": bool(manifest._git("status", "--porcelain", "--untracked-files=no"))}
    with open(os.path.join(report, "hidden_mules_settings.json"), "w") as f:
        json.dump(settings, f, indent=2)
    lines = [f"# Who each method catches: cohort month(s) {', '.join(map(str, months))}, weeks 0-{HORIZON}", "",
             f"{len(mules)} mules by the end of week {HORIZON}; every method flags at the rules' weekly budget "
             f"({settings['budget']} flags), permanently, as in `evaluation.score`.", "",
             "## Bank-confirmed vs never confirmed", "", res["hidden"].to_markdown(index=False), "",
             "## By type", "", res["type"].to_markdown(index=False), "",
             "## By main laundering pattern", "", res["pattern"].to_markdown(index=False), "",
             "## Paired differences in mules caught (1,000 account-level resamples, 95% interval)", "",
             res["bootstrap"].round(1).to_markdown(index=False), "",
             f"## Top {N_ALARMS} false alarms per method (normal accounts, highest score at the flag week)", "",
             "In `alarms.csv`, with the outlier inputs of that account-week."]
    with open(os.path.join(report, "hidden_mules.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m evaluation.hidden_mules", description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=amldata.DEFAULT_OUT)
    ap.add_argument("--months", nargs="+", type=int, default=[5])
    ap.add_argument("--scores", nargs="+", required=True, help="NAME=PATH score files (account_id, weeks_since_open, score)")
    ap.add_argument("--report", default=None, help=f"folder (default {REPORT}/<data>/)")
    a = ap.parse_args(argv)
    paths = dict(s.split("=", 1) for s in a.scores)
    report = a.report or os.path.join(REPORT, os.path.basename(os.path.normpath(a.out)))
    run(a.out, a.months, paths, report)
    print(f"-> {report}/hidden_mules.md")


if __name__ == "__main__":
    main()
