"""Phase 5, step 2: calibrate a trained model on month 5 (due 4 Nov 2026).

    PYTHONPATH=src python -m models calibrate --out data/v1_full --model frozen_tuned

The model is trained with class_weight='balanced', so its raw scores are far too high as probabilities (a mule
account-week is ~0.2% of rows, but the model's average score is far higher). Calibration maps each raw score to the
chance that the account is a mule by the end of that week, fitted on month 5, which no model has seen.

  rows      every open account-week of the accounts opened in month 5, weeks 0-26 since opening (closed weeks
            dropped, as in training); label mule_by_day, read through amldata.labels (month 5 is allowed)
  methods   isotonic regression (a step function that never goes down) and Platt scaling (a logistic regression on
            the log-odds of the raw score)
  checked   out of fold: month 5's accounts are split into 5 groups, each scored by a mapping fitted on the other 4,
            so the reported Brier score, log loss and reliability table come from rows the mapping did not see
  chosen    the method with the lower out-of-fold Brier score (rule fixed before the run), then refitted on all of
            month 5 and saved to <out>/models/<model>/calibration.json (readable: thresholds or coefficients)

What it does NOT change: the harness ranks accounts week by week, and both mappings keep the order of the raw scores
(isotonic can make ties, so the harness keeps ranking on the raw score). Caught counts, precision at the rules' budget
and every result in outputs/modelling/results/ stay as they are. Calibration is for reporting probabilities, the
expected precision of a flag, and comparisons at other prevalences (professor's comment 1).
Report: outputs/modelling/models/<data>/<model>/calibration/ (report.md, reliability.csv, 01_reliability.png).
"""
from __future__ import annotations
import argparse
import json
import os

import numpy as np
import pandas as pd

import amldata
from models import train as trainer

MONTH = 5
WEEKS = (0, 26)
N_GROUPS = 5
EPS = 1e-6


def rows(out: str, model: str) -> pd.DataFrame:
    """Open account-weeks of month 5 with the raw score and the label."""
    s = trainer.predict(out, (MONTH,), WEEKS, model)
    lab = pd.concat([amldata.labels(out, months=(MONTH,), weeks_since_open=w)
                     [["account_id", "mule_by_day", "open_by_day"]].assign(weeks_since_open=w)
                     for w in range(WEEKS[0], WEEKS[1] + 1)], ignore_index=True)
    d = s.merge(lab, on=["account_id", "weeks_since_open"], how="inner", validate="1:1")
    return d[d["open_by_day"] == 1].drop(columns="open_by_day").reset_index(drop=True)


def _logit(p):
    p = np.clip(np.asarray(p, dtype=float), EPS, 1 - EPS)
    return np.log(p / (1 - p))


def fit(method: str, score, y) -> dict:
    """A calibration mapping as plain numbers (JSON-ready)."""
    score, y = np.asarray(score, dtype=float), np.asarray(y).astype(int)
    if method == "isotonic":
        from sklearn.isotonic import IsotonicRegression
        iso = IsotonicRegression(y_min=0.0, y_max=1.0, out_of_bounds="clip").fit(score, y)
        return {"method": "isotonic", "x": iso.X_thresholds_.tolist(), "y": iso.y_thresholds_.tolist()}
    if method == "platt":
        from sklearn.linear_model import LogisticRegression
        lr = LogisticRegression(C=1e6, max_iter=1000).fit(_logit(score).reshape(-1, 1), y)
        return {"method": "platt", "a": float(lr.coef_[0, 0]), "b": float(lr.intercept_[0])}
    raise ValueError(f"unknown method {method}")


def apply(mapping: dict, score) -> np.ndarray:
    score = np.asarray(score, dtype=float)
    if mapping["method"] == "isotonic":
        return np.interp(score, mapping["x"], mapping["y"])
    return 1 / (1 + np.exp(-(mapping["a"] * _logit(score) + mapping["b"])))


def out_of_fold(d: pd.DataFrame, method: str, seed: int = 0) -> np.ndarray:
    ids = d["account_id"].unique()
    group = pd.Series(np.random.default_rng(seed).permutation(len(ids)) % N_GROUPS, index=ids)
    g = d["account_id"].map(group).to_numpy()
    p = np.empty(len(d))
    for k in range(N_GROUPS):
        p[g == k] = apply(fit(method, d.loc[g != k, "score"], d.loc[g != k, "mule_by_day"]), d.loc[g == k, "score"])
    return p


def quality(y, p) -> dict:
    y, p = np.asarray(y, dtype=float), np.clip(np.asarray(p, dtype=float), EPS, 1 - EPS)
    return {"brier": float(np.mean((p - y) ** 2)), "log_loss": float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))),
            "mean_predicted": float(p.mean()), "observed_rate": float(y.mean())}


