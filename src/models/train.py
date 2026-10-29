"""Phase 5, step 1: train the frozen model on all training months and save it for the harness.

    PYTHONPATH=src python -m models train --out data/v1_full                       # default LightGBM settings
    PYTHONPATH=src python -m models train --out data/v1_full --params tuned.json   # tuning step 2's settings

The model is the one the team froze on 28 Oct 2026: LightGBM on 38 inputs, the 28 store features + the 8 adopted
`roll4` features + weeks_since_open + the application score. It is fitted on every account opened in months 0-4,
weeks 0-26 since opening, label mule_by_day, closed weeks dropped (lgbm_baseline.load_table, adopted=True); the
application score is the logistic regression of notebook 06 (accounts_linear, label: mule by the end of week 26),
out of fold for the training accounts, and fitted on all of them for scoring new accounts.

Saved to <out>/models/<name>/ (data, git-ignored): lgbm.txt (LightGBM text model), app_logreg.json (columns,
coefficients, intercept: readable, no pickle) and manifest.json (inputs, settings, data and store hashes, git commit).
A copy of the manifest and the feature importances go to outputs/modelling/models/<data>/<name>/ (committed).
Calibration on month 5 is a later step (4 Nov 2026); this file only trains.
"""
from __future__ import annotations
import argparse
import json
import os
import time

import numpy as np
import pandas as pd

import amldata
from features import candidates, fingerprint, manifest, weekly
from features.weekly import FEATURES as WEEKLY
from models import lgbm_baseline as base
from models.tuning import _logreg, app_score

MONTHS = (0, 1, 2, 3, 4)
WEEKS = (0, 26)
INPUTS = WEEKLY + candidates.ADOPTED + ["weeks_since_open", "app_score"]      # the 38 frozen inputs
# "activity" = the frozen inputs without the application score: the yardstick for the value of onboarding
# information (professor's comment 2): same rows, same settings, same cohort, only the application left out
INPUT_SETS = {"frozen": INPUTS, "activity": [c for c in INPUTS if c != "app_score"]}
DEFAULT_PARAMS = {"class_weight": "balanced", "random_state": 42, "deterministic": True, "force_row_wise": True,
                  "verbose": -1}
REPORT_ROOT = "outputs/modelling/models"


def machine() -> dict:
    """Where a result was computed: LightGBM's trees can differ between machines (OS, threads) even with
    deterministic=True, so every model, calibration and harness run records it."""
    import platform
    return {"os": platform.platform(), "processor": platform.processor() or platform.machine(),
            "cpu_count": os.cpu_count(), "python": platform.python_version()}


def data_identity(out: str) -> dict:
    """What decides the simulated data, without the machine-specific parts of run_manifest.json (BAF path, git
    commit, package versions): the settings file's hash, the --set overrides, the seed and the BAF file's hash."""
    m = json.load(open(os.path.join(out, "run_manifest.json")))
    return {k: m.get(k) for k in ("version", "seed", "set", "config_sha256", "baf_sha256")}


VERIFIED = "verified.json"
MODEL_FILES = ("lgbm.txt", "app_logreg.json", "manifest.json")


def model_files_sha256(folder: str) -> dict:
    """Hashes of the model files with line endings normalised, so a Windows checkout (CRLF) matches a Mac one."""
    import hashlib
    return {f: hashlib.sha256(open(os.path.join(folder, f), "rb").read().replace(b"\r\n", b"\n")).hexdigest()
            for f in MODEL_FILES}


def model_dir(out: str, name: str) -> str:
    """Where `train` writes a model trained on this machine (data, git-ignored)."""
    return os.path.join(out, "models", name)


def shared_dir(out: str, name: str, report_root: str | None = None) -> str:
    """Where a shared model lives in git: outputs/modelling/models/<data>/<name>/ with its lgbm.txt."""
    return os.path.join(report_root or REPORT_ROOT, os.path.basename(os.path.normpath(out)), name)


def find_model_dir(out: str, name: str) -> str:
    """The model's folder: the shared copy in git when it holds a model file (the model of record, the same for every
    team member, decision option B 29 Oct 2026), else the one trained on this machine."""
    shared = shared_dir(out, name)
    return shared if os.path.exists(os.path.join(shared, "lgbm.txt")) else model_dir(out, name)


def feature_table(out: str, months, weeks: tuple[int, int]) -> pd.DataFrame:
    """Public inputs for every account-week of accounts opened in `months` (no label, no closure): the store, the
    adopted features and each account's opening month. Rows sorted by account and week."""
    wk = weekly.load(out, (0, weeks[1]), months=tuple(months))
    for c in WEEKLY:
        wk[c] = wk[c].astype("float32")
    wk, names = candidates.add(wk, [candidates.ADOPTED_GROUP])
    wk = wk.drop(columns=[c for c in names[candidates.ADOPTED_GROUP] if c not in candidates.ADOPTED])
    wk = wk[wk["weeks_since_open"] >= weeks[0]].reset_index(drop=True)
    acc = amldata.public(out).execute("SELECT account_id, open_month, open_day FROM accounts").df()
    return wk.merge(acc, on="account_id", how="left", validate="m:1")


