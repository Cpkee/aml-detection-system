"""Neighbour-suspicion features: how suspicious are the accounts of the bank this account exchanged money with?
(proposal 28 Oct 2026, 'version A': the neighbours' scores come from our own model, so no label and no rule alert of
any neighbour is used; run in the feature lab as the `graph_nb` group).

Why: in a chain the later member pays a member who started laundering ~7 weeks earlier (153 of 163 launderer-to-
launderer payments in months 0-4 of v1_full go to a neighbour who started first; median 49 days), so when the later
member's burst begins its neighbour may already look suspicious. First contact comes a median of 6 days after the
account's own start, so this strengthens catching at the start; it cannot flag anyone before laundering begins.

Two stages per fold (train months T, validation month V of lgbm_baseline.FOLDS):
  stage 1  the lab's tuned model (store features + adopted roll4 + weeks_since_open + app_score; LightGBM as in the
           lab) scores every account-week of every account (months 0-7) whose cut-off is on or before the last
           cut-off the focal rows need. Training accounts are scored out of fold: T's accounts are split into
           INNER groups, each scored by a model fitted on the others; every other account is scored by a model fitted
           on all of T. Only T's labels are read. app_score is built the same way (feature_lab.app_scores).
  stage 2  for each focal account-week (months 0-4, weeks 0-26, cut-off c): its neighbours are the accounts of the
           bank it exchanged money with on or before c (features/graph_edges.parquet). Each neighbour contributes
           its latest stage-1 score whose own cut-off is on or before c (an as-of join on the calendar day):
             g_nb_max_score      highest score among all neighbours so far (NaN if none)
             g_nb_max_score_4wk  highest score among neighbours contacted in weeks w-3..w
             g_nb_n_hot          neighbours whose score is in the top 1% of the stage-1 scores of T's
                                 account-weeks 0-26 (the lab's weekly budget size)

Known small leak, accepted: a training focal account's own label is one of ~100k training accounts behind its
neighbours' inner-fold models. Validation accounts' labels are never used.

Results are cached per fold in <out>/features/graph_nb/ (data, git-ignored) with the settings that made them.
"""
from __future__ import annotations
import hashlib
import inspect
import json
import os

import numpy as np
import pandas as pd

import amldata
from features import candidates, graph, weekly
from features.weekly import FEATURES as WEEKLY
from models import lgbm_baseline as base

FEATURES = ["g_nb_max_score", "g_nb_max_score_4wk", "g_nb_n_hot"]
INNER = 3
WEEKS = (0, 26)
FOCAL_MONTHS = (0, 1, 2, 3, 4)
HOT_PCT = 0.01
STAGE1 = WEEKLY + candidates.ADOPTED + ["weeks_since_open", "app_score"]


def _lgbm(seed):
    import lightgbm as lgb
    return lgb.LGBMClassifier(class_weight="balanced", random_state=seed, n_jobs=-1, verbose=-1, deterministic=True,
                              force_row_wise=True)


def nb_sql(grid: str, edges: str, scores: str, hot: float) -> str:
    """Stage 2 on registered tables: grid (account_id, w, open_day), edges (account_id, nb_id, day), scores
    (account_id, cutoff_day, score, sorted). Output: account_id, weeks_since_open + FEATURES for every grid row."""
    return f"""
    WITH g AS (SELECT account_id, w, open_day + 7 * w + 6 AS cut FROM {grid}),
    contact AS (SELECT DISTINCT e.account_id, e.nb_id, (e.day - g0.open_day) // 7 AS cw
                FROM {edges} e JOIN (SELECT DISTINCT account_id, open_day FROM {grid}) g0 USING (account_id)),
    gp AS (SELECT g.account_id, g.w, g.cut, c.nb_id, max(c.cw) AS last_w
           FROM g JOIN contact c ON c.account_id = g.account_id AND c.cw <= g.w
           GROUP BY 1, 2, 3, 4),
    sc AS (SELECT gp.*, s.score FROM gp ASOF LEFT JOIN {scores} s ON gp.nb_id = s.account_id AND gp.cut >= s.cutoff_day),
    agg AS (SELECT account_id, w,
                   max(score)                                  AS g_nb_max_score,
                   max(score) FILTER (WHERE last_w >= w - 3)   AS g_nb_max_score_4wk,
                   count(*) FILTER (WHERE score >= {hot})      AS g_nb_n_hot
            FROM sc GROUP BY 1, 2)
    SELECT g.account_id, g.w AS weeks_since_open, a.g_nb_max_score, a.g_nb_max_score_4wk,
           coalesce(a.g_nb_n_hot, 0) AS g_nb_n_hot
    FROM g LEFT JOIN agg a USING (account_id, w) ORDER BY 1, 2"""


def _settings(out: str, seed: int) -> dict:
    code = inspect.getsource(inspect.getmodule(nb_sql))
    return {"seed": seed, "inner": INNER, "weeks": list(WEEKS), "hot_pct": HOT_PCT, "stage1": STAGE1,
            "store_manifest_sha256": weekly.manifest._sha256(os.path.join(out, "features", weekly.manifest.MANIFEST)),
            "graph_manifest_sha256": weekly.manifest._sha256(os.path.join(out, "features", graph.MANIFEST)),
            "code_sha256": hashlib.sha256(code.encode()).hexdigest()}


