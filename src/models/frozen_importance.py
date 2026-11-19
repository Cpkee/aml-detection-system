"""Gain importance of the frozen model inputs (feature list frozen 28 Oct 2026).

    PYTHONPATH=src python -m models.frozen_importance                  # data/v1_full, ~30 s
    PYTHONPATH=src python -m models.frozen_importance --out data/v1

The model is the feature lab's baseline exactly: 28 store features + the adopted four-week windows
(features.candidates.ADOPTED) + weeks_since_open + the application score, LightGBM with the lab's settings, the same
3 temporal folds on months 0-4 and seed 42 (models.feature_lab.fit_folds). For each fold it records every input's
share of the total split gain; `mean_share` is the mean over the folds. As a check it prints each fold's weekly recall,
which must equal the lab's baseline (v1_full: 0.407 / 0.366 / 0.453).

Gain share says what the trees lean on, not what the model could do without: inputs that measure the same thing
share the credit. Month 5 and test months 6-7 are never read.

Output: outputs/modelling/models/<data folder>/frozen_importance/importance.csv
"""
from __future__ import annotations
import argparse
import os

import lightgbm as lgb
import pandas as pd

from features import candidates
from models import feature_lab as lab, lgbm_baseline as base

SEED = 42
INPUTS = lab.WEEKLY + candidates.ADOPTED + ["weeks_since_open", "app_score"]


def importance(out: str) -> tuple[pd.DataFrame, list[float]]:
    """Gain share per input and fold (columns 1-3) and its mean, sorted; plus each fold's weekly recall."""
    df, _ = base.load_table(out, lab.MONTHS, lab.WEEKS, adopted=True)
    df = df.sort_values(candidates.KEY, kind="stable").reset_index(drop=True)
    scores = lab.app_scores(out, SEED)
    shares, recall = {}, []
    for f, (train_m, valid_m) in enumerate(base.FOLDS, start=1):
        d = df.assign(app_score=df["account_id"].map(scores[f]))
        train, valid = d[d.open_month.isin(train_m)], d[d.open_month == valid_m]
        model = lgb.LGBMClassifier(class_weight="balanced", random_state=SEED, n_jobs=-1, verbose=-1,
                                   deterministic=True, force_row_wise=True).fit(train[INPUTS], train["mule_by_day"])
        gain = pd.Series(model.booster_.feature_importance("gain"), index=INPUTS)
        shares[f] = gain / gain.sum()
        recall.append(lab.weekly_recall(lab.weekly_top1(valid, model.predict_proba(valid[INPUTS])[:, 1])))
    imp = pd.DataFrame(shares)
    imp["mean_share"] = imp.mean(axis=1)
    return imp.sort_values("mean_share", ascending=False).rename_axis("input"), recall


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m models.frozen_importance", description=__doc__.split("\n")[0])
    ap.add_argument("--out", default="data/v1_full", help="data folder (default data/v1_full)")
    a = ap.parse_args(argv)
    imp, recall = importance(a.out)
    report = os.path.join(base.REPORT_ROOT, os.path.basename(os.path.normpath(a.out)), "frozen_importance")
    os.makedirs(report, exist_ok=True)
    imp.to_csv(os.path.join(report, "importance.csv"))
    top = imp["mean_share"].cumsum()
    print(f"{len(INPUTS)} inputs; weekly recall per fold {' / '.join(f'{r:.3f}' for r in recall)}; "
          f"top 5 carry {top.iloc[4]:.1%}, top 10 {top.iloc[9]:.1%} -> {report}/importance.csv")


if __name__ == "__main__":
    main()
