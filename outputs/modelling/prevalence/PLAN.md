# Imbalance check: model vs rules at 0.1%, 0.3% and 1% prevalence (plan, drafted 19 Nov 2026)

**Status: both runs approved 19 Nov 2026 (Kee Chee Pheng); added to the robustness plan as Amendment 1 and
committed before any run. **Both runs done 19 Nov 2026: result below.** This closes the open half of the professor's comment 1
(`docs/professor_feedback.md`). It changes nothing in the simulator, `configs/sim.yaml`, the main data, the frozen
feature list or the model of record, and it never re-reads months 6–7 of v1_full.

## What the professor asked, and what is still missing

> "You can try artificially adjusting your currently balanced test set to a realistically imbalanced ratio
> (e.g., 1% phishing) to evaluate if false positives spike."

Our answer of 8 Oct 2026 had two parts:

| Part | Status |
|---|---|
| The test set is not balanced: it is at the natural 0.3% rate and never resampled | Done; stated in the report |
| The rules at 0.1% / 0.3% / 1%: false alarms 97.8% / 93.4% / 81.3% (whole dataset) | Done (sensitivity runs) |
| "The same comparison for the model (false-alarm share and precision at 0.1 / 0.3 / 1%)" | **Not done** |

Only the 0.3% column has a model number (the final test). This plan fills the other two.

## The question

When mules are three times rarer (0.1%) or three times more common (1%), do the model's false alarms spike, and
does it still beat the rules at the rules' own weekly budget?

## Datasets (already defined; rules frozen at 1.516, seed 42)

| Run | Accounts | Launderers | In test months 6–7 | Rules: false alarms, caught (whole dataset) |
|---|---|---|---|---|
| `prevalence__0.1pct` | 732,000 | 732 | 192 | 97.8%, 30% |
| v1_full (0.3%, the headline) | 244,000 | 732 | 180 | 93.4%, 32% |
| `prevalence__1pct` | 244,000 | 2,440 | 611 | 81.3%, 31% |

The 0.1% run uses three times the accounts so its test months keep about as many launderers as the headline
(decision 7 Oct 2026). Both datasets have their small files and run manifests in `data/sensitivity/`; the large
files were deleted and are rebuilt exactly from the manifest.

## Method: the robustness recipe, unchanged

Each dataset is treated exactly like the 7 robustness runs (`outputs/modelling/robustness/PLAN.md`, "How each run
is done"), so the numbers are comparable with the headline and with those runs:

1. Rebuild the dataset from its `run_manifest.json`; confirm it matches its committed
   `outputs/sensitivity/runs/<name>/summary.json` (same alerts, same caught share); run `sim.checks`.
2. Build its weekly store and cleaned tables (fitted on its own months 0–4).
3. Train `robust_avg5` on its own months 0–4: the tuned settings of the model of record, five seeds averaged,
   nothing tuned per dataset.
4. Score its months 6–7 **once** at the rules' weekly budget (its own lock; weeks 0–26 main).

Why retrain on each dataset: a bank whose mule rate is 1% would train on its own data. It also keeps this
identical to the other robustness runs.

## What is reported

One table, all three columns on the same basis: the harness's fixed test cohort, weeks 0–26. (The whole-dataset
percentages above are a different basis and are not mixed in.)

| | 0.1% | 0.3% (headline) | 1% |
|---|---|---|---|
| Rules: flagged, caught, precision, false-alarm share | new | 264, 50, 0.19, 81% | new |
| Model: flagged, caught, precision, false-alarm share | new | 280, 120, 0.43, 57% | new |
| Lead with 95% interval; verdict | new | 0.43 | new |
| Normal accounts flagged per 1,000 (model, rules) | new | from `by_age_w26.csv` | new |

## How we will read it (decided now)

- **Verdict on the lead:** the robustness plan's rule, unchanged: holds / shrinks / fails against the chance band
  0.31–0.55.
- **"Do false positives spike?"** answered with two numbers per prevalence, model beside rules:
  the false-alarm share of flags, and normal accounts flagged per 1,000.
- **Expected, stated in advance:** the false-alarm share must rise for both methods at 0.1% and fall at 1%,
  because the same flags are spread over fewer or more mules. That alone is arithmetic, not a failure. The finding
  is whether the model's false-alarm share stays below the rules' at every prevalence.

| Result | What we say |
|---|---|
| Model's false-alarm share below the rules' at all three, lead holds | False alarms move with prevalence for both; the model's advantage does not depend on the 0.3% assumption |
| Lead shrinks at one prevalence | Reported as a dependence on prevalence, with the numbers |
| Model's false-alarm share above the rules' at some prevalence, or lead fails | Reported plainly as the main limit of the result |

## Result: both runs scored once (19 Nov 2026)

