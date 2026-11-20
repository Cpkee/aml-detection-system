# Imbalance check: model vs rules at 0.1%, 0.3% and 1% prevalence (plan, drafted 19 Nov 2026)

**Status: draft for the team. Nothing has been run.** This closes the open half of the professor's comment 1
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

1. Run both, or only the 1% run?
2. Add the optional extra?
