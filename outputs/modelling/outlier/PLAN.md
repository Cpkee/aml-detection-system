# Outlier detection: plan (written 30 Oct 2026)

A proposal for the team (Kee Chee Pheng, 30 Oct 2026). **Report-appendix work only.** It changes nothing in the
frozen model (`frozen_tuned`), the feature store, the frozen feature list or `configs/sim.yaml`, and it never reads
test months 6–7. Every setting below is fixed **before** any label is looked at, so the result cannot be tuned to
look good.

## Why

Our model learns from the simulator's answer key (`accounts_truth`), which marks all 732 launderers. A real bank
only knows the mules its rules alerted and its investigators confirmed (`aml_outcomes`). Counted on v1_full
(30 Oct 2026, via `amldata.evaluation()`):

| | Launderers | Confirmed by the bank | Never confirmed ("hidden") |
|---|---|---|---|
| All months | 732 | 189 (fake 141, witting 21, unwitting 27) | 543 |
| Training months 0–4 | 455 | 118 | 337 |
| Calibration month 5 | 97 | 23 | 74 |

From the bank's side, the 543 hidden mules look like normal customers. Outlier detection needs no labels, so it
is the natural tool for "suspicious accounts nobody has labelled". Our simulator gives us something a bank never
has: the truth to check whether it finds them.

## Questions

1. **No labels:** can a detector that never sees a label beat the bank's rules at the rules' own weekly budget?
2. **Hidden mules:** of the mules the bank never confirmed, how many does each method find?
3. **Bank labels:** how much does our supervised model lose when it is trained on the bank's own labels
   (confirmed only) instead of the simulator's truth? This is the realistic version of our main result.

## What counts as an outlier

An **account-week** whose money passes through faster, from more payers, than for similar accounts at the same
stage of life or than the account's own past. In the simulator that is the laundering burst (about 2 weeks, 15
SAML-D patterns, forwarded at RUSI speed). Expected blind spots, stated in advance:

- **Mules before they start:** they look normal by design (EDA, 21 Oct 2026: activity adds nothing before the start).
- **Fake accounts at opening:** that is an application signal; out of scope here (the supervised application
  model was already weak, PR-AUC 0.011).
- **Busy but innocent accounts:** the main source of false alarms; peer- and self-relative inputs limit it.

## Methods (all fixed now)

| # | Method | Labels used for training | Status |
|---|---|---|---|
| M0 | Bank's rules R1–R6 | none | exists |
| M1 | `frozen_tuned` (38 inputs) | simulator truth (`mule_by_day`) | exists: the upper reference |
| M1b | `truth_macos`: M1's recipe and settings retrained on this Mac (added 30 Oct 2026) | simulator truth | built 30 Oct: M2's yardstick on the same machine (the recipe gave 63 vs 65 catches on two machines) |
| M2 | Bank-label LightGBM (`bank_label`): same 38 inputs and tuned settings as M1, application score refitted the same way | **confirmed mules only**; every other account counts as normal | built 30 Oct (1,516 mule-weeks vs 8,327) |
| M3 | Rarity score (ECOD-style; was robust z-score, changed 30 Oct 2026) | none | built 30 Oct |
| M4 | Isolation Forest | none | built 30 Oct |
| M5 | Autoencoder (optional, only if M2–M4 are done by 4 Nov) | none | new |

**Inputs for M3–M5** (activity only, behaviour shape, not size; no `app_score`): `passthrough_wk`,
`out_1h_share_wk`, `out_24h_share_wk`, `med_in_out_minutes_wk`, `n_payers_wk`, `n_payees_wk`,
`new_payer_share_wk`, `self_vs_past_money_in`, `self_vs_past_payers`, `self_vs_past_rows`, `peer_ratio_money_in`,
`internal_out_share_cum`, `cash_in_share_cum`, `abroad_out_share_cum`, `high_risk_out_share_cum`,
`out_1h_share_4wk`, `out_24h_share_4wk`, `passthrough_4wk`, `n_payers_4wk` (19). One sensitivity run with all 37
activity inputs is reported beside it, never used to choose.

