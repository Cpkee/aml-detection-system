"""Feature lab: does a group of candidate features improve the activity model? One trial, logged in a ledger.

    PYTHONPATH=src python -m models.feature_lab --out data/v1 --groups lag1 roll2 roll4 running_max --name item1
    PYTHONPATH=src python -m models.feature_lab --out data/v1_full --groups roll2 --name item1-confirm

Candidates come from src/features/candidates.py. For each trial:
  screen    each new feature's AUC against started_by_day (launderers whose laundering has begun vs normal
            accounts) at weeks 8, 12 and 26, with a 95% bootstrap interval over launderers; 0.5 = no signal
  model     the activity LightGBM of models.lgbm_baseline (28 store features + weeks_since_open, same rows, folds,
            seed and settings), refitted with each group added and with all groups together
  measures  per fold: account-level PR-AUC (an account's best week in weeks 0-26); caught_2wk, the share of
            launderers starting in weeks 0-25 who are in that week's top 1% in their start week or the next (the
            rules flag a median 9 days after start); early_recall, the share of each week's mules in that week's
            top 1% averaged over weeks 0-8 (the tuning notebook's measure; mostly fakes before they start, which
            activity cannot see, so no verdict on it)
  verdict   per measure: 'better' only if all 3 folds improve AND the mean gain reaches the noise level below;
            'worse' if all 3 folds fall; else 'no clear change'

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

ROOT = "outputs/modelling/feature_lab"
LEDGER = os.path.join(ROOT, "ledger.csv")
MONTHS = (0, 1, 2, 3, 4)
SCREEN_WEEKS = (8, 12, 26)
EARLY = (0, 8)
NOISE = {"acc_pr_auc": 0.04,      # team plan working rule: PR-AUC differences under ~0.04 are fold noise
         "caught_2wk": 0.05}      # assumption: ~1 binomial s.e. with ~90 starts per fold on v1_full; test 0.03 / 0.08
SHOWN = ["acc_pr_auc", "caught_2wk", "early_recall"]


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


def start_weeks(out: str, weeks: tuple[int, int]) -> pd.Series:
    """Each launderer's first week with started_by_day = 1 inside `weeks` (accounts not started there are absent)."""
    started = [amldata.labels(out, months=MONTHS, weeks_since_open=w).query("started_by_day == 1")
               [["account_id"]].assign(w=w) for w in range(weeks[0], weeks[1] + 1)]
    return pd.concat(started).groupby("account_id")["w"].min()


def weekly_top1(valid: pd.DataFrame, score: np.ndarray) -> pd.DataFrame:
    """valid with the score and a flag for the top 1% of each week (k as in lgbm_baseline.top_k)."""
    v = valid.assign(score=score)
    rank = v.groupby("weeks_since_open")["score"].rank(ascending=False, method="first")
    k = v.groupby("weeks_since_open")["score"].transform(lambda s: max(1, int(round(0.01 * len(s)))))
    return v.assign(flag=rank <= k)


def early_recall(v: pd.DataFrame) -> float:
    e = v[v.weeks_since_open.between(*EARLY)]
    r = [g.loc[g.mule_by_day == 1, "flag"].mean() for _, g in e.groupby("weeks_since_open") if g.mule_by_day.any()]
    return float(np.mean(r))


def caught_2wk(v: pd.DataFrame, start: pd.Series) -> float:
    """Share of launderers starting in weeks 0-25 who are flagged in their start week or the next."""
    st = start[(start <= 25) & start.index.isin(v["account_id"])]
    s = v["account_id"].map(st)
    near = v[(v.weeks_since_open >= s) & (v.weeks_since_open <= s + 1)]
    return float(near.groupby("account_id")["flag"].any().reindex(st.index, fill_value=False).mean())


