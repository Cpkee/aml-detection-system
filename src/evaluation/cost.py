"""Money gone before the first flag, month 5 (closing plan item 7).

    PYTHONPATH=src python -m evaluation.cost --out data/v1_full

For each month-5 cohort mule (a mule by the end of week 26 since opening, exactly as the harness: fake accounts from
opening, real customers from their start), the laundering money paid out of the account up to a policy's first flag,
or up to the end of week 26 if that policy never flags it. Summed per policy, against the ceiling (all laundering money
the cohort's mules paid out by the end of week 26). Policies and where their first flags come from (committed runs of
`evaluation.score`, never re-run here):

  rules      the bank's rules: first alert week in month5_dryrun_frozen_tuned_avg5/launderers.csv, dated by the exact
             first alert day (the harness's own flag day for the rules; checked against the file's week)
  model      the model of record frozen_tuned_avg5: model_flag_week_w26 of the same file
  scorecard  the rule scorecard: model_flag_week_w26 of month5_scorecard/launderers.csv

Definitions:
  paid out   a transaction row of the mule's account with direction 'out' and the hidden label is_laundering = 1
             (transfers, cash withdrawals, cross-border payments; the same rows as accounts_truth.laundered_out)
  flag day   as the harness dates a flag (score.flag_day): the rules on their first alert day, a weekly model flag at
             the end of its week (open_day + 7w + 6), the day the weekly score exists. Both use every row up to and
             including that day, so rows ON the flag day count as gone; a flag stops everything after it (an ideal
             freeze: the bank's 3-30 day review is ignored for every policy alike)
  closed     the bank closes an account only after a rule alert; the simulator removes all activity after closure.
             A model can no longer flag a closed account (as in the harness), and the money it paid out before
             closure counts as gone for that model; nothing after closure exists to count

Scoring code (src/evaluation): it may read hidden tables through amldata.evaluation(); nothing goes back into a model.
Month 5 only: the test months 6-7 are never read here.
"""
from __future__ import annotations

import argparse
import json
import os
import time

import numpy as np
import pandas as pd

import amldata
from evaluation import score
from features import manifest

MONTHS = (5,)
HORIZON = 26
RUNS = {"dryrun": "month5_dryrun_frozen_tuned_avg5", "scorecard": "month5_scorecard"}
POLICIES = {"rules": ("dryrun", "rules_first_alert_week"),            # policy -> (run, first-flag-week column)
            "model": ("dryrun", f"model_flag_week_w{HORIZON}"),
            "scorecard": ("scorecard", f"model_flag_week_w{HORIZON}")}
OUT_NAME = "month5_cost"
BOOT_N, BOOT_SEED = 10_000, 0


# ---------------------------------------------------------------- pure functions
def flag_days(mules: pd.DataFrame, weeks: pd.Series, rules: bool, w_hi: int = HORIZON) -> pd.Series:
    """First flag day per mule (NaN = not flagged by the end of week w_hi).

    mules: account_id (index), open_day, first_alert_day. weeks: first flag week since opening per account (from a
    committed launderers.csv). Rules: the exact first alert day, after checking it falls in the file's week. Model:
    the end of the flag week, as score.flag_day."""
    w = weeks.reindex(mules.index)
    w = w.where(w <= w_hi)
    if not rules:
        return score.cutoff(mules["open_day"], w)
    day = mules["first_alert_day"].where(w.notna())
    week_of_day = (day - mules["open_day"]) // 7
    bad = w.notna() & (week_of_day != w)
    if bad.any():
        raise ValueError(f"rules' first alert week in the file differs from the alert day for {list(w.index[bad])}")
    return day


def money_gone(rows: pd.DataFrame, end_day: pd.Series, flag_day: pd.Series) -> pd.Series:
    """Per mule: laundering money paid out on or before its flag day, or on or before end_day if never flagged.

    rows: account_id, day, amount (laundering rows paid out). end_day, flag_day: indexed by account_id."""
    stop = flag_day.reindex(end_day.index).fillna(end_day).clip(upper=end_day)
    r = rows[rows["account_id"].isin(end_day.index)]
    r = r[r["day"].to_numpy() <= r["account_id"].map(stop).to_numpy()]
    return r.groupby("account_id")["amount"].sum().reindex(end_day.index, fill_value=0.0)