def _linear(out: str) -> tuple[pd.DataFrame, list[str]]:
    lin = pd.read_parquet(os.path.join(out, "features", "accounts_linear.parquet")).set_index("account_id")
    return lin, [c for c in lin.columns if c != "open_month"]


def app_scores_for(out: str, model: dict, ids) -> pd.Series:
    """The saved application model's score (log-odds) for any accounts, from the public cleaned table."""
    lin, _ = _linear(out)
    x = lin.loc[list(ids), model["columns"]].to_numpy(dtype=float)
    return pd.Series(x @ np.asarray(model["coef"]) + model["intercept"], index=list(ids))


def train(out: str = amldata.DEFAULT_OUT, name: str = "frozen", params: dict | None = None, seed: int = 42,
          report_root: str = REPORT_ROOT, input_set: str = "frozen") -> dict:
    import lightgbm as lgb
    if os.path.exists(os.path.join(shared_dir(out, name, report_root), "lgbm.txt")):
        raise ValueError(f"`{name}` is a shared model in {shared_dir(out, name, report_root)} (committed, the same for "
                         "everyone): load it, or train under another name")
    t0 = time.time()
    lin, cols = _linear(out)
    lin = lin[lin["open_month"].isin(MONTHS)]
    y26 = amldata.labels(out, months=MONTHS, weeks_since_open=WEEKS[1]).set_index("account_id")["mule_by_day"]
    oof, _ = app_score(lin[cols], y26.loc[lin.index], lin[cols].iloc[:1], seed=seed)
    full = _logreg().fit(lin[cols].to_numpy(), y26.loc[lin.index].to_numpy().astype(int))
    app_model = {"columns": cols, "coef": full.coef_[0].tolist(), "intercept": float(full.intercept_[0]),
                 "label": "mule_by_day at week 26", "fitted_on_months": list(MONTHS)}

    df, _ = base.load_table(out, MONTHS, WEEKS, adopted=True)
    df["app_score"] = df["account_id"].map(pd.Series(oof, index=lin.index)).astype("float32")
    settings = {**DEFAULT_PARAMS, "random_state": seed, **(params or {})}
    inputs = INPUT_SETS[input_set]
    model = lgb.LGBMClassifier(n_jobs=-1, **settings).fit(df[inputs], df["mule_by_day"])

    folder = model_dir(out, name)
    os.makedirs(folder, exist_ok=True)
    model.booster_.save_model(os.path.join(folder, "lgbm.txt"))
    with open(os.path.join(folder, "app_logreg.json"), "w") as f:
        json.dump(app_model, f)
    gain = model.booster_.feature_importance("gain")
    imp = pd.DataFrame({"feature": inputs, "gain": gain, "share": gain / gain.sum()}).sort_values("gain", ascending=False)
    store = manifest.check(out, WEEKLY)
    m = {"name": name, "data_folder": out, "input_set": input_set, "inputs": inputs, "n_inputs": len(inputs), "train_months": list(MONTHS),
         "weeks": list(WEEKS), "label": "mule_by_day; account-weeks after closure dropped",
         "rows": int(len(df)), "mule_rows": int(df["mule_by_day"].sum()), "accounts": int(df["account_id"].nunique()),
         "lightgbm_params": settings, "params_source": "default" if not params else "file",
         "app_score": "LogisticRegression(class_weight='balanced', max_iter=2000) on accounts_linear; out of fold "
                      "(5 folds) for training rows, fitted on all training accounts for new ones",
         "run_manifest_sha256": manifest._sha256(os.path.join(out, "run_manifest.json")),
         "data_identity": data_identity(out), "input_fingerprints": fingerprint.fingerprints(out),
         "store_code_sha256": store.get("code_sha256"),
         "preprocess_manifest_sha256": manifest._sha256(os.path.join(out, "features", "preprocess_manifest.json")),
         "git_commit": manifest._git("rev-parse", "HEAD"),
         "git_uncommitted_changes": bool(manifest._git("status", "--porcelain", "--untracked-files=no")),
         "lightgbm": lgb.__version__, "machine": machine(), "seconds": round(time.time() - t0)}
    with open(os.path.join(folder, "manifest.json"), "w") as f:
        json.dump(m, f, indent=2)
    report = shared_dir(out, name, report_root)
    os.makedirs(report, exist_ok=True)
    with open(os.path.join(report, "manifest.json"), "w") as f:
        json.dump(m, f, indent=2)
    imp.to_csv(os.path.join(report, "importance.csv"), index=False)
    return m