def fit_folds(df: pd.DataFrame, cols: list[str], prof: pd.Series, start: pd.Series, seed: int) -> pd.DataFrame:
    import lightgbm as lgb
    rows = []
    for f, (train_m, valid_m) in enumerate(base.FOLDS, start=1):
        train, valid = df[df.open_month.isin(train_m)], df[df.open_month == valid_m]
        model = lgb.LGBMClassifier(class_weight="balanced", random_state=seed, n_jobs=-1, verbose=-1,
                                   deterministic=True, force_row_wise=True)
        model.fit(train[cols], train["mule_by_day"])
        score = model.predict_proba(valid[cols])[:, 1]
        m = base.evaluate(valid, score, prof)
        v = weekly_top1(valid, score)
        rows.append({"fold": f, "acc_pr_auc": m["acc_pr_auc"], "caught_2wk": caught_2wk(v, start),
                     "early_recall": early_recall(v),
                     "acc_top_1%_recall": m["acc_top_1%_recall"], "top_1%_witting": m["top_1%_witting"],
                     "top_1%_unwitting": m["top_1%_unwitting"]})
    return pd.DataFrame(rows)


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


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m models.feature_lab", description=__doc__.split("\n")[0])
    ap.add_argument("--out", default="data/v1", help="data folder (default data/v1, the fast 50k run)")
    ap.add_argument("--groups", nargs="+", required=True, help=f"candidate groups: {', '.join(candidates.GROUPS)}")
    ap.add_argument("--name", required=True, help="trial name, used for the report folder and the ledger")
    ap.add_argument("--hypothesis", default="", help="one line: what laundering behaviour the group should catch")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args(argv)

    t0 = time.time()
    data = os.path.basename(os.path.normpath(a.out))
    report = os.path.join(ROOT, data, a.name)
    os.makedirs(report, exist_ok=True)
    df, _ = base.load_table(a.out, MONTHS, (0, 26))
    df = df.sort_values(candidates.KEY, kind="stable").reset_index(drop=True)
    df, names = candidates.add(df, a.groups)
    prof = base.profiles(a.out, MONTHS)
    start = start_weeks(a.out, (0, 26))
    new = [c for g in a.groups for c in names[g]]
    print(f"{len(df):,} account-weeks, {len(new)} candidate columns ({time.time() - t0:.0f}s)")

    scr = screen(a.out, df, new)
    baseline = WEEKLY + ["weeks_since_open"]
    variants = {"baseline": baseline, **{f"+{g}": baseline + names[g] for g in a.groups}}
    if len(a.groups) > 1:
        variants["+all"] = baseline + new
    res = []
    for v, cols in variants.items():
        r = fit_folds(df, cols, prof, start, a.seed).assign(variant=v, n_features=len(cols))
        res.append(r)
        print(f"{v:14s} PR-AUC {r.acc_pr_auc.mean():.3f}  caught within 2 weeks {r.caught_2wk.mean():.3f}  "
              f"early recall {r.early_recall.mean():.3f}  ({time.time() - t0:.0f}s)")
    res = pd.concat(res, ignore_index=True)

    b = res[res.variant == "baseline"].set_index("fold")
    summary = []
    for v in variants:
        r = res[res.variant == v].set_index("fold")
        row = {"variant": v, "n_features": int(r.n_features.iloc[0])}
        for m in SHOWN:
            d = r[m] - b[m]
            row |= {m: r[m].mean(), f"d_{m}": d.mean(), f"d_{m}_folds": " / ".join(f"{x:+.3f}" for x in d)}
            if m in NOISE:
                row[f"{m}_verdict"] = verdict(d, NOISE[m]) if v != "baseline" else ""
        summary.append(row)
    summary = pd.DataFrame(summary)

    res.to_csv(os.path.join(report, "folds.csv"), index=False)
    scr.to_csv(os.path.join(report, "screen.csv"), index=False)
    summary.to_csv(os.path.join(report, "summary.csv"), index=False)
    write_report(report, a, data, summary, scr, res)
    stamp = {"date": datetime.date.today().isoformat(), "commit": git_commit(), "data": data, "trial": a.name,
             "hypothesis": a.hypothesis, "seed": a.seed}
    led = summary[summary.variant != "baseline"].assign(**stamp)
    led["features"] = led.variant.map(lambda v: " ".join(new if v == "+all" else names[v[1:]]))
    led = led[list(stamp) + [c for c in led.columns if c not in stamp]]
    led.to_csv(LEDGER, mode="a", header=not os.path.exists(LEDGER), index=False)
    print(f"-> {report}, ledger {LEDGER}  ({time.time() - t0:.0f}s)")


def write_report(report, a, data, summary, scr, res):
    wide = scr.assign(v=scr.apply(lambda r: f"{r.auc:.3f} ({r.lo:.2f}-{r.hi:.2f})", axis=1)) \
              .pivot(index="feature", columns="week", values="v")
    wide.columns = [f"week {w}" for w in wide.columns]
    lines = [f"# Feature lab: {a.name}", "",
             f"data `{data}`, groups {', '.join(a.groups)}, seed {a.seed}, commit {git_commit()}", "",
             f"Hypothesis: {a.hypothesis or '(none given)'}", "",
             "## Model: activity LightGBM, baseline vs baseline + candidates (3 folds, months 0-4)", ""]
    for m in SHOWN:
        cols = ["variant", "n_features", m, f"d_{m}", f"d_{m}_folds"] + ([f"{m}_verdict"] if m in NOISE else [])
        lines += [f"### {m}", "", summary[cols].to_markdown(index=False, floatfmt=".3f"), ""]
    lines += [f"- acc_pr_auc: account-level PR-AUC, weeks 0-26. caught_2wk: launderers starting in weeks 0-25 "
             f"flagged (weekly top 1%) in their start week or the next. early_recall: share of each week's mules "
             f"in that week's top 1%, weeks {EARLY[0]}-{EARLY[1]} (mostly fakes not yet laundering; no verdict).",
             f"- verdict 'better' = all 3 folds improve and the mean gain is at least {NOISE['acc_pr_auc']} "
             f"(PR-AUC, the team's fold-noise rule) / {NOISE['caught_2wk']} (caught_2wk, an assumption).",
             "- Real-customer mules in the account-level top 1% per fold (witting / unwitting) are in folds.csv.",
             "", "## Screen: AUC vs started launderers (95% interval over launderers)", "",
             wide.to_markdown(), ""]
    with open(os.path.join(report, "report.md"), "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