def bootstrap_sum(diff: pd.Series, n: int = BOOT_N, seed: int = BOOT_SEED) -> tuple[float, float]:
    """95% percentile interval of sum(diff), resampling mules with replacement (paired: one value per mule)."""
    x = diff.to_numpy(dtype=float)
    idx = np.random.default_rng(seed).integers(0, len(x), size=(n, len(x)))
    sums = x[idx].sum(axis=1)
    return float(np.percentile(sums, 2.5)), float(np.percentile(sums, 97.5))


def summarise(per_mule: pd.DataFrame, policies, by=None) -> pd.DataFrame:
    """Per policy (and group, if `by`): mules, caught, money gone, ceiling, shares. per_mule has, per policy p,
    flag_day_<p> and gone_<p>, and the column ceiling (all laundering paid out by the end of the horizon)."""
    groups = [("all", per_mule)] if by is None else list(per_mule.groupby(by))
    rows = []
    for g, d in groups:
        for p in policies:
            caught = d[f"flag_day_{p}"].notna()
            gone, ceiling = d[f"gone_{p}"].sum(), d["ceiling"].sum()
            rows.append({**({} if by is None else {by: g}), "policy": p, "mules": len(d), "caught": int(caught.sum()),
                         "money_gone": round(gone, 2), "gone_caught_mules": round(d.loc[caught, f"gone_{p}"].sum(), 2),
                         "gone_missed_mules": round(d.loc[~caught, f"gone_{p}"].sum(), 2),
                         "ceiling": round(ceiling, 2), "share_gone": gone / ceiling if ceiling else np.nan,
                         "share_prevented": 1 - gone / ceiling if ceiling else np.nan})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- data
def laundering_out(out: str, ids) -> pd.DataFrame:
    """Laundering rows paid out of the given accounts: account_id, day, amount (DuckDB, filtered before pandas)."""
    con = amldata.evaluation(out)
    con.execute("SET enable_progress_bar = false")
    con.register("ids", pd.DataFrame({"account_id": list(ids)}))
    return con.execute("""SELECT t.account_id, t.day, t.amount
        FROM transactions t JOIN ids USING (account_id) JOIN transactions_truth r USING (txn_id)
        WHERE r.is_laundering = 1 AND t.direction = 'out' ORDER BY 1, 2""").df()


def load_runs(results: str) -> dict[str, pd.DataFrame]:
    """The committed launderers.csv of each run, indexed by account_id."""
    runs = {k: pd.read_csv(os.path.join(results, name, "launderers.csv")).set_index("account_id")
            for k, name in RUNS.items()}
    a, b = runs["dryrun"], runs["scorecard"]
    if not (a.index.equals(b.index) and a["rules_first_alert_week"].equals(b["rules_first_alert_week"])):
        raise ValueError("the two runs disagree on the launderers or the rules' alerts: not the same cohort")
    for k, (run, col) in POLICIES.items():
        if col not in runs[run].columns:
            raise ValueError(f"{RUNS[run]}/launderers.csv has no {col}: the first flag of '{k}' is unknown")
    return runs


def check_caught(summary: pd.DataFrame, results: str) -> None:
    """Mules and caught per policy must equal the committed harness summaries (same cohort, same flags)."""
    for k, (run, _) in POLICIES.items():
        s = pd.read_csv(os.path.join(results, RUNS[run], f"summary_w{HORIZON}.csv")).set_index("policy")
        pol = "rules" if k == "rules" else "model"
        mine = summary.set_index("policy").loc[k]
        if (int(mine["mules"]), int(mine["caught"])) != (int(s.loc[pol, "mules"]), int(s.loc[pol, "caught"])):
            raise ValueError(f"{k}: {mine['caught']} of {mine['mules']} caught here, harness says "
                             f"{s.loc[pol, 'caught']} of {s.loc[pol, 'mules']}")


