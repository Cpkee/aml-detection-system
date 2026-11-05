# Robustness checks: results

Plan: `PLAN.md` (approved and committed 5 Nov 2026, before any run). Numbers: `summary.csv`
(`python -m evaluation.robustness seed__44 ...`). Weeks 0–26, months 6–7 of each dataset, scored once.

## Run 1: `seed__44` (chance yardstick), 5 Nov 2026

Data unchanged since 7 Oct (no rebuild needed): 10 of 10 checks pass, 3,542 alerts, 93.1% false alarms, as in its
committed `summary.json`. Store built (19.0M account-weeks), cleaned tables fitted on its own months 0–4, recipe of
`frozen_tuned_avg5` trained as `robust_avg5` (38 inputs, LightGBM seeds 1–5, application score seed 42, tuned
settings unchanged; 4.45M account-weeks), months 6–7 scored once (`results/seed__44/final_test/`, locked).

| Data | Mules | Model caught | Rules caught | Lead | 95% interval | Precision model / rules |
|:--|--:|--:|--:|--:|:--|:--|
| v1_full (headline) | 163 | 120 | 50 | 0.43 | 0.35–0.52 | 0.43 / 0.19 |
| seed__44 | 145 | 114 | 35 | 0.54 | 0.47–0.62 | 0.47 / 0.15 |

By type (model / rules): fakes 104 / 32 of 132, witting 8 / 2 of 10, unwitting 2 / 1 of 3 (v1_full: 109 / 46 of
147, 8 / 3 of 11, 3 / 1 of 5). Median days from start to first flag: 9 / 9 (v1_full 8 / 9). Weeks 0–77: model 136,
rules 46 of 176.

**Chance band (fixed by the plan):** headline lead 0.43 ± 0.12 (the gap to seed 44, above the ±0.05 minimum) =
**0.31 to 0.55**. A scenario *holds* if its lead is at least 0.31.

What this means: with nothing changed but the random seed, the lead moved by 0.12. The model's catch rate barely
moved (0.74 -> 0.79); most of the change is the rules catching fewer (0.31 -> 0.24). The band is therefore wide, and
only a scenario that cuts the lead below 0.31 will read as *shrinks* or *fails*. This is stated, not changed: the
rule was fixed before the run.

## Run 2: `in_window_mix__1` (53% fakes instead of 73%), 5 Nov 2026

Rebuilt from its `run_manifest.json` (same `--set`, seed and BAF file): 10 of 10 checks pass, and every number in
its committed `summary.json` is identical (3,587 alerts, 173 closures). Store, cleaned tables and `robust_avg5` as in
run 1 (4.45M account-weeks, 6,248 mule weeks vs 8,497 in seed 44: fewer fakes means fewer mule weeks from opening).

| Data | Mules | Model caught | Rules caught | Lead | 95% interval | Precision model / rules | Verdict |
|:--|--:|--:|--:|--:|:--|:--|:--|
| in_window_mix__1 | 124 | 99 | 30 | 0.56 | 0.46–0.66 | 0.38 / 0.12 | **holds** |

By type (model / rules): fakes 81 / 24 of 103, witting 9 / 4 of 11, unwitting 9 / 2 of 10. Median days from start:
7 / 9. Weeks 0–77: model 136, rules 43 of 164 (real customers 48 / 15 of 61).

What this means: with a quarter fewer fakes the lead does not shrink. The model still catches about 4 in 5 fakes, and
it also catches most real-customer mules (18 of 21 by week 26), where the rules catch 6. So the advantage does not
rest only on recognising fake accounts at opening. Caution: 21 real-customer mules is a small number.
