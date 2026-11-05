# Fake-mix stress test: plan (draft 5 Nov 2026, to be agreed before any run)

Owner: Kee Chee Pheng (took over from Teammate 4, 5 Nov 2026). Report section: robustness and limitations.
Every setting below is fixed **before** any stress dataset is rebuilt or scored, so the result cannot be tuned to
look good. Status: **draft, not yet agreed.**

## Why

In the main data 73% of launderers are fake accounts (BAF fraud rows), and the model's headline win rests mostly on
them: on the final test it caught 109 of 147 fakes but only 11 of 16 real-customer mules (witting + unwitting).
CLAUDE.md calls the fake share "the main threat to the result". This test asks: **if fewer launderers are fakes,
does the model still catch clearly more mules than the rules?**

## What changes, what stays

| | Main (`v1_full`) | Stress 1 (`in_window_mix__1`) | Stress 2 (`in_window_mix__2`) |
|---|---|---|---|
| Fake / witting / unwitting | 73.3% / 13.35% / 13.35% | 53% / 23.5% / 23.5% | 56% / 22% / 22% |
| Accounts, launderers | 244,000, 732 | same | same |
| Launderers in test months 6-7 | 180 | 164 | 165 |
| Rules (frozen at scale 1.516): caught / false alarms | 32% / 93.4% | 28.7% / 94.1% | 31.0% / 93.7% |
| Rule alerts (true) over 18 months | 3,614 (240) | 3,587 (211) | 3,587 (227) |

The two stress datasets are the existing sensitivity runs (built 8 Oct 2026, `outputs/sensitivity/runs/`), rebuilt
exactly from their `run_manifest.json` (simulator unchanged since; only description notes in `configs/sim.yaml`).
Everything else equals the main data: seed 42, 244k accounts, 0.3% launderers, the bank's rules frozen.

## The model (decision needed: S1)

- **S1, retrain the recipe on each stress dataset** (proposed): the frozen recipe of the model of record
  `frozen_tuned_avg5`, fitted on each dataset's own months 0-4: preprocessing fitted per dataset (decision 10 Oct
  2026), the 38 frozen inputs, tuning step 2's settings (`lgbm_tuning_step2/tuned_params.json`), application score
  seed 42, LightGBM seeds 1-5 averaged. Name `stress_avg5`. No re-tuning, no new inputs. This follows CLAUDE.md
  ("use each variant for training AND testing with the same split"). The model of record itself is never touched.
- Not done: scoring the stress data with the model trained on the main data (an optional extra, as for the variants).

## How it is scored

The same harness, unchanged (`python -m evaluation.score`): month 5 dry run first, then test months 6-7 **once**
per dataset (`--final-test`, its own lock under `outputs/modelling/results/<dataset>/final_test/`). Main horizon
weeks 0-26; the rules' own weekly alert count as the budget; permanent flags. Measures as the main final test:
caught, recall, precision, caught by type, head to head, by age band, by opening month.

**Uncertainty:** a paired bootstrap of the model-minus-rules recall difference, resampling the test-month mules
(1,000 resamples, seed 0), from each run's `launderers.csv` (computed after the run, same code for all datasets).

**Chance yardstick (S2, proposed):** the same pipeline on `seed__43` (same settings as the main data, seed 43; 185
test-month launderers; rules 33.5% caught, 93.2% false alarms; its large files were kept; its store was built
28 Oct for the `roll4` check, possibly on another team member's machine, so it may need rebuilding locally). It shows how much the result moves from a different random draw alone, so a stress-test
change is only read as real if it is clearly larger than the seed 43 change.

## How the result will be read (written before the run)

Main data, final test, weeks 0-26: model 120 vs rules 50 of 163 mules, recall 0.736 vs 0.307 (gap 0.429).

| Result on both stress datasets | Reading |
|---|---|
| Model recall above the rules, interval of the gap excludes 0, gap within the seed 43 range of the main gap | **The advantage holds** without the 73% fake share. |
| Model above the rules, but the gap clearly smaller than main and seed 43 | **The advantage shrinks** with fewer fakes: report by how much; the headline depends partly on the fake share. |
| Interval of the gap includes 0 | **No clear advantage** without many fakes: the main result is mostly a fake-account result; stated as the main limitation. |
| Rules ahead | The model's win depends on fakes; stated plainly. |

**Also reported, whatever the main reading:** real-customer mules (witting + unwitting) caught by model vs rules.
The stress datasets hold about twice as many real-customer mules as the main test months (16), so this is our best
estimate of how the model does on recruited real customers. Expectation stated in advance: real-customer mules
show no signal before their laundering starts (EDA round r01), so the model's lead on them, if any, comes from
catching their burst sooner or more often, not earlier.

## Limits

- One draw per mix (seed 42); seed 43 is the only chance yardstick.
- Only the fake share changes; prevalence (0.1% / 1%) and Variants II / IV are separate tests.
- The test months of each stress dataset are scored once; never re-run with other settings.

## Steps

1. Team agrees S1, S2 and the readings above; this file is committed with "agreed" and the date.
2. Rebuild `in_window_mix__1` and `__2`; `sim.checks` must pass and match `summary.json` (`__1`: 3,587 alerts,
   211 true; `__2`: 3,587 alerts, 227 true). A mismatch stops the test until explained.
3. Per dataset: weekly store, preprocessing, `models train --name stress_avg5`, month 5 dry run, test months once.
4. Seed 43: preprocessing (if missing), `models train --name stress_avg5`, month 5 dry run, test months once.
5. Bootstrap the gaps; write the result into this folder and the report's robustness section.
