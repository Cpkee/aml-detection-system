"""Methods comparison: rivals of the model of record on the feature lab's 3 temporal folds (months 0-4 only).

    PYTHONPATH=src python -m models.comparison --out data/v1_full --methods ref
    PYTHONPATH=src python -m models.comparison --out data/v1_full --mde
    PYTHONPATH=src python -m models.comparison --out data/v1_full --methods anchor A1_activity A2_raw_app A3_app_only A4_logistic
    PYTHONPATH=src python -m models.comparison --out data/v1_full --f2

Plan, decided and pre-registered 2 Nov 2026: outputs/modelling/comparison/PLAN.md. Every method sees the lab's rows,
label, folds and app score (stability.lab_setup) and is judged by catch_rules: permanent flags at the rules' weekly
alert count, the share of each week's mules already flagged, averaged over weeks 0-26. Methods with randomness average
the scores of seeds 1-5 per account-week before flagging, as the model of record does.

Writes outputs/modelling/comparison/<run>/folds.csv (a method's rows are replaced when it is re-run),
first_flags.csv (first flag week per account at the rules' budget: the paired bootstrap's input) and MDE.json;
out-of-fold scores go to <out>/comparison/<method>.parquet. Month 5 and test months 6-7 are never read here.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import subprocess
import time

import numpy as np
import pandas as pd
from scipy.stats import norm

from evaluation import hybrid
from features import candidates
from features.weekly import FEATURES as WEEKLY
from models import feature_lab as fl
from models import lgbm_baseline as base
from models import stability

SEEDS = (1, 2, 3, 4, 5)
TUNED = "outputs/modelling/models/v1_full/lgbm_tuning_step2/tuned_params.json"
ACTIVITY = WEEKLY + candidates.ADOPTED + ["weeks_since_open"]
NOISE = fl.NOISE["catch_rules"]                 # 0.012, measured refit noise (placebo, 28 Oct 2026)
N_RIVALS = 13       # planned rivals: anchor, A1-A4, B1-B4, C1, D0, D1, F2 (the Holm bar of the first step)
N_BOOT, BOOT_SEED = 2000, 0
REPORT_ROOT = "outputs/modelling/comparison"


# ---------------------------------------------------------------- methods
def lgbm(cols: list[str], params: dict | None, seeds=SEEDS):
    """LightGBM on cols with balanced class weights; the scores of `seeds` averaged."""
    import lightgbm as lgb

    def fit(train: pd.DataFrame, valid: pd.DataFrame) -> np.ndarray:
        s = np.zeros(len(valid))
        for seed in seeds:
            m = lgb.LGBMClassifier(class_weight="balanced", random_state=seed, **stability.FIXED, **(params or {}))
            m.fit(train[cols], train["mule_by_day"])
            s += m.predict_proba(valid[cols])[:, 1]
        return s / len(seeds)
    return fit


def app_only(train: pd.DataFrame, valid: pd.DataFrame) -> np.ndarray:
    """A3: the application score alone, the same every week."""
    return valid["app_score"].to_numpy(dtype=float)


def logistic(train: pd.DataFrame, valid: pd.DataFrame) -> np.ndarray:
    """A4: logistic regression on the 38 inputs with notebook 04's recipe (balanced class weights)."""
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import FunctionTransformer, StandardScaler

    def part(fn):
        return make_pipeline(SimpleImputer(strategy="median", add_indicator=True),
                             FunctionTransformer(fn, feature_names_out="one-to-one"), StandardScaler())
    shares = [c for c in stability.INPUTS if "share" in c or c.startswith("passthrough")]
    zscore = [c for c in stability.INPUTS if c.startswith("self_vs_past")]
    logged = [c for c in WEEKLY + candidates.ADOPTED if c not in shares + zscore]
    pipe = make_pipeline(ColumnTransformer([
        ("log", part(lambda x: np.log1p(np.clip(x, 0, None))), logged),
        ("share", part(lambda x: np.clip(x, 0, 1)), shares),
        ("z", part(lambda x: np.clip(x, -10, 10)), zscore),
        ("scale", StandardScaler(), ["weeks_since_open", "app_score"])]),
        LogisticRegression(class_weight="balanced", max_iter=2000))
    pipe.fit(train, train["mule_by_day"])
    return pipe.predict_proba(valid)[:, 1]


