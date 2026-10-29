"""Feature selection helpers: which of the tuned model's inputs earn their place?

The tuned model (notebooks/06_lgbm_tuning.ipynb, plus the adopted 4-week windows) reads 38 inputs: the 28 store
features, the 8 adopted 4-week features, weeks_since_open and the application score. This module gives the pieces
notebooks/10_feature_selection.ipynb uses to narrow them down, all on training months 0-4 only:

  FAMILIES             the 38 inputs in 10 groups of the same kind (used for leave-one-group-out trials:
                       `python -m models.feature_lab --drop FAMILY ...`)
  spearman_clusters    groups of near-duplicate features (|Spearman| at or above a threshold for every pair)
  permutation_drop     how much the tuning measure falls when a feature, or a whole group, is shuffled in the
                       validation month (shuffling a group together stops a near-copy hiding the loss)
  mean_abs_contrib     mean |SHAP value| per feature (LightGBM's own pred_contrib), and its sign against the value

Nothing here changes the store or the adopted list; a narrower list is a team decision (CLAUDE.md).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from features import candidates
from features.weekly import FEATURES as WEEKLY

FAMILIES = {
    "volume_wk": ["n_rows_wk", "n_in_wk", "n_out_wk", "money_in_wk", "money_out_wk", "max_in_wk", "max_out_wk",
                  "card_items_wk"],
    "volume_cum": ["n_rows_cum", "money_in_cum", "money_out_cum"],
    "counterparties": ["n_payers_wk", "n_payees_wk", "new_payer_share_wk", "n_payers_cum", "n_payees_cum"],
    "flow": ["passthrough_wk", "out_1h_share_wk", "out_24h_share_wk", "med_in_out_minutes_wk"],
    "self_vs_past": ["self_vs_past_money_in", "self_vs_past_payers", "self_vs_past_rows"],
    "peer": ["peer_ratio_money_in"],
    "mix": ["internal_out_share_cum", "cash_in_share_cum", "abroad_out_share_cum", "high_risk_out_share_cum"],
    "window_4wk": list(candidates.ADOPTED),
    "clock": ["weeks_since_open"],
    "application": ["app_score"],
}
ALL_INPUTS = WEEKLY + candidates.ADOPTED + ["weeks_since_open", "app_score"]   # the tuned model's 38 inputs
FAMILY_OF = {c: fam for fam, cols in FAMILIES.items() for c in cols}


def spearman_clusters(df: pd.DataFrame, cols: list[str], threshold: float = 0.8, sample: int = 200_000,
                      seed: int = 0) -> tuple[pd.DataFrame, pd.Series]:
    """Spearman correlation between features and the groups of near-duplicates.

    Rows are a random sample (pairs use the rows where both values exist). Groups come from complete-linkage
    clustering on 1 - |rho|, cut at 1 - threshold, so every pair inside a group has |rho| >= threshold.
    Returns (rho matrix, cluster number per feature; a feature alone in its group has its own number)."""
    from scipy.cluster.hierarchy import fcluster, linkage
    from scipy.spatial.distance import squareform

    d = df[cols].sample(min(sample, len(df)), random_state=seed) if len(df) > sample else df[cols]
    rho = d.rank().corr(method="pearson")                 # Spearman = Pearson on ranks; NaN pairs left out
    dist = (1 - rho.abs()).fillna(1.0).to_numpy(copy=True)
    np.fill_diagonal(dist, 0.0)
    dist = (dist + dist.T) / 2
    z = linkage(squareform(dist, checks=False), method="complete")
    labels = fcluster(z, t=1 - threshold, criterion="distance")
    return rho, pd.Series(labels, index=cols, name="cluster")


def permute_columns(x: pd.DataFrame, cols: list[str], rng: np.random.Generator) -> pd.DataFrame:
    """A copy of x with `cols` shuffled together: one row order for all of them, so a group moves as a block."""
    order = rng.permutation(len(x))
    out = x.copy()
    out[cols] = x[cols].to_numpy()[order]
    return out


def permutation_drop(model, valid: pd.DataFrame, cols: list[str], groups: dict[str, list[str]], measure,
                     repeats: int = 3, seed: int = 0) -> pd.DataFrame:
    """Fall in `measure(valid, score)` when each group's columns are shuffled, `repeats` times each.

    measure takes the validation rows and a score array and returns one number (higher = better), or a dict of
    named numbers to score several measures on the same shuffles; then each row also has a `measure` column. A
    positive drop means the model needed that group; about 0 means it did not (or a near-copy stood in for it)."""
    def as_dict(m):
        return m if isinstance(m, dict) else {None: m}

    x = valid[cols]
    base = as_dict(measure(valid, model.predict_proba(x)[:, 1]))
    rng = np.random.default_rng(seed)
    rows = []
    for name, g in groups.items():
        for r in range(repeats):
            got = as_dict(measure(valid, model.predict_proba(permute_columns(x, g, rng))[:, 1]))
            for k, b in base.items():
                rows.append({"group": name, "repeat": r, **({"measure": k} if k is not None else {}),
                             "base": b, "drop": b - got[k]})
    return pd.DataFrame(rows)


def mean_abs_contrib(model, x: pd.DataFrame) -> pd.DataFrame:
    """Mean |SHAP value| per feature (LightGBM pred_contrib, on the log-odds scale) and the Spearman sign between a
    feature's value and its contribution (+ = higher value pushes the score up)."""
    c = model.booster_.predict(x, pred_contrib=True)[:, :-1]          # last column is the bias
    sign = [pd.Series(x[col].to_numpy()).corr(pd.Series(c[:, i]), method="spearman") for i, col in enumerate(x.columns)]
    return pd.DataFrame({"feature": x.columns, "mean_abs_shap": np.abs(c).mean(axis=0), "direction": sign})
