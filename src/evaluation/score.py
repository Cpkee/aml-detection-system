"""Phase 5 harness: the frozen model against the bank's rules on a fixed cohort, at the rules' own weekly budget.

    PYTHONPATH=src python -m evaluation.score --out data/v1_full                 # dry run: cohort = month 5, model of record
    PYTHONPATH=src python -m evaluation.score --out data/v1_full --months 6 7 --final-test   # once, 5 Nov 2026
    PYTHONPATH=src python -m evaluation.score --out data/v1_full --scores data/v1_full/scores/frozen_tuned_m5.parquet

The comparison agreed on 8 Oct 2026 (CLAUDE.md, "Fixed cohort"): every account opened in the cohort months, a clock
that counts weeks since each account opened, and in week w of their lives the model may flag as many accounts as the
rules raised alerts on the same cohort in that week. A model flag is permanent (decision 9 Oct 2026): each week it
takes the highest-scoring open accounts it has not flagged before. An account the bank closed stays in the cohort as
caught by the rules; the model can no longer flag it. Scores come from the model of record (`models.train.predict`,
trained on months 0-4 only), or from any file given with --scores: columns account_id, weeks_since_open, score, one row
per cohort account-week (e.g. `python -m models predict`, or another team's model). Equal scores: lower account id first.

Measures, over weeks 0-W (W = 26 main, 77 appendix):
  caught      launderers who are mules by the end of week W (fake accounts from opening, real customers from their
              start) and were flagged by then: by the model, by the rules, by both, by either. recall_final_label:
              caught / all launderers in the cohort by the fixed final label (label maturity: late starters count)
  precision   share of flagged accounts that are such mules (false-alarm share = 1 - precision); also against the
              fixed final label (a launderer at any point in the 18 months), the label-maturity view
  timing      days from each launderer's laundering start to its first flag (negative = before it started), and,
              for launderers both catch, how many days earlier the model flags than the rules' first alert. For
              launderers only the model catches, median_min_days_earlier_model_only: days from the model's flag to
              the end of week W, "at least this many days earlier" (the rules may alert later or never). A model
              flag is dated at the end of its week, the day the weekly score exists
  catch_mean  per week the share of that week's mules already flagged, averaged over weeks 0-W (the lab's catch_rules)
  any time    secondary policy (8 Oct 2026): one score threshold over the horizon, applied to each account's highest
              score, flagging as many accounts as the rules' total number of alerts. Not an upper bound: the model is
              trained on weeks 0-26 only, so past week 26 its running-total features leave the training range and
              late scores are not comparable across weeks
  by type     caught per hidden type (fake / witting / unwitting); per week: accounts still open, mules, starts

Test months 6-7 need --final-test and are scored once: before anything about them is read the run writes
outputs/modelling/results/<data>/final_test/STARTED.json, and on success LOCK.json; a final run is refused while
either exists (even after a crash: clearing it is a team decision). settings.json records where the scores came from
(score_source, scores_sha256 for a file), the data run (run_manifest_sha256) and the code (git_commit). This file is
scoring code, so it may read hidden tables (amldata.evaluation); nothing it reads goes back into a model.
"""
from __future__ import annotations
import argparse
import json
import os
import time
import warnings

import numpy as np
import pandas as pd

import amldata
from evaluation import budget as rules_budget
from features import manifest

RESULTS = "outputs/modelling/results"
TRAINED_WEEKS = 26            # models.train.WEEKS: the model is trained on weeks 0-26 since opening
PROFILES = ("fake", "witting", "unwitting")
AGE_BANDS = {"under 30": (0, 29), "30-49": (30, 49), "50+": (50, 200)}    # BAF customer_age is in decades


# ---------------------------------------------------------------- inputs
def cohort_truth(out: str, months, allow_test: bool = False) -> pd.DataFrame:
    """Per cohort account: opening day, hidden label, type, laundering start, closure and first rule alert day."""
    m = rules_budget._months(months, allow_test)
    return amldata.evaluation(out).execute(f"""
        SELECT a.account_id, a.open_month, a.open_day, a.customer_age, t.is_launderer,
               CASE WHEN t.is_launderer = 1 THEN t.profile END AS profile, t.launder_start_day AS start_day,
               o.aml_exit_day AS exit_day, al.first_alert_day
        FROM accounts a JOIN accounts_truth t USING (account_id)
        LEFT JOIN aml_outcomes o USING (account_id)
        LEFT JOIN (SELECT account_id, min(alert_day) AS first_alert_day FROM aml_alerts GROUP BY 1) al USING (account_id)
        WHERE a.open_month IN ({m}) ORDER BY a.account_id""").df()