def app_columns(out: str) -> list[str]:
    import pyarrow.parquet as pq
    names = pq.read_schema(os.path.join(out, "features", "accounts_tree.parquet")).names
    return [c for c in names if c not in ("account_id", "open_month")]


def methods(out: str) -> dict:
    tuned = json.load(open(TUNED))
    return {"ref": lgbm(stability.INPUTS, tuned),
            "anchor": lgbm(stability.INPUTS, None, seeds=(1,)),    # defaults sample nothing: the seed changes nothing
            "A1_activity": lgbm(ACTIVITY, tuned),
            "A2_raw_app": lgbm(ACTIVITY + app_columns(out), tuned),
            "A3_app_only": app_only,
            "A4_logistic": logistic}


# ---------------------------------------------------------------- measures
def budget_measures(first: pd.Series, mules: pd.DataFrame, start: pd.Series, prof: pd.Series) -> dict:
    """Measures of one set of permanent flags at the rules' budget (first flag week per account)."""
    ids = pd.Index(mules["account_id"].unique())          # mule by week 26 (the label never goes back to 0)
    caught = ids.intersection(first.index)
    st = start.reindex(caught).dropna()
    return {"catch_rules": fl.catch_mean(first, mules), "flags": len(first), "mules": len(ids),
            "caught": len(caught), "recall_w26": len(caught) / max(len(ids), 1),
            "precision": len(caught) / max(len(first), 1),
            "median_weeks_from_start": float((first.loc[st.index] - st).median()) if len(st) else np.nan,
            **fl.real_mules_caught(first, mules, prof)}


def cohort_mules(setup: dict, valid_m: int) -> pd.DataFrame:
    m = setup["ctx"]["mules"]
    return m[m.open_month == valid_m]


def run_method(out: str, setup: dict, name: str, fit) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Fit on each fold's training months, score its validation month: (fold rows, first flags, out-of-fold scores)."""
    from sklearn.metrics import roc_auc_score
    rows, flags, oof = [], [], []
    for f, (train_m, valid_m) in enumerate(base.FOLDS, start=1):
        d = fl.with_fold_columns(setup["df"], f, setup["scores"])
        train, valid = d[d.open_month.isin(train_m)], d[d.open_month == valid_m]
        t = time.time()
        score = fit(train, valid)
        seconds = time.time() - t
        v = valid.assign(score=score)
        first = fl.first_flag_weeks(v, setup["ctx"]["budget"][valid_m])
        acc = base.accounts(valid, score)
        row = {"method": name, "fold": f, "valid_month": valid_m, "fit_seconds": round(seconds, 1),
               **stability.fold_measures(valid, score, valid_m, setup),
               **budget_measures(first, cohort_mules(setup, valid_m), setup["start"], setup["prof"]),
               "acc_roc_auc": float(roc_auc_score(acc["y"], acc["s"]))}
        rows.append(row)
        flags.append(first.rename("week").rename_axis("account_id").reset_index().assign(method=name, fold=f))
        oof.append(valid[base.KEY].assign(score=score, fold=f))
        print(f"  {name} fold {f}: catch_rules {row['catch_rules']:.4f}  caught {row['caught']}/{row['mules']}"
              f"  ({seconds:.0f} s)", flush=True)
        del d, train, valid
    return pd.DataFrame(rows), pd.concat(flags, ignore_index=True), pd.concat(oof, ignore_index=True)


