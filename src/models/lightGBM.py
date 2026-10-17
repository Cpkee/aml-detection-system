"""Phase 4, first pass: a plain LightGBM on the account-week table (no tuning yet).

    PYTHONPATH=src python -m models.lgbm_baseline                      # data/v1_full, weeks 0-26, 3 temporal folds
    PYTHONPATH=src python -m models.lgbm_baseline --out data/v1        # 50k, quick
    PYTHONPATH=src python -m models.lgbm_baseline --drop weeks_since_open

What it does
  rows      one per account per week since opening (weeks 0-26 by default), accounts opened in months 0-4 only
  label     mule_by_day at the end of that week (fake accounts from opening, real customers from their start)
  dropped   account-weeks after the bank closed the account (open_by_day = 0), as agreed for training
  folds     expanding window by opening month: train 0-1 -> validate 2, train 0-2 -> 3, train 0-3 -> 4
            (an account is in one month only, so its weeks never sit on both sides; month 5 stays for
            calibration, months 6-7 stay closed)
  inputs    application = 35 cleaned BAF columns (accounts_tree.parquet: 29 columns + 6 missing flags)
            activity    = 28 weekly features (features/weekly.parquet) + weeks_since_open
  views     application only / activity only / combined, same rows, same settings
  model     LightGBM with default settings except class weights ('balanced') and a fixed seed

Metrics per fold and view: ROC-AUC, PR-AUC, and precision / recall / F1 at three cut-offs (score >= 0.5, the
best-F1 threshold on that fold, the top 1% of accounts). Account level = an account's highest weekly score in
the horizon against whether it was ever a mule in the horizon.

Outputs (outputs/modelling/models/<data folder>/lgbm_baseline/): report.md, metrics_by_fold.csv,
oof_by_week.csv, importance.csv and 5 figures. Labels come only through amldata; no hidden file is read.
"""
from __future__ import annotations
import argparse
import json
import os
import time

import numpy as np
import pandas as pd

import amldata
from features import manifest
from features.weekly import FEATURES as WEEKLY

REPORT_ROOT = "outputs/modelling/models"
KEY = ["account_id", "weeks_since_open"]
FOLDS = [((0, 1), 2), ((0, 1, 2), 3), ((0, 1, 2, 3), 4)]
COLORS = {"application": "#eb6834", "activity": "#2a78d6", "combined": "#1baf7a"}   # validated categorical slots


# ---------------------------------------------------------------- data
def load_table(out: str, months: tuple[int, ...], weeks: tuple[int, int]) -> tuple[pd.DataFrame, list[str]]:
    """Account-week rows for accounts opened in `months`: application + weekly features + label."""
    tree_path = os.path.join(out, "features", "accounts_tree.parquet")
    if not os.path.exists(tree_path):
        raise FileNotFoundError(f"{tree_path} not found - run `python -m features preprocess --out {out}` first")
    app = pd.read_parquet(tree_path)
    app = app[app["open_month"].isin(months)].reset_index(drop=True)
    app_cols = [c for c in app.columns if c not in ("account_id", "open_month")]

    manifest.check(out, WEEKLY, weeks)            # refuses a stale or missing store
    con = amldata.loaders._connect()
    con.register("keep", app[["account_id"]])
    wk = con.execute(f"""
        SELECT w.* FROM read_parquet('{os.path.join(out, 'features', 'weekly.parquet')}') w
        JOIN keep USING (account_id)
        WHERE w.weeks_since_open BETWEEN {weeks[0]} AND {weeks[1]}""").df()
    for c in WEEKLY:
        wk[c] = wk[c].astype("float32")

    lab = []
    for w in range(weeks[0], weeks[1] + 1):       # label at the end of each account's own week w
        y = amldata.labels(out, months=months, weeks_since_open=w)
        lab.append(y[["account_id", "open_month", "mule_by_day", "open_by_day"]].assign(weeks_since_open=w))
    lab = pd.concat(lab, ignore_index=True)

    df = wk.merge(lab, on=KEY, how="inner", validate="1:1").merge(
        app.drop(columns="open_month"), on="account_id", how="left", validate="m:1")
    df = df[df["open_by_day"] == 1].drop(columns="open_by_day").reset_index(drop=True)
    return df, app_cols


