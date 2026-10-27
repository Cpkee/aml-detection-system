"""Feature lab: does a group of candidate features improve the model? One trial, logged in a ledger.

    PYTHONPATH=src python -m models.feature_lab --out data/v1 --groups lag1 roll2 roll4 running_max --name item1
    PYTHONPATH=src python -m models.feature_lab --out data/v1_full --groups roll2 --name item1-confirm --views app activity

Candidates come from src/features/candidates.py. For each trial:
  screen    each new feature's AUC against started_by_day (launderers whose laundering has begun vs normal
            accounts) at weeks 8, 12 and 26, with a 95% bootstrap interval over launderers; 0.5 = no signal
  model     LightGBM as in notebooks/06_lgbm_tuning.ipynb (same rows, folds, seed and settings), refitted with each
            group added and with all groups together. Views: 'app' = activity + application score (the model the
            team tunes, decision 26 Oct 2026; default), 'activity' = store features + weeks_since_open only.
            The baseline includes the adopted candidates (features.candidates.ADOPTED, since 26 Oct 2026: the
            roll4 group), so a new group must beat the model as it now stands
  measures  weekly_recall, the tuning measure (decision 26 Oct 2026): the share of each week's mules in that week's
            top 1% of open accounts, averaged over weeks 0-26 (recall_top_1pct of lgbm_baseline.by_week). The
            summary shows it pooled over the 3 validation months, as notebook 06 reports it, and per fold.
            Beside it: account-level PR-AUC (an account's best week) and caught_2wk, the share of launderers
            starting in weeks 0-25 who are in that week's top 1% in their start week or the next
  verdict   per measure, from the 3 folds: 'better' only if all 3 improve AND the mean gain reaches NOISE; 'worse'
            if all 3 fall; else 'no clear change'. weekly_recall decides; the others are reported beside it

Only accounts opened in months 0-4 are used (the baseline's folds); month 5 and test months 6-7 are never read.
Every trial appends to outputs/modelling/feature_lab/ledger.csv, so the number of looks is on record: the more
groups are tried against the same folds, the more likely one wins by chance.
"""
from __future__ import annotations
import argparse
import datetime
import os
import subprocess
import time

import numpy as np
import pandas as pd

import amldata
from features import candidates
from features.weekly import FEATURES as WEEKLY
from models import lgbm_baseline as base
from models.tuning import app_score

ROOT = "outputs/modelling/feature_lab"
LEDGER = os.path.join(ROOT, "ledger.csv")
MONTHS = (0, 1, 2, 3, 4)
WEEKS = (0, 26)
SCREEN_WEEKS = (8, 12, 26)
NOISE = {"weekly_recall": 0.02,   # assumption: 2 points of recall, no measured fold noise yet; test 0.01 / 0.04
         "acc_pr_auc": 0.04,      # team plan working rule: PR-AUC differences under ~0.04 are fold noise
         "caught_2wk": 0.05}      # assumption: ~1 binomial s.e. with ~90 starts per fold on v1_full; test 0.03 / 0.08
MAIN = "weekly_recall"
INFO = ["pre_start_recall", "start_recall", "later_recall", "first_caught_2wk"]   # where a gain comes from; no verdict


def auc_ci(x, y, n_boot: int = 1000, seed: int = 0) -> tuple[float, float, float]:
    """Rank AUC with a 95% bootstrap interval over positives; NaN ranks lowest (as in notebooks/01_eda_train)."""
    x, y = np.asarray(x, dtype=float), np.asarray(y).astype(bool)
    if y.sum() < 20 or (~y).sum() == 0:
        return np.nan, np.nan, np.nan
    x = np.where(np.isnan(x), -np.inf, x)
    neg, pos = np.sort(x[~y]), x[y]
    place = np.sort((np.searchsorted(neg, pos, "left") + np.searchsorted(neg, pos, "right")) / (2 * len(neg)))
    if np.all(place == place[0]):
        return place.mean(), np.nan, np.nan
    boots = np.random.default_rng(seed).choice(place, size=(n_boot, len(place))).mean(axis=1)
    return place.mean(), *np.percentile(boots, [2.5, 97.5])


