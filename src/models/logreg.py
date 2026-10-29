"""Logistic regression on the 38 frozen inputs: the linear model the report compares LightGBM with.

Same inputs as the frozen LightGBM (the 28 store features, the 8 adopted 4-week features, weeks_since_open and the
application score), so the only difference between the two models is the model. A linear model needs its inputs
prepared; the steps are those of notebooks/04_logreg_baseline.ipynb, extended to the 4-week features and app_score,
and fitted on the training rows only:

  log    counts, money, maxima, running totals, peer ratio, minutes (long right tail): fill a gap with the training
         median, log(1 + x) of the value clipped at 0, standardise
  share  pass-through, speed and mix shares, also over 4 weeks: fill with the median, clip to [0, 1] (the speed
         shares pass 1 when last week's money leaves this week; notebook 04, 25 Oct 2026), standardise
  z      the three self-vs-past z-scores: fill with the median, clip to [-10, 10], standardise
  std    weeks_since_open and app_score (already log-odds): fill with the median, standardise
  flag   every input with a gap in the training rows also gets a 0/1 column "<input>__missing" (not standardised)

The fitted preparation and coefficients are plain numbers, saved as JSON (readable, diffable, no pickle), like the
application model of models.train. MuleLogit is a small scikit-learn style estimator (fit / predict_proba) so the
feature lab's folds and measures can be reused unchanged (models.feature_lab.fit_folds, `make_model`).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from features import candidates
from features.weekly import FEATURES as WEEKLY

INPUTS = WEEKLY + candidates.ADOPTED + ["weeks_since_open", "app_score"]      # the 38 frozen inputs (models.train)
SHARES = ["new_payer_share_wk", "passthrough_wk", "out_1h_share_wk", "out_24h_share_wk", "internal_out_share_cum",
          "cash_in_share_cum", "abroad_out_share_cum", "high_risk_out_share_cum",
          "out_1h_share_4wk", "out_24h_share_4wk", "passthrough_4wk"]
ZSCORE = ["self_vs_past_money_in", "self_vs_past_payers", "self_vs_past_rows"]
PLAIN = ["weeks_since_open", "app_score"]
LOGGED = [c for c in INPUTS if c not in SHARES + ZSCORE + PLAIN]
KIND = {**{c: "log" for c in LOGGED}, **{c: "share" for c in SHARES}, **{c: "z" for c in ZSCORE},
        **{c: "std" for c in PLAIN}}
DEFAULTS = {"C": 1.0, "class_weight": "balanced", "max_iter": 2000}       # notebook 04's settings


def _shape(x: np.ndarray, kind: str) -> np.ndarray:
    if kind == "log":
        return np.log1p(np.clip(x, 0, None))
    if kind == "share":
        return np.clip(x, 0, 1)
    if kind == "z":
        return np.clip(x, -10, 10)
    return x


def fit_prep(df: pd.DataFrame, cols: list[str]) -> dict:
    """Preparation fitted on training rows: per input its kind, gap-filling median, whether it gets a missing flag,
    and the mean / sd used to standardise. A pure function of the rows given."""
    prep = {}
    for c in cols:
        x = df[c].to_numpy(dtype="float64")
        miss = np.isnan(x)
        med = float(np.nanmedian(x)) if (~miss).any() else 0.0
        v = _shape(np.where(miss, med, x), KIND[c])
        sd = float(v.std())
        prep[c] = {"kind": KIND[c], "median": med, "flag": bool(miss.any()), "mean": float(v.mean()),
                   "sd": sd if sd > 0 else 1.0}
    return prep


def columns_out(prep: dict) -> list[str]:
    """Names of the prepared columns, in order: every input, then the missing flags."""
    return list(prep) + [f"{c}__missing" for c, p in prep.items() if p["flag"]]


def transform(df: pd.DataFrame, prep: dict) -> np.ndarray:
    """The prepared matrix (rows of df, columns_out(prep)); no NaN."""
    out, flags = [], []
    for c, p in prep.items():
        x = df[c].to_numpy(dtype="float64")
        miss = np.isnan(x)
        out.append((_shape(np.where(miss, p["median"], x), p["kind"]) - p["mean"]) / p["sd"])
        if p["flag"]:
            flags.append(miss.astype("float64"))
    return np.column_stack(out + flags)


class MuleLogit:
    """Prepare (fitted on the training rows) + class-weighted logistic regression, scikit-learn style."""

    def __init__(self, C: float = DEFAULTS["C"], class_weight=DEFAULTS["class_weight"],
                 max_iter: int = DEFAULTS["max_iter"], random_state: int = 42):
        self.C, self.class_weight, self.max_iter, self.random_state = C, class_weight, max_iter, random_state

    def fit(self, x: pd.DataFrame, y) -> "MuleLogit":
        from sklearn.linear_model import LogisticRegression
        self.inputs_ = list(x.columns)
        self.prep_ = fit_prep(x, self.inputs_)
        lr = LogisticRegression(C=self.C, class_weight=self.class_weight, max_iter=self.max_iter,
                                random_state=self.random_state)
        lr.fit(transform(x, self.prep_), np.asarray(y).astype(int))
        self.coef_, self.intercept_ = lr.coef_[0].copy(), float(lr.intercept_[0])
        self.n_iter_ = int(lr.n_iter_[0])
        return self

    def decision_function(self, x: pd.DataFrame) -> np.ndarray:
        return transform(x[self.inputs_], self.prep_) @ self.coef_ + self.intercept_

    def predict_proba(self, x: pd.DataFrame) -> np.ndarray:
        p = 1 / (1 + np.exp(-self.decision_function(x)))
        return np.column_stack([1 - p, p])

    def predict(self, x: pd.DataFrame) -> np.ndarray:
        """The probability of 'mule' (as LightGBM's Booster.predict, which models.train.predict calls)."""
        return self.predict_proba(x)[:, 1]

    def coefficients(self) -> pd.DataFrame:
        """Coefficient per prepared column (per standard deviation for inputs; for flags, missing vs not)."""
        return pd.DataFrame({"column": columns_out(self.prep_), "coef": self.coef_}) \
            .assign(odds_ratio=lambda d: np.exp(d["coef"])).sort_values("coef", key=np.abs, ascending=False)

    def to_dict(self) -> dict:
        return {"model": "logistic regression", "inputs": self.inputs_, "prep": self.prep_,
                "columns": columns_out(self.prep_), "coef": self.coef_.tolist(), "intercept": self.intercept_,
                "settings": {"C": self.C, "class_weight": self.class_weight, "max_iter": self.max_iter},
                "n_iter": self.n_iter_}

    @classmethod
    def from_dict(cls, d: dict) -> "MuleLogit":
        m = cls(**d["settings"])
        m.inputs_, m.prep_ = d["inputs"], d["prep"]
        m.coef_, m.intercept_, m.n_iter_ = np.asarray(d["coef"], dtype="float64"), float(d["intercept"]), d["n_iter"]
        if columns_out(m.prep_) != d["columns"]:
            raise ValueError("saved logistic model: columns do not match its preparation")
        return m