def profiles(out: str, months: tuple[int, ...]) -> pd.Series:
    """Hidden launderer type (fake / witting / unwitting) for the evaluation breakdown only, never a feature."""
    p = amldata.labels(out, months=months, profile=True)
    return p.set_index("account_id")["profile"]


# ---------------------------------------------------------------- metrics
def prf(y: np.ndarray, flag: np.ndarray) -> dict:
    tp = int((flag & (y == 1)).sum())
    n_flag, n_pos = int(flag.sum()), int(y.sum())
    p = tp / n_flag if n_flag else 0.0
    r = tp / n_pos if n_pos else 0.0
    return {"flagged": n_flag, "tp": tp, "precision": p, "recall": r, "f1": 2 * p * r / (p + r) if p + r else 0.0}


def best_f1(y: np.ndarray, s: np.ndarray) -> dict:
    from sklearn.metrics import precision_recall_curve
    p, r, t = precision_recall_curve(y, s)
    f = np.where(p + r > 0, 2 * p * r / np.maximum(p + r, 1e-12), 0)[:-1]
    i = int(np.argmax(f))
    return {"threshold": float(t[i]), **prf(y, s >= t[i])}


def top_k(y: np.ndarray, s: np.ndarray, pct: float) -> dict:
    k = max(1, int(round(pct * len(s))))
    flag = np.zeros(len(s), dtype=bool)
    flag[np.argsort(-s, kind="stable")[:k]] = True
    return {"k": k, **prf(y, flag)}


def accounts(valid: pd.DataFrame, score: np.ndarray) -> pd.DataFrame:
    return valid.assign(score=score).groupby("account_id").agg(y=("mule_by_day", "max"), s=("score", "max"))


def evaluate(valid: pd.DataFrame, score: np.ndarray, prof: pd.Series) -> dict:
    from sklearn.metrics import average_precision_score, roc_auc_score
    y = valid["mule_by_day"].to_numpy()
    acc = accounts(valid, score)
    ya, sa = acc["y"].to_numpy(), acc["s"].to_numpy()
    m = {"rows": len(y), "row_mules": int(y.sum()), "row_base_rate": float(y.mean()),
         "row_roc_auc": float(roc_auc_score(y, score)), "row_pr_auc": float(average_precision_score(y, score)),
         "accounts": len(acc), "account_mules": int(ya.sum()),
         "acc_roc_auc": float(roc_auc_score(ya, sa)), "acc_pr_auc": float(average_precision_score(ya, sa))}
    for tag, d in {"acc_at_0.5": prf(ya, sa >= 0.5), "acc_best_f1": best_f1(ya, sa),
                   "acc_top_0.1%": top_k(ya, sa, 0.001), "acc_top_0.5%": top_k(ya, sa, 0.005),
                   "acc_top_1%": top_k(ya, sa, 0.01)}.items():
        for k, v in d.items():
            m[f"{tag}_{k}"] = v
    k = max(1, int(round(0.01 * len(acc))))
    top = set(acc.index[np.argsort(-sa, kind="stable")[:k]])
    t = prof.reindex(acc.index[ya == 1]).fillna("unknown")
    for typ in ("fake", "witting", "unwitting"):
        ids = t.index[t == typ]
        m[f"top_1%_{typ}"] = f"{sum(a in top for a in ids)}/{len(ids)}"
    return m


def by_week(oof: pd.DataFrame) -> pd.DataFrame:
    from sklearn.metrics import average_precision_score, roc_auc_score
    rows = []
    for (view, w), g in oof.groupby(["view", "weeks_since_open"]):
        y, s = g["mule_by_day"].to_numpy(), g["score"].to_numpy()
        r = {"view": view, "week": int(w), "accounts": len(g), "mules": int(y.sum())}
        if 0 < y.sum() < len(y):
            t1 = top_k(y, s, 0.01)
            r.update(roc_auc=roc_auc_score(y, s), pr_auc=average_precision_score(y, s),
                     precision_top_1pct=t1["precision"], recall_top_1pct=t1["recall"], f1_top_1pct=t1["f1"])
        rows.append(r)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- figures