def screen(out: str, df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    rows = []
    for w in SCREEN_WEEKS:
        lab = amldata.labels(out, months=MONTHS, weeks_since_open=w)[["account_id", "started_by_day"]]
        d = df[df.weeks_since_open == w].merge(lab, on="account_id", validate="1:1")
        d = d[(d.started_by_day == 1) | (d.mule_by_day == 0)]          # started launderers vs normal accounts
        for c in cols:
            auc, lo, hi = auc_ci(d[c], d.started_by_day)
            rows.append({"feature": c, "week": w, "auc": auc, "lo": lo, "hi": hi})
    return pd.DataFrame(rows)


def start_weeks(out: str) -> pd.Series:
    """Each launderer's first week with started_by_day = 1 inside WEEKS (accounts not started there are absent)."""
    started = [amldata.labels(out, months=MONTHS, weeks_since_open=w).query("started_by_day == 1")
               [["account_id"]].assign(w=w) for w in range(WEEKS[0], WEEKS[1] + 1)]
    return pd.concat(started).groupby("account_id")["w"].min()


def app_scores(out: str, seed: int) -> dict[int, pd.Series]:
    """Per fold, the application score of every training and validation account, exactly as notebook 06 builds it:
    a logistic regression on accounts_linear, label 'mule by the end of week 26', out of fold for training accounts."""
    lin = pd.read_parquet(os.path.join(out, "features", "accounts_linear.parquet"))
    lin = lin[lin["open_month"].isin(MONTHS)].set_index("account_id")
    cols = [c for c in lin.columns if c != "open_month"]
    y26 = amldata.labels(out, months=MONTHS, weeks_since_open=WEEKS[1]).set_index("account_id")["mule_by_day"]
    scores = {}
    for f, (train_m, valid_m) in enumerate(base.FOLDS, start=1):
        tr, va = lin.index[lin.open_month.isin(train_m)], lin.index[lin.open_month == valid_m]
        s_tr, s_va = app_score(lin.loc[tr, cols], y26.loc[tr], lin.loc[va, cols], seed=seed)
        scores[f] = pd.concat([pd.Series(s_tr, index=tr), pd.Series(s_va, index=va)])
    return scores


def weekly_top1(valid: pd.DataFrame, score: np.ndarray) -> pd.DataFrame:
    """valid with the score and a flag for the top 1% of each week (k and tie order as in lgbm_baseline.top_k)."""
    v = valid.assign(score=score)
    rank = v.groupby("weeks_since_open")["score"].rank(ascending=False, method="first")
    k = v.groupby("weeks_since_open")["score"].transform(lambda s: max(1, int(round(0.01 * len(s)))))
    return v.assign(flag=rank <= k)


def weekly_recall(v: pd.DataFrame) -> float:
    r = [g.loc[g.mule_by_day == 1, "flag"].mean() for _, g in v.groupby("weeks_since_open") if g.mule_by_day.any()]
    return float(np.mean(r))


def caught_2wk(v: pd.DataFrame, start: pd.Series) -> float:
    """Share of launderers starting in weeks 0-25 who are flagged in their start week or the next."""
    st = start[(start <= 25) & start.index.isin(v["account_id"])]
    s = v["account_id"].map(st)
    near = v[(v.weeks_since_open >= s) & (v.weeks_since_open <= s + 1)]
    return float(near.groupby("account_id")["flag"].any().reindex(st.index, fill_value=False).mean())


def phase_recall(v: pd.DataFrame, start: pd.Series) -> dict[str, float]:
    """Share of mule weeks flagged, split by weeks since the account's laundering start: before it (fake accounts,
    mules from opening), the start week and the next, and 2+ weeks after. weekly_recall mixes all three; a gain only
    in 'later' re-flags mules a permanent flag would already have caught."""
    m = v[v.mule_by_day == 1]
    since = m["weeks_since_open"] - m["account_id"].map(start)
    return {"pre_start_recall": float(m.loc[since < 0, "flag"].mean()),
            "start_recall": float(m.loc[since.between(0, 1), "flag"].mean()),
            "later_recall": float(m.loc[since >= 2, "flag"].mean())}


def first_flag_weeks(v: pd.DataFrame) -> pd.Series:
    """Week of each account's first flag when a flag is permanent (decision 9 Oct 2026): every week the top 1% of
    that week's open accounts is flagged from the accounts not flagged before (same k as weekly_top1)."""
    first = {}
    for w, g in v.groupby("weeks_since_open"):
        k = max(1, int(round(0.01 * len(g))))
        pool = g[~g["account_id"].isin(first.keys())]
        for a in pool.sort_values("score", ascending=False, kind="stable")["account_id"].head(k):
            first[a] = w
    return pd.Series(first, dtype=float)


def first_caught_2wk(v: pd.DataFrame, start: pd.Series) -> float:
    """caught_2wk with permanent flags: share of launderers starting in weeks 0-25 whose first flag comes no later
    than the week after their start (a flag before the start counts: it is earlier still)."""
    st = start[(start <= 25) & start.index.isin(v["account_id"])]
    first = first_flag_weeks(v).reindex(st.index)
    return float((first <= st + 1).mean())


def fit_folds(df, cols, prof, start, scores, seed) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Per-fold measures and the out-of-fold scores of one variant."""
    import lightgbm as lgb
    rows, oof = [], []
    for f, (train_m, valid_m) in enumerate(base.FOLDS, start=1):
        d = df.assign(app_score=df["account_id"].map(scores[f])) if scores else df
        train, valid = d[d.open_month.isin(train_m)], d[d.open_month == valid_m]
        model = lgb.LGBMClassifier(class_weight="balanced", random_state=seed, n_jobs=-1, verbose=-1,
                                   deterministic=True, force_row_wise=True)
        model.fit(train[cols], train["mule_by_day"])
        score = model.predict_proba(valid[cols])[:, 1]
        m = base.evaluate(valid, score, prof)
        v = weekly_top1(valid, score)
        rows.append({"fold": f, "weekly_recall": weekly_recall(v), "acc_pr_auc": m["acc_pr_auc"],
                     "caught_2wk": caught_2wk(v, start), **phase_recall(v, start),
                     "first_caught_2wk": first_caught_2wk(v, start), "top_1%_witting": m["top_1%_witting"],
                     "top_1%_unwitting": m["top_1%_unwitting"]})
        oof.append(valid[base.KEY + ["mule_by_day"]].assign(score=score))
    return pd.DataFrame(rows), pd.concat(oof, ignore_index=True)


def pooled_weekly_recall(oof: pd.DataFrame) -> float:
    """The tuning measure as notebook 06 reports it: by_week on the pooled validation months, mean over weeks."""
    return float(base.by_week(oof.assign(view="v"))["recall_top_1pct"].mean())


def verdict(delta: pd.Series, noise: float) -> str:
    if (delta > 0).all() and delta.mean() >= noise:
        return "better"
    if (delta < 0).all():
        return "worse"
    return "no clear change"


def git_commit() -> str:
    try:
        c = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "src"], capture_output=True, text=True).stdout.strip()
        return c + ("-dirty" if dirty else "")
    except OSError:
        return "unknown"


def append_ledger(rows: pd.DataFrame):
    """Add rows to the ledger. Earlier rows are kept byte for byte when the columns fit; only a new column forces a
    rewrite, which leaves that column empty for earlier rows."""
    if os.path.exists(LEDGER):
        old = pd.read_csv(LEDGER, nrows=0).columns
        if set(rows.columns) <= set(old):
            rows.reindex(columns=old).to_csv(LEDGER, mode="a", header=False, index=False)
            return
        rows = pd.concat([pd.read_csv(LEDGER), rows], ignore_index=True)
    rows.to_csv(LEDGER, index=False)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m models.feature_lab", description=__doc__.split("\n")[0])
    ap.add_argument("--out", default="data/v1", help="data folder (default data/v1, the fast 50k run)")
    ap.add_argument("--groups", nargs="+", required=True, help=f"candidate groups: {', '.join(candidates.GROUPS)}")
    ap.add_argument("--name", required=True, help="trial name, used for the report folder and the ledger")
    ap.add_argument("--views", nargs="+", default=["app"], choices=["app", "activity"],
                    help="app = activity + application score (default, the tuned model); activity = store features only")
    ap.add_argument("--hypothesis", default="", help="one line: what laundering behaviour the group should catch")
    ap.add_argument("--baseline", default="adopted", choices=["adopted", "store"],
                    help="adopted = store + features.candidates.ADOPTED (default); store = store features only, to "
                         "re-check an adopted group")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args(argv)
    adopted = candidates.ADOPTED if a.baseline == "adopted" else []

    t0 = time.time()
    data = os.path.basename(os.path.normpath(a.out))
    report = os.path.join(ROOT, data, a.name)
    os.makedirs(report, exist_ok=True)
    df, _ = base.load_table(a.out, MONTHS, WEEKS, adopted=bool(adopted))
    df = df.sort_values(candidates.KEY, kind="stable").reset_index(drop=True)
    df, names = candidates.add(df, a.groups)
    prof, start = base.profiles(a.out, MONTHS), start_weeks(a.out)
    scores = app_scores(a.out, a.seed) if "app" in a.views else None
    new = [c for g in a.groups for c in names[g]]
    print(f"{len(df):,} account-weeks, {len(new)} candidate columns ({time.time() - t0:.0f}s)")

    scr = screen(a.out, df, new)
    adds = {f"+{g}": names[g] for g in a.groups} | ({"+all": new} if len(a.groups) > 1 else {})
    res, summary = [], []
    for view in a.views:
        base_cols = WEEKLY + adopted + ["weeks_since_open"] + (["app_score"] if view == "app" else [])
        b = None
        for v, extra in {"baseline": [], **adds}.items():
            r, oof = fit_folds(df, base_cols + extra, prof, start, scores if view == "app" else None, a.seed)
            r = r.assign(view=view, variant=v, n_features=len(base_cols + extra))
            res.append(r)
            row = {"view": view, "variant": v, "n_features": len(base_cols + extra),
                   "weekly_recall_pooled": pooled_weekly_recall(oof)}
            b = r.set_index("fold") if b is None else b
            for m in list(NOISE) + INFO:
                d = r.set_index("fold")[m] - b[m]
                row |= {m: r[m].mean(), f"d_{m}": d.mean(), f"d_{m}_folds": " / ".join(f"{x:+.3f}" for x in d)}
                if m in NOISE:
                    row[f"{m}_verdict"] = verdict(d, NOISE[m]) if v != "baseline" else ""
            summary.append(row)
            print(f"{view:8s} {v:14s} weekly recall {row['weekly_recall_pooled']:.3f} (pooled)  "
                  f"PR-AUC {row['acc_pr_auc']:.3f}  caught 2wk {row['caught_2wk']:.3f}  ({time.time() - t0:.0f}s)")
    res, summary = pd.concat(res, ignore_index=True), pd.DataFrame(summary)

    res.to_csv(os.path.join(report, "folds.csv"), index=False)
    scr.to_csv(os.path.join(report, "screen.csv"), index=False)
    summary.to_csv(os.path.join(report, "summary.csv"), index=False)
    write_report(report, a, data, summary, scr)
    stamp = {"date": datetime.date.today().isoformat(), "commit": git_commit(), "data": data, "trial": a.name,
             "hypothesis": a.hypothesis, "seed": a.seed,
             "baseline": f"store + {candidates.ADOPTED_GROUP}" if adopted else "store"}
    led = summary[summary.variant != "baseline"].assign(**stamp)
    led["features"] = led.variant.map(lambda v: " ".join(adds[v]))
    append_ledger(led[list(stamp) + [c for c in led.columns if c not in stamp]])
    print(f"-> {report}, ledger {LEDGER}  ({time.time() - t0:.0f}s)")


def write_report(report, a, data, summary, scr):
    wide = scr.assign(v=scr.apply(lambda r: f"{r.auc:.3f} ({r.lo:.2f}-{r.hi:.2f})", axis=1)) \
              .pivot(index="feature", columns="week", values="v")
    wide.columns = [f"week {w}" for w in wide.columns]
    lines = [f"# Feature lab: {a.name}", "",
             f"data `{data}`, groups {', '.join(a.groups)}, views {', '.join(a.views)}, seed {a.seed}, "
             f"commit {git_commit()}", "", f"Hypothesis: {a.hypothesis or '(none given)'}", ""]
    for view in a.views:
        s = summary[summary.view == view]
        lines += [f"## View `{view}`: baseline vs baseline + candidates (3 folds, months 0-4)", ""]
        for m in NOISE:
            cols = ["variant", "n_features"] + (["weekly_recall_pooled"] if m == MAIN else []) + \
                   [m, f"d_{m}", f"d_{m}_folds", f"{m}_verdict"]
            lines += [f"### {m}{' (decides)' if m == MAIN else ''}", "",
                      s[cols].to_markdown(index=False, floatfmt=".3f"), ""]
        cols = ["variant"] + [c for m in INFO for c in (m, f"d_{m}_folds")]
        lines += ["### Where the gain comes from (no verdict)", "", s[cols].to_markdown(index=False, floatfmt=".3f"),
                  "", "Share of mule weeks in the weekly top 1%, by weeks since the account's laundering start: "
                  "pre_start (fake accounts before they launder), start (start week and the next), later (2+ weeks "
                  "after). first_caught_2wk: as caught_2wk, but a flag is permanent (decision 9 Oct 2026), so a mule "
                  "flagged earlier counts as caught and later re-flags count for nothing.", ""]
    lines += [
        "- weekly_recall: share of each week's mules in that week's top 1% of open accounts, mean over weeks 0-26 "
        "(the tuning measure, decision 26 Oct 2026). `weekly_recall_pooled` pools the 3 validation months per week, "
        "as notebook 06 reports it; the per-fold column and the verdict use each fold alone.",
        "- acc_pr_auc: account-level PR-AUC (an account's best week). caught_2wk: launderers starting in weeks 0-25 "
        "flagged in their start week or the next.",
        f"- verdict 'better' = all 3 folds improve and the mean gain is at least the noise level: "
        f"{', '.join(f'{m} {n}' for m, n in NOISE.items())} (PR-AUC: team rule; the others: assumptions).",
        "- Real-customer mules in the account-level top 1% per fold (witting / unwitting) are in folds.csv.",
        "", "## Screen: AUC vs started launderers (95% interval over launderers)", "", wide.to_markdown(), ""]
    with open(os.path.join(report, "report.md"), "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
