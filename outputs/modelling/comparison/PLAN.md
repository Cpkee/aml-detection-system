# Methods comparison: plan (pre-registered 2 Nov 2026)

Decisions by Kee Chee Pheng, 2 Nov 2026. Team version with the research behind it: decision-record doc, tab
"Methods comparison: research + plan" (https://claude.ai/artifact/LchcqbsutNLSHWKESoWWQL). This file is the
pre-registration: it is committed before any rival is trained, and later changes are added as dated amendments at
the bottom, never edited in place.

**Question.** Do other methods catch mules earlier or more often than our two-stage model (`frozen_tuned_avg5`:
application logistic score + tuned LightGBM, LightGBM seeds 1-5 averaged), with the same number of flags as the
bank's rules? Report-strength work; a clear winner may become a team proposal to replace the model.

**Never touched:** test months 6-7 (one counted re-test only for an agreed winner, `evaluation.score --retest`),
the frozen feature list, the feature store, `configs/sim.yaml`, `amldata`.

## How methods are judged

- **Deciding measure: `catch_rules`.** Each week since opening a method flags as many accounts as the rules alerted
  that week (`evaluation.budget.weekly_budget`), from accounts not flagged before (a flag is permanent). For each week
  w, the share of the accounts that are mules at week w already flagged; averaged over weeks 0-26
  (`feature_lab.catch_mean`). It rewards catching early.
- **Reported beside it:** recall by week 26 at the budget (mules by week 26 flagged by week 26 / mules by week 26),
  precision at the budget (flagged accounts that are mules by week 26 / flagged), account-level PR-AUC and ROC-AUC,
  `first_caught_2wk`, median weeks from laundering start to first flag, catches by mule type (real-customer mules as
  counts only), fit time. Top-1% weekly recall is a tuning measure only: it rewards re-flagging and never decides.
- **Data:** the 3 temporal folds of months 0-4 (`lgbm_baseline.FOLDS`: train months 0-1 -> validate 2, 0-2 -> 3,
  0-3 -> 4; weeks 0-26; closed account-weeks dropped from training) and, once every group is done, month 5, scored
  once with code and settings frozen and committed first.
- **Win rule (pooled + Holm).** One paired account-level bootstrap pooled over the 3 folds and month 5: mule accounts
  are resampled within each cohort with the same draw for both methods; the pooled statistic is the mean of the
  4 cohorts' `catch_rules`. A rival wins when (1) its pooled gain over ours is above 0.012 (measured refit noise of
  `catch_rules`, feature_lab.NOISE), (2) its two-sided bootstrap p-value passes Holm's correction at 0.05 over all
  rivals compared, and (3) it leads in at least 3 of the 4 cohorts. 2000 bootstrap draws, seed 0.
- **Smallest detectable gain:** computed from the reference run before any rival is fitted and recorded below.
- **"No winner"** is reported as "no rival beat ours; the paired intervals rule out gains above X", within this
  simulation. It is not a proof that ours is best.

## Shared rules for every method

- Same rows (`stability.lab_setup`: months 0-4, weeks 0-26, the 38 frozen inputs available), label `mule_by_day`,
  folds, and scoring code (`stability.fold_measures` + `models.comparison`).
- Same application score: the fold's out-of-fold logistic score (`feature_lab.app_scores`, seed 42); only A2 uses the
  raw application columns, on purpose.
- Methods with randomness: seeds 1-5, the 5 scores averaged per account-week before flagging (as the model of record).
- Early stopping, when a method uses it, on the last training month, never the validation month.
- Rivals that are tuned (groups B-D, later): 40 trials each on top-1% weekly recall, grids written here first.

## Group A + F2 (started 2 Nov 2026)

| Method | Inputs | Learner | Seeds |
|---|---|---|---|
| `ref` (ours) | 38 frozen inputs | LightGBM, tuned settings (`lgbm_tuning_step2/tuned_params.json`), balanced class weights | 1-5 averaged |
| `anchor` | 38 frozen inputs | LightGBM defaults, balanced class weights | 1 (no row or column sampling, so the seed changes nothing) |
| `A1_activity` | 37: without `app_score` | as `ref` | 1-5 averaged |
| `A2_raw_app` | 36 activity + `weeks_since_open` + the 35 cleaned application columns (`accounts_tree`) instead of `app_score` | as `ref` | 1-5 averaged |
| `A3_app_only` | `app_score` alone (same score every week) | none: the score itself | - |
| `A4_logistic` | 38 frozen inputs, notebook 04 recipe (median impute + missing flags; log1p of counts and money, shares clipped to [0, 1], self-vs-past z-scores clipped to [-10, 10], standardised) | logistic regression, balanced class weights, max_iter 2000 | - |
| `F2_hybrid_<s>` | `ref`'s scores + the rules' alerts | budget split, below | - |

Ablations keep our tuned LightGBM settings and change only the inputs (decision 2 Nov 2026), so a difference is due
to the inputs.

**F2, rules + model split of the weekly budget** (`evaluation.hybrid`). Week w has budget k_w (the rules' alerts
that week). With model share s, the rules get floor(k_w x (1 - s)) slots: that week's alerts in arrival order (alert
day, then alert id), skipping accounts already flagged. The model gets the remaining slots, including rule slots left
unused, filled with its top-scoring accounts not yet flagged. Every slot flags a different account, as the model
alone does. Shares 0, 0.25, 0.5, 0.75, 1; the pre-registered point is s = 0.5 (s = 1 is `ref` itself).

**F1** (re-ranking only the rules' alerts) is not here: the triage plan (`outputs/modelling/triage/PLAN.md`) covers it.

## Outputs

`outputs/modelling/comparison/v1_full/`: `folds.csv` (one row per method and fold, all measures), `first_flags.csv`
(method, fold, account_id, first flag week at the rules' budget; the input of the paired bootstrap), `MDE.json`.
Out-of-fold scores in `data/v1_full/comparison/` (not committed). Write-up: `notebooks/14_methods_comparison.ipynb`.

## Smallest detectable gain

Recorded 2 Nov 2026 from the reference run (commit 9e1a46f), before any rival was fitted; `v1_full/MDE.json`.

- `ref` on the folds: `catch_rules` 0.473 / 0.450 / 0.440 (the 28-29 Oct seed-spread means were 0.470 / 0.453 /
  0.437); caught 58/64, 58/70, 64/76 mules by week 26.
- Bootstrap SD of `ref`'s `catch_rules`: 0.027 / 0.028 / 0.027 per fold, 0.016 pooled over the 3 folds.
- With 13 rivals (Holm's first bar, two-sided 0.05/13) and 80% power, and treating a rival's errors as independent of
  ours (SD of a difference = sqrt(2) x SD), the smallest detectable pooled gain is **0.085 `catch_rules`**. Pairing
  lowers the real figure, and month 5 adds a 4th cohort; both are recomputed at the 17 Nov gate.
- So on the folds alone a rival must lift `catch_rules` from about 0.45 to about 0.54 to be sure of a win; smaller
  real gains may be missed, and "no winner" means "no gain above about 0.085 ruled in", not "no gain".

## Amendments

(none)