def figures(report: str, oof: pd.DataFrame, folds: pd.DataFrame, wk: pd.DataFrame, imp: pd.DataFrame) -> list[str]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.metrics import precision_recall_curve, roc_curve
    plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                         "grid.color": "#e4e4e0", "grid.linewidth": 0.8, "font.size": 10})
    views = [v for v in COLORS if v in oof["view"].unique()]
    acc = {v: accounts(oof[oof.view == v], oof.loc[oof.view == v, "score"].to_numpy()) for v in views}
    files = []

    def save(fig, name):
        fig.tight_layout()
        fig.savefig(os.path.join(report, name), dpi=130)
        plt.close(fig)
        files.append(name)

    # 1 PR curves, account level, pooled out-of-fold
    fig, ax = plt.subplots(figsize=(6, 4.5))
    for v in views:
        p, r, _ = precision_recall_curve(acc[v]["y"], acc[v]["s"])
        auc = folds.loc[folds.view == v, "acc_pr_auc"].mean()
        ax.plot(r, p, color=COLORS[v], lw=2, label=f"{v} (PR-AUC {auc:.3f})")
    base = acc[views[0]]["y"].mean()
    ax.axhline(base, color="#888", ls="--", lw=1, label=f"chance ({base:.4f})")
    ax.set(xlabel="Recall (share of mules found)", ylabel="Precision (share of flags that are mules)",
           title="Precision-recall, account level, validation months 2-4", xlim=(0, 1), ylim=(0, 1.02))
    ax.legend(frameon=False, fontsize=9)
    save(fig, "01_pr_curve.png")

    # 2 ROC curves
    fig, ax = plt.subplots(figsize=(6, 4.5))
    for v in views:
        f, t, _ = roc_curve(acc[v]["y"], acc[v]["s"])
        ax.plot(f, t, color=COLORS[v], lw=2, label=f"{v} (ROC-AUC {folds.loc[folds.view == v, 'acc_roc_auc'].mean():.3f})")
    ax.plot([0, 1], [0, 1], color="#888", ls="--", lw=1, label="chance")
    ax.set(xlabel="False positive rate", ylabel="True positive rate (recall)", title="ROC, account level")
    ax.legend(frameon=False, fontsize=9)
    save(fig, "02_roc_curve.png")

    # 3 metrics per fold: does the result hold across folds?
    mets = [("acc_pr_auc", "PR-AUC"), ("acc_top_1%_precision", "Precision, top 1%"),
            ("acc_top_1%_recall", "Recall, top 1%"), ("acc_top_1%_f1", "F1, top 1%")]
    fig, axes = plt.subplots(1, 4, figsize=(13, 3.6), sharey=False)
    for ax, (col, lab) in zip(axes, mets):
        for i, v in enumerate(views):
            vals = folds.loc[folds.view == v, col].to_numpy()
            ax.bar(i, vals.mean(), color=COLORS[v], width=0.6)
            ax.scatter(np.full(len(vals), i), vals, color="#222", s=14, zorder=3)
        ax.set_xticks(range(len(views)), views, rotation=0, fontsize=9)
        ax.set_title(lab, fontsize=10)
    fig.suptitle("Account level, bar = mean of 3 folds, dots = each fold", fontsize=10)
    save(fig, "03_metrics_by_fold.png")

    # 4 by week since opening
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.8))
    for v in views:
        t = wk[wk.view == v].sort_values("week")
        axes[0].plot(t["week"], t["pr_auc"], color=COLORS[v], lw=2, marker="o", ms=3, label=v)
        axes[1].plot(t["week"], t["recall_top_1pct"], color=COLORS[v], lw=2, marker="o", ms=3, label=v)
    axes[0].set(xlabel="Week since opening", ylabel="PR-AUC", title="PR-AUC of that week's ranking")
    axes[1].set(xlabel="Week since opening", ylabel="Recall", title="Share of that week's mules in its top 1%")
    for ax in axes:
        ax.axvspan(8, 17, color="#f3e2c7", alpha=0.6, lw=0, label="fakes start laundering (weeks 8-17)")
    axes[0].legend(frameon=False, fontsize=9)
    save(fig, "04_by_week.png")

    # 5 feature importance, combined view (falls back to the first view run)
    v = "combined" if "combined" in views else views[0]
    t = imp[imp.view == v].groupby("feature")["share"].mean().sort_values().tail(15)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(t.index, t.values, color=COLORS[v])
    for y, val in enumerate(t.values):
        ax.text(val, y, f" {val:.1%}", va="center", fontsize=8)
    ax.set(xlabel="Share of total gain (mean of 3 folds)", title=f"Top 15 features, {v} view")
    ax.grid(axis="y", visible=False)
    save(fig, "05_importance.png")
    return files


