# Robustness checks: plan (written 3 Nov 2026, before any run)

Proposal by Kee Chee Pheng. **Approved 5 Nov 2026 (Kee Chee Pheng), committed before any run.** **Question:** if one of the simulator's guesses were wrong, would our method still beat
the bank's rules? Everything below is fixed before any scenario is scored.

## What runs

Each scenario is one of the existing sensitivity datasets (`data/sensitivity/<name>/`: one `configs/sim.yaml`
setting changed to its `test` value, rules frozen at 1.516, all 10 data checks passed on 7–9 Oct).

| # | Run | Changes | Why |
|--:|:--|:--|:--|
| 1 | `seed__44` | random seed only | chance yardstick (no rebuild needed) |
| 2 | `in_window_mix__1` | 53% fakes instead of 73% | 90% of the lead is fakes; CLAUDE.md's "main threat" |
| 3 | `bursts_per_launderer__1` | repeated bursts | rules catch 76% there |
| 4 | `fake_start_days__2` | fakes start at 150–210 days | unsourced assumption; horizon effect |
| 5 | `fake_start_days__1` | fakes start at 15–45 days | little history, thin early budget |
| 6 | `out_transfer_mean__1` | £1,500 transfers | rules catch 75% there |
| 7 | `fake_age_rule__1` | young fake ages | fairness check (age pattern of false alarms) |

Run in this order; stop and report after run 1 so the chance spread is known before any scenario result is read.

## How each run is done (same for all)

1. Rebuild the dataset exactly from its `run_manifest.json` (`sim.run all --set ...`); check it against its committed
   `outputs/sensitivity/runs/<name>/summary.json` (same alerts and caught share) and run `sim.checks`.
2. Build its weekly store (`features weekly --weeks 0-77`) and cleaned tables (`features preprocess`, fitted on its
   own months 0–4).
3. Train the recipe of `frozen_tuned_avg5` on its months 0–4: same tuned settings, LightGBM seeds 1–5 averaged,
   application score out of fold (`models train --params .../frozen_tuned/manifest.json --tree-seeds 1 2 3 4 5`).
   Nothing is tuned per scenario.
4. Score its months 6–7 once (`evaluation.score --months 6 7 --final-test`): same harness, rules' weekly budget,
   permanent flags, weeks 0–26 main, 0–77 beside it. Each dataset's own lock applies; v1_full is untouched.

## Measure and criteria (decided now)

- **Lead** = mules caught by the model minus mules caught by the rules, weeks 0–26, as a share of the cohort's mules
  (scenarios have different numbers of mules). Headline (v1_full): (120 − 50) / 163 = 0.43.
- **Chance band** = headline ± the gap between the headline and seed 44's lead (at least ±0.05).
- For each scenario, a paired bootstrap over its mules (1,000 resamples) gives a 95% interval for its lead.

| Verdict | Rule |
|:--|:--|
| **Holds** | lead inside or above the chance band |
| **Shrinks** | lead below the chance band, but its interval is above 0 (model still ahead) |
| **Fails** | interval includes 0, or the rules catch more |

Reported beside the verdict, never used to change it: precision, median days from start, catches by type
(fake / witting / unwitting), weeks 0–77, and for run 7 false alarms per 1,000 normal accounts by age band.

## Rules

- Months 6–7 of v1_full are never re-read here. Each scenario is scored once; no setting changes after a result.
- A "shrinks" or "fails" is reported as a dependence on that assumption, not hidden or re-run.
- Outputs: `outputs/modelling/results/<name>/final_test/`, a summary table `outputs/modelling/robustness/summary.csv`,
  and a short report. Time: ~15 min for run 1, ~25–30 min each after (~3 h in all).