def cutoff(open_day, w):
    return open_day + 7 * w + 6


def mule_at(truth: pd.DataFrame, w: int) -> pd.Series:
    """mule_by_day at the end of week w (as amldata.labels): fake accounts from opening, real customers from start."""
    started = truth["start_day"].notna() & (truth["start_day"] <= cutoff(truth["open_day"], w))
    return (truth["is_launderer"] == 1) & ((truth["profile"] == "fake") | started)


def score_cohort(out: str, months, weeks: tuple[int, int], model_name: str = "frozen",
                 check_data: bool = True) -> pd.DataFrame:
    """account_id, weeks_since_open, score for every cohort account-week (public inputs only; models.train.predict)."""
    from models import train as trainer
    return trainer.predict(out, months, weeks, model_name, check_data)


def load_scores(path: str, cohort, w_max: int) -> pd.DataFrame:
    """Scores from a file (parquet or csv: account_id, weeks_since_open, score), checked against the cohort: one row
    per account-week, only cohort accounts, weeks 0-w_max, finite scores. Missing account-weeks only warn."""
    if path.endswith(".csv"):
        s = pd.read_csv(path, float_precision="round_trip")      # exact floats, as in the parquet file
    else:
        s = pd.read_parquet(path)
    s = s[["account_id", "weeks_since_open", "score"]]
    cohort = set(cohort)
    problems = []
    if s.duplicated(["account_id", "weeks_since_open"]).any():
        problems.append("more than one score for some account-weeks")
    if not set(s["account_id"]) <= cohort:
        problems.append(f"{len(set(s['account_id']) - cohort)} accounts are not in the cohort")
    week = s["weeks_since_open"]
    if not (week.between(0, w_max) & (week % 1 == 0)).all():
        problems.append(f"weeks other than the whole numbers 0-{w_max} (e.g. `models predict --weeks 0-{w_max}`)")
    if not np.isfinite(s["score"].to_numpy(dtype=float)).all():
        problems.append("missing or infinite scores")
    if problems:
        raise ValueError(f"{path}: " + "; ".join(problems))
    s = s.astype({"weeks_since_open": "int64"})
    missing = len(cohort) * (w_max + 1) - len(s)
    if missing:
        warnings.warn(f"{path}: {missing} cohort account-weeks in weeks 0-{w_max} have no score (never flagged then)")
    return s


# ---------------------------------------------------------------- flagging
def open_rows(scores: pd.DataFrame, truth: pd.DataFrame) -> pd.DataFrame:
    """Scores of account-weeks whose account is still open at the end of that week (not yet closed by the bank)."""
    t = truth.set_index("account_id")
    exit_day = scores["account_id"].map(t["exit_day"])
    cut = cutoff(scores["account_id"].map(t["open_day"]), scores["weeks_since_open"])
    return scores[exit_day.isna() | (exit_day > cut)]


def permanent_flags(scores: pd.DataFrame, k: dict[int, int], ties: dict | None = None) -> pd.Series:
    """First flag week per account: each week the k[w] highest-scoring accounts not flagged before (ties: account id).
    ties, if given, receives per week the number of accounts tied at the cut line (0 when no tie crosses it)."""
    first: dict[str, int] = {}
    for w, g in scores.sort_values(["weeks_since_open", "score", "account_id"], ascending=[True, False, True],
                                   kind="stable").groupby("weeks_since_open", sort=True):
        n = int(k.get(int(w), 0))
        if n <= 0:
            continue
        pool = g[~g["account_id"].isin(first.keys())]
        if ties is not None and len(pool) > n and pool["score"].iloc[n] == pool["score"].iloc[n - 1]:
            ties[int(w)] = int((pool["score"] == pool["score"].iloc[n - 1]).sum())
        first.update({a: int(w) for a in pool["account_id"].head(n)})
    return pd.Series(first, dtype=float)


