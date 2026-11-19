"""Budget check (15 Nov 2026): does it matter that the model's weekly budget counts rule alerts, not accounts?

The harness lets the model flag as many accounts each week as the rules raised alerts (evaluation.budget). The rules
can alert one account more than once, while every model flag is a new account, so the model flags a few more
distinct accounts than the rules (month 5 of v1_full, weeks 0-26: 124 vs 119). This scores the same cohort twice,
with the budget as committed and with it capped at the accounts the rules alerted for the first time that week.

    PYTHONPATH=src python -m evaluation.budget_check [--out data/v1_full --months 5 --model frozen_tuned_avg5]

Months 0-5 only: test months are refused (cohort_truth without allow_test). -> outputs/modelling/results/<data>/
budget_check_m<months>/summary.csv and report.md. A check beside the harness, not a change to it.
"""
from __future__ import annotations
import argparse
import os

import pandas as pd

from evaluation import budget as rules_budget, score as sc

HORIZONS = (26, 77)
COLUMNS = ["flagged", "mules", "caught", "recall", "precision", "caught_fake", "caught_witting", "caught_unwitting",
           "median_days_from_start", "catch_mean"]


def distinct_budget(truth: pd.DataFrame, w_hi: int) -> dict[int, int]:
    """Per week since opening: the number of cohort accounts whose first rule alert falls in that week."""
    first = sc.rules_flags(truth, w_hi).astype(int).value_counts()
    return {w: int(first.get(w, 0)) for w in range(w_hi + 1)}


def run(out: str, months, model: str) -> pd.DataFrame:
    truth = sc.cohort_truth(out, months)                      # refuses test months
    scores = sc.score_cohort(out, months, (0, max(HORIZONS)), model)
    live = sc.open_rows(scores, truth)
    alerts = rules_budget.weekly_budget(out, months, (0, max(HORIZONS))).groupby("week")["alerts"].sum()
    rows = []
    for w in HORIZONS:
        budgets = {"alerts (harness)": {int(k): int(n) for k, n in alerts.items() if k <= w},
                   "distinct accounts": distinct_budget(truth, w)}
        for name, k in budgets.items():
            r = sc.evaluate_horizon(truth, live, k, w)
            s = r["summary"].set_index("policy")
            for policy in ("model", "rules"):
                rows.append({"weeks": f"0-{w}", "budget": name, "budget_total": sum(k.values()), "policy": policy,
                             **s.loc[policy, COLUMNS].to_dict(), "both": r["h2h"]["both"],
                             "model_only": r["h2h"]["model_only"], "rules_only": r["h2h"]["rules_only"]})
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="data/v1_full")
    ap.add_argument("--months", type=int, nargs="+", default=[5])
    ap.add_argument("--model", default="frozen_tuned_avg5")
    a = ap.parse_args()
    t = run(a.out, tuple(a.months), a.model)
    folder = os.path.join(sc.RESULTS, os.path.basename(os.path.normpath(a.out)),
                          "budget_check_m" + "".join(map(str, a.months)))
    os.makedirs(folder, exist_ok=True)
    t.to_csv(os.path.join(folder, "summary.csv"), index=False)
    m = t[t.policy == "model"]
    same = all(g["caught"].nunique() == 1 for _, g in m.groupby("weeks"))
    with open(os.path.join(folder, "report.md"), "w", encoding="utf-8") as f:
        f.write(f"# Budget check: rule alerts vs distinct accounts\n\n"
                f"Data `{a.out}`, cohort months {a.months}, model `{a.model}` (`python -m evaluation.budget_check`).\n"
                "The harness's budget counts rule alerts; the rules can alert one account more than once, so the "
                "model flags a few more distinct accounts than the rules. Here the model is scored again with the "
                "budget capped at the accounts the rules alerted for the first time each week. Test months are not "
                "read.\n\n"
                + m[["weeks", "budget", "budget_total", "flagged", "caught", "mules", "precision", "catch_mean"]]
                .round(3).to_markdown(index=False)
                + "\n\nRules (the same under both budgets): "
                + "; ".join(f"weeks {r.weeks}: {r.caught} of {r.mules}, precision {r.precision:.3f}"
                            for r in t[(t.policy == "rules") & (t.budget == "alerts (harness)")].itertuples())
                + ".\n\n**Reading:** "
                + ("the model catches the same number of mules under both budgets at every horizon, so counting "
                   "alerts instead of accounts does not drive the comparison on this cohort."
                   if same else "the number of mules caught differs between the two budgets: see the table.")
                + "\n")
    print(t.round(3).to_string(index=False))
    print(f"-> {folder}")


if __name__ == "__main__":
    main()
