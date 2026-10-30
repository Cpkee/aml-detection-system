"""Stability and imbalance checks of the 38-input LightGBM on the feature lab's 3 temporal folds (months 0-4 only).

Used by notebooks/10_stability_undersampling.ipynb:

  reproducibility  the lab's default baseline (store + roll4 + app score, LightGBM defaults) fitted twice in a row
                   with feature_lab.fit_folds, unchanged, and compared to the last decimal
  seed spread      the tuned settings (tuning step 2, trial 24) with LightGBM random_state 1-5, data and app score fixed
  undersampling    the 1:20 ablation promised in the 9 Oct 2026 plan: every account that is a mule in some training week
                   is kept whole, and whole normal accounts are drawn at random until label-0 rows are about 20 x the
                   mule rows; no class weights. The validation month is never resampled

Rows, folds, app score and measures are the lab's (models.feature_lab): fit_eval below fits LightGBM with any settings
and scores each fold exactly as feature_lab.fit_folds does (the notebook checks that both give identical numbers with
the default settings). Labels come only through amldata (via the lab); month 5 and test months 6-7 are never read.
"""
from __future__ import annotations

import time

import numpy as np
import pandas as pd

from features import candidates
from features.weekly import FEATURES as WEEKLY
from models import feature_lab as fl
from models import lgbm_baseline as base

INPUTS = WEEKLY + candidates.ADOPTED + ["weeks_since_open", "app_score"]   # the 38 frozen inputs (28 Oct 2026)
FIXED = dict(n_jobs=-1, verbose=-1, deterministic=True, force_row_wise=True)  # as the lab and train.py
MEASURES = ["weekly_recall", "catch_0.1pct", "catch_rules", "first_caught_2wk", "start_recall", "acc_pr_auc",
            "pre_start_recall", "later_recall"]


def lab_setup(out: str, seed: int = 42) -> dict:
    """Everything the lab's baseline needs, built as feature_lab.main builds it (adopted baseline, no groups)."""
    df, _ = base.load_table(out, fl.MONTHS, fl.WEEKS, adopted=True)
    df = df.sort_values(candidates.KEY, kind="stable").reset_index(drop=True)
    return {"df": df, "prof": base.profiles(out, fl.MONTHS), "start": fl.start_weeks(out),
            "scores": fl.app_scores(out, seed), "ctx": fl.rules_context(out)}


def undersample(train: pd.DataFrame, ratio: float = 20, seed: int = 42) -> pd.DataFrame:
    """Whole-account sample of the training rows: all accounts with a mule week are kept with all their weeks; normal
    accounts (no mule week) are taken in a random order (seed) until the label-0 rows reach ratio x the mule rows.
    Rows keep their original order. Never used on a validation month."""
    y = train["mule_by_day"].to_numpy()
    ids = train["account_id"]
    mule_acc = pd.Index(ids[y == 1].unique())
    in_mule_acc = ids.isin(mule_acc).to_numpy()
    target = ratio * int(y.sum()) - int((in_mule_acc & (y == 0)).sum())   # label-0 rows still wanted
    sizes = ids[~in_mule_acc].value_counts().sort_index()                 # rows per normal account, fixed order
    order = sizes.iloc[np.random.default_rng(seed).permutation(len(sizes))]
    n_take = int(np.searchsorted(order.cumsum().to_numpy(), max(target, 0))) + 1 if target > 0 else 0
    keep = mule_acc.append(order.index[:n_take])
    return train[ids.isin(keep).to_numpy()]


def fold_measures(valid: pd.DataFrame, score: np.ndarray, valid_m: int, setup: dict) -> dict:
    """One fold's measures, the same row feature_lab.fit_folds builds (with the rules context)."""
    prof, start = setup["prof"], setup["start"]
    m = base.evaluate(valid, score, prof)
    v = fl.weekly_top1(valid, score)
    row = {"weekly_recall": fl.weekly_recall(v), "acc_pr_auc": m["acc_pr_auc"], "caught_2wk": fl.caught_2wk(v, start),
           **fl.phase_recall(v, start), "first_caught_2wk": fl.first_caught_2wk(v, start),
           "top_1%_witting": m["top_1%_witting"], "top_1%_unwitting": m["top_1%_unwitting"]}
    c = fl.catch_measures(v, valid_m, setup["ctx"])
    row |= {k: x for k, x in c.items() if not k.startswith("_")}
    row |= {f"{k}_boot_sd": fl.catch_boot_sd(c["_first"][k], c["_mules"]) for k in c["_first"]}
    row |= fl.real_mules_caught(c["_first"]["catch_rules"], c["_mules"], prof)
    return row


def fit_eval(setup: dict, params: dict | None = None, seed: int = 42, class_weight: str | None = "balanced",
             sample_ratio: float | None = None, sample_seed: int = 42, scores: dict | None = None,
             cols: list[str] | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Fit LightGBM on each fold's training months and score its validation month with the lab's measures.

    params: LightGBM settings over the defaults (None = defaults, as the lab); seed: random_state; sample_ratio: train
    on undersample(train, sample_ratio, sample_seed) instead of all training rows; scores: app scores per fold
    (default the lab's). Returns (one row per fold, out-of-fold scores)."""
    import lightgbm as lgb
    cols = cols or INPUTS
    rows, oof = [], []
    for f, (train_m, valid_m) in enumerate(base.FOLDS, start=1):
        d = fl.with_fold_columns(setup["df"], f, scores or setup["scores"])
        train, valid = d[d.open_month.isin(train_m)], d[d.open_month == valid_m]
        if sample_ratio is not None:
            train = undersample(train, sample_ratio, sample_seed)
        model = lgb.LGBMClassifier(class_weight=class_weight, random_state=seed, **FIXED, **(params or {}))
        t = time.time()
        model.fit(train[cols], train["mule_by_day"])
        fit_s = time.time() - t
        score = model.predict_proba(valid[cols])[:, 1]
        rows.append({"fold": f, "train_rows": len(train), "train_mule_rows": int(train["mule_by_day"].sum()),
                     "train_accounts": int(train["account_id"].nunique()), "fit_seconds": fit_s,
                     **fold_measures(valid, score, valid_m, setup)})
        oof.append(valid[base.KEY + ["mule_by_day"]].assign(score=score, fold=f))
        del d, train, valid
    return pd.DataFrame(rows), pd.concat(oof, ignore_index=True)


def perturb_scores(scores: dict, rel: float, seed: int = 0) -> dict:
    """App scores times (1 + rel x standard normal noise): a stand-in for the last-digit differences another machine's
    maths library can leave in a logistic regression."""
    rng = np.random.default_rng(seed)
    return {f: s * (1 + rel * rng.standard_normal(s.shape)) for f, s in scores.items()}


def seed_summary(runs: pd.DataFrame, measures=MEASURES) -> pd.DataFrame:
    """Per variant and fold: mean, SD (ddof=1) and range over seeds of each measure. runs: variant, seed, fold, ..."""
    g = runs.groupby(["variant", "fold"])[list(measures)]
    out = pd.concat({"mean": g.mean(), "sd": g.std(ddof=1), "min": g.min(), "max": g.max()}, axis=1)
    out.columns = [f"{m}_{stat}" for stat, m in out.columns]
    return out.reset_index()
