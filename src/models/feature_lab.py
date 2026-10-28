"""Feature lab: does a group of candidate features improve the model? One trial, logged in a ledger.

    PYTHONPATH=src python -m models.feature_lab --out data/v1 --groups lag1 roll2 roll4 running_max --name item1
    PYTHONPATH=src python -m models.feature_lab --out data/v1_full --groups roll2 --name item1-confirm --views app activity

Candidates come from src/features/candidates.py. For each trial:
  screen    each new feature's AUC against started_by_day (launderers whose laundering has begun vs normal
            accounts) at weeks 8, 12 and 26, with a 95% bootstrap interval over launderers; 0.5 = no signal
  model     LightGBM as in notebooks/06_lgbm_tuning.ipynb (same rows, folds, seed and settings), refitted with each
            group added and with all groups together. Views: 'app' = activity + application score (the model the
            team tunes, decision 26 Oct 2026; default), 'activity' = store features + weeks_since_open only.
            The baseline includes the adopted candidates (features.candidates.ADOPTED, since 26 Oct 2026: the
            roll4 group), so a new group must beat the model as it now stands
  measures  weekly_recall, the tuning measure (decision 26 Oct 2026): the share of each week's mules in that week's
            top 1% of open accounts, averaged over weeks 0-26 (recall_top_1pct of lgbm_baseline.by_week). The
            summary shows it pooled over the 3 validation months, as notebook 06 reports it, and per fold.
            Beside it: account-level PR-AUC (an account's best week) and caught_2wk, the share of launderers
            starting in weeks 0-25 who are in that week's top 1% in their start week or the next
  verdict   per measure, from the 3 folds: 'better' only if all 3 improve AND the mean gain reaches NOISE; 'worse'
            if all 3 fall; else 'no clear change'. weekly_recall decides; the others are reported beside it

Only accounts opened in months 0-4 are used (the baseline's folds); month 5 and test months 6-7 are never read.
Every trial appends to outputs/modelling/feature_lab/ledger.csv, so the number of looks is on record: the more
groups are tried against the same folds, the more likely one wins by chance.

Proposal 28 Oct 2026 (pending the team; the defaults above are unchanged):
  catch_rules   permanent flags at the RULES' budget: each week since opening the model flags as many not-yet-flagged
                open accounts as the rules raised alerts that week on the same month's accounts (~6 a week per
                validation month on v1_full, vs ~300 for the top 1%). catch_w = share of the accounts that are mules
                at week w that the model has flagged by week w (closed accounts stay in the denominator: if the
                model missed them, the rules caught them); catch_rules = mean of catch_w over weeks 0-26. The
                rules' own value (an account counts once alerted) is reported beside it as `rules`.
  catch_0.1pct  the same with 0.1% of open accounts per week: steadier than ~6 flags a week, still ~5x the rules
  --decide      which measure gives the deciding verdict (default weekly_recall, the 26 Oct 2026 decision)
  --placebo N   N groups of shuffled store columns (permuted across accounts within each week: no link to the
                label). Their gains are pure refit noise; noise.csv proposes NOISE = 2 x their root mean square
  special groups, not from candidates.py: app_split (the application as two scores, tuning.app_score_split, in
                place of app_score), graph_struct (features/graph_weekly.parquet, features.graph), graph_nb
                (neighbours' scores, models.graph_nb; fitted per fold)
"""
from __future__ import annotations
import argparse
import datetime
import os
import subprocess
import time

import numpy as np
import pandas as pd

import amldata
from features import candidates
from features.weekly import FEATURES as WEEKLY
from evaluation import budget as rules_budget
from models import lgbm_baseline as base
from models.tuning import app_score, app_score_split

ROOT = "outputs/modelling/feature_lab"
LEDGER = os.path.join(ROOT, "ledger.csv")
MONTHS = (0, 1, 2, 3, 4)
WEEKS = (0, 26)
SCREEN_WEEKS = (8, 12, 26)
NOISE = {"weekly_recall": 0.02,   # assumption: 2 points of recall, no measured fold noise yet; test 0.01 / 0.04
         "acc_pr_auc": 0.04,      # team plan working rule: PR-AUC differences under ~0.04 are fold noise
         "caught_2wk": 0.05,      # assumption: ~1 binomial s.e. with ~90 starts per fold on v1_full; test 0.03 / 0.08
         # proposal 28 Oct 2026, measured: 2 x root mean square gain of 5 placebo groups on v1_full (trial
         # noise-placebo5, noise.csv: 0.0123 / 0.0046). The same run measures weekly_recall 0.006, acc_pr_auc 0.008,
         # caught_2wk 0.023; the three values above are left as agreed until the team decides
         "catch_rules": 0.012,
         "catch_0.1pct": 0.005}
