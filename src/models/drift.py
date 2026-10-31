"""Calendar drift in the application score, and the fold fits that notebook 11_policy_drift shares with the policy study.

BAF's velocity_* columns drift with the calendar month (cleaned velocity_4w means +1.29 in month 0 down to -2.81 in
month 7). The test cohort (months 6 + 7) is ranked together, so month-7 accounts may get different application scores
for calendar reasons alone. This module gives:

  app_model          the application logistic regression fitted exactly as models.train fits it (accounts_linear,
                     label mule by the end of week 26, months 0-4 only), optionally without some columns
  score_months       that model's score for every account of any month, from the public cleaned table (no label)
  month_summary      per opening month: accounts, mean and 99th / 99.9th percentile of the score
  month_tilt         inside a group of months ranked together: each month's share of the top q of scores against
                     its share of the accounts
  fold_app_scores    the application score for one fold arrangement (any training months, any months to score), out
                     of fold for training accounts, as feature_lab.app_scores builds it for the lab's fixed folds
  fit_score          the tuned LightGBM on the 38 frozen inputs, fitted on some months and scoring others
  flag_shares        where a policy's flags go, by opening month, against each month's share of mules

Labels only through amldata.labels() and only for training months 0-4; months 5-7 are read only as public cleaned
application columns (no label, no score of theirs feeds a choice).
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

import amldata
from models import lgbm_baseline as base
from models import train as trainer
from models.tuning import _logreg, app_score

VELOCITY = ["velocity_6h", "velocity_24h", "velocity_4w"]
TRAIN_MONTHS = (0, 1, 2, 3, 4)
LABEL_WEEK = 26
TUNED_MANIFEST = "outputs/modelling/models/v1_full/frozen_tuned/manifest.json"


def _check_months(months):
    bad = set(int(m) for m in months) - set(TRAIN_MONTHS)
    if bad:
        raise ValueError(f"labels are used for months 0-4 only here, got {sorted(bad)}")


def app_model(out: str, months=TRAIN_MONTHS, drop=()) -> dict:
    """The application model as models.train fits it (same table, label, settings), without the columns in `drop`.
    Returns the dict models.train saves as app_logreg.json: columns, coef, intercept."""
    _check_months(months)
    lin, cols = trainer._linear(out)
    cols = [c for c in cols if c not in set(drop)]
    lin = lin[lin["open_month"].isin(months)]
    y = amldata.labels(out, months=tuple(months), weeks_since_open=LABEL_WEEK).set_index("account_id")["mule_by_day"]
    full = _logreg().fit(lin[cols].to_numpy(), y.loc[lin.index].to_numpy().astype(int))
    return {"columns": cols, "coef": full.coef_[0].tolist(), "intercept": float(full.intercept_[0]),
            "fitted_on_months": list(months), "dropped": list(drop)}


def score_months(out: str, model: dict, months=range(8)) -> pd.DataFrame:
    """account_id, open_month, app_score for every account opened in `months` (public cleaned columns only)."""
    lin, _ = trainer._linear(out)
    lin = lin[lin["open_month"].isin(list(months))]
    s = trainer.app_scores_for(out, model, lin.index)
    return pd.DataFrame({"account_id": lin.index, "open_month": lin["open_month"].to_numpy(),
                         "app_score": s.to_numpy()})


def month_summary(scores: pd.DataFrame, col: str = "app_score") -> pd.DataFrame:
    """Per open_month: accounts, mean, 99th and 99.9th percentile of `col`."""
    g = scores.groupby("open_month")[col]
    return pd.DataFrame({"accounts": g.size(), "mean": g.mean(), "p99": g.quantile(0.99),
                         "p99.9": g.quantile(0.999)}).reset_index()


def month_tilt(scores: pd.DataFrame, months, tops=(0.001, 0.01), col: str = "app_score") -> pd.DataFrame:
    """Rank the accounts of `months` together; per month its share of accounts and of each top q (k = round(q * n),
    at least 1; ties by account id). ratio = share of the top / share of accounts (1 = no tilt)."""
    s = scores[scores["open_month"].isin(list(months))].sort_values([col, "account_id"], ascending=[False, True],
                                                                      kind="stable")
    n = len(s)
    rows = []
    for m in months:
        r = {"open_month": int(m), "accounts": int((s["open_month"] == m).sum())}
        r["share_accounts"] = r["accounts"] / n
        for q in tops:
            k = max(1, int(round(q * n)))
            top = s.head(k)
            r[f"top_{q:g}_k"] = k
            r[f"top_{q:g}_n"] = int((top["open_month"] == m).sum())
            r[f"top_{q:g}_share"] = r[f"top_{q:g}_n"] / k
            r[f"top_{q:g}_ratio"] = r[f"top_{q:g}_share"] / r["share_accounts"]
        rows.append(r)
    return pd.DataFrame(rows)


def fold_app_scores(out: str, train_months, score_months_, drop=(), seed: int = 42) -> pd.Series:
    """Application score per account for one arrangement: out of fold for accounts of `train_months` (5 folds,
    tuning.app_score with this seed, as feature_lab.app_scores), a model fitted on all of them for `score_months_`.
    Label: mule by the end of week 26, read for the training months only."""
    _check_months(train_months)
    lin = pd.read_parquet(os.path.join(out, "features", "accounts_linear.parquet")).set_index("account_id")
    cols = [c for c in lin.columns if c != "open_month" and c not in set(drop)]
    tr = lin.index[lin["open_month"].isin(train_months)]
    va = lin.index[lin["open_month"].isin(score_months_)]
    y = amldata.labels(out, months=tuple(train_months), weeks_since_open=LABEL_WEEK).set_index("account_id")["mule_by_day"]
    s_tr, s_va = app_score(lin.loc[tr, cols], y.loc[tr], lin.loc[va, cols], seed=seed)
    return pd.Series(np.concatenate([s_tr, s_va]), index=tr.append(va))


def tuned_params(path: str = TUNED_MANIFEST) -> dict:
    """The frozen tuned model's LightGBM settings (random_state included; override it to change the seed)."""
    return dict(json.load(open(path))["lightgbm_params"])