def reliability(y, p, edges=(0, 1e-4, 1e-3, 3e-3, 1e-2, 3e-2, 0.1, 0.3, 1.0001)) -> pd.DataFrame:
    """Predicted vs observed mule rate in bins of the predicted probability (log-spaced: the base rate is ~0.2%)."""
    d = pd.DataFrame({"y": y, "p": p})
    d["bin"] = pd.cut(d["p"], list(edges), right=False)
    t = d.groupby("bin", observed=True).agg(rows=("y", "size"), mules=("y", "sum"), predicted=("p", "mean"),
                                            observed=("y", "mean")).reset_index()
    t["bin"] = t["bin"].astype(str)
    return t


def calibrate(out: str = amldata.DEFAULT_OUT, model: str = "frozen", report_root: str = trainer.REPORT_ROOT,
              seed: int = 0) -> dict:
    d = rows(out, model)
    y = d["mule_by_day"].to_numpy()
    res = {"raw": quality(y, d["score"])}
    oof = {}
    for method in ("isotonic", "platt"):
        oof[method] = out_of_fold(d, method, seed)
        res[method] = quality(y, oof[method])
    chosen = min(("isotonic", "platt"), key=lambda m: res[m]["brier"])
    mapping = fit(chosen, d["score"], y)
    mapping |= {"fitted_on": f"month {MONTH}, open account-weeks {WEEKS[0]}-{WEEKS[1]}", "rows": int(len(d)),
                "mule_rows": int(y.sum()), "out_of_fold": res, "chosen_by": "lower out-of-fold Brier score",
                "machine": trainer.machine()}
    folder = trainer.find_model_dir(out, model)
    with open(os.path.join(folder, "calibration.json"), "w") as f:
        json.dump(mapping, f)

    report = os.path.join(trainer.shared_dir(out, model, report_root), "calibration")
    os.makedirs(report, exist_ok=True)
    rel = pd.concat([reliability(y, d["score"]).assign(scores="raw")] +
                    [reliability(y, oof[m]).assign(scores=f"{m} (out of fold)") for m in oof], ignore_index=True)
    rel.to_csv(os.path.join(report, "reliability.csv"), index=False)
    _figure(report, rel)
    q = pd.DataFrame(res).T.rename_axis("scores")
    lines = [f"# Calibration of `{model}` on month {MONTH}", "",
             f"{len(d):,} open account-weeks of month {MONTH} (weeks {WEEKS[0]}-{WEEKS[1]}), {int(y.sum()):,} of them mule "
             f"weeks ({y.mean():.3%}). Chosen: **{chosen}** (lower out-of-fold Brier score), refitted on all of "
             f"month {MONTH} -> `{folder}/calibration.json`. Machine: "
             f"`{json.dumps(trainer.machine())}`.", "",
             "## Quality (calibrated rows scored out of fold: 5 groups of month-5 accounts)", "",
             q.to_markdown(floatfmt=".5f"), "",
             "Brier score and log loss: lower is better. mean_predicted should be close to observed_rate.", "",
             "## Reliability: predicted vs observed mule rate by predicted-probability bin", "",
             rel.to_markdown(index=False, floatfmt=".5f"), "", "![reliability](01_reliability.png)", "",
             "Calibration keeps the order of the scores, so the harness's caught counts and precision at the rules' "
             "budget do not change; it turns scores into probabilities for reporting."]
    with open(os.path.join(report, "report.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    return mapping


def _figure(report, rel):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    colors = {"raw": "#888888", "isotonic (out of fold)": "#2a78d6", "platt (out of fold)": "#1baf7a"}
    fig, ax = plt.subplots(figsize=(5.5, 5))
    for name, g in rel.groupby("scores", sort=False):
        g = g[g["rows"] >= 50]
        ax.plot(g["predicted"].clip(lower=1e-5), g["observed"].clip(lower=1e-5), marker="o", lw=2,
                color=colors.get(name), label=name)
    ax.plot([1e-5, 1], [1e-5, 1], ls="--", color="#bbbbbb", lw=1, label="perfect")
    ax.set(xscale="log", yscale="log", xlabel="predicted probability (bin mean)", ylabel="observed mule rate",
           title=f"Reliability on month {MONTH} (bins with 50+ rows)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(report, "01_reliability.png"), dpi=130)
    plt.close(fig)


def load(out: str, model: str) -> dict:
    path = os.path.join(trainer.find_model_dir(out, model), "calibration.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found - run `python -m models calibrate --out {out} --model {model}`")
    return json.load(open(path))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m models calibrate", description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=amldata.DEFAULT_OUT)
    ap.add_argument("--model", default="frozen_tuned", help="model name (default frozen_tuned, the model of record)")
    a = ap.parse_args(argv)
    m = calibrate(a.out, a.model)
    print(f"{a.model}: chose {m['method']}; out-of-fold Brier raw {m['out_of_fold']['raw']['brier']:.5f}, "
          f"isotonic {m['out_of_fold']['isotonic']['brier']:.5f}, platt {m['out_of_fold']['platt']['brier']:.5f}")


if __name__ == "__main__":
    main()
