"""Rules vs model at several alert volumes: a sensitivity check on the benchmark's threshold (19 Nov 2026).

    PYTHONPATH=src python -m evaluation.budget_curve --out data/v1_full        # month 5, model of record

Plan and limits: outputs/modelling/budget_curve/PLAN.md (committed before any run). The bank's rules R3-R6 were
tuned to one threshold scale. Here the simulator's own rule code (sim.rules) is re-applied to the finished
transactions at seven scales fixed in the plan. At each scale the rules' alerts per week since opening become the
model's weekly budget, and both are scored by the harness (evaluation.score: permanent flags, the same label).
At the scale of record the re-applied rules must reproduce `aml_alerts` on the cohort exactly, or the run stops.

Approximate by design: the data was built with closures at the scale of record, and no data is regenerated. The
model may flag an account only while it is open both in the data and under the scale being scored.
This is scoring code, so it may read hidden files; nothing it reads goes back into a model. Months 0-5 only.
"""
from __future__ import annotations
import argparse
import json
import os

import numpy as np
import pandas as pd

import amldata
from evaluation import budget as rules_budget
from evaluation import score as sc
from sim import rules as sim_rules
from sim import run as sim_run
from sim.config import Cfg

SCALES = (1.0, 1.149, 1.32, 1.516, 1.741, 2.0, 2.639)     # fixed in the plan; 1.516 = the scale of record
HORIZON = 26
MODEL = "frozen_tuned_avg5"
REPORT = "outputs/modelling/budget_curve"
MODEL_COLOR, RULES_COLOR, MUTED, GRID = "#2a78d6", "#eb6834", "#898781", "#e1e0d9"


def rule_features(out: str, months) -> tuple[pd.DataFrame, pd.DataFrame]:
    """The six rules' weekly inputs for the cohort (sim.rules.weekly_features on the finished transactions), and
    the accounts table in file order (the rules number accounts by their row)."""
    m = rules_budget._months(months)                       # refuses test months 6-7
    p = sim_run._paths(out)
    acc = pd.read_parquet(p["accounts"], columns=["account_id", "open_month", "open_day"])
    tx = (f"(SELECT x.* FROM read_parquet('{p['tx']}') x SEMI JOIN (SELECT account_id FROM "
          f"read_parquet('{p['accounts']}') WHERE open_month IN ({m})) c USING (account_id))")
    f = sim_rules.weekly_features(sim_run._con(), tx, p["accounts"], Cfg.for_run(out))
    cohort = np.flatnonzero(acc["open_month"].isin([int(x) for x in m.split(", ")]).to_numpy())
    return f[f["acct"].isin(cohort)].reset_index(drop=True), acc


def alerts_at(f: pd.DataFrame, acc: pd.DataFrame, out: str, scale: float) -> tuple[pd.DataFrame, pd.Series]:
    """The rules' alerts (account_id, alert_day) and closures (account_id -> exit day) at one threshold scale."""
    cfg = Cfg.for_run(out)
    start, is_l = sim_run._truth_arrays(sim_run._paths(out))
    al, exits = sim_rules.decide(sim_rules.hits(f, cfg, scale), cfg, start, is_l, cfg.get("meta.seed"))
    ids = acc["account_id"].to_numpy()
    alerts = pd.DataFrame({"account_id": ids[al["acct"].to_numpy()], "alert_day": al["alert_day"].to_numpy()})
    return alerts, pd.Series({ids[a]: d for a, d in exits.items()}, dtype=float)


def truth_at(truth: pd.DataFrame, alerts: pd.DataFrame, exits: pd.Series) -> tuple[pd.DataFrame, dict[int, int]]:
    """The cohort as the harness would see it under these alerts: first alert day, closure (the earlier of the
    data's and this scale's), and the weekly budget (alerts per week since opening; twice alerted counts twice)."""
    t = truth.copy()
    t["first_alert_day"] = t["account_id"].map(alerts.groupby("account_id")["alert_day"].min())
    t["exit_day"] = np.fmin(t["exit_day"].to_numpy(dtype=float), t["account_id"].map(exits).to_numpy(dtype=float))
    week = (alerts["alert_day"] - alerts["account_id"].map(truth.set_index("account_id")["open_day"])) // 7
    return t, {int(w): int(n) for w, n in week.value_counts().items()}


def curve(out: str, months, scores: pd.DataFrame, scales=SCALES, horizon: int = HORIZON) -> pd.DataFrame:
    """One row per scale: budget, flags, mules caught and precision for the rules and the model, and the lead."""
    truth = sc.cohort_truth(out, months)
    f, acc = rule_features(out, months)
    record = json.load(open(os.path.join(out, "_internal/rules_state.json")))["scale"]
    rows = []
    for s in scales:
        alerts, exits = alerts_at(f, acc, out, s)
        if s == record:
            check_reproduces(out, months, alerts)
        t, k = truth_at(truth, alerts, exits)
        res = sc.evaluate_horizon(t, sc.open_rows(scores, t), k, horizon)
        by = res["summary"].set_index("policy")
        h = res["h2h"]
        rows.append({"scale": s, "scale_of_record": s == record, "budget": res["budget"], "mules": h["mules"],
                     "rules_flagged": int(by.loc["rules", "flagged"]), "rules_caught": int(by.loc["rules", "caught"]),
                     "rules_precision": by.loc["rules", "precision"],
                     "model_flagged": int(by.loc["model", "flagged"]), "model_caught": int(by.loc["model", "caught"]),
                     "model_precision": by.loc["model", "precision"],
                     "lead": (by.loc["model", "caught"] - by.loc["rules", "caught"]) / max(h["mules"], 1),
                     "both": h["both"], "model_only": h["model_only"], "rules_only": h["rules_only"]})
    return pd.DataFrame(rows)