# ---------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m models.lgbm_baseline", description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=amldata.DEFAULT_OUT, help="data folder (default data/v1_full)")
    ap.add_argument("--weeks", default="0-26", help="weeks since opening (default 0-26, the main horizon)")
    ap.add_argument("--drop", nargs="*", default=[], help="feature names to leave out, e.g. weeks_since_open")
    ap.add_argument("--views", nargs="*", default=["application", "activity", "combined"])
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--report", default=None, help="output folder (default outputs/modelling/models/<data>/lgbm_baseline)")
    a = ap.parse_args(argv)

    import lightgbm as lgb
    w = [int(x) for x in a.weeks.split("-")]
    weeks = (w[0], w[-1])
    t0 = time.time()
    df, app_cols = load_table(a.out, (0, 1, 2, 3, 4), weeks)
    prof = profiles(a.out, (0, 1, 2, 3, 4))
    print(f"{len(df):,} account-weeks ({int(df.mule_by_day.sum()):,} mule weeks) loaded in {time.time() - t0:.0f}s")

    views = {"application": app_cols, "activity": WEEKLY + ["weeks_since_open"],
             "combined": app_cols + WEEKLY + ["weeks_since_open"]}
    report = a.report or os.path.join(REPORT_ROOT, os.path.basename(os.path.normpath(a.out)), "lgbm_baseline")
    os.makedirs(report, exist_ok=True)

    fold_rows, oof, imps = [], [], []
    for f, (train_m, valid_m) in enumerate(FOLDS, start=1):
        train, valid = df[df.open_month.isin(train_m)], df[df.open_month == valid_m]
        for name in a.views:
            cols = [c for c in views[name] if c not in a.drop]
            model = lgb.LGBMClassifier(class_weight="balanced", random_state=a.seed, n_jobs=-1, verbose=-1)
            model.fit(train[cols], train["mule_by_day"])
            score = model.predict_proba(valid[cols])[:, 1]
            m = evaluate(valid, score, prof)
            fold_rows.append({"fold": f, "train_months": "-".join(map(str, train_m)), "valid_month": valid_m,
                              "view": name, "features": len(cols), **m})
            oof.append(valid[KEY + ["mule_by_day"]].assign(score=score, view=name, fold=f))
            g = model.booster_.feature_importance("gain")
            imps.append(pd.DataFrame({"feature": cols, "gain": g, "share": g / g.sum(), "view": name, "fold": f}))
            print(f"fold {f} (train {train_m} -> valid {valid_m}) {name:12s} account PR-AUC {m['acc_pr_auc']:.3f} "
                  f"top-1% P {m['acc_top_1%_precision']:.2f} R {m['acc_top_1%_recall']:.2f} F1 {m['acc_top_1%_f1']:.2f}")

    folds = pd.DataFrame(fold_rows)
    oof = pd.concat(oof, ignore_index=True)
    imp = pd.concat(imps, ignore_index=True)
    wk = by_week(oof)
    folds.to_csv(os.path.join(report, "metrics_by_fold.csv"), index=False)
    wk.to_csv(os.path.join(report, "oof_by_week.csv"), index=False)
    imp.to_csv(os.path.join(report, "importance.csv"), index=False)
    figs = figures(report, oof, folds, wk, imp)
    settings = {"data": a.out, "weeks": list(weeks), "folds": [f"{t} -> {v}" for t, v in FOLDS],
                "dropped_features": a.drop, "model": "LGBMClassifier(class_weight='balanced'), defaults otherwise",
                "seed": a.seed, "lightgbm": lgb.__version__}
    write_report(report, settings, folds, wk, imp, figs)
    print(f"-> {report}  ({time.time() - t0:.0f}s)")


