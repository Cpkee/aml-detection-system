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
| M3 | Rarity score: per input the tail share in its suspicious direction, mean of the 3 rarest (was robust z-score, then two-sided; see the review below) | none | built 30 Oct |
| M3s | `rarity_sum`: ECOD's own aggregation, the sum over all 19 inputs; a fixed side-by-side comparison, never used to choose (added 30 Oct 2026) | none | built 30 Oct |
| M4 | Isolation Forest | none | built 30 Oct |
| M5 | Autoencoder | none | **not included** (D4, decided 31 Oct 2026): further work |

**Inputs for M3–M4** (activity only, behaviour shape, not size; no `app_score`): `passthrough_wk`,
`out_1h_share_wk`, `out_24h_share_wk`, `med_in_out_minutes_wk`, `n_payers_wk`, `n_payees_wk`,
`new_payer_share_wk`, `self_vs_past_money_in`, `self_vs_past_payers`, `self_vs_past_rows`, `peer_ratio_money_in`,
`internal_out_share_cum`, `cash_in_share_cum`, `abroad_out_share_cum`, `high_risk_out_share_cum`,
`out_1h_share_4wk`, `out_24h_share_4wk`, `passthrough_4wk`, `n_payers_4wk` (19). One sensitivity run with all 37
activity inputs is reported beside it, never used to choose.

**Fixed settings:**

- Rows: months 0–4, weeks 0–26, open account-weeks only (`open_by_day = 1`; a bank knows what it closed). The same
  no-peek cut-off as the store.
- Preparation: each input is compared by rank, not by raw value, with the training account-weeks of the same week
  since opening. A missing value (no payment out that week; fewer than 4 past weeks for `self_vs_past_*`) counts as
  "no evidence" (rarity 0, rank 0.5).
- **One reference per week since opening (0, 1, …, 26)** (changed 30 Oct 2026, Kee Chee Pheng; was bands 0–3,
  4–12, 13–26): each account-week is compared with accounts of exactly the same age.
- M3 (changed 30 Oct 2026, Kee Chee Pheng; first a robust z-score, then two-sided tails): rarity score. Per input,
  the share of training weeks at least as extreme **in its suspicious direction**: high for 18 inputs, low for
  `med_in_out_minutes_wk` (fast forwarding) (+1 smoothed); rarity = −log10 of it. Score = mean of the 3 largest
  rarities. The tail shares follow ECOD (Li et al. 2022); the fixed directions and the top-3 mean depart from it
  (ECOD picks each tail by skewness and sums all inputs). Why not z-scores: a MAD of 0 for 9 of the 19 inputs in
  at least one band (`out_1h_share_wk` among them) and tails of thousands of MADs.
- M3s (`rarity_sum`): the same rarities summed over all 19 inputs (ECOD's aggregation).
- M4: scikit-learn `IsolationForest(n_estimators=300, max_samples=256, random_state=42)` per week since opening, on
  each input's mid-rank (0–1), score = `-score_samples`. Fitted on all account-weeks, mules included: a bank cannot
  remove what it does not know. Direction-free by design.
- M5 (not included, D4 31 Oct 2026; the design is kept for the further-work note): torch, 19 → 8 → 3 → 8 → 19 on
  the same ranks, ReLU, 20 epochs, Adam 1e-3, seed 42; score = mean squared rebuild error.
- M2: label = `mule_by_day` **and** confirmed by the bank at any time in the window (decisions D2, D3). The
  application score is refitted out-of-fold with the same bank label. D2 and D3 decided 30 Oct 2026.
  "Confirmed at any time" = closed by the end of the window: `amldata.labels(..., as_of_day=<after the last
  day>)["open_by_day"] == 0`. The simulator closes an account only after a confirmed alert, so this equals the
  confirmed mules exactly (checked 30 Oct 2026 on v1_full: 32 / 24 / 23 / 22 / 17 / 23 in months 0–5, no normal
  account closed). No `amldata` change is needed (D5).

## Development without labels

Before the single look, only label-free checks are allowed:

- score distributions by account age;
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
harness's). **Disclosure:** that run printed in-sample catch counts on month 4 (bands and two-sided version: rarity
19, Isolation Forest 9, rules 21 of 76 mules). Two settings changed after it (week references and direction,
below). Those changes come from label-free checks run by review agents that never saw these counts, and each has a
label-free reason recorded below; still, they were made after the counts were seen. M2 and M1b trained in 40 s /
35 s with `frozen_tuned`'s settings and 38 inputs.

