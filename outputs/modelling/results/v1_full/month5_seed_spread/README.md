# Seed spread on month 5 (30 Oct 2026)

The month-5 harness (cohort opened in month 5, rules' weekly budget, permanent flags) for each of the 5 LightGBM
models inside the model of record `frozen_tuned_avg5` scored alone, for their average (the model of record), and for
the previous model of record `frozen_tuned` (seed 42, trained on Li Ann's machine; from `month5_dryrun_v2`).
Descriptive only: the decision to average 5 seeds (30 Oct 2026, Kee Chee Pheng) was made before this ran, on
notebook 10's pre-registered rule, and nothing was chosen from these numbers.

| model | weeks 0-26 caught (of 78) | precision | weeks 0-77 caught (of 97) |
|:--|--:|--:|--:|
| seed 1 | 65 | 0.524 | 79 |
| seed 2 | 65 | 0.524 | 78 |
| seed 3 | 63 | 0.508 | 77 |
| seed 4 | 63 | 0.508 | 77 |
| seed 5 | 64 | 0.516 | 77 |
| **average of 5 (model of record)** | **65** | **0.524** | **79** |
| frozen_tuned (seed 42) | 63 | 0.508 | 76 |

The seed alone moves the catch by about 2 mules (63-65 of 78), as large as the gap between the two models of record,
so a difference of 1-2 mules between single-seed runs is chance. All measures: `seed_spread.csv` (the `model` row of
each run's `summary_w<W>.csv`). The average scored from a file here equals the model path
(`month5_dryrun_frozen_tuned_avg5`).
