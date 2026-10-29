"""Two harness runs on the same cohort, side by side (e.g. the value of onboarding information, professor's comment 2).

    PYTHONPATH=src python -m evaluation.compare --out data/v1_full \
        --a month5_dryrun_frozen_tuned --b month5_dryrun_activity_tuned --name month5_onboarding_value

Both runs must score the same cohort months with the same horizons, so the rules' budget, the accounts and the
transactions are identical and only the models differ. For the onboarding question, a = the frozen model (activity +
application score) and b = the same model without the application score (`python -m models train --inputs activity`
with the same settings): the gap is what the application data adds, week by week since opening.
Writes outputs/modelling/results/<data>/<name>/report.md + by_week_w<h>.csv.
"""
from __future__ import annotations
import argparse
import json
import os

import pandas as pd

import amldata
from evaluation.score import RESULTS, PROFILES

SHOW = ["flagged", "caught", "mules", "recall", "precision", "catch_mean", "median_days_from_start",
        "flagged_before_start"] + [f"caught_{p}" for p in PROFILES]


def compare(out: str, a: str, b: str, name: str) -> str:
    data = os.path.basename(os.path.normpath(out))
    sa, sb = (json.load(open(os.path.join(RESULTS, data, r, "settings.json"))) for r in (a, b))
    for k in ("cohort_months", "horizons", "budget_per_horizon", "cohort_accounts"):
        if sa[k] != sb[k]:
            raise ValueError(f"{a} and {b} differ in {k}: {sa[k]} vs {sb[k]}; compare runs on the same cohort")
    report = os.path.join(RESULTS, data, name)
    os.makedirs(report, exist_ok=True)
    lines = [f"# {a} (a) vs {b} (b), cohort month(s) {', '.join(map(str, sa['cohort_months']))}", "",
             f"Models: a = `{sa['model']}`, b = `{sb['model']}`. Same accounts, transactions and rules' budget; "
             "flags are permanent, at the rules' weekly alert count.", ""]
    for h in sa["horizons"]:
        x, y = (pd.read_csv(os.path.join(RESULTS, data, r, f"summary_w{h}.csv")).set_index("policy") for r in (a, b))
        t = pd.DataFrame({"a": x.loc["model", SHOW], "b": y.loc["model", SHOW], "rules": x.loc["rules", SHOW]})
        t = t.apply(lambda col: col.map(lambda v: f"{v:.3f}" if isinstance(v, float) and not float(v).is_integer()
                                        else (f"{v:.0f}" if isinstance(v, (int, float)) and v == v else str(v))))
        wa, wb = (pd.read_csv(os.path.join(RESULTS, data, r, f"weekly_w{h}.csv")) for r in (a, b))
        wk = pd.DataFrame({"week": wa["week"], "mules": wa["mules"], "catch_a": wa["catch_model"],
                           "catch_b": wb["catch_model"], "catch_rules": wa["catch_rules"]})
        wk["a_minus_b"] = wk["catch_a"] - wk["catch_b"]
        wk.to_csv(os.path.join(report, f"by_week_w{h}.csv"), index=False)
        pick = wk[wk.week.isin([0, 2, 4, 8, 10, 12, 14, 17, 20, 26, 52, 77])].round(3)
        lines += [f"## Weeks 0-{h}", "", t.to_markdown(), "",
                  "### Share of each week's mules already flagged", "", pick.to_markdown(index=False), "",
                  f"Weeks where a is ahead: {int((wk.a_minus_b > 0).sum())}, behind: {int((wk.a_minus_b < 0).sum())}, "
                  f"level: {int((wk.a_minus_b == 0).sum())} (of {len(wk)}).", ""]
    with open(os.path.join(report, "report.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m evaluation.compare", description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=amldata.DEFAULT_OUT)
    ap.add_argument("--a", required=True, help="first harness run folder (e.g. the frozen model)")
    ap.add_argument("--b", required=True, help="second harness run folder (e.g. the activity-only model)")
    ap.add_argument("--name", required=True, help="report folder name")
    a = ap.parse_args(argv)
    r = compare(a.out, a.a, a.b, a.name)
    print(open(os.path.join(r, "report.md")).read())


if __name__ == "__main__":
    main()