Fixed test cohort (accounts opened in months 6–7), weeks 0–26, the rules' weekly budget. Each dataset was rebuilt
from its manifest, equalled its committed sensitivity summary exactly and passed all 10 checks before scoring.
Results: `outputs/modelling/results/prevalence__1pct/final_test/` and `prevalence__0.1pct/final_test/` (locked);
leads and verdicts in `outputs/modelling/robustness/summary_amendment1.csv`.

| | 0.1% | 0.3% (headline) | 1% |
|---|---|---|---|
| Test-cohort accounts | 149,992 | 50,061 | 50,061 |
| Mules by week 26 | 172 | 163 | 524 |
| Rules: flagged / caught | 665 / 40 | 264 / 50 | 352 / 138 |
| Model: flagged / caught | 740 / 151 | 280 / 120 | 369 / 297 |
| Rules: precision | 0.06 | 0.19 | 0.39 |
| Model: precision | 0.20 | 0.43 | 0.81 |
| **Rules: false-alarm share of flags** | **94%** | **81%** | **61%** |
| **Model: false-alarm share of flags** | **80%** | **57%** | **20%** |
| Rules: normal accounts flagged per 1,000 | 4.2 | 4.3 | 4.3 |
| Model: normal accounts flagged per 1,000 | 3.9 | 3.2 | 1.5 |
| Lead (95% interval) | 0.65 (0.57–0.72) | 0.43 (0.35–0.52) | 0.30 (0.25–0.36) |
| Verdict (chance band 0.31–0.55) | holds (above the band) | – | shrinks |
| McNemar: model only / rules only | 114 / 3 | 77 / 7 | 207 / 48 |

**Reading, by the table decided above:**

- **Do false positives spike?** The false-alarm share rises as mules get rarer for both methods, as expected
  (model 20% → 57% → 80%; rules 61% → 81% → 94%). The model's share is below the rules' at all three
  prevalences. The model also flags fewer normal accounts per 1,000 than the rules at all three.
- **Lead:** holds at 0.1% (above the band) and **shrinks at 1%** (0.30, just under the band's lower edge of 0.31;
  the model still catches more than twice as many mules, 297 vs 138). By the plan's rule this is reported as a
  dependence on prevalence.
- **One explanation of the 1% result, worked out after seeing it (so not a pre-registered claim):** the budget is
  the rules' alert count, which barely moves with prevalence (369 flags at 1% against 280 at 0.3%) while the mules
  more than triple (524 against 163). With 369 flags a perfect model could catch at most 369 of 524 (0.70), so
  the lead as a share of mules is capped by the budget. At 0.1% the opposite holds: 740 flags for 172 mules.
- **Fairness, beside the result:** the model's false alarms stay uneven across ages at every prevalence (lowest ÷
  highest rate 0.31 / 0.31 / 0.32); the rules stay near even (0.83 / 0.94 / 0.93).

**Not done as planned:** the rebuilt large files were kept, not deleted (8 GB and 25 GB under `data/sensitivity/`,
git-ignored), like the other robustness datasets. Compute was 14 min (1%) and 39 min (0.1%), well under the
estimates. These runs are spent: nothing is re-scored and no setting changes.

## Cost and risks

| Run | Compute (estimate) | Disk while running | Risk |
|---|---|---|---|
| `prevalence__1pct` | ~35 min | ~15 GB | Low: same size as the 7 runs already done |
| `prevalence__0.1pct` | ~2 h | ~45 GB | Medium: three times every step; never modelled at this size |

- For the 0.1% run set `SIM_DUCKDB_MEMORY=8GB` (as `src/sim/run.py` notes for 732k). Training has about 13 million
  account-weeks; this Mac has 24 GB of memory, which should be enough but is untested.
- 534 GB of disk is free. Delete the large files again afterwards (the stores and models stay).
- **Order: 1% first.** It is the professor's own example and the cheap one.
- **Fallback, decided now:** if the 0.1% run cannot finish by 21 Nov, report the 1% result and say that at 0.1%
  only the rules were tested. No setting is changed to make it fit.

## Rules

- This plan is added to the robustness plan as an amendment and committed before any run.
- Each dataset's months 6–7 are scored once; no setting changes after a result; both results are reported.
- The original 7 rows of `outputs/modelling/robustness/summary.csv` stay identical; these two runs are added as
  amendment rows.
- Results: `outputs/modelling/results/<name>/final_test/`, and the table above written into this file.

## Optional extra, only if asked: the model of record on a different prevalence

The professor's wording is closer to "same model, different test mix". A second view: score `frozen_tuned_avg5`
(trained at 0.3%) on **month 5** of each prevalence dataset, with no retraining. It shows what happens when the
mule rate in production differs from the rate the model was trained at. Month 5 only, so no test months are used
twice. Not part of the main plan.

## Decisions for the team

1. ~~Run both, or only the 1% run?~~ Both (19 Nov 2026, Kee Chee Pheng).
2. Add the optional extra?
