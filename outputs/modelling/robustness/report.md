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

## Runs 3–7, 6 Nov 2026

Each rebuilt from its committed `run_manifest.json` (run 3 rebuilt 5 Nov, then paused; checks re-run 6 Nov), 10 of
10 checks pass and every number in its committed `summary.json` is identical; store, cleaned tables and
`robust_avg5` as in run 1 (settings checked equal to `frozen_tuned_avg5` before scoring); months 6–7 scored once.

| # | Run | Mules | Model | Rules | Lead | 95% interval | Precision model / rules | Verdict |
|--:|:--|--:|--:|--:|--:|:--|:--|:--|
| 3 | `bursts_per_launderer__1` (repeated bursts) | 163 | 150 | 75 | 0.46 | 0.37–0.54 | 0.48 / 0.26 | **holds** |
| 4 | `fake_start_days__2` (fakes start at 150–210 days) | 163 | 91 | 30 | 0.37 | 0.30–0.45 | 0.35 / 0.12 | **holds** |
| 5 | `fake_start_days__1` (fakes start at 15–45 days) | 163 | 118 | 54 | 0.39 | 0.31–0.49 | 0.42 / 0.20 | **holds** |
| 6 | `out_transfer_mean__1` (£1,500 transfers) | 163 | 148 | 120 | 0.17 | 0.10–0.24 | 0.42 / 0.36 | **shrinks** |
| 7 | `fake_age_rule__1` (young fake ages) | 163 | 128 | 47 | 0.50 | 0.42–0.58 | 0.46 / 0.18 | **holds** |

(The same 163 cohort accounts are mules by week 26 in runs 3–6 as in v1_full: same seed and BAF rows, fakes count from
opening. Run 7 changes which rows become fakes.)

Beside the verdicts (model / rules, weeks 0–26 unless stated):
- **Run 3, repeated bursts.** The rules double their catch (50 -> 75), the model rises too (120 -> 150); fakes 137 /
  71 of 147. Median days from start 9 / 17. Weeks 0–77: 172 / 135 of 180.
- **Run 4, late fakes.** Many fakes start laundering after week 26, so fewer are caught inside the horizon (78 / 24
  of 147). The lead is the lowest of the "holds" (0.37). Its interval, 0.30–0.45, reaches just below the band floor
  (0.31), so this is a borderline "holds": the verdict follows the plan's rule (the lead itself, 0.37, is inside
  the band). 13 model flags
  fall before laundering starts (fakes found from application and early activity; they count as mules from opening).
  Weeks 0–77: 154 / 56 of 180, so the model catches them once they start.
- **Run 5, early fakes.** Little history before the burst: fakes 110 / 51; witting 5 / 1 of 11. Median days from
  start 11 / 7: the only run where the rules' median catch is faster. Also borderline: lead 0.39 inside the band, interval
  0.31–0.49 with its lower end (0.307) just below the floor (0.314).
- **Run 6, £1,500 transfers (shrinks).** Larger transfers trip the rules' amount thresholds: rules 120 of 163 (0.74).
  The model still catches more (148, 0.91) and is still ahead (interval above 0), but the lead falls to 0.17 and the
  precision gap closes (0.42 vs 0.36). Median days from start 4 / 6.
- **Run 7, young fake ages.** False alarms per 1,000 normal accounts by age band:

  | Age | v1_full model | v1_full rules | Run 7 model | Run 7 rules |
  |:--|--:|--:|--:|--:|
  | under 30 | 1.9 | 4.2 | 3.4 | 4.2 |
  | 30–49 | 2.9 | 4.3 | 3.0 | 4.3 |
  | 50+ | 6.1 | 4.4 | 2.3 | 4.4 |

  The rules' false alarms are flat across ages. The model's follow the fakes' ages: on v1_full (fakes skew older) it
  over-flags normal 50+ accounts (6.1, above the rules' 4.4); with young fakes the excess moves to under-30s (3.4).
  It is below the rules in every band in run 7. The model learns the fakes' age profile, so whichever age group fakes
  come from carries more false alarms: a fairness point for the report.

## Note on the run records (added 15 Nov 2026)

Each run's `settings.json` and model manifest record `git_uncommitted_changes: true` (the headline run on v1_full
records false). The flag looks at tracked files only. The one known cause is an uncommitted edit to
`notebooks/10_stability_undersampling.ipynb` made on 4 Nov, before the runs (a blank line and a cleared cell
counter; no code under `src/`); report files being written between runs may also have set it. The flag cannot say
which file it was, so this is stated here, and the locked runs are not re-run.

Borderline verdicts: runs 4 and 5 "hold" by the plan's rule (lead inside the band), but both intervals reach just
below the band floor of 0.31. Read them as "no clear change", not as evidence that the lead is untouched.

## Summary

| Verdict | Runs |
|:--|:--|
| Holds | 2 fewer fakes, 3 repeated bursts, 4 late fakes, 5 early fakes, 7 young fake ages |
| Shrinks | 6 £1,500 transfers (lead 0.17, 0.10–0.24) |
| Fails | none |