Re-run with the reviewed settings (30 Oct 2026, same rows): rarity 1 s fit / 9 s score, rarity_sum the same,
Isolation Forest 15 s / 41 s; two runs identical; no missing scores. Ties: one week has 2 account-weeks tied at its
top rarity score; 8 of the 675 rows in the weekly top 25s share a score (the harness breaks ties by account id and
reports them). Rarity's top weeks are fan-in bursts (13–16 payers, money forwarded within hours); the inputs among
the 3 rarest in its top 1% are now led by the speed shares (`out_1h_share_4wk` 34%, `med_in_out_minutes_wk` 28%,
`out_1h_share_wk` 25%) and abroad / high-risk (21–24%); `passthrough_wk` 0% and `passthrough_4wk` 6% (were driven
by their innocent low side).

## Review of the judgment calls (30 Oct 2026)

Five review agents checked the five judgment calls in parallel. The outlier settings were judged without labels (by
the published method, label-free statistics and stability); M2's settings only with the bank's own labels on
months 0–4. No agent read months 5–7. Scripts and outputs: session scratchpad (not committed). Decided by Kee Chee
Pheng, 30 Oct 2026.

| # | Judgment call | Finding | Decision |
|---|---|---|---|
| 1 | Two-sided rarity | Half of the top 1% had a low-side input among its 3 rarest, mostly innocent (money kept: `passthrough_*`; accounts going quiet). In the weekly top 0.05%, 20% were there partly for such a low side. ECOD's skewness rule would pick the innocent low tail of pass-through and the slow tail of forwarding time | **Changed:** fixed direction, high for 18 inputs, low for `med_in_out_minutes_wk`. Matches this plan's definition and the rules R3 / R4. ~17% of the weekly top 0.05% changes |
| 2 | Mean of the 3 rarest | ECOD, COPOD and HBOS all sum over every input. Summing adds ~0.3 per non-missing input even when nothing is unusual, so it favours busy, ordinary accounts (27% of its top 25s have no input rarer than 1 in 1,000 vs 0.3%); K = 1 is fragile (top-5 stability 0.69 vs 0.86) | **Approved** (K = 3). ECOD's sum added as M3s, reported beside it |
| 3 | Bands 0–3 / 4–12 / 13–26 | Weeks 0–3 never settle (4-week windows fill up; week 0 vs its band KS 0.43); week 4 is a real edge (`self_vs_past_*` start); nothing supports the 12/13 cut (a monthly bill cycle runs through weeks 4–26). ~165k account-weeks per week is enough for each reference | **Changed:** one reference per week. ~14% of the rarity top 1% changes (about one flag a week); for Isolation Forest no more than a seed change |
| 4 | The 19 inputs | No pair above 0.73 at the extremes; none tied to income beyond ±0.11 except `passthrough_4wk` (−0.3); each of the 15 SAML-D shapes covered by at least one input; cash smurfing and cash withdrawal (4% of shape weight) only partly, and the store features that would add them mostly re-count activity | **Approved** (unchanged) |
| 5 | M2 keeps M1's tuned settings | On bank labels, 3 temporal folds: frozen settings 0.507 catch at the rules' budget vs 0.492–0.499 for min_child_samples 500 / 200 and num_leaves 31, all within noise (bootstrap 0.034–0.061 per fold); the trees use every leaf, so min_child_samples 2000 does not bind | **Approved** (unchanged). Caveat for the report: every bank-confirmed mule was first alerted by the rules, so bank labels teach "find the rules' mules, earlier"; M2's real test is the month-5 look against the truth |

The settings are then written to `outputs/modelling/outlier/v1_full/settings.json` and committed **before** month 5
is scored.

## Evaluation (one look: month 5, weeks 0–26)

Each method writes `account_id, weeks_since_open, score` for the month-5 cohort. `python -m evaluation.score
--scores PATH` then scores it at the rules' weekly budget with permanent flags, the same as the month-5 dry run
(29,120 accounts, 78 mules by week 26, 124 flags).