**Fixed settings:**

- Rows: months 0–4, weeks 0–26, open account-weeks only (`open_by_day = 1`; a bank knows what it closed). The same
  no-peek cut-off as the store.
- Preparation: each input is compared with the training weeks of the same band by rank, not by raw value. A
  missing value (no payment out that week; fewer than 4 past weeks for `self_vs_past_*`) counts as "no evidence"
  (rarity 0, rank 0.5).
- Week bands **0–3, 4–12, 13–26**: each band gets its own reference values and fitted models, because new
  accounts behave differently.
- M3 (**changed 30 Oct 2026, Kee Chee Pheng**, before any label was looked at; was a robust z-score): rarity score
  (ECOD-style, Li et al. 2022). Per input, the share of training weeks in the band at least as extreme, on either
  side (+1 smoothed); rarity = −log10 of it. Score = mean of the 3 largest rarities. Why: the label-free spread
  check found a MAD of 0 for 9 of the 19 inputs in at least one band (`out_1h_share_wk` among them) and tails of
  thousands of MADs, so z-scores would skip the speed shares and be ruled by the longest tail.
- M4: scikit-learn `IsolationForest(n_estimators=300, max_samples=256, random_state=42)` on each input's mid-rank
  within its band (0–1), score = `-score_samples`. Fitted on all account-weeks, mules included: a bank cannot
  remove what it does not know. (Ranks as inputs: changed 30 Oct 2026 with M3.)
- M5: torch, 19 → 8 → 3 → 8 → 19 on the same ranks, ReLU, 20 epochs, Adam 1e-3, seed 42; score = mean squared
  rebuild error.
- M2: label = `mule_by_day` **and** confirmed by the bank at any time in the window (decisions D2, D3). The
  application score is refitted out-of-fold with the same bank label. D2 and D3 decided 30 Oct 2026.
  "Confirmed at any time" = closed by the end of the window: `amldata.labels(..., as_of_day=<after the last
  day>)["open_by_day"] == 0`. The simulator closes an account only after a confirmed alert, so this equals the
  confirmed mules exactly (checked 30 Oct 2026 on v1_full: 32 / 24 / 23 / 22 / 17 / 23 in months 0–5, no normal
  account closed). No `amldata` change is needed (D5).

## Development without labels

Before the single look, only label-free checks are allowed:

- score distributions per week band;
- the 50 highest-scored account-weeks of months 0–4, inspected by their features only;
- runtime;
- two runs give identical scores.

Done for M3 and M4, 30 Oct 2026 (v1_full months 0–4, 4,449,169 open account-weeks, in-sample): rarity fits in 1 s
and scores in 10 s, Isolation Forest 12 s and 36 s; two runs identical; no missing scores; no week ties at its top
score. The rarity score's top weeks are mostly bursts with 14–16 payers passed straight through within hours, and
very large cash deposits; no single input dominates (each is among the 3 rarest in 6–33% of the top 1% of rows,
except `new_payer_share_wk`, 0%). Isolation Forest's top weeks are unusual mixes (cash, abroad and high-risk
shares together).