def _account_frame(out: str, month: int, max_cut: int) -> pd.DataFrame:
    """Stage-1 inputs (without app_score) for every account of one opening month, weeks whose cut-off <= max_cut."""
    acc = amldata.public(out).execute(f"SELECT account_id, open_day FROM accounts WHERE open_month = {month}").df()
    w_hi = int(min(weekly.LAST_WEEK, (max_cut - acc["open_day"].min() - 6) // 7))
    if w_hi < 0:
        return pd.DataFrame()
    wk = weekly.load(out, (0, w_hi), months=(month,))
    for c in WEEKLY:
        wk[c] = wk[c].astype("float32")
    wk, names = candidates.add(wk, [candidates.ADOPTED_GROUP])
    wk = wk.drop(columns=[c for c in names[candidates.ADOPTED_GROUP] if c not in candidates.ADOPTED])
    wk = wk.merge(acc, on="account_id", validate="m:1")
    wk["cutoff_day"] = wk["open_day"] + 7 * wk["weeks_since_open"] + 6
    return wk[wk["cutoff_day"] <= max_cut].drop(columns="open_day").reset_index(drop=True)


def build_fold(out: str, f: int, seed: int, app: pd.Series, months: list[int]) -> pd.DataFrame:
    train_m, _ = base.FOLDS[f - 1]
    con = amldata.public(out)
    acc = con.execute("SELECT account_id, open_month, open_day FROM accounts").df()
    focal = acc[acc.open_month.isin(FOCAL_MONTHS)]
    max_cut = int(focal["open_day"].max() + 7 * WEEKS[1] + 6)

    train, _ = base.load_table(out, train_m, WEEKS, adopted=True)
    train["app_score"] = train["account_id"].map(app).astype("float32")
    ids = np.sort(train["account_id"].unique())
    group = pd.Series(np.random.default_rng(seed + f).permutation(len(ids)) % INNER, index=ids)
    models = {}
    for g in range(INNER):
        rows = train["account_id"].map(group).to_numpy() != g
        models[g] = _lgbm(seed).fit(train.loc[rows, STAGE1], train.loc[rows, "mule_by_day"])
    models["all"] = _lgbm(seed).fit(train[STAGE1], train["mule_by_day"])
    train_scores = []
    for g in range(INNER):
        part = train[train["account_id"].map(group).to_numpy() == g]
        train_scores.append(models[g].predict_proba(part[STAGE1])[:, 1])
    hot = float(np.quantile(np.concatenate(train_scores), 1 - HOT_PCT))
    del train

    scores = []
    for m in months:
        d = _account_frame(out, m, max_cut)
        if d.empty:
            continue
        d["app_score"] = d["account_id"].map(app).astype("float32")
        who = d["account_id"].map(group) if m in train_m else pd.Series(np.nan, index=d.index)
        s = np.empty(len(d))
        for key in list(range(INNER)) + ["all"]:
            rows = (who == key).to_numpy() if key != "all" else who.isna().to_numpy()
            if rows.any():
                s[rows] = models[key].predict_proba(d.loc[rows, STAGE1])[:, 1]
        scores.append(d[["account_id", "cutoff_day"]].assign(score=s))
        print(f"  fold {f}: stage-1 scores for month {m}: {len(d):,} account-weeks")
    scores = pd.concat(scores, ignore_index=True).sort_values(["account_id", "cutoff_day"], kind="stable")

    grid = focal[["account_id", "open_day"]].merge(pd.DataFrame({"w": range(WEEKS[0], WEEKS[1] + 1)}), how="cross")
    con.execute("PRAGMA memory_limit='6GB'")
    con.register("grid_t", grid)
    con.register("scores_t", scores)
    con.execute(f"CREATE TEMP TABLE edges_t AS SELECT account_id, nb_id, day FROM read_parquet('{graph.edges(out)}') "
                f"WHERE account_id IN (SELECT account_id FROM grid_t)")
    res = con.execute(nb_sql("grid_t", "edges_t", "scores_t", hot)).df()
    for c in FEATURES:
        res[c] = res[c].astype("float32")
    return res


def load_or_build(out: str, seed: int = 42) -> dict[int, pd.DataFrame]:
    """Per fold, KEY + FEATURES for every focal account-week (months 0-4, weeks 0-26). Cached under
    <out>/features/graph_nb/ and rebuilt when the settings, code, store or graph store change."""
    from models.feature_lab import app_scores
    graph.check(out)
    folder = os.path.join(out, "features", "graph_nb")
    os.makedirs(folder, exist_ok=True)
    settings = _settings(out, seed)
    meta = os.path.join(folder, "settings.json")
    fresh = os.path.exists(meta) and json.load(open(meta)) == settings and all(
        os.path.exists(os.path.join(folder, f"fold{f}.parquet")) for f in range(1, len(base.FOLDS) + 1))
    if fresh:
        return {f: pd.read_parquet(os.path.join(folder, f"fold{f}.parquet")) for f in range(1, len(base.FOLDS) + 1)}
    months = [r[0] for r in amldata.public(out).execute("SELECT DISTINCT open_month FROM accounts ORDER BY 1").fetchall()]
    app = app_scores(out, seed, other_months=months)
    res = {}
    for f in range(1, len(base.FOLDS) + 1):
        res[f] = build_fold(out, f, seed, app[f]["app_score"], months)
        res[f].to_parquet(os.path.join(folder, f"fold{f}.parquet"), index=False)
    with open(meta, "w") as fh:
        json.dump(settings, fh, indent=2)
    return res