def run_f2(out: str, setup: dict, shares=hybrid.SHARES) -> tuple[pd.DataFrame, pd.DataFrame]:
    """F2 on the folds: ref's out-of-fold scores and the rules' alerts share each week's budget."""
    oof = pd.read_parquet(os.path.join(out, "comparison", "ref.parquet"))
    alerts = hybrid.rules_alerts(out, fl.MONTHS, fl.WEEKS)
    rows, flags = [], []
    for f, (_, valid_m) in enumerate(base.FOLDS, start=1):
        v = oof[oof.fold == f]
        a = alerts[alerts.open_month == valid_m]
        for s in shares:
            name = f"F2_hybrid_{s:g}"
            first = hybrid.split_flags(v, a, setup["ctx"]["budget"][valid_m], s)
            rows.append({"method": name, "fold": f, "valid_month": valid_m, "model_share": s,
                         **budget_measures(first, cohort_mules(setup, valid_m), setup["start"], setup["prof"])})
            flags.append(first.rename("week").rename_axis("account_id").reset_index().assign(method=name, fold=f))
    return pd.DataFrame(rows), pd.concat(flags, ignore_index=True)


# ---------------------------------------------------------------- paired bootstrap
def hit_matrices(first: pd.Series, mules: pd.DataFrame, ids: pd.Index, weeks: pd.Index) -> tuple:
    """(is_mule, hit) as account x week arrays in a fixed order: hit = flagged at that week or earlier."""
    t = mules.assign(one=1.0, hit=(mules["account_id"].map(first) <= mules["weeks_since_open"]).astype(float))
    is_mule = t.pivot_table(index="account_id", columns="weeks_since_open", values="one", fill_value=0.0)
    hit = t.pivot_table(index="account_id", columns="weeks_since_open", values="hit", fill_value=0.0)
    return (is_mule.reindex(index=ids, columns=weeks, fill_value=0.0).to_numpy(),
            hit.reindex(index=ids, columns=weeks, fill_value=0.0).to_numpy())


def boot_catch(firsts: list[pd.Series], cohorts: list[pd.DataFrame], n_boot: int = N_BOOT,
               seed: int = BOOT_SEED) -> np.ndarray:
    """catch_rules of each method in each bootstrap draw, pooled = mean over cohorts. Mule accounts are resampled
    within each cohort, with the same draw for every method (paired). Returns (n_boot, n_methods)."""
    rng = np.random.default_rng(seed)
    pooled = np.zeros((n_boot, len(firsts)))
    for mules in cohorts:
        ids = pd.Index(sorted(mules["account_id"].unique()))
        weeks = pd.Index(sorted(mules["weeks_since_open"].unique()))
        w = rng.multinomial(len(ids), np.full(len(ids), 1 / len(ids)), size=n_boot)
        for j, first in enumerate(firsts):
            is_mule, hit = hit_matrices(first, mules, ids, weeks)
            with np.errstate(invalid="ignore", divide="ignore"):
                pooled[:, j] += np.nanmean((w @ hit) / (w @ is_mule), axis=1)
    return pooled / len(cohorts)


def paired_test(first_a: pd.Series, first_b: pd.Series, cohorts: list[pd.DataFrame]) -> dict:
    """Rival a vs reference b (first flag week per account, all cohorts together; account ids never repeat across
    cohorts): pooled gain, 95% interval and two-sided p from the paired bootstrap, and the cohorts where a leads."""
    each = [fl.catch_mean(first_a, m) - fl.catch_mean(first_b, m) for m in cohorts]
    x = boot_catch([first_a, first_b], cohorts)
    d = x[:, 0] - x[:, 1]
    gain, lead = float(np.mean(each)), sum(e > 0 for e in each)
    p = min(1.0, 2 * min((d <= 0).mean(), (d >= 0).mean()))
    lo, hi = np.percentile(d, [2.5, 97.5])
    return {"gain": float(gain), "lo": float(lo), "hi": float(hi), "p": float(p), "cohorts_ahead": int(lead),
            "cohorts": len(cohorts)}


