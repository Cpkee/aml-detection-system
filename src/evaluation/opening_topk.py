"""What account-opening data buys at opening, report appendix (plan: outputs/modelling/opening_topk/PLAN.md).

The harness gives the model about 5 flags a week, so in the weeks before laundering starts it spends too few flags
(24 on month 5) to show whether the application carries an early signal. This asks the question directly: rank the
month-5 accounts by the model of record's application score on the day they open, take the top N, and count how many
later launder, next to what chance would give.

  flagged        the N accounts with the highest application score (ties: lower account id first)
  launderers     of those, accounts that launder at any time in their 18 months (the fixed final label), by type
  precision      launderers / N;   reviews_per_launderer = N / launderers
  chance         launderers expected if the N accounts were picked at random = N x the cohort's launderer share
  lift           launderers / chance;   p_chance = chance of at least this many launderers in a random pick
  share_caught   launderers / all launderers in the cohort
  head start     median days from opening (the flag day) to the launderer's laundering start

The application score is the saved logistic model inside the model of record (fitted on months 0-4 only, label "mule
by week 26"), so month 5 is unseen by it. Nothing is fitted here. Month 5 only: test months 6-7 are refused. This is
scoring code, so it may read hidden tables (amldata.evaluation, through the harness's cohort_truth).

    PYTHONPATH=src python -m evaluation.opening_topk --out data/v1_full
    -> outputs/modelling/opening_topk/<data>/table.csv + report.md
"""
from __future__ import annotations
import argparse
import json
import os

import numpy as np
import pandas as pd
from scipy.stats import hypergeom

import amldata
from evaluation import score as harness

REPORT = "outputs/modelling/opening_topk"
MONTHS = (5,)                             # plan: month 5 only, never test months 6-7
TOP_N = (25, 50, 100, 200, 500)           # fixed in the plan before any run
PROFILES = harness.PROFILES


def table(scores: pd.Series, truth: pd.DataFrame, top_n=TOP_N) -> pd.DataFrame:
    """One row per N. scores: application score per account_id; truth: the harness's cohort_truth columns."""
    t = truth.set_index("account_id")
    if set(scores.index) != set(t.index) or scores.index.has_duplicates:
        raise ValueError("scores must cover every cohort account exactly once")
    if not np.isfinite(scores.to_numpy(dtype=float)).all():
        raise ValueError("missing or infinite scores")
    order = (pd.DataFrame({"score": scores}).rename_axis("account_id").reset_index()
             .sort_values(["score", "account_id"], ascending=[False, True], kind="stable")["account_id"])
    launderer = t["is_launderer"] == 1
    total, n_all = int(launderer.sum()), len(t)
    rows = []
    for n in top_n:
        if n > n_all:
            raise ValueError(f"top {n} is more than the cohort's {n_all} accounts")
        top = t.loc[order.head(n)]
        hit = top[top["is_launderer"] == 1]
        k = len(hit)
        r = {"top_n": n, "share_of_accounts": n / n_all, "launderers": k, "precision": k / n,
             "reviews_per_launderer": n / k if k else np.nan, "chance": n * total / n_all,
             "lift": k / (n * total / n_all) if total else np.nan,
             "p_chance": float(hypergeom.sf(k - 1, n_all, total, n)), "share_caught": k / max(total, 1)}
        for p in PROFILES:
            r[p] = int((hit["profile"] == p).sum())
        r["median_days_opening_to_start"] = float((hit["start_day"] - hit["open_day"]).median()) if k else np.nan
        rows.append(r)
    return pd.DataFrame(rows)


def app_scores(out: str, ids, model: str) -> pd.Series:
    """The model of record's saved application score for these accounts (public cleaned table only)."""
    from models import train as trainer
    app_model = json.load(open(os.path.join(trainer.find_model_dir(out, model), "app_logreg.json")))
    return trainer.app_scores_for(out, app_model, ids)


def run(out: str = amldata.DEFAULT_OUT, months=MONTHS, model: str | None = None, report: str | None = None) -> str:
    if tuple(months) != MONTHS:
        raise ValueError(f"opening_topk scores month {MONTHS[0]} only (plan: never test months 6-7), got {list(months)}")
    from models import train as trainer
    model = model or trainer.MODEL_OF_RECORD
    truth = harness.cohort_truth(out, months)
    tab = table(app_scores(out, truth["account_id"], model), truth)
    report = report or os.path.join(REPORT, os.path.basename(os.path.normpath(out)))
    os.makedirs(report, exist_ok=True)
    tab.to_csv(os.path.join(report, "table.csv"), index=False)
    n, total = len(truth), int((truth["is_launderer"] == 1).sum())
    by_type = truth.loc[truth["is_launderer"] == 1, "profile"].value_counts().to_dict()
    show = tab.assign(share_of_accounts=tab["share_of_accounts"].map("{:.2%}".format),
                      precision=tab["precision"].map("{:.1%}".format), chance=tab["chance"].round(2),
                      lift=tab["lift"].round(1), p_chance=tab["p_chance"].map("{:.3g}".format),
                      share_caught=tab["share_caught"].map("{:.1%}".format),
                      reviews_per_launderer=tab["reviews_per_launderer"].round(1))
    lines = [f"# Top N by application score at opening: month {MONTHS[0]} of {out}", "",
             f"Cohort: {n:,} accounts, {total} launder at some point in their 18 months "
             f"({', '.join(f'{k} {v}' for k, v in by_type.items())}); launderer share {total / n:.2%}.",
             f"Application score: the saved logistic model inside `{model}` (fitted on months 0-4).", "",
             show.to_markdown(index=False), "",
             "- chance: launderers expected in a random pick of N; p_chance: chance of at least this many by luck.",
             "- median_days_opening_to_start: the head start a flag at opening gives over the launderer's start.",
             "- launderers are counted by the fixed final label (at any time in the 18 months), since the flag is "
             "raised on the opening day."]
    with open(os.path.join(report, "report.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m evaluation.opening_topk", description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=amldata.DEFAULT_OUT)
    ap.add_argument("--months", nargs="+", type=int, default=list(MONTHS))
    ap.add_argument("--model", default=None, help="model whose application score is used (default: model of record)")
    a = ap.parse_args(argv)
    report = run(a.out, a.months, a.model)
    print(open(os.path.join(report, "report.md")).read())
    print(f"-> {report}")


if __name__ == "__main__":
    main()