def fit_score(df: pd.DataFrame, train_months, score_months_, app: pd.Series, params: dict,
              seed: int | None = None) -> pd.DataFrame:
    """Fit the tuned LightGBM on the 38 frozen inputs (models.train.INPUTS) for accounts of `train_months` and score
    the account-weeks of `score_months_`. df: lgbm_baseline.load_table(..., adopted=True) rows sorted by account and
    week; app: application score per account (fold_app_scores). Returns the scored rows: account_id,
    weeks_since_open, open_month, mule_by_day, score."""
    import lightgbm as lgb
    settings = {**params, **({"random_state": seed} if seed is not None else {})}
    keep = df["open_month"].isin(list(train_months) + list(score_months_))
    d = df.loc[keep].assign(app_score=lambda x: x["account_id"].map(app).astype("float32"))
    if d["app_score"].isna().any():
        raise ValueError("some accounts have no application score")
    train = d[d["open_month"].isin(train_months)]
    valid = d[d["open_month"].isin(score_months_)]
    model = lgb.LGBMClassifier(n_jobs=-1, **settings).fit(train[trainer.INPUTS], train["mule_by_day"])
    score = model.predict_proba(valid[trainer.INPUTS])[:, 1]
    return valid[base.KEY + ["open_month", "mule_by_day"]].assign(score=score).reset_index(drop=True)


def flag_shares(first: pd.Series, month_of: pd.Series, mules) -> pd.DataFrame:
    """Per opening month: share of the policy's flags and share of the mules. first: first flag week per account;
    month_of: opening month per account; mules: ids of the mule accounts."""
    f = month_of.reindex(first.index).value_counts()
    m = month_of.reindex(pd.Index(mules)).value_counts()
    months = sorted(set(f.index) | set(m.index))
    return pd.DataFrame({"open_month": months,
                         "flags": [int(f.get(x, 0)) for x in months],
                         "share_flags": [f.get(x, 0) / max(f.sum(), 1) for x in months],
                         "mules": [int(m.get(x, 0)) for x in months],
                         "share_mules": [m.get(x, 0) / max(m.sum(), 1) for x in months]})