def run(out: str, results: str | None = None, name: str = OUT_NAME) -> str:
    t0 = time.time()
    data = os.path.basename(os.path.normpath(out))
    results = results or os.path.join(score.RESULTS, data)
    report = os.path.join(results, name)
    if os.path.exists(report):
        raise SystemExit(f"{report} exists: results folders are never overwritten (pass --name for a new one)")
    runs = load_runs(results)

    truth = score.cohort_truth(out, MONTHS)                        # month 5 only (allow_test stays False)
    mules = truth[score.mule_at(truth, HORIZON).to_numpy()].set_index("account_id")
    days = ["open_day", "start_day", "exit_day", "first_alert_day"]
    mules[days] = mules[days].astype(float)                       # plain NaN, not DuckDB's nullable <NA>
    end_day = score.cutoff(mules["open_day"], HORIZON)
    rows = laundering_out(out, mules.index)

    per = pd.DataFrame({"profile": mules["profile"], "open_day": mules["open_day"], "start_day": mules["start_day"],
                        "exit_day": mules["exit_day"], "end_day": end_day})
    per["ceiling"] = money_gone(rows, end_day, pd.Series(np.nan, index=mules.index))
    for k, (r, col) in POLICIES.items():
        per[f"flag_day_{k}"] = flag_days(mules, runs[r][col], rules=k == "rules")
        per[f"gone_{k}"] = money_gone(rows, end_day, per[f"flag_day_{k}"])
    summary = summarise(per, POLICIES)
    check_caught(summary, results)
    boot = {}                                       # money the policy stops that the rules let through, paired by mule
    for k in POLICIES:
        if k != "rules":
            saved = per["gone_rules"] - per[f"gone_{k}"]
            boot[k] = (round(saved.sum(), 2), *(round(v, 2) for v in bootstrap_sum(saved)))
    for i, col in enumerate(["saved_vs_rules", "saved_lo", "saved_hi"]):
        summary[col] = summary["policy"].map({k: v[i] for k, v in boot.items()})
    by_type = summarise(per, POLICIES, by="profile")
    closed = per["exit_day"].notna() & (per["exit_day"] <= per["end_day"])
    closed_unflagged = {k: int((closed & ~(per[f"flag_day_{k}"] < per["exit_day"])).sum())     # NaN flag: not flagged
                        for k in POLICIES if k != "rules"}

    os.makedirs(report)
    per.reset_index().to_csv(os.path.join(report, "per_mule.csv"), index=False)
    summary.to_csv(os.path.join(report, "summary.csv"), index=False)
    by_type.to_csv(os.path.join(report, "by_type.csv"), index=False)
    inputs = [os.path.join(results, RUNS[r], f) for r in RUNS for f in ("launderers.csv", f"summary_w{HORIZON}.csv")]
    settings = {"data": data, "cohort_months": list(MONTHS), "horizon_weeks": HORIZON, "mules": len(per),
                "policies": {k: f"{RUNS[r]}/launderers.csv:{c}" for k, (r, c) in POLICIES.items()},
                "inputs_sha256": {os.path.relpath(p, results): manifest._sha256(p) for p in inputs},
                "run_manifest_sha256": manifest._sha256(os.path.join(out, "run_manifest.json")),
                "paid_out": "direction = 'out' and is_laundering = 1",
                "flag_day": "rules: first alert day; model / scorecard: end of the flag week (open_day + 7w + 6); "
                            "rows on the flag day count as gone",
                "closed_by_week26_and_not_flagged_before_closure": closed_unflagged,
                "bootstrap": {"n": BOOT_N, "seed": BOOT_SEED, "unit": "mule", "interval": "2.5-97.5 percentile",
                              "of": "sum over mules of (gone_rules - gone_policy)"},
                "git_commit": manifest._git("rev-parse", "HEAD"),
                "git_uncommitted_changes": bool(manifest._git("status", "--porcelain", "--untracked-files=no")),
                "seconds": round(time.time() - t0)}
    with open(os.path.join(report, "settings.json"), "w") as f:
        json.dump(settings, f, indent=2)
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m evaluation.cost", description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=amldata.DEFAULT_OUT)
    ap.add_argument("--name", default=OUT_NAME, help=f"new results folder (default {OUT_NAME})")
    a = ap.parse_args(argv)
    report = run(a.out, name=a.name)
    pd.set_option("display.width", 200)
    print(pd.read_csv(os.path.join(report, "summary.csv")).to_string(index=False))
    print(pd.read_csv(os.path.join(report, "by_type.csv")).to_string(index=False))
    print(f"-> {report}")


if __name__ == "__main__":
    main()
