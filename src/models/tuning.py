"""Phase 4 tuning helpers for the two ideas against the combined model's overfitting.

The untuned combined LightGBM fits its training accounts almost perfectly (account-level PR-AUC 1.00) but reaches only
0.40 on the next month, with 87% of its gain from application columns: a fake account is a mule in every week and
repeats its application values in all of them, so the trees learn to recognise individual training fakes.

  idea 1  account_weights: every account carries the same total weight, however many weeks it has, so a fake
          account's 27 weeks count once instead of 27 times.
  idea 2  app_score: the 56 prepared application columns become one number from a logistic regression, scored out of
          fold for training accounts, so the trees get the application's signal but cannot memorise accounts by it.

  split   app_score_split: the same idea with two scores, one for fake accounts and one for recruited real
          customers (proposal 28 Oct 2026; tried in the feature lab as the `app_split` variant).

Used by notebooks/06_lgbm_tuning.ipynb and src/models/feature_lab.py.
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


def app_score_split(x_train, y_week0, y_week26, x_other, n_splits: int = 5, seed: int = 0) -> dict[str, tuple]:
    """Two application scores instead of one (proposal 28 Oct 2026): {name: (training scores, other scores)}.

      fake  label: mule at the end of week 0. Real customers start laundering in week 1 or later, so this is in
            practice "a fake account" (fake accounts are mules from opening), learnt from a public label
      real  label: mule by the end of week 26, fitted only on accounts that were not mules at week 0: what a
            recruited real customer's application looks like, without fake accounts drowning it out

    The single app_score's label (mule by week 26) is ~70% fake accounts, so it ranks real-customer mules no higher
    than normal accounts (0 of 32 in the top 1% on v1_full). Both scores are out of fold for training accounts as in
    app_score. Week-0 mules are not in the 'real' model's training rows, so a model fitted on all its rows scores
    them, as it scores the other accounts."""
    x_train, x_other = np.asarray(x_train), np.asarray(x_other)
    y0, y26 = np.asarray(y_week0).astype(int), np.asarray(y_week26).astype(int)
    fake = app_score(x_train, y0, x_other, n_splits, seed)
    keep = y0 == 0
    real_tr = np.zeros(len(x_train))
    real_tr[keep], rest = app_score(x_train[keep], y26[keep], np.vstack([x_train[~keep], x_other]), n_splits, seed)
    real_tr[~keep] = rest[:(~keep).sum()]
    return {"fake": fake, "real": (real_tr, rest[(~keep).sum():])}