def data_problems(out: str, folder: str, m: dict) -> list[str]:
    """Is the local data the data this model was trained on? By content (option B, 29 Oct 2026), so a model file
    trained on another machine can be used here:
      1. the same run_manifest.json file (same machine): yes
      2. the manifest's input fingerprints (models trained since 29 Oct 2026) equal the local ones: yes
      3. a verified.json from `python -m models verify` (a shared model trained before): its fingerprints, taken
         when the model reproduced a committed reference run here, equal the local ones: yes"""
    if m["run_manifest_sha256"] == manifest._sha256(os.path.join(out, "run_manifest.json")):
        return []
    ref = m.get("input_fingerprints")
    how = "fingerprints in the model's manifest"
    if ref is None and os.path.exists(os.path.join(folder, VERIFIED)):
        v = json.load(open(os.path.join(folder, VERIFIED)))
        if v.get("model_files_sha256") != model_files_sha256(folder):
            return [f"{VERIFIED} was written for other model files: verify again"]
        ref, how = v["input_fingerprints"], VERIFIED
    if ref is None:
        return ["the data run changed (a model from another machine without fingerprints: check it once with "
                f"`python -m models verify --out {out} --model {os.path.basename(folder)} --reference <results run>`)"]
    diff = fingerprint.differences(ref, fingerprint.fingerprints(out))
    if diff:
        return [f"the local data differs from the training data ({how}): {', '.join(diff)}. If the data is the "
                "same and only the DuckDB version differs, `python -m models verify` accepts the model by "
                "reproducing a committed run of it"]
    return []


def load(out: str = amldata.DEFAULT_OUT, name: str = "frozen", check_data: bool = True) -> tuple:
    """(booster, app model dict, manifest), after checking the model was trained on this data run and store."""
    import lightgbm as lgb
    folder = find_model_dir(out, name)
    if not os.path.exists(os.path.join(folder, "lgbm.txt")):
        raise FileNotFoundError(f"{folder} has no model - run `python -m models train --out {out}`")
    m = json.load(open(os.path.join(folder, "manifest.json")))
    problems = data_problems(out, folder, m) if check_data else []
    if m["store_code_sha256"] != manifest.check(out, WEEKLY).get("code_sha256"):
        problems.append("the feature store code changed")
    if m["inputs"] != INPUT_SETS[m.get("input_set", "frozen")]:
        problems.append(f"the {m.get('input_set', 'frozen')} input list changed")
    if problems:
        raise ValueError(f"model {folder} is stale: {'; '.join(problems)}. Retrain.")
    booster = lgb.Booster(model_file=os.path.join(folder, "lgbm.txt"))
    return booster, json.load(open(os.path.join(folder, "app_logreg.json"))), m


def predict(out: str, months, weeks: tuple[int, int], name: str = "frozen", check_data: bool = True) -> pd.DataFrame:
    """account_id, weeks_since_open, score (the model's raw probability) for every account-week of the accounts
    opened in `months` (public inputs only; the caller decides which weeks are open)."""
    booster, app_model, man = load(out, name, check_data)
    trained = set(man["train_months"]) & {int(m) for m in months}
    if trained:
        raise ValueError(f"the model was trained on months {sorted(trained)}; score other months")
    x = feature_table(out, months, weeks)
    if "app_score" in man["inputs"]:
        x["app_score"] = x["account_id"].map(app_scores_for(out, app_model, x["account_id"].unique())).astype("float32")
    x["score"] = booster.predict(x[man["inputs"]])
    return x[["account_id", "weeks_since_open", "score"]]


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m models train", description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=amldata.DEFAULT_OUT)
    ap.add_argument("--name", default="frozen", help="model folder name under <out>/models/")
    ap.add_argument("--params", default=None, help="JSON file of LightGBM settings (tuning step 2), merged over defaults")
    ap.add_argument("--inputs", default="frozen", choices=list(INPUT_SETS),
                    help="frozen = the 38 inputs (default); activity = without app_score (onboarding-value yardstick)")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args(argv)
    params = json.load(open(a.params)) if a.params else None
    if params:
        for k in ("n_estimators", "num_leaves", "min_child_samples", "subsample_freq", "max_depth"):
            if k in params:
                params[k] = int(params[k])
    m = train(a.out, a.name, params, a.seed, input_set=a.inputs)
    print(f"trained {m['name']} on {m['rows']:,} account-weeks ({m['mule_rows']:,} mule weeks), "
          f"{m['n_inputs']} inputs, {m['seconds']}s -> {model_dir(a.out, a.name)}")


if __name__ == "__main__":
    main()