1. **Main table** (M0–M4): caught, precision, `recall_final_label`, median days from start, caught by type,
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
| `src/models/outlier.py` | `fit(train, settings)` / `score(df, fitted)` for M3–M4: pure functions |
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
| D4 | Include the autoencoder M5 | **Decided 31 Oct 2026 (Kee Chee Pheng): not included.** Like Isolation Forest it scores unusual combinations without a suspicious direction, so it would mostly repeat M4 on 19 ranked inputs, and its open settings (one network per week or pooled, deterministic torch) could not be reviewed before the 3 Nov freeze. Isolation Forest is our "unusual combination" method (fewer settings); the autoencoder is named as further work |
| D5 | Code additions outside `src/models/` | **Decided 30 Oct 2026 (Kee Chee Pheng):** no `amldata` change (M2's bank label comes from the existing `open_by_day`, a new use of it as a label); only `src/evaluation/hidden_mules.py`, inside the data rules. Team informed |

## Next steps (updated 31 Oct 2026; PR #47 merged)

1. ~~Team reviews this plan and PR #47; decides D4 (autoencoder) by 4 Nov.~~ PR #47 merged; D4 decided 31 Oct
   (not included).
2. ~~3 Nov, freeze~~ **done 31 Oct 2026, 18:24** (early: nothing was left to decide): `python -m
   evaluation.outlier_look freeze --out data/v1_full` wrote `outputs/modelling/outlier/v1_full/settings.json`
   (outlier settings + sha256 of each model's files, code commit `2d0f91f`) and copied the M1b / M2 model files to
   `outputs/modelling/models/v1_full/<name>/` (shared, as `frozen_tuned`); both committed. No setting changes after
   this.
3. 4–5 Nov: pause (calibration, final test run).
4. ~~6 Nov~~ **the one look, done 31 Oct 2026, 19:03–19:04** (Kee Chee Pheng; earlier than planned, before the
   final test run): `check` passed, then `look` on commit `39119ed` (the committed freeze, merged in PR #49 at
   19:02); results in PR #50. The settings were frozen and committed first, so the pre-registration holds; only the
   date moved. It reads month 5 only and changes nothing in the frozen model or the final test. It wrote the six
   score files, the harness on each (weeks 0–26) and `evaluation.hidden_mules` on all six
   (`outputs/modelling/outlier/v1_full/`). First reading (month 5, 78 mules by week 26, 124 flags): rules 16,
   M1 `frozen_tuned` 63 (equals `month5_dryrun_v2`), M1b `truth_macos` 63, M2 `bank_label` 54, M3 `rarity` 16, M3s
   `rarity_sum` 39, M4 `iforest` 16. Against "How to read the result": M3 / M4 ≈ the rules (difference 0, 95%
   interval −10 to 11); M2 below M1b by 9 (interval 2 to 16) but 38 above the rules; never-confirmed mules caught
   (of 62): rules 3, M1 50, M2 42, M3 12, M4 13; M3 / M4 catch 8 mules M2 misses (union of their flags, so twice
   the budget). `rarity_sum` (side by side only, never used to choose) beats the rules by 23 (interval 12 to 33).
5. 7–9 Nov: `notebooks/12_outlier_detection.ipynb`, `report.md`, appendix text, read against "How to read the result".
6. 10 Nov: into the report draft.

## Timeline (around the 4–5 Nov calibration and test run, which take priority)

| Date | Step |
|---|---|
| 30–31 Oct | D1, D2, D3, D5 decided 30 Oct; D4 decided 31 Oct (no autoencoder) |
| 31 Oct – 3 Nov | Build M2–M4, tests, label-free checks; commit `settings.json` (frozen 31 Oct) |
| 4–5 Nov | Pause (calibration, final test run) |
| ~~6 Nov~~ 31 Oct | The one look on month 5 (done 31 Oct) |
| 7–9 Nov | Notebook, `report.md`, appendix text |
| 10 Nov | Into the report draft (final 11 Nov) |

Owner: to be agreed.

## Caveat for the report

The store's 28 features were chosen in Phase 1 by looking at labels, so even the "label-free" detectors benefit
from knowing what laundering looks like. A bank with truly no labels would start from more generic features.