MAIN = "weekly_recall"
INFO = ["pre_start_recall", "start_recall", "later_recall", "first_caught_2wk"]   # where a gain comes from; no verdict
BUDGET_PCT = 0.001                # catch_0.1pct: share of open accounts flagged per week
PLACEBO_COLS = ["n_rows_wk", "n_in_wk", "money_in_wk", "money_out_wk", "n_payers_wk", "out_1h_share_wk",
                "out_24h_share_wk", "passthrough_wk"]   # 8 columns, as many as the adopted roll4 group
SPECIAL = ("app_split", "graph_struct", "graph_nb")


def auc_ci(x, y, n_boot: int = 1000, seed: int = 0) -> tuple[float, float, float]:
    """Rank AUC with a 95% bootstrap interval over positives; NaN ranks lowest (as in notebooks/01_eda_train)."""
    x, y = np.asarray(x, dtype=float), np.asarray(y).astype(bool)
    if y.sum() < 20 or (~y).sum() == 0:
        return np.nan, np.nan, np.nan
    x = np.where(np.isnan(x), -np.inf, x)
    neg, pos = np.sort(x[~y]), x[y]
    place = np.sort((np.searchsorted(neg, pos, "left") + np.searchsorted(neg, pos, "right")) / (2 * len(neg)))
    if np.all(place == place[0]):
        return place.mean(), np.nan, np.nan
    boots = np.random.default_rng(seed).choice(place, size=(n_boot, len(place))).mean(axis=1)
    return place.mean(), *np.percentile(boots, [2.5, 97.5])