def write_report(report, settings, folds, wk, imp, figs):
    show = [("acc_roc_auc", "ROC-AUC"), ("acc_pr_auc", "PR-AUC"),
            ("acc_at_0.5_precision", "P @0.5"), ("acc_at_0.5_recall", "R @0.5"), ("acc_at_0.5_f1", "F1 @0.5"),
            ("acc_best_f1_precision", "P @best"), ("acc_best_f1_recall", "R @best"), ("acc_best_f1_f1", "F1 @best"),
            ("acc_top_1%_precision", "P top 1%"), ("acc_top_1%_recall", "R top 1%"), ("acc_top_1%_f1", "F1 top 1%")]
    g = folds.groupby("view", sort=False)
    mean, lo, hi = g[[c for c, _ in show]].mean(), g[[c for c, _ in show]].min(), g[[c for c, _ in show]].max()
    lines = ["# LightGBM baseline (untuned), 3 temporal folds", "", "Settings: `" + json.dumps(settings) + "`", "",
             "## Account level, mean of 3 folds (min to max)", "",
             "| view | " + " | ".join(l for _, l in show) + " |", "|---" * (len(show) + 1) + "|"]
    for v in mean.index:
        lines.append(f"| {v} | " + " | ".join(f"{mean.loc[v, c]:.3f} ({lo.loc[v, c]:.2f}-{hi.loc[v, c]:.2f})"
                                             for c, _ in show) + " |")
    lines += ["", "- **@0.5**: flag accounts whose highest weekly score is at least 0.5. With class weights this "
              "flags far more accounts than a bank could review.",
              "- **@best**: the threshold with the highest F1 on that fold's own validation month (optimistic: "
              "the threshold is chosen on the data it is scored on).",
              "- **top 1%**: flag the 1% highest-scoring accounts, the review-budget view the project uses.", "",
              "## Each fold", "",
              folds[["fold", "train_months", "valid_month", "view", "accounts", "account_mules", "acc_pr_auc",
                     "acc_top_1%_precision", "acc_top_1%_recall", "acc_top_1%_f1", "top_1%_fake",
                     "top_1%_witting", "top_1%_unwitting"]].to_markdown(index=False, floatfmt=".3f"),
              "", "top_1%_<type> = mules of that hidden type in the top 1% / all mules of that type.", ""]
    for name in figs:
        lines += [f"![{name}]({name})", ""]
    t = wk[wk["week"].isin([0, 1, 4, 8, 12, 17, 26])][["view", "week", "mules", "pr_auc", "precision_top_1pct",
                                                       "recall_top_1pct", "f1_top_1pct"]]
    fmt = tuple(".0f" if c in ("week", "mules") else ".3f" for c in t.columns)
    lines += ["## By week since opening (pooled out-of-fold)", "", t.to_markdown(index=False, floatfmt=fmt), ""]
    for v in folds["view"].unique():
        s = imp[imp.view == v].groupby("feature")["share"].mean().sort_values(ascending=False).head(15)
        lines += [f"## Top 15 features by gain: {v}", "", s.to_frame("share").to_markdown(floatfmt=".3f"), ""]
    with open(os.path.join(report, "report.md"), "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()