def check_reproduces(out: str, months, alerts: pd.DataFrame) -> None:
    """At the scale of record the re-applied rules must give exactly the cohort's alerts in the data."""
    m = rules_budget._months(months)
    real = amldata.evaluation(out).execute(f"""SELECT x.account_id, x.alert_day FROM aml_alerts x
        JOIN accounts a USING (account_id) WHERE a.open_month IN ({m})""").df()
    key = ["account_id", "alert_day"]
    a = alerts[key].sort_values(key).reset_index(drop=True).astype({"alert_day": "int64"})
    b = real[key].sort_values(key).reset_index(drop=True).astype({"alert_day": "int64"})
    if not a.equals(b):
        raise SystemExit(f"re-applied rules at the scale of record give {len(a)} alerts, the data has {len(b)} "
                         "(or different ones): the rule code or settings differ from the run's; nothing written")


def chart(df: pd.DataFrame, path: str, title: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=200)
    mules = int(df["mules"].iloc[0])
    ax.axhline(mules, color=MUTED, lw=1, ls=(0, (2, 3)))
    ax.text(df["budget"].min(), mules + 1, f"all {mules} mules", color=MUTED, fontsize=8, ha="left", va="bottom")
    for col, color, name in (("model_caught", MODEL_COLOR, "Model of record"), ("rules_caught", RULES_COLOR, "Rules")):
        ax.plot(df["budget"], df[col], color=color, lw=2, marker="o", ms=6, mec="white", mew=1.5, label=name)
        last = df.loc[df["budget"].idxmax()]
        ax.annotate(name, (last["budget"], last[col]), xytext=(8, 0), textcoords="offset points",
                    color="#0b0b0b", fontsize=9, va="center")
    rec = df[df["scale_of_record"]]
    if len(rec):
        r = rec.iloc[0]
        ax.plot([r["budget"]] * 2, [r["rules_caught"], r["model_caught"]], color=MUTED, lw=1)
        ax.annotate(f"scale of record ({r['scale']})", (r["budget"], (r["rules_caught"] + r["model_caught"]) / 2),
                    xytext=(6, 0), textcoords="offset points", color="#52514e", fontsize=8, va="center")
    ax.set_xscale("log")
    ax.set_xticks([30, 100, 300, 1000])
    ax.set_xticklabels(["30", "100", "300", "1,000"])
    ax.minorticks_off()
    ax.set_xlim(df["budget"].min() * 0.85, df["budget"].max() * 1.9)
    ax.set_ylim(0, mules * 1.1)
    ax.set_xlabel("Alerts on the cohort in weeks 0-26 = accounts the model may flag (log scale; one point per rule threshold)", fontsize=9)
    ax.set_ylabel("Mules caught", fontsize=9)
    ax.set_title(title, fontsize=10, loc="left", color="#0b0b0b")
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors="#52514e", labelsize=8)
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def write_report(df: pd.DataFrame, folder: str, out: str, months, source: str) -> None:
    holds = bool((df["model_caught"] > df["rules_caught"]).all())
    t = df.assign(**{c: df[c].round(3) for c in ("rules_precision", "model_precision", "lead")})
    t = t.drop(columns=["scale_of_record"])
    lines = [
        "# Rules vs model at several alert volumes", "",
        f"Data `{out}`, cohort months {list(months)}, weeks 0-{HORIZON}, model scores `{source}`. "
        "Plan and limits: `../PLAN.md`. Made by `python -m evaluation.budget_curve`.", "",
        f"**Reading (fixed in the plan): the lead {'holds' if holds else 'does NOT hold'} across thresholds** "
        f"(the model catches more mules than the rules at {int((df['model_caught'] > df['rules_caught']).sum())} "
        f"of {len(df)} scales).", "",
        "`budget` = the rules' alerts on the cohort in weeks 0-26 at that scale = the accounts the model may flag. "
        "`lead` = (model caught - rules caught) / mules.", "",
        t.to_markdown(index=False), "", "![curve](curve.png)", "",
        "Approximate: closures in the data are those of the scale of record; see the plan's limits.", ""]
    with open(os.path.join(folder, "report.md"), "w") as fh:
        fh.write("\n".join(lines))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=amldata.DEFAULT_OUT)
    ap.add_argument("--months", nargs="+", type=int, default=[5])
    ap.add_argument("--scores", default=None, help=f"scores file (default <out>/scores/{MODEL}_m<months>.parquet)")
    a = ap.parse_args(argv)
    months = tuple(a.months)
    rules_budget._months(months)                           # refuses test months before anything is read
    source = a.scores or os.path.join(a.out, "scores", f"{MODEL}_m{''.join(map(str, months))}.parquet")
    truth = sc.cohort_truth(a.out, months)
    scores = sc.load_scores(source, truth["account_id"], HORIZON)
    df = curve(a.out, months, scores)
    folder = os.path.join(REPORT, os.path.basename(os.path.normpath(a.out)))
    os.makedirs(folder, exist_ok=True)
    df.to_csv(os.path.join(folder, "curve.csv"), index=False)
    chart(df, os.path.join(folder, "curve.png"), f"Mules caught at each rule threshold, cohort opened in month {', '.join(map(str, months))}")
    write_report(df, folder, a.out, months, source)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