def screen(out: str, df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    rows = []
    for w in SCREEN_WEEKS:
        lab = amldata.labels(out, months=MONTHS, weeks_since_open=w)[["account_id", "started_by_day"]]
        d = df[df.weeks_since_open == w].merge(lab, on="account_id", validate="1:1")
        d = d[(d.started_by_day == 1) | (d.mule_by_day == 0)]          # started launderers vs normal accounts
        for c in cols:
            auc, lo, hi = auc_ci(d[c], d.started_by_day)
            rows.append({"feature": c, "week": w, "auc": auc, "lo": lo, "hi": hi})
    return pd.DataFrame(rows)


def start_weeks(out: str) -> pd.Series:
    """Each launderer's first week with started_by_day = 1 inside WEEKS (accounts not started there are absent)."""
    started = [amldata.labels(out, months=MONTHS, weeks_since_open=w).query("started_by_day == 1")
               [["account_id"]].assign(w=w) for w in range(WEEKS[0], WEEKS[1] + 1)]
    return pd.concat(started).groupby("account_id")["w"].min()


def app_scores(out: str, seed: int, split: bool = False, other_months=None) -> dict[int, pd.DataFrame]:
    """Per fold, the application score of every training and validation account, exactly as notebook 06 builds it:
    a logistic regression on accounts_linear, label 'mule by the end of week 26', out of fold for training accounts.
    Column app_score; split=True adds app_score_fake and app_score_real (tuning.app_score_split). other_months:
    opening months to score as well with the model fitted on the training months (no label of theirs is read;
    models.graph_nb scores neighbours in any month)."""
    lin = pd.read_parquet(os.path.join(out, "features", "accounts_linear.parquet"))
    keep = set(MONTHS) | set(other_months or ())
    lin = lin[lin["open_month"].isin(keep)].set_index("account_id")
    cols = [c for c in lin.columns if c != "open_month"]
    lab = {w: amldata.labels(out, months=MONTHS, weeks_since_open=w).set_index("account_id")["mule_by_day"]
           for w in (0, WEEKS[1])}
    scores = {}
    for f, (train_m, valid_m) in enumerate(base.FOLDS, start=1):
        tr, va = lin.index[lin.open_month.isin(train_m)], lin.index[~lin.open_month.isin(train_m)]
        if other_months is None:
            va = lin.index[lin.open_month == valid_m]
        s_tr, s_va = app_score(lin.loc[tr, cols], lab[WEEKS[1]].loc[tr], lin.loc[va, cols], seed=seed)
        d = {"app_score": np.concatenate([s_tr, s_va])}
        if split:
            for name, (a, b) in app_score_split(lin.loc[tr, cols], lab[0].loc[tr], lab[WEEKS[1]].loc[tr],
                                                lin.loc[va, cols], seed=seed).items():
                d[f"app_score_{name}"] = np.concatenate([a, b])
        scores[f] = pd.DataFrame(d, index=tr.append(va))
    return scores


def weekly_top1(valid: pd.DataFrame, score: np.ndarray) -> pd.DataFrame:
    """valid with the score and a flag for the top 1% of each week (k and tie order as in lgbm_baseline.top_k)."""
    v = valid.assign(score=score)
    rank = v.groupby("weeks_since_open")["score"].rank(ascending=False, method="first")
    k = v.groupby("weeks_since_open")["score"].transform(lambda s: max(1, int(round(0.01 * len(s)))))
    return v.assign(flag=rank <= k)


def weekly_recall(v: pd.DataFrame) -> float:
    r = [g.loc[g.mule_by_day == 1, "flag"].mean() for _, g in v.groupby("weeks_since_open") if g.mule_by_day.any()]
    return float(np.mean(r))


def caught_2wk(v: pd.DataFrame, start: pd.Series) -> float:
    """Share of launderers starting in weeks 0-25 who are flagged in their start week or the next."""
    st = start[(start <= 25) & start.index.isin(v["account_id"])]
    s = v["account_id"].map(st)
    near = v[(v.weeks_since_open >= s) & (v.weeks_since_open <= s + 1)]
    return float(near.groupby("account_id")["flag"].any().reindex(st.index, fill_value=False).mean())


def phase_recall(v: pd.DataFrame, start: pd.Series) -> dict[str, float]:
    """Share of mule weeks flagged, split by weeks since the account's laundering start: before it (fake accounts,
    mules from opening), the start week and the next, and 2+ weeks after. weekly_recall mixes all three; a gain only
    in 'later' re-flags mules a permanent flag would already have caught."""
    m = v[v.mule_by_day == 1]
    since = m["weeks_since_open"] - m["account_id"].map(start)
    return {"pre_start_recall": float(m.loc[since < 0, "flag"].mean()),
            "start_recall": float(m.loc[since.between(0, 1), "flag"].mean()),
            "later_recall": float(m.loc[since >= 2, "flag"].mean())}


def first_flag_weeks(v: pd.DataFrame, k: dict[int, int] | None = None) -> pd.Series:
    """Week of each account's first flag when a flag is permanent (decision 9 Oct 2026): every week the top 1% of
    that week's open accounts is flagged from the accounts not flagged before (same k as weekly_top1). k: flags per
    week since opening instead (a week missing from k gets none)."""
    first = {}
    for w, g in v.groupby("weeks_since_open"):
        n = max(1, int(round(0.01 * len(g)))) if k is None else int(k.get(int(w), 0))
        pool = g[~g["account_id"].isin(first.keys())]
        for a in pool.sort_values("score", ascending=False, kind="stable")["account_id"].head(n):
            first[a] = w
    return pd.Series(first, dtype=float)


def pct_budget(v: pd.DataFrame, pct: float = BUDGET_PCT) -> dict[int, int]:
    """Flags per week = pct of that week's open accounts (at least 1)."""
    return {int(w): max(1, int(round(pct * n))) for w, n in v.groupby("weeks_since_open").size().items()}


def catch_curve(first: pd.Series, mules: pd.DataFrame) -> pd.Series:
    """Per week w: share of the accounts that are mules at week w (account_id, weeks_since_open rows, closed accounts
    included) flagged at week w or earlier. A flag before the laundering start counts: it is earlier still."""
    flagged_by = mules["account_id"].map(first)
    hit = (flagged_by <= mules["weeks_since_open"]).astype(float)
    return hit.groupby(mules["weeks_since_open"].to_numpy()).mean()


def catch_mean(first: pd.Series, mules: pd.DataFrame) -> float:
    """The proposed earliness measure: catch_curve averaged over the weeks that hold mules."""
    return float(catch_curve(first, mules).mean())


def catch_boot_sd(first: pd.Series, mules: pd.DataFrame, n_boot: int = 500, seed: int = 0) -> float:
    """Spread of catch_mean when the month's mule accounts are resampled (flags held fixed)."""
    hit = (mules["account_id"].map(first) <= mules["weeks_since_open"]).astype(float)
    t = mules.assign(hit=hit, one=1.0)
    is_mule = t.pivot_table(index="account_id", columns="weeks_since_open", values="one", fill_value=0.0)
    hits = t.pivot_table(index="account_id", columns="weeks_since_open", values="hit", fill_value=0.0)
    hits = hits.reindex_like(is_mule).to_numpy()
    is_mule = is_mule.to_numpy()
    n = len(is_mule)
    weights = np.random.default_rng(seed).multinomial(n, np.full(n, 1 / n), size=n_boot)   # accounts drawn
    with np.errstate(invalid="ignore", divide="ignore"):
        per_week = (weights @ hits) / (weights @ is_mule)
    return float(np.std(np.nanmean(per_week, axis=1)))


def real_mules_caught(first: pd.Series, mules: pd.DataFrame, prof: pd.Series) -> dict:
    """Real-customer mules of the month flagged by the end of the horizon, per hidden type ('caught/all')."""
    ids = pd.Index(mules["account_id"].unique())
    t = prof.reindex(ids).fillna("unknown")
    return {f"rules_budget_{typ}": f"{int(ids[t == typ].isin(first.index).sum())}/{int((t == typ).sum())}"
            for typ in ("fake", "witting", "unwitting")}


def mule_weeks(out: str) -> pd.DataFrame:
    """account_id, open_month, weeks_since_open of every mule account-week in WEEKS, closed accounts included."""
    rows = []
    for w in range(WEEKS[0], WEEKS[1] + 1):
        y = amldata.labels(out, months=MONTHS, weeks_since_open=w)
        rows.append(y.loc[y.mule_by_day == 1, ["account_id", "open_month"]].assign(weeks_since_open=w))
    return pd.concat(rows, ignore_index=True)


def rules_context(out: str) -> dict:
    """What the catch measures need besides the model's scores: mule weeks, the rules' budget and first alerts."""
    b = rules_budget.weekly_budget(out, MONTHS, WEEKS)
    return {"mules": mule_weeks(out),
            "budget": {m: dict(zip(g["week"], g["alerts"])) for m, g in b.groupby("open_month")},
            "rules_first": rules_budget.rules_first_alert(out, MONTHS, WEEKS)}


def catch_measures(v: pd.DataFrame, valid_m: int, ctx: dict) -> dict:
    """catch_rules / catch_0.1pct for the model, and the rules' own catch_mean, on one validation month."""
    mules = ctx["mules"][ctx["mules"].open_month == valid_m]
    first_r = first_flag_weeks(v, ctx["budget"][valid_m])
    first_p = first_flag_weeks(v, pct_budget(v))
    return {"catch_rules": catch_mean(first_r, mules), "catch_0.1pct": catch_mean(first_p, mules),
            "rules": catch_mean(ctx["rules_first"], mules),
            "flags_rules_budget": len(first_r), "flags_0.1pct": len(first_p),
            "_curves": {"catch_rules": catch_curve(first_r, mules), "catch_0.1pct": catch_curve(first_p, mules),
                        "rules": catch_curve(ctx["rules_first"], mules)},
            "_first": {"catch_rules": first_r, "catch_0.1pct": first_p}, "_mules": mules}


def first_caught_2wk(v: pd.DataFrame, start: pd.Series) -> float:
    """caught_2wk with permanent flags: share of launderers starting in weeks 0-25 whose first flag comes no later
    than the week after their start (a flag before the start counts: it is earlier still)."""
    st = start[(start <= 25) & start.index.isin(v["account_id"])]
    first = first_flag_weeks(v).reindex(st.index)
    return float((first <= st + 1).mean())


def with_fold_columns(df: pd.DataFrame, f: int, scores=None, fold_extra=None) -> pd.DataFrame:
    """df plus fold f's account-level scores (app_score, ...) and fold-fitted account-week columns (graph_nb)."""
    d = df
    if scores:
        s = scores[f]
        s = s.to_frame("app_score") if isinstance(s, pd.Series) else s
        d = d.assign(**{c: d["account_id"].map(s[c]) for c in s.columns})
    if fold_extra:
        d = d.merge(fold_extra[f], on=base.KEY, how="left", validate="1:1")
    return d


def fit_folds(df, cols, prof, start, scores, seed, ctx=None, fold_extra=None,
              curves=None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Per-fold measures and the out-of-fold scores of one variant. ctx (rules_context) adds the catch measures;
    curves, a list, collects their per-week curves."""
    import lightgbm as lgb
    rows, oof = [], []
    for f, (train_m, valid_m) in enumerate(base.FOLDS, start=1):
        d = with_fold_columns(df, f, scores, fold_extra)
        train, valid = d[d.open_month.isin(train_m)], d[d.open_month == valid_m]
        model = lgb.LGBMClassifier(class_weight="balanced", random_state=seed, n_jobs=-1, verbose=-1,
                                   deterministic=True, force_row_wise=True)
        model.fit(train[cols], train["mule_by_day"])
        score = model.predict_proba(valid[cols])[:, 1]
        m = base.evaluate(valid, score, prof)
        v = weekly_top1(valid, score)
        row = {"fold": f, "weekly_recall": weekly_recall(v), "acc_pr_auc": m["acc_pr_auc"],
               "caught_2wk": caught_2wk(v, start), **phase_recall(v, start),
               "first_caught_2wk": first_caught_2wk(v, start), "top_1%_witting": m["top_1%_witting"],
               "top_1%_unwitting": m["top_1%_unwitting"]}
        if ctx is not None:
            c = catch_measures(v, valid_m, ctx)
            row |= {k: x for k, x in c.items() if not k.startswith("_")}
            row |= {f"{k}_boot_sd": catch_boot_sd(c["_first"][k], c["_mules"]) for k in c["_first"]}
            row |= real_mules_caught(c["_first"]["catch_rules"], c["_mules"], prof)
            if curves is not None:
                curves.append(pd.DataFrame(c["_curves"]).rename_axis("week").reset_index().assign(fold=f))
        rows.append(row)
        oof.append(valid[base.KEY + ["mule_by_day"]].assign(score=score))
    return pd.DataFrame(rows), pd.concat(oof, ignore_index=True)


def pooled_weekly_recall(oof: pd.DataFrame) -> float:
    """The tuning measure as notebook 06 reports it: by_week on the pooled validation months, mean over weeks."""
    return float(base.by_week(oof.assign(view="v"))["recall_top_1pct"].mean())


def verdict(delta: pd.Series, noise: float | None) -> str:
    if noise is None:
        return "no noise level yet"
    if (delta > 0).all() and delta.mean() >= noise:
        return "better"
    if (delta < 0).all():
        return "worse"
    return "no clear change"


def git_commit() -> str:
    try:
        c = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "src"], capture_output=True, text=True).stdout.strip()
        return c + ("-dirty" if dirty else "")
    except OSError:
        return "unknown"


def append_ledger(rows: pd.DataFrame):
    """Add rows to the ledger. Earlier rows are kept byte for byte: a new column is added to the header and earlier
    lines only gain empty fields at their end (their values are never re-read and re-written)."""
    if not os.path.exists(LEDGER):
        rows.to_csv(LEDGER, index=False)
        return
    old = list(pd.read_csv(LEDGER, nrows=0).columns)
    extra = [c for c in rows.columns if c not in old]
    if extra:
        import csv
        with open(LEDGER, newline="") as f:
            text = f.read()
        lines = text.rstrip("\n").split("\n")
        with open(LEDGER, newline="") as f:
            n_records = sum(1 for _ in csv.reader(f))
        if n_records != len(lines):
            raise RuntimeError("a ledger record spans several lines; add the new columns by hand")
        pad = "," * len(extra)
        head = pd.DataFrame(columns=old + extra).to_csv(index=False).rstrip("\n")
        with open(LEDGER, "w", newline="") as f:
            f.write("\n".join([head] + [line + pad for line in lines[1:]]) + "\n")
        old += extra
    rows.reindex(columns=old).to_csv(LEDGER, mode="a", header=False, index=False)


def add_placebo(df: pd.DataFrame, i: int) -> tuple[pd.DataFrame, list[str]]:
    """Placebo group i: PLACEBO_COLS with their values shuffled across accounts inside each week. Same weekly
    distributions as real features, no link to any account's label: any gain from it is refit noise."""
    rng = np.random.default_rng(1000 + i)
    cols = {}
    for c in PLACEBO_COLS:
        x = df[c].to_numpy(dtype="float32")
        out = np.empty_like(x)
        for pos in df.groupby("weeks_since_open").indices.values():
            out[pos] = x[rng.permutation(pos)]
        cols[f"placebo{i}_{c}"] = out
    return pd.concat([df, pd.DataFrame(cols, index=df.index)], axis=1), list(cols)


def noise_table(summary: pd.DataFrame, res: pd.DataFrame) -> pd.DataFrame:
    """From placebo variants: root mean square of their mean gains per measure, and the proposed NOISE = 2 x that.
    Beside it, the bootstrap spread of the baseline's catch measures (mule accounts resampled, mean of folds)."""
    p = summary[summary.variant.str.startswith("+placebo")]
    rows = []
    for m in list(NOISE) + INFO:
        d = p[f"d_{m}"].astype(float)
        rows.append({"measure": m, "placebos": len(d), "mean_gain": d.mean(), "rms_gain": float(np.sqrt((d ** 2).mean())),
                     "max_abs_gain": d.abs().max(), "proposed_noise": 2 * float(np.sqrt((d ** 2).mean())),
                     "current_noise": NOISE.get(m)})
    t = pd.DataFrame(rows)
    b = res[res.variant == "baseline"]
    for m in ("catch_rules", "catch_0.1pct"):
        if f"{m}_boot_sd" in b:
            t.loc[t.measure == m, "baseline_boot_sd_per_fold"] = b[f"{m}_boot_sd"].mean()
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m models.feature_lab", description=__doc__.split("\n")[0])
    ap.add_argument("--out", default="data/v1", help="data folder (default data/v1, the fast 50k run)")
    ap.add_argument("--groups", nargs="*", default=[],
                    help=f"candidate groups: {', '.join(candidates.GROUPS)}; special: {', '.join(SPECIAL)}")
    ap.add_argument("--name", required=True, help="trial name, used for the report folder and the ledger")
    ap.add_argument("--views", nargs="+", default=["app"], choices=["app", "activity"],
                    help="app = activity + application score (default, the tuned model); activity = store features only")
    ap.add_argument("--hypothesis", default="", help="one line: what laundering behaviour the group should catch")
    ap.add_argument("--baseline", default="adopted", choices=["adopted", "store"],
                    help="adopted = store + features.candidates.ADOPTED (default); store = store features only, to "
                         "re-check an adopted group")
    ap.add_argument("--decide", default=MAIN, choices=list(NOISE),
                    help=f"measure whose verdict decides (default {MAIN}; proposal 28 Oct 2026: catch_rules)")
    ap.add_argument("--placebo", type=int, default=0, help="add N placebo groups (shuffled columns) to measure noise")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--scratch", default=None,
                    help="development run: write the report to this folder and do not touch the ledger")
    a = ap.parse_args(argv)
    adopted = candidates.ADOPTED if a.baseline == "adopted" else []
    unknown = set(a.groups) - set(candidates.GROUPS) - set(SPECIAL)
    if unknown:
        raise SystemExit(f"unknown groups {sorted(unknown)}")
    if not a.groups and not a.placebo:
        raise SystemExit("give --groups and/or --placebo N")
    if "app_split" in a.groups and a.views != ["app"]:
        raise SystemExit("app_split replaces app_score, so it needs --views app")

    t0 = time.time()
    data = os.path.basename(os.path.normpath(a.out))
    report = os.path.join(a.scratch, a.name) if a.scratch else os.path.join(ROOT, data, a.name)
    os.makedirs(report, exist_ok=True)
    df, _ = base.load_table(a.out, MONTHS, WEEKS, adopted=bool(adopted))
    df = df.sort_values(candidates.KEY, kind="stable").reset_index(drop=True)
    df, names = candidates.add(df, [g for g in a.groups if g in candidates.GROUPS])
    groups = list(a.groups)
    for i in range(1, a.placebo + 1):
        df, names[f"placebo{i}"] = add_placebo(df, i)
        groups.append(f"placebo{i}")
    drops = {g: [] for g in groups}
    if "app_split" in groups:
        names["app_split"], drops["app_split"] = ["app_score_fake", "app_score_real"], ["app_score"]
    if "graph_struct" in groups:
        from features import graph
        g = graph.load(a.out, WEEKS, months=MONTHS)
        df = df.merge(g, on=base.KEY, how="left", validate="1:1")
        names["graph_struct"] = graph.FEATURES
    fold_extra = None
    if "graph_nb" in groups:
        from models import graph_nb
        fold_extra = graph_nb.load_or_build(a.out, a.seed)
        names["graph_nb"] = graph_nb.FEATURES
    prof, start = base.profiles(a.out, MONTHS), start_weeks(a.out)
    scores = app_scores(a.out, a.seed, split="app_split" in groups) if "app" in a.views else None
    ctx = rules_context(a.out)
    new = [c for g in groups for c in names[g]]
    print(f"{len(df):,} account-weeks, {len(new)} candidate columns ({time.time() - t0:.0f}s)")

    shown = with_fold_columns(df, len(base.FOLDS), scores, fold_extra)     # fold-fitted columns: last fold's values
    scr = screen(a.out, shown, new)
    del shown
    adds = {f"+{g}": (names[g], drops[g]) for g in groups}
    if len(groups) > 1 and not a.placebo:
        adds["+all"] = (new, [c for g in groups for c in drops[g]])
    res, summary, curves = [], [], []
    for view in a.views:
        base_cols = WEEKLY + adopted + ["weeks_since_open"] + (["app_score"] if view == "app" else [])
        b = None
        for v, (extra, drop) in {"baseline": ([], []), **adds}.items():
            cols = [c for c in base_cols if c not in drop] + extra
            cv = []
            r, oof = fit_folds(df, cols, prof, start, scores if view == "app" else None, a.seed, ctx, fold_extra, cv)
            r = r.assign(view=view, variant=v, n_features=len(cols))
            res.append(r)
            curves.append(pd.concat(cv).assign(view=view, variant=v))
            row = {"view": view, "variant": v, "n_features": len(cols),
                   "weekly_recall_pooled": pooled_weekly_recall(oof), "rules": r["rules"].mean()}
            b = r.set_index("fold") if b is None else b
            for m in list(NOISE) + INFO:
                d = r.set_index("fold")[m] - b[m]
                row |= {m: r[m].mean(), f"d_{m}": d.mean(), f"d_{m}_folds": " / ".join(f"{x:+.3f}" for x in d)}
                if m in NOISE:
                    row[f"{m}_verdict"] = verdict(d, NOISE[m]) if v != "baseline" else ""
            summary.append(row)
            print(f"{view:8s} {v:14s} weekly recall {row['weekly_recall_pooled']:.3f} (pooled)  "
                  f"catch@rules {row['catch_rules']:.3f} (rules {row['rules']:.3f})  catch@0.1% "
                  f"{row['catch_0.1pct']:.3f}  PR-AUC {row['acc_pr_auc']:.3f}  ({time.time() - t0:.0f}s)")
    res, summary = pd.concat(res, ignore_index=True), pd.DataFrame(summary)
    curves = pd.concat(curves, ignore_index=True)

    res.to_csv(os.path.join(report, "folds.csv"), index=False)
    scr.to_csv(os.path.join(report, "screen.csv"), index=False)
    summary.to_csv(os.path.join(report, "summary.csv"), index=False)
    curves.to_csv(os.path.join(report, "catch_curves.csv"), index=False)
    noise = noise_table(summary, res) if a.placebo else None
    if noise is not None:
        noise.to_csv(os.path.join(report, "noise.csv"), index=False)
    write_report(report, a, data, summary, scr, curves, noise, groups)
    stamp = {"date": datetime.date.today().isoformat(), "commit": git_commit(), "data": data, "trial": a.name,
             "hypothesis": a.hypothesis, "seed": a.seed,
             "baseline": f"store + {candidates.ADOPTED_GROUP}" if adopted else "store", "decides": a.decide}
    if a.scratch:
        print(f"-> {report} (scratch run, ledger untouched)  ({time.time() - t0:.0f}s)")
        return
    led = summary[summary.variant != "baseline"].assign(**stamp)
    led["features"] = led.variant.map(lambda v: " ".join(adds[v][0]) + "".join(f" -{c}" for c in adds[v][1]))
    append_ledger(led[list(stamp) + [c for c in led.columns if c not in stamp]])
    print(f"-> {report}, ledger {LEDGER}  ({time.time() - t0:.0f}s)")


def write_report(report, a, data, summary, scr, curves, noise, groups):
    wide = scr.assign(v=scr.apply(lambda r: f"{r.auc:.3f} ({r.lo:.2f}-{r.hi:.2f})", axis=1)) \
              .pivot(index="feature", columns="week", values="v")
    wide.columns = [f"week {w}" for w in wide.columns]
    lines = [f"# Feature lab: {a.name}", "",
             f"data `{data}`, groups {', '.join(groups)}, views {', '.join(a.views)}, seed {a.seed}, "
             f"decides `{a.decide}`, commit {git_commit()}", "", f"Hypothesis: {a.hypothesis or '(none given)'}", ""]
    order = [a.decide] + [m for m in NOISE if m != a.decide]
    for view in a.views:
        s = summary[summary.view == view]
        lines += [f"## View `{view}`: baseline vs baseline + candidates (3 folds, months 0-4)", ""]
        for m in order:
            cols = ["variant", "n_features"] + (["weekly_recall_pooled"] if m == "weekly_recall" else []) + \
                   (["rules"] if m.startswith("catch") else []) + [m, f"d_{m}", f"d_{m}_folds", f"{m}_verdict"]
            lines += [f"### {m}{' (decides)' if m == a.decide else ''}", "",
                      s[cols].to_markdown(index=False, floatfmt=".3f"), ""]
        cols = ["variant"] + [c for m in INFO for c in (m, f"d_{m}_folds")]
        lines += ["### Where the gain comes from (no verdict)", "", s[cols].to_markdown(index=False, floatfmt=".3f"),
                  "", "Share of mule weeks in the weekly top 1%, by weeks since the account's laundering start: "
                  "pre_start (fake accounts before they launder), start (start week and the next), later (2+ weeks "
                  "after). first_caught_2wk: as caught_2wk, but a flag is permanent (decision 9 Oct 2026), so a mule "
                  "flagged earlier counts as caught and later re-flags count for nothing.", ""]
        c = curves[curves.view == view].groupby(["variant", "week"], sort=False)[["catch_rules", "catch_0.1pct", "rules"]] \
            .mean().reset_index()
        c = c[c.week.isin([0, 2, 4, 8, 12, 17, 26])]
        t = c.pivot(index="variant", columns="week", values="catch_rules")
        t.loc["rules (alerts)"] = c[c.variant == "baseline"].set_index("week")["rules"]
        lines += ["### Catch curve at the rules' budget (mean of 3 folds)", "",
                  "Share of the accounts that are mules at week w already flagged by week w; flags are permanent and "
                  "the model gets as many flags each week as the rules raised alerts.", "",
                  t.to_markdown(floatfmt=".3f"), ""]
    if noise is not None:
        lines += ["## Noise from placebo groups", "",
                  "Each placebo group is 8 store columns shuffled across accounts within each week, so it carries no "
                  "information about any account. The gain it brings is what refitting alone moves a measure by. "
                  "proposed_noise = 2 x root mean square of the placebo gains (mean of 3 folds).", "",
                  noise.to_markdown(index=False, floatfmt=".4f"), ""]
    lines += [
        "- weekly_recall: share of each week's mules in that week's top 1% of open accounts, mean over weeks 0-26 "
        "(the tuning measure, decision 26 Oct 2026). `weekly_recall_pooled` pools the 3 validation months per week, "
        "as notebook 06 reports it; the per-fold column and the verdict use each fold alone.",
        "- catch_rules (proposal 28 Oct 2026): flags are permanent and limited to the rules' alert count in each week "
        "since opening on the same month's accounts; per week w the share of mule accounts (closed ones included) "
        "flagged by week w, averaged over weeks 0-26. `rules` = the same for the rules' own alerts. catch_0.1pct: "
        "the same with 0.1% of open accounts per week. Real-customer mules caught at the rules' budget per fold "
        "(`rules_budget_witting` / `_unwitting`) are in folds.csv.",
        "- acc_pr_auc: account-level PR-AUC (an account's best week). caught_2wk: launderers starting in weeks 0-25 "
        "flagged in their start week or the next.",
        f"- verdict 'better' = all 3 folds improve and the mean gain is at least the noise level: "
        f"{', '.join(f'{m} {n}' for m, n in NOISE.items())} (PR-AUC: team rule; the others: assumptions or placebo "
        "measurements, see the comments in feature_lab.py).",
        "- Real-customer mules in the account-level top 1% per fold (witting / unwitting) are in folds.csv.",
        "", "## Screen: AUC vs started launderers (95% interval over launderers)", "", wide.to_markdown(), ""]
    with open(os.path.join(report, "report.md"), "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