def holm(p: pd.Series, alpha: float = 0.05) -> pd.Series:
    """True where Holm's step-down procedure rejects 'no difference'."""
    order = p.sort_values()
    ok, keep = pd.Series(False, index=p.index), True
    for i, (k, v) in enumerate(order.items()):
        keep = keep and v <= alpha / (len(p) - i)
        ok[k] = keep
    return ok


def mde(ref_first: pd.Series, cohorts: list[pd.DataFrame], n_rivals: int = N_RIVALS, power: float = 0.8,
        alpha: float = 0.05) -> dict:
    """Smallest pooled catch_rules gain the win rule would detect with the given power, from the reference alone.
    Uses the bootstrap SD of the reference's pooled catch_rules and treats a rival's errors as independent of ours
    (SD of a difference = sqrt(2) x SD): pairing only lowers it, so this is the conservative figure."""
    sd = float(np.std(boot_catch([ref_first], cohorts)[:, 0]))
    per = [float(np.std(boot_catch([ref_first], [m])[:, 0])) for m in cohorts]
    z = norm.ppf(1 - alpha / 2 / n_rivals) + norm.ppf(power)
    return {"ref_pooled_sd": sd, "per_cohort_sd": per, "n_rivals": n_rivals, "power": power, "alpha": alpha,
            "z": float(z), "mde_independent": float(z * np.sqrt(2) * sd), "noise_floor": NOISE,
            "mde": float(max(z * np.sqrt(2) * sd, NOISE))}


# ---------------------------------------------------------------- files
def report_dir(out: str) -> str:
    d = os.path.join(REPORT_ROOT, os.path.basename(os.path.normpath(out)))
    os.makedirs(d, exist_ok=True)
    return d


def replace_rows(path: str, new: pd.DataFrame) -> None:
    """Write new rows into a csv, replacing earlier rows of the same methods."""
    if os.path.exists(path):
        old = pd.read_csv(path)
        new = pd.concat([old[~old["method"].isin(new["method"].unique())], new], ignore_index=True)
    new.to_csv(path, index=False)


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def first_flags(out: str, method: str) -> pd.Series:
    """A method's first flag week per account over all folds (account ids never repeat across folds)."""
    t = pd.read_csv(os.path.join(report_dir(out), "first_flags.csv"), dtype={"account_id": str})
    return t[t.method == method].set_index("account_id")["week"].astype(float)


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="data/v1_full")
    ap.add_argument("--methods", nargs="*", default=[])
    ap.add_argument("--f2", action="store_true", help="the rules + model budget split (needs ref's scores)")
    ap.add_argument("--mde", action="store_true", help="smallest detectable gain from ref's flags")
    a = ap.parse_args(argv)
    rep = report_dir(a.out)
    stamp = {"run_at": datetime.datetime.now().isoformat(timespec="seconds"), "git_commit": git_commit()}
    print(f"loading {a.out} ...", flush=True)
    setup = stability.lab_setup(a.out)
    cohorts = [cohort_mules(setup, valid_m) for _, valid_m in base.FOLDS]
    available = methods(a.out)
    for name in a.methods:
        rows, flags, oof = run_method(a.out, setup, name, available[name])
        os.makedirs(os.path.join(a.out, "comparison"), exist_ok=True)
        oof.to_parquet(os.path.join(a.out, "comparison", f"{name}.parquet"), index=False)
        replace_rows(os.path.join(rep, "folds.csv"), rows.assign(**stamp))
        replace_rows(os.path.join(rep, "first_flags.csv"), flags)
    if a.f2:
        rows, flags = run_f2(a.out, setup)
        replace_rows(os.path.join(rep, "folds.csv"), rows.assign(**stamp))
        replace_rows(os.path.join(rep, "first_flags.csv"), flags)
    if a.mde:
        m = mde(first_flags(a.out, "ref"), cohorts) | {"cohorts": "folds 1-3 (month 5 added at the gate)", **stamp}
        json.dump(m, open(os.path.join(rep, "MDE.json"), "w"), indent=2)
        print(json.dumps(m, indent=2))


if __name__ == "__main__":
    main()