The model beats the rules in every scenario. The lead depends most on how launderers move money: when transfers are
large enough for the rules' amount thresholds, the rules catch 3 in 4 and most of the model's lead goes. The fake-
account assumptions (share, start time, ages) move the lead within the chance band.

## Is the model's lead more than chance? McNemar's test (added 19 Nov 2026)

The lead compares two counts taken on the **same** mules, so the right test is a paired one. McNemar's test ignores
the mules both methods caught or both missed, and looks only at the ones where they disagree: if the model and the
rules were equally good, those disagreements would split about 50/50. Exact two-sided p from the binomial on the
disagreements; chi-square with continuity correction beside it. Weeks 0–26, from each run's committed
`final_test/launderers.csv` (`python -m evaluation.robustness` prints it; `robustness.mcnemar(run)`).

| Run | Both caught | Model only | Rules only | Neither | Chi-square | Exact p |
|:--|--:|--:|--:|--:|--:|--:|
| v1_full (headline) | 43 | 77 | 7 | 36 | 56.68 | 5.1e-16 |
| 1 `seed__44` | 35 | 79 | 0 | 31 | 77.01 | 3.3e-24 |
| 2 `in_window_mix__1` | 24 | 75 | 6 | 19 | 57.09 | 2.9e-16 |
| 3 `bursts_per_launderer__1` | 70 | 80 | 5 | 8 | 64.42 | 1.8e-18 |
| 4 `fake_start_days__2` | 29 | 62 | 1 | 71 | 57.14 | 1.4e-17 |
| 5 `fake_start_days__1` | 46 | 72 | 8 | 37 | 49.61 | 5.4e-14 |
| 6 `out_transfer_mean__1` | 118 | 30 | 2 | 13 | 22.78 | 2.5e-07 |
| 7 `fake_age_rule__1` | 42 | 86 | 5 | 30 | 70.33 | 4.0e-20 |

- **Headline:** on the same 163 test mules, the model caught 77 that the rules missed, and the rules caught 7 that
  the model missed. A split this lopsided would almost never happen by chance (p ≈ 5 × 10⁻¹⁶).
- **Every run agrees.** The rules catch at most 8 mules per run that the model misses; the model finds nearly
  everything the rules find, and more. The smallest gap is run 6 (£1,500 transfers, 30 vs 2), where the rules
  already catch most mules: still far beyond chance, matching its "shrinks" verdict.
- **What it does not say:** it covers mules only, nothing about false alarms (see precision above and the false-
  positive rate by age); and a tiny p says the gap is real, not how big it is (that is the lead and its interval).
  It is evidence within the simulation, not about real banking.

## Amendment 2 (19 Nov 2026): Variant II and patient launderers

Plan: `PLAN.md`, "Amendment 2" (committed before either run). Same recipe, same verdict rule, same chance band
(0.31–0.55). Numbers: `summary_amendments.csv` (`python -m evaluation.robustness --amendment`); `summary.csv` is
unchanged.

**`variant_II`, 19 Nov 2026.** BAF Variant II (launderer rate higher for ages 50+ in all months), 244,000 accounts,
seed 42, rules frozen at 1.516. Not rebuilt: its store and cleaned tables pass their manifest checks. `robust_avg5`
trained on its months 0–4 (settings of `frozen_tuned`, LightGBM seeds 1–5, nothing tuned; 4.45M account-weeks, 8,528
mule weeks), months 6–7 scored once (`results/variant_II/final_test/`, locked).

| Run | Mules | Model | Rules | Lead | 95% interval | Precision model / rules | Verdict |
|:--|--:|--:|--:|--:|:--|:--|:--|
| `variant_II` | 152 | 134 | 57 | 0.51 | 0.42–0.59 | 0.51 / 0.22 | **holds** |

Beside the verdict (model / rules, weeks 0–26): fakes 126 / 53 of 138, witting 6 / 3 of 10, unwitting 2 / 1 of 4.
Median days from start 7 / 9. McNemar: model only 79, rules only 2 (exact p 2.7e-21). Weeks 0–77: 147 / 63 of 169.
False-positive rate by age (normal accounts flagged; lowest ÷ highest over 3 bands, and under 50 vs 50+):

| Policy | Under 30 | 30–49 | 50+ | Ratio, 3 bands | Ratio, 2 groups | v1_full ratios |
|:--|--:|--:|--:|--:|--:|:--|
| Model | 0.07% | 0.23% | 0.35% | 0.19 | 0.52 | 0.31 / 0.43 |
| Rules | 0.23% | 0.37% | 0.47% | 0.48 | 0.69 | 0.94 / 0.96 |

The lead holds where older customers launder more. The model still flags 50+ normal customers most, but less often
than the rules do in every band; its uneven spread comes mostly from almost never flagging under-30s. Variant II's
test cohort is half 50+ (16% on v1_full), and here the rules' false alarms also rise with age. Variant IV is left out
(its store is not built).

**`forward_delay_shares__1`:** not yet run.
