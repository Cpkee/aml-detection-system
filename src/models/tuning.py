"""Phase 4 tuning helpers for the two ideas against the combined model's overfitting.

The untuned combined LightGBM fits its training accounts almost perfectly (account-level PR-AUC 1.00) but reaches only
0.40 on the next month, with 87% of its gain from application columns: a fake account is a mule in every week and
repeats its application values in all of them, so the trees learn to recognise individual training fakes.

  idea 1  account_weights: every account carries the same total weight, however many weeks it has, so a fake
          account's 27 weeks count once instead of 27 times.
  idea 2  app_score: the 56 prepared application columns become one number from a logistic regression, scored out of
          fold for training accounts, so the trees get the application's signal but cannot memorise accounts by it.

Used by notebooks/06_lgbm_tuning.ipynb.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold


def account_weights(account_id, y) -> np.ndarray:
    """Row weights: each account's rows share one unit of weight, then mule and normal rows get equal totals.

    A row gets 1 / (rows of its account), so every account counts once however many weeks it has. The mule rows are
    then scaled so that mule rows and normal rows carry the same total weight, as class_weight='balanced' does."""
    ids = pd.Series(np.asarray(account_id))
    w = 1.0 / ids.map(ids.value_counts()).to_numpy(dtype=float)
    y = np.asarray(y).astype(bool)
    w[y] *= w[~y].sum() / w[y].sum()
    return w


def _logreg() -> LogisticRegression:
    return LogisticRegression(class_weight="balanced", max_iter=2000)


def app_score(x_train, y_train, x_other, n_splits: int = 5, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """The application data as one number (log-odds of a logistic regression), one row per account.

    Training accounts are scored out of fold: each by a model fitted on the other folds, never on itself, so the score
    the trees train on is as honest as the one they will meet on new accounts. Other accounts (the validation month)
    are scored by a model fitted on all training accounts. Returns (training scores, other scores)."""
    x_train, y_train, x_other = np.asarray(x_train), np.asarray(y_train).astype(int), np.asarray(x_other)
    oof = np.zeros(len(x_train))
    for fit_rows, score_rows in StratifiedKFold(n_splits, shuffle=True, random_state=seed).split(x_train, y_train):
        oof[score_rows] = _logreg().fit(x_train[fit_rows], y_train[fit_rows]).decision_function(x_train[score_rows])
    return oof, _logreg().fit(x_train, y_train).decision_function(x_other)