def anytime_flags(scores: pd.DataFrame, total: int) -> pd.Series:
    """Secondary policy: one threshold over the horizon so that `total` accounts are flagged, each at the first week
    its score reaches it."""
    if total <= 0 or scores.empty:
        return pd.Series(dtype=float)
    best = scores.groupby("account_id")["score"].max().sort_values(ascending=False, kind="stable")
    thr = best.iloc[min(total, len(best)) - 1]
    hit = scores[scores["score"] >= thr]
    first = hit.groupby("account_id")["weeks_since_open"].min()
    keep = best.index[:total]                                  # ties at the threshold: keep exactly `total`
    return first.reindex(keep).astype(float)


def rules_flags(truth: pd.DataFrame, w_hi: int) -> pd.Series:
    """The rules' first alert week since opening, for accounts alerted by the end of week w_hi."""
    t = truth.dropna(subset=["first_alert_day"])
    w = (t["first_alert_day"] - t["open_day"]) // 7
    return pd.Series(w.to_numpy(dtype=float), index=t["account_id"])[lambda s: s <= w_hi]


# ---------------------------------------------------------------- measures
def flag_day(truth: pd.DataFrame, first: pd.Series, rules: bool) -> pd.Series:
    """Day of each first flag: the rules' actual first alert day, the model's end of its flag week."""
    t = truth.set_index("account_id").loc[first.index]
    return t["first_alert_day"] if rules else cutoff(t["open_day"], first)


