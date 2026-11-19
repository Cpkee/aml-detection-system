# Closing the modelling plan: implementation plan (drafted 19 Nov 2026)

**Status: draft for the team. Nothing below has been run.** The modelling plan (decision-record doc, tab
"Modelling plan", 9 Oct 2026) promised some things that are not in the repo yet. This file says, for each one, what
to build, what it reads, how long it takes and how the result will be read. Report deadline: 22 Nov 2026.

Nothing here changes the simulator, the data, the feature store, the frozen feature list, the model of record or
`configs/sim.yaml`. Months 6–7 of v1_full are **not read again** by any item: items 1–3 use only the committed
output of the locked final test (`outputs/modelling/results/v1_full/final_test/`).

| # | Item | Reads | New compute | Effort | Do it? |
|---|---|---|---|---|---|
| 1 | Paired significance test for the headline | Committed final-test output | None | 30 min | Yes |
| 2 | Fairness as a ratio of false-positive rates | Committed final-test output | None | 30 min | Yes |
| 3 | Interpretability and scoring time | PR #39; one timing run on month 5 | ~5 min | 1 h | Yes |
| 4 | Which inputs rest on which simulator assumptions | Robustness results, source check | None | 1–2 h writing | Yes |
| 5 | Evasion test: patient launderers | One new sensitivity dataset | ~45 min | Half a day | Yes, if the team approves the test value |
| 6 | Fairness on Variant II | `data/variant_II` (store already built) | ~30 min | 2–3 h | Optional |
| 7 | Money gone before the first flag (£) | Month 5 hidden transactions | ~5 min | 2–3 h | Optional |
| 8 | Unseen shapes, PCA / autoencoder, CNN, LLM | – | – | – | No: state as limits |
| 9 | Model vs rules at 0.1% and 1% prevalence (professor's comment 1) | Two sensitivity datasets, rebuilt | ~35 min + ~2 h | Half a day | Yes: plan in `outputs/modelling/prevalence/PLAN.md` |

Suggested order: 19 Nov items 1–4; 20 Nov item 5 (then 6 if time); 21 Nov report text. Items 1–4 need no decision.

## 1. Paired significance test (McNemar)

- **Why:** the plan promised a test that the model-vs-rules gap is real. The robustness runs have a bootstrap; the
  headline itself has no test stated.
- **What:** McNemar's test on the mules where exactly one method made the catch (weeks 0–26). The locked report
  already holds the counts: caught by both 43, model only 77, rules only 7, neither 36 (163 mules).
- **Expected arithmetic** (from those committed counts, so not a new look): chi-square with continuity correction
  = (|77 − 7| − 1)² / (77 + 7) = 56.7; exact two-sided p ≈ 5 × 10⁻¹⁶.
- **Build:** `mcnemar(run)` in `src/evaluation/robustness.py`, beside `mules(run)` which already loads these rows;
  returns both, model_only, rules_only, chi-square, exact p. One test in `tests/test_robustness.py` on a small
  made-up table. Print it for `v1_full` and the 7 robustness runs.
- **Report wording:** the test covers mules only. It says the model catches more mules than the rules at the same
  budget; it says nothing about false alarms, which precision covers.
- **Also state** (plan, 9 Oct): with ~160 mules, a gap of 3–5 catches is not significant. That applies to the
  onboarding comparison (65 vs 61 of 78 on month 5).
- **Result (done 19 Nov 2026):** `mcnemar(run)` in `src/evaluation/robustness.py`; `python -m evaluation.robustness`
  prints it (not saved in `summary.csv`). Weeks 0–26, mules of the test cohort (months 6–7), from the committed
  `final_test/launderers.csv` of each run; nothing re-scored. v1_full matches the expected arithmetic above.

  | Run | Both | Model only | Rules only | Neither | Chi-square | Exact p |
  |---|---|---|---|---|---|---|
  | v1_full (headline) | 43 | 77 | 7 | 36 | 56.68 | 5.1e-16 |
  | seed__44 | 35 | 79 | 0 | 31 | 77.01 | 3.3e-24 |
  | in_window_mix__1 | 24 | 75 | 6 | 19 | 57.09 | 2.9e-16 |
  | bursts_per_launderer__1 | 70 | 80 | 5 | 8 | 64.42 | 1.8e-18 |
  | fake_start_days__2 | 29 | 62 | 1 | 71 | 57.14 | 1.4e-17 |
  | fake_start_days__1 | 46 | 72 | 8 | 37 | 49.61 | 5.4e-14 |
  | out_transfer_mean__1 | 118 | 30 | 2 | 13 | 22.78 | 2.5e-07 |
  | fake_age_rule__1 | 42 | 86 | 5 | 30 | 70.33 | 4.0e-20 |

  In every run the model catches many mules the rules miss, and the rules catch few that the model misses. The
  gap is far beyond chance in all 8 runs. It is smallest with £1,500 transfers (30 vs 2), where the rules
  already catch most mules. The test covers mules only: it says the model catches more mules than the rules at
  the same budget, and nothing about false alarms (precision covers those).

## 2. Fairness: ratio of false-positive rates between age groups

- **Why:** the plan names the BAF paper's fairness measure. The harness already writes the rates per age band but
  no ratio, and the report has no fairness number for the headline.
- **What the committed file already shows** (`final_test/by_age_w26.csv`, share of normal accounts flagged):

  | Age band | Model | Rules |
  |---|---|---|
  | Under 30 | 0.19% | 0.42% |
  | 30–49 | 0.29% | 0.43% |
  | 50+ | 0.61% | 0.44% |

  Lowest ÷ highest rate: model 0.31, rules 0.94 (1.0 = equal treatment). The model flags fewer normal customers
  overall but spreads its false alarms much less evenly.
- **Build:** `fpr_ratio(run)` in `src/evaluation/robustness.py` reading `by_age_w26.csv`: lowest ÷ highest rate per
  policy, for the three bands and for under-50 vs 50+ (BAF's own grouping; recomputed from the counts in the
  file). One test on a made-up table.
- **How we read it (decided now):** reported as a cost of the model, with the cause already found in robustness
  run 7 (false alarms follow the fake accounts' ages). No threshold is applied and nothing is tuned to improve it.
- **Result (done 19 Nov 2026; `robustness.fpr_ratio(run)`, `tests/test_robustness.py`).** Weeks 0–26, test cohort,
  read only from the committed `final_test/by_age_w26.csv` files. The rate is the harness's own: normal accounts
  flagged ÷ (accounts − mules) in the band, where a mule is a mule by the end of week 26 (`score.by_age`). The code
  first rebuilds the file's three rates from its counts this way and stops if they differ. Under 50 pools the
  counts of the two younger bands. Ratio = lowest rate ÷ highest rate (1.0 = equal treatment).

  *Headline (v1_full).* Normal accounts: 12,500 under 30, 29,255 aged 30–49, 8,143 aged 50+.

  | Policy | Under 30 | 30–49 | 50+ | Ratio, 3 bands | Under 50 | Ratio, under 50 vs 50+ |
  |---|---|---|---|---|---|---|
  | Model | 0.19% (24) | 0.29% (86) | 0.61% (50) | **0.31** | 0.26% (110) | **0.43** |
  | Rules | 0.42% (52) | 0.43% (126) | 0.44% (36) | 0.94 | 0.43% (178) | 0.96 |

  (In brackets: normal accounts flagged.) **This is a cost of the model.** It raises fewer false alarms overall
  than the rules (160 vs 214), but it puts them unevenly: a normal customer aged 50+ is about 3 times as likely to
  be flagged as one under 30 (0.61% vs 0.19%), and 1.4 times as likely as under the rules (0.61% vs 0.44%). The
  rules treat the age groups almost equally. The cause is known (robustness run 7): the model's false alarms
  follow the fake accounts' ages, and in this data the fakes are older.

  *Robustness runs* (each its own `robust_avg5` model, months 6–7 scored once; model rates per band, then the
  ratios):

  | Run | Model: under 30 / 30–49 / 50+ | Model, 3 bands | Model, 2 groups | Rules, 3 bands | Rules, 2 groups |
  |---|---|---|---|---|---|
  | seed__44 | 0.09% / 0.25% / 0.54% | 0.16 | 0.37 | 0.79 | 0.92 |
  | in_window_mix__1 | 0.30% / 0.28% / 0.51% | 0.55 | 0.55 | 0.94 | 0.97 |
  | bursts_per_launderer__1 | 0.22% / 0.30% / 0.58% | 0.37 | 0.48 | 0.94 | 0.96 |
  | fake_start_days__2 | 0.17% / 0.28% / 0.82% | 0.20 | 0.30 | 0.94 | 0.96 |
  | fake_start_days__1 | 0.22% / 0.29% / 0.64% | 0.35 | 0.43 | 0.94 | 0.96 |
  | out_transfer_mean__1 | 0.22% / 0.36% / 0.90% | 0.24 | 0.36 | 0.94 | 0.96 |
  | fake_age_rule__1 | 0.35% / 0.30% / 0.23% | 0.67 | 0.75 | 0.95 | 0.97 |

  The model is less even than the rules in every run (3-band ratio 0.16–0.67 vs the rules' 0.79–0.95). In six runs
  the 50+ band carries the highest rate. With young fakes (`fake_age_rule__1`) the gap shrinks and turns round: the
  under-30s now have the highest rate. That supports the cause above: the model learns the fakes' ages, so whichever
  age group the fakes come from pays for it in false alarms. With fewer fakes (`in_window_mix__1`, 53%) the ratio is
  also better (0.55). The rules' rates barely move, because the rules do not see age.

## 3. Interpretability and scoring time

- **Interpretability:** PR #39 (`frozen-importance`, `models.frozen_importance`, importance of the 38 inputs) is
  open and unmerged. Bring it up to date with `main`, check its numbers are for `frozen_tuned_avg5` (it was written
  for the earlier `frozen_tuned`; if so, re-run it on the model of record: reads the model files only), merge.
- **Scoring time:** time `python -m models predict --out data/v1_full --months 5 --weeks 0-26` three times; report
  the median seconds, account-weeks per second and the machine (the harness already records `machine`). Feature
  build time is already known (~4 min for 19.0M account-weeks).
- **Report wording:** two of the three criteria the plan cites from lecture 1 (the third is fairness, item 2).

## 4. Which inputs rest on which simulator assumptions

Writing only. One table for the report's limitations section, filled from the robustness report
(`outputs/modelling/robustness/report.md`) and the source check of 18 Nov 2026 (PR #59). Draft rows:

| Model inputs | Simulator setting they rest on | Evidence for the setting | Tested by | Result |
|---|---|---|---|---|
| Forwarding speed (1 h / 24 h shares, minutes) | `forward_delay_shares` | RUSI 2025, confirmed | Not yet: item 5 | – |
| Money in, pass-through | `out_transfer_mean` (£532) | RUSI 2025, confirmed | `out_transfer_mean__1` | Shrinks (lead 0.17) |
| Payers, new payers | Laundering shapes; `group_collection` | SAML-D (itself synthetic); assumption | Not tested for the model | – |
| Application score | `in_window_mix` (73% fake), BAF fraud rows | Our inference (Which?, RUSI do not state it) | `in_window_mix__1` | Holds (0.56) |
| Application score: age | `fake_age_rule`, `real_mule_age_weights` | Cifas, confirmed | `fake_age_rule__1` | Holds (0.50) |
| Weeks since opening | `fake_start_days` (~90 days) | Assumption, no source | `fake_start_days__1`, `__2` | Borderline (0.39, 0.37) |
| All activity inputs | `bursts_per_launderer` (one burst) | Assumption, no source | `bursts_per_launderer__1` | Holds (0.46) |

To finish: check each row against the importance table from item 3, so the inputs the model uses most are the
ones listed.

## 5. Evasion test: patient launderers

- **Why:** the plan's evasion test was never run, and it matters more now. The model and the rule scorecard both
  lean on forwarding speed, and forwarding speed is the one heavily used input with no robustness run (item 4).
- **What:** one new sensitivity dataset where launderers forward slowly, everything else as v1_full (244,000
  accounts, seed 42, rules frozen at 1.516). One change only, as in every sensitivity run. The plan's other ideas
  (amounts under the R4 limit, extra hops) are not run: `out_transfer_mean__1` already covers amounts.
- **Test value (an assumption; needs a team yes before the run):**

  | Share of money forwarded | Main run (RUSI) | Patient launderers (proposed) |
  |---|---|---|
  | Within 15 minutes | 28% | 5% |
  | 15–60 minutes | 25% | 10% |
  | 1–24 hours | 32% | 35% |
  | After 24 hours (up to 7 days) | 15% | 50% |

  No source: no published figure describes launderers who deliberately slow down. Passed with `--set` for this run
  only; `configs/sim.yaml` is not edited.
- **Steps** (the robustness plan's recipe, unchanged):
  1. Write this run into `outputs/modelling/robustness/PLAN.md` as an amendment and commit it before the run.
  2. Build `data/sensitivity/forward_delay_shares__1` with `sim.run all` and the three `--set` values; run
     `sim.checks`.
  3. Build its store and cleaned tables; train `robust_avg5` on its months 0–4 (nothing tuned).
  4. Score its months 6–7 once (its own lock). Add the run to `evaluation.robustness` and `summary.csv`.
- **How we read it (the robustness plan's rule, unchanged):** holds / shrinks / fails by the lead and its interval
  against the chance band 0.31–0.55. A "shrinks" or "fails" is reported as a dependence on forwarding speed.
- **Expectation, stated in advance:** the rules do not use forwarding speed inside a week, so they should lose
  little; the model should lose more. A smaller lead is the likely outcome.

## 6. Fairness on Variant II (optional)

- **Why:** Variant II was generated for fairness (launderer rate higher for 50+ in every month) and has never been
  modelled. Item 2 gives a fairness number on the main data; this checks it where the age bias is stronger.
- **State:** `data/variant_II` exists with its weekly store and cleaned tables. Variant IV's store is not built
  and is left out.
- **Steps:** train `robust_avg5` on its months 0–4, score its months 6–7 once (own lock), report the lead and the
  item-2 ratio. Added to the robustness plan in the same amendment as item 5.
- **How we read it:** reported beside item 2, never used to change the model.

## 7. Money gone before the first flag, month 5 (optional)

- **Why:** the plan's cost measure: what a miss or a late catch costs, in pounds.
- **What:** for each month-5 mule, the laundering money paid out up to its first flag (all of it by week 26 if
  never flagged), summed per policy: rules, rule scorecard, model. Month 5 only: months 6–7 would be another counted
  look at the test months.
- **Build:** `src/evaluation/cost.py`, reading the committed `launderers.csv` of each month-5 run and the hidden
  transaction labels through `amldata.evaluation()` (scoring code, so allowed).
- **Left out:** investigator cost in pounds. There is no sourced cost per alert, and all policies flag the same
  number of accounts by design, so it would add an invented number and no information.

## 8. Not done: stated as limits

| Plan item | Why not | Where it is said |
|---|---|---|
| Unseen laundering shapes | About 12 test mules per shape: too few to conclude anything | Limitations |
| PCA / autoencoder | Dropped by decision D4 (31 Oct 2026); the outlier appendix covers label-free detection | Outlier appendix |
| MLP / 1D CNN, LLM case summary | Marked "skip unless time is left" in the plan itself | Further work |

The "Modelling plan" doc tab still describes the autoencoder as a challenger and gives the old baseline's McNemar
example. Add one line at its top pointing here.

## Decisions for the team

1. Item 5: is the patient-launderer test value acceptable as an assumption? (Blocks item 5.)
2. Items 6 and 7: do them, or state them as not done?
3. Item 3: re-run importance on `frozen_tuned_avg5` if PR #39 used `frozen_tuned`?