Scoring chain checked end to end on training month 4 (30 Oct 2026; `evaluation.hidden_mules` counts equal the
harness's). That run showed M3/M4 catch counts on month 4, in-sample; recorded here because the settings must not
change after it, and none did. M2 and M1b trained in 40 s / 35 s with `frozen_tuned`'s settings and 38 inputs.

The settings are then written to `outputs/modelling/outlier/v1_full/settings.json` and committed **before** month 5
is scored.

## Evaluation (one look: month 5, weeks 0–26)

Each method writes `account_id, weeks_since_open, score` for the month-5 cohort. `python -m evaluation.score
--scores PATH` then scores it at the rules' weekly budget with permanent flags, the same as the month-5 dry run
(29,120 accounts, 78 mules by week 26, 124 flags).

1. **Main table** (M0–M5): caught, precision, `recall_final_label`, median days from start, caught by type,
   head-to-head with the rules.
2. **Hidden mules:** the 78 mules split into confirmed by the bank vs never confirmed (`aml_outcomes`), with
   caught per method in each group. A new scoring-only module, `src/evaluation/hidden_mules.py`; the harness stays
   unchanged.
3. **By laundering pattern:** caught per SAML-D pattern (`transactions_truth.laundering_type`, scoring code only).
   This shows which patterns each method sees. It is the cheap version of a held-out-pattern test.
4. **Top false alarms:** the 20 highest-scored normal accounts and the features that drove them (what "unusual
   but innocent" looks like in our data).
5. **Uncertainty:** with 78 mules, a few accounts are noise. Account-level bootstrap (1,000 resamples): a method
   "beats" another only if the 95% interval of the paired difference in caught excludes 0.

## How to read the result (written before it exists)

| Result | Meaning for the report |
|---|---|
| M3/M4 > M0 | Even without labels a bank can beat its rules on this kind of laundering |
| M3/M4 ≈ M0 or below | The supervised result depends on labels; outlier detection alone is not enough |
| M2 close to M1b | Our main result survives realistic labels |
| M2 far below M1b | Our main result is a best case; state it as the main limitation |
| M3/M4 catch hidden mules that M2 misses | Labels and outliers find different mules: a case for combining them |

## Out of scope

- Outlier scores as LightGBM inputs (the feature list is frozen).
- The final test run on months 6–7 (`final_test` lock); this work is not added to it.
- `data/sensitivity/seed__43` (reserved for feature-lab promotion candidates).
- Training with patterns hidden (it needs pattern information in training code; a team decision).
- Application-only outlier detection on the 29 BAF columns.

## Code and files

| Item | Purpose |
|---|---|
| `src/models/outlier.py` | `fit(train, settings)` / `score(df, fitted)` for M3–M5: pure functions |
| `src/models/train.py` | M2: `train --label bank` (`bank_confirmed`); `--params` also takes a model's manifest. Default unchanged |
| `src/evaluation/hidden_mules.py` | sections 2–4 of the evaluation |
| `notebooks/12_outlier_detection.ipynb` | the write-up |
| `tests/test_outlier.py` | the fit reads months 0–4 only; identical scores twice; months 6–7 refused; the hidden-file guard passes |
| `outputs/modelling/outlier/v1_full/` | `settings.json`, score files' sha256, `report.md`, CSVs |

## Decisions for the team

| # | Decision | Recommendation |
|---|---|---|
| D1 | Appendix only, month 5 only, not in the final test run | **Decided 30 Oct 2026 (Kee Chee Pheng): month 5 only** |
| D2 | When the bank "knows" a mule: confirmed at any time in the window, or only by a fixed training date | **Decided 30 Oct 2026 (Kee Chee Pheng): any time** (separates incomplete labels from late labels; simpler) |
| D3 | M2's mule weeks for a confirmed account: from its true start (investigators rebuild the timeline), or from the bank's first alert | **Decided 30 Oct 2026 (Kee Chee Pheng): true start** |
| D4 | Include the autoencoder M5 | only if M2–M4 are done by 4 Nov |
| D5 | Code additions outside `src/models/` | **Decided 30 Oct 2026 (Kee Chee Pheng):** no `amldata` change (M2's bank label comes from the existing `open_by_day`, a new use of it as a label); only `src/evaluation/hidden_mules.py`, inside the data rules. Team informed |

## Timeline (around the 4–5 Nov calibration and test run, which take priority)

| Date | Step |
|---|---|
| 30–31 Oct | D1, D2, D3, D5 decided 30 Oct; team decides D4 |
| 31 Oct – 3 Nov | Build M2–M4, tests, label-free checks; commit `settings.json` |
| 4–5 Nov | Pause (calibration, final test run) |
| 6 Nov | The one look on month 5; M5 if agreed |
| 7–9 Nov | Notebook, `report.md`, appendix text |
| 10 Nov | Into the report draft (final 11 Nov) |

Owner: to be agreed.

## Caveat for the report

The store's 28 features were chosen in Phase 1 by looking at labels, so even the "label-free" detectors benefit
from knowing what laundering looks like. A bank with truly no labels would start from more generic features.