def measures(truth: pd.DataFrame, flags: dict[str, pd.Series], w_hi: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Summary per policy and the per-week table. flags: policy -> first flag week per account."""
    t = truth.set_index("account_id")
    mules = t.index[mule_at(truth, w_hi).to_numpy()]
    ever = t.index[t["is_launderer"] == 1]
    rows = []
    for name, f in flags.items():
        f = f[f <= w_hi]
        flagged = f.index
        caught = flagged.intersection(mules)
        day = flag_day(truth, f, rules=name == "rules")
        lead = (day - t.loc[f.index, "start_day"]).loc[caught]
        r = {"policy": name, "flagged": len(flagged), "mules": len(mules), "caught": len(caught),
             "recall": len(caught) / max(len(mules), 1), "recall_final_label": len(caught) / max(len(ever), 1),
             "precision": len(caught) / max(len(flagged), 1),
             "false_alarm_share": 1 - len(caught) / max(len(flagged), 1),
             "precision_final_label": len(flagged.intersection(ever)) / max(len(flagged), 1),
             "median_days_from_start": float(lead.median()) if len(lead) else np.nan,
             "flagged_before_start": int((lead < 0).sum())}
        for p in PROFILES:
            ids = t.index[(t["profile"] == p).to_numpy()].intersection(mules)
            r[f"caught_{p}"] = f"{len(caught.intersection(ids))}/{len(ids)}"
            lp = lead.reindex(caught.intersection(ids))
            r[f"median_days_from_start_{p}"] = float(lp.median()) if len(lp) else np.nan
        rows.append(r)
    summary = pd.DataFrame(rows)

    weekly = []
    for w in range(0, w_hi + 1):
        m_w = t.index[mule_at(truth, w).to_numpy()]
        cut = cutoff(t["open_day"], w)
        row = {"week": w, "open_accounts": int((t["exit_day"].isna() | (t["exit_day"] > cut)).sum()),
               "mules": len(m_w), "started": int((t["start_day"].notna() & (t["start_day"] <= cut)).sum())}
        for name, f in flags.items():
            got = f.index[(f <= w).to_numpy()]
            row[f"flagged_{name}"] = len(got)
            row[f"catch_{name}"] = len(m_w.intersection(got)) / max(len(m_w), 1)
        weekly.append(row)
    weekly = pd.DataFrame(weekly)
    for name in flags:
        summary.loc[summary.policy == name, "catch_mean"] = weekly.loc[weekly.mules > 0, f"catch_{name}"].mean()
    return summary, weekly


def by_age(truth: pd.DataFrame, flags: dict[str, pd.Series], w_hi: int) -> pd.DataFrame:
    """Per policy and age band: mules caught (recall) and normal accounts flagged (false-positive rate), the fairness
    view for Variant II. Normal = not a mule by the end of the horizon."""
    t = truth.set_index("account_id")
    mule = pd.Series(mule_at(truth, w_hi).to_numpy(), index=t.index)
    rows = []
    for name, f in flags.items():
        hit = t.index.isin(f[f <= w_hi].index)
        for band, (lo, hi) in AGE_BANDS.items():
            inb = t["customer_age"].between(lo, hi).to_numpy()
            m, n = inb & mule.to_numpy(), inb & ~mule.to_numpy()
            rows.append({"policy": name, "age": band, "accounts": int(inb.sum()), "mules": int(m.sum()),
                         "caught": int((hit & m).sum()), "recall": (hit & m).sum() / max(m.sum(), 1),
                         "normal_flagged": int((hit & n).sum()),
                         "false_positive_rate": (hit & n).sum() / max(n.sum(), 1),
                         "precision": (hit & m).sum() / max((hit & inb).sum(), 1)})
    return pd.DataFrame(rows)


def head_to_head(truth: pd.DataFrame, model: pd.Series, rules: pd.Series, w_hi: int) -> dict:
    """Launderers caught by both / model only / rules only / either, and the model's lead over the rules."""
    mules = truth["account_id"][mule_at(truth, w_hi)]
    m, r = set(model[model <= w_hi].index) & set(mules), set(rules[rules <= w_hi].index) & set(mules)
    both, only = sorted(m & r), sorted(m - r)
    lead = (flag_day(truth, rules.loc[both], True) - flag_day(truth, model.loc[both], False)) if both else pd.Series([])
    # model only: the rules have not alerted by the end of week w_hi, so the lead is at least flag day -> end of w_hi
    t = truth.set_index("account_id").loc[only]
    min_lead = cutoff(t["open_day"], w_hi) - flag_day(truth, model.loc[only], False)
    return {"mules": len(mules), "both": len(both), "model_only": len(only), "rules_only": len(r - m),
            "either": len(m | r), "neither": len(set(mules) - m - r),
            "median_days_model_earlier_when_both": float(lead.median()) if len(lead) else np.nan,
            "model_first_when_both": int((lead > 0).sum()), "rules_first_when_both": int((lead < 0).sum()),
            "median_min_days_earlier_model_only": float(min_lead.median()) if len(min_lead) else np.nan}


# ---------------------------------------------------------------- main
def evaluate_horizon(truth: pd.DataFrame, live: pd.DataFrame, k: dict[int, int], w_hi: int) -> dict:
    """Everything for one horizon (weeks 0-w_hi): flags of the three policies and their measures."""
    live = live[live["weeks_since_open"] <= w_hi]
    kh = {w: n for w, n in k.items() if w <= w_hi}
    ties: dict[int, int] = {}
    flags = {"model": permanent_flags(live, kh, ties), "rules": rules_flags(truth, w_hi),
             "model_anytime": anytime_flags(live, int(sum(kh.values())))}
    summary, weekly = measures(truth, flags, w_hi)
    weekly["budget"] = weekly["week"].map(kh).fillna(0).astype(int)
    weekly["tied_at_cut"] = weekly["week"].map(ties).fillna(0).astype(int)
    return {"flags": flags, "summary": summary, "weekly": weekly, "by_age": by_age(truth, flags, w_hi),
            "h2h": head_to_head(truth, flags["model"], flags["rules"], w_hi), "budget": int(sum(kh.values()))}


def run(out: str, months, horizons: list[int], name: str, model_name: str = "frozen",
        final_test: bool = False, check_data: bool = True, results: str | None = None,
        scores_path: str | None = None) -> str:
    """check_data=False and results=<folder> only for `python -m models verify` (rescoring a reference run).
    scores_path: score a file (load_scores) instead of the model `model_name`."""
    t0 = time.time()
    months = tuple(int(m) for m in months)
    test = bool(set(months) & set(amldata.TEST_MONTHS))
    if test and not final_test:
        raise SystemExit("test months 6-7 are scored once, with --final-test (5 Nov 2026); use month 5 to dry-run")
    if final_test and not test:
        raise SystemExit("--final-test is only for test months 6-7")
    data = os.path.basename(os.path.normpath(out))
    root = results or RESULTS
    if test and (not check_data or results):
        raise SystemExit("the final test runs with every check and into the committed results folder")
    lock = os.path.join(RESULTS, data, "final_test", "LOCK.json")
    started = os.path.join(RESULTS, data, "final_test", "STARTED.json")
    for f in (lock, started):
        if test and os.path.exists(f):
            raise SystemExit(f"the test months were already scored or a final run started ({f}); they are scored "
                             "once. Clearing this file is a team decision, recorded in CHANGELOG.md")
    report = os.path.join(root, data, "final_test" if test else name)
    os.makedirs(report, exist_ok=True)
    if scores_path and not os.path.isfile(scores_path):     # before STARTED.json: a typo must not use up the final run
        raise SystemExit(f"scores file {scores_path} not found")
    source = f"file:{scores_path}" if scores_path else f"model:{model_name}"
    if test:                                                 # written before anything about months 6-7 is read
        with open(started, "w") as f:
            json.dump({"started": time.strftime("%Y-%m-%d %H:%M"), "cohort_months": list(months),
                       "score_source": source}, f, indent=2)

    w_max = max(horizons)
    truth = cohort_truth(out, months, allow_test=test)
    if scores_path:
        scores = load_scores(scores_path, truth["account_id"], w_max)
    else:
        scores = score_cohort(out, months, (0, w_max), model_name, check_data)
    live = open_rows(scores, truth)
    b = rules_budget.weekly_budget(out, months, (0, w_max), allow_test=test).groupby("week")["alerts"].sum()
    k = {int(w): int(n) for w, n in b.items()}
    res = {h: evaluate_horizon(truth, live, k, h) for h in sorted(horizons)}

    lt = truth[truth["is_launderer"] == 1].set_index("account_id")
    launderers = pd.DataFrame({"profile": lt["profile"], "open_month": lt["open_month"],
                               "start_week": (lt["start_day"] - lt["open_day"]) // 7,
                               "closed_week": (lt["exit_day"] - lt["open_day"]) // 7,
                               "rules_first_alert_week": (lt["first_alert_day"] - lt["open_day"]) // 7})
    for h, r in res.items():
        r["summary"].to_csv(os.path.join(report, f"summary_w{h}.csv"), index=False)
        r["weekly"].to_csv(os.path.join(report, f"weekly_w{h}.csv"), index=False)
        r["by_age"].to_csv(os.path.join(report, f"by_age_w{h}.csv"), index=False)
        launderers[f"model_flag_week_w{h}"] = r["flags"]["model"].reindex(lt.index)
        launderers[f"model_anytime_flag_week_w{h}"] = r["flags"]["model_anytime"].reindex(lt.index)
    launderers.reset_index().to_csv(os.path.join(report, "launderers.csv"), index=False)
    from models.train import load as load_model, machine
    man = {} if scores_path else load_model(out, model_name, check_data)[2]
    settings = {"data": out, "cohort_months": list(months), "horizons": sorted(horizons),
                "model": None if scores_path else model_name,
                "model_params_source": man.get("params_source"), "model_git_commit": man.get("git_commit"),
                "model_machine": man.get("machine"), "machine": machine(),
                "cohort_accounts": int(len(truth)), "launderers": int(len(lt)),
                "budget_per_horizon": {str(h): r["budget"] for h, r in res.items()},
                "score_source": source, "scores_sha256": manifest._sha256(scores_path) if scores_path else None,
                "run_manifest_sha256": manifest._sha256(os.path.join(out, "run_manifest.json")),
                "git_commit": manifest._git("rev-parse", "HEAD"),
                "git_uncommitted_changes": bool(manifest._git("status", "--porcelain", "--untracked-files=no")),
                "seconds": round(time.time() - t0)}
    with open(os.path.join(report, "settings.json"), "w") as f:
        json.dump({**settings, "head_to_head": {str(h): r["h2h"] for h, r in res.items()}}, f, indent=2)
    write_report(report, settings, res, test)
    if test:
        with open(lock, "w") as f:
            json.dump({"scored": time.strftime("%Y-%m-%d %H:%M"), **settings}, f, indent=2)
    return report


def write_report(report, settings, res, test):
    show = ["flagged", "caught", "mules", "recall", "recall_final_label", "precision", "false_alarm_share",
            "precision_final_label",
            "catch_mean", "median_days_from_start", "flagged_before_start"] + [f"caught_{p}" for p in PROFILES]
    title = "final test" if test else "dry run"
    lines = [f"# Harness, {title}: cohort opened in month(s) {', '.join(map(str, settings['cohort_months']))}", "",
             f"Settings: `{json.dumps(settings)}`", "",
             "Model vs rules on the same accounts. Each week since opening the model may flag as many accounts as the "
             "rules raised alerts on this cohort that week; a flag is permanent. `model_anytime`: a secondary policy, "
             "one score threshold over the horizon (on each account's highest score) flagging the same total number "
             "of accounts.", "",
             "- The weekly budget counts the rules' alerts: an account alerted twice counts twice, so the model can "
             "flag slightly more distinct accounts than the rules (e.g. 124 vs 119 over weeks 0-26 in the month-5 dry run).",
             "- The model is trained on weeks 0-26 only (models.train WEEKS); weeks 27-77 are outside its training "
             "range, so its running-total features drift there and late scores are not comparable across weeks.", ""]
    for h, r in res.items():
        late = h > TRAINED_WEEKS
        s = r["summary"].set_index("policy")[show].T
        if late:
            s = s.drop(columns="model_anytime")
        s = s.apply(lambda col: col.map(lambda v: f"{v:.3f}" if isinstance(v, float) and not float(v).is_integer()
                                        else (f"{v:.0f}" if isinstance(v, (int, float)) and v == v else str(v))))
        w = r["weekly"][r["weekly"].week.isin([0, 2, 4, 8, 12, 17, 26, 52, 77])].round(3)
        age = r["by_age"].round(4)
        if late:
            w = w.drop(columns=["flagged_model_anytime", "catch_model_anytime"])
            age = age[age["policy"] != "model_anytime"]
        tie = r["weekly"]["tied_at_cut"]
        lines += [f"## Weeks 0-{h}{' (main)' if h == 26 else ''}: launderers who are mules by the end of week {h}", "",
                  s.to_markdown(), "",
                  *([f"`model_anytime`: not meaningful (model trained on weeks 0-{TRAINED_WEEKS}).", ""] if late else []),
                  f"Ties at the cut line (decided by account id): {int((tie > 0).sum())} of {len(tie)} weeks, "
                  f"{int(tie.sum())} tied accounts in all (weekly column `tied_at_cut`).", "",
                  "### Head to head (permanent model flags vs the rules' first alerts)", "",
                  pd.Series(r["h2h"]).to_frame("value").to_markdown(floatfmt=".1f"), "",
                  "### By age band (recall; false_positive_rate = share of normal accounts flagged)", "",
                  age.to_markdown(index=False), "",
                  "### By week since opening", "", w.to_markdown(index=False), ""]
    lines += ["- recall / precision: against mule accounts by the end of the horizon (fake accounts from opening, real "
              "customers from their start). recall_final_label / precision_final_label: against launderers at any "
              "time in the 18 months (label maturity).",
              "- median_min_days_earlier_model_only: launderers caught by the model but not by the rules within the "
              "horizon; days from the model's flag to the end of the horizon, so the model is at least this many "
              "days earlier (the count is model_only).",
              "- median_days_from_start: days from laundering start to the first flag, caught launderers only "
              "(negative = flagged before it started). A model flag is dated at the end of its week.",
              "- catch_mean: per week the share of that week's mules already flagged, averaged over the weeks.",
              "- Accounts closed by the bank stay in the cohort (caught by the rules); `open_accounts` counts the ones "
              "still open at the end of each week."]
    with open(os.path.join(report, "report.md"), "w") as f:
        f.write("\n".join(lines) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m evaluation.score", description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=amldata.DEFAULT_OUT)
    ap.add_argument("--months", nargs="+", type=int, default=[5], help="cohort opening months (default 5, dry run)")
    ap.add_argument("--horizons", nargs="+", type=int, default=[26, 77],
                    help="last week of each horizon since opening (default 26 = main, 77 = appendix)")
    ap.add_argument("--model", default="frozen_tuned",
                    help="model name (default frozen_tuned, the shared model of record committed in git)")
    ap.add_argument("--name", default=None, help="report folder name (default month<M>_dryrun_w<W>)")
    ap.add_argument("--scores", default=None,
                    help="score this file (parquet/csv: account_id, weeks_since_open, score) instead of --model")
    ap.add_argument("--final-test", action="store_true", help="score test months 6-7, once")
    a = ap.parse_args(argv)
    name = a.name or f"month{''.join(map(str, a.months))}_dryrun"
    report = run(a.out, a.months, a.horizons, name, a.model, a.final_test, scores_path=a.scores)
    print(open(os.path.join(report, "report.md")).read())
    print(f"-> {report}")


if __name__ == "__main__":
    main()
