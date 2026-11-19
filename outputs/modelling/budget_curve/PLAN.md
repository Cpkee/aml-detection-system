# Rules vs model at several alert volumes (plan, 19 Nov 2026)

**Status: plan accepted 19 Nov 2026 (Kee Chee Pheng); committed before any run.** Report-appendix work only. It
changes nothing in the simulator, the six rules, the data, the feature store or the model of record, and it never
reads test months 6–7. The headline result (final test, 2 Nov 2026) stays as it is.

## Why

The rules R3–R6 were tuned to one threshold scale (1.516), and every comparison so far uses the alert count that
scale produces. A reader can fairly ask: "did the model win only because of that one threshold?" This is a
sensitivity check on the benchmark: move the rules' threshold, and see whether the model still catches more at
the alert volume each threshold gives.

## The question

On month 5 (78 mules by week 26), if the bank had set R3–R6 looser or stricter, how many mules do the rules catch,
and how many does the model of record catch when it may flag the same number of accounts each week?

## Method

1. **Scales, fixed here before any run:** 1.0, 1.149, 1.32, **1.516** (the scale of record), 1.741, 2.0, 2.639.
   Seven of the 26 values of the tuning grid (`rules.tune_scales`, as rounded in `_internal/rules_tuning.csv`).
   Below 1.0 the alerts explode (about 89,000 at 0.871 on the whole data, against 3,635 at 1.516); above about 2.6
   only the fixed cash rules R1 and R2 are left. No scale is added or dropped after seeing results.
2. **Rules at each scale:** the simulator's own `sim.rules.weekly_features`, `hits` and `decide` are re-applied to
   the finished `data/v1_full` transactions, so the 28-day pause, review and confirmation work exactly as in the
   data. No data is regenerated.
3. **Self-check:** at 1.516 the re-applied rules must reproduce the cohort's alerts in `aml_alerts` exactly, and the
   whole comparison must equal the committed month-5 dry run (`results/v1_full/month5_dryrun_avg5_v2`: rules 16,
   model 65 of 78). The run stops if it does not.
4. **Model at the same budget:** for each scale, the rules' alerts per week since opening on the cohort are the
   model's weekly budget (permanent flags, as in the harness, `evaluation.score`). The model of record
   `frozen_tuned_avg5` is not retrained; its committed month-5 scores are reused
   (`data/v1_full/scores/frozen_tuned_avg5_m5.parquet`).
5. **Measures**, weeks 0–26, the harness's own label (`mule_at`: fake accounts from opening, real customers from
   their start): flags, mules caught and precision for the rules and the model, and the lead
   (model caught − rules caught) / mules.
6. **Output:** `outputs/modelling/budget_curve/v1_full/curve.csv`, `curve.png` (alerts on the x-axis, mules caught
   on the y-axis) and `report.md`. Code: `src/evaluation/budget_curve.py` (`python -m evaluation.budget_curve`;
   refuses months 6–7), test `tests/test_budget_curve.py`.

## How we will read it (fixed in advance)

The lead **holds across thresholds** if the model catches more mules than the rules at every one of the seven
scales. All seven are reported, including any where the gap narrows. Month 5 has 78 mules, so small differences
between neighbouring scales are noise; only the direction at each scale is read.

## Limits

- **Closures are approximate.** The data was built with accounts closed at scale 1.516. At another scale different
  accounts would have been closed and their later activity removed; this re-scoring ignores that. An account the
  data closed has no activity afterwards, so at stricter scales the rules lose a few later chances (a small bias
  against the rules at the strict end).
- **The model's pool.** The model may flag an account only while it is open both in the data and under the scale
  being scored (the earlier of the two closures). At 1.516 this is exactly the harness's rule.
- **The model was trained in the 1.516 world** and is not re-fitted for each budget.
- **R1 and R2 never move** (they are fixed limits), so the rules' line flattens at the strict end by construction.
- **Month 5 only.** It is the calibration month and has been looked at many times. Months 6–7 are not read; scoring
  this there would be a counted re-test (decision 2 Nov 2026) and is a separate team decision.
