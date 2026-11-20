# Changelog

Changes to the simulator and the data it generates, newest first. Settings changes are also noted in the
`source` of each value in `configs/sim.yaml`; decisions are recorded in the "Simulated Dataset: Logic,
Assumptions and Use" doc.



## 19 Nov 2026 — Methods comparison: interim paired tests now include group B (B1 XGBoost, B2 CatBoost)

No change to the data, the store, the feature list or the model of record; folds 1-3 only (months 0-4), computed from
the committed `first_flags.csv`. `python -m models.comparison --interim` (new; the table was first made by hand on
19 Nov) rewrites `comparison/v1_full/interim_paired_tests_folds.csv` for every rival in `first_flags.csv`: the 13
earlier rows keep the same gain, interval and p. B1 XGBoost: gain -0.003 (95% -0.017 to +0.010, p 0.60), ahead in 1 of
3 folds. B2 CatBoost: -0.049 (-0.076 to -0.024). No rival wins. With 15 rivals instead of 13, Holm's bar is stricter:
A4c (p 0.009) no longer passes it, so it is no longer counted as significantly worse than ours (its gain is unchanged).
`wins_on_folds` is now written down in code: gain above 0.012, passes Holm, ahead in at least 2 of the 3 folds (the
plan's "3 of 4 cohorts" read for the folds alone).

## 19 Nov 2026 — New sensitivity dataset `forward_delay_shares__1` (patient launderers); Variant II scored

- New dataset `data/sensitivity/forward_delay_shares__1` (robustness plan Amendment 2): forwarding-delay shares
  0.05 / 0.10 / 0.35 / 0.50 instead of RUSI's 0.28 / 0.25 / 0.32 / 0.15, set with `--set` only. An unsourced
  assumption, approved 19 Nov 2026 by Kee Chee Pheng; `configs/sim.yaml` unchanged. 244,000 accounts, seed 42, rules
  frozen at 1.516, built from commit c4e47d8; 10/10 checks pass. Rules: 3,572 alerts, 94.4% false alarms, 199 of 732
  launderers alerted (27%), median 8 days. Store, cleaned tables and `robust_avg5` built; months 6-7 scored once
  (locked). The folder is kept whole, like the 7 robustness runs (the amendment said large files would be deleted).
- `data/variant_II`: no data change; `robust_avg5` trained on its months 0-4 and months 6-7 scored once (locked).
- No change to v1_full, the main data or the model of record.

## 19 Nov 2026 — Methods comparison: G1_graphsage and A4c_logistic_inter on the training folds (Keith Tan)

No change to the data, the store, the feature list or the model of record. Two rivals added to
`outputs/modelling/comparison/PLAN.md` as dated amendments (G1 approved by Kee Chee Pheng; A4c labelled post hoc) and
run on folds 1-3 only (months 0-4; months 5-7 untouched). G1 (2-layer GraphSAGE on payment links): `catch_rules`
0.434 / 0.451 / 0.465 vs ref 0.473 / 0.450 / 0.440, pooled gain -0.004 (95% -0.035 to +0.025). A4c (logistic with 4
share x money interactions): 0.447 / 0.412 / 0.392, gain -0.038 (-0.066 to -0.010). Interim paired tests of every
rival vs ref (folds only): `comparison/v1_full/interim_paired_tests_folds.csv`; no rival wins. Out-of-fold scores in
`data/v1_full/comparison/` (not committed).

## 16 Nov 2026 — Methods comparison, group B: B1 XGBoost and B2 CatBoost on the 3 training folds

No data, simulator, setting, feature store or model-of-record change; months 0-4 only (month 5 and months 6-7 not
read). `requirements.txt` gains xgboost 3.4.1 and catboost 1.2.10 (team decision, Kee Chee Pheng 16 Nov). Plan
amendment committed before any fit (`outputs/modelling/comparison/PLAN.md`, 16 Nov, commit 839bed6): same rows,
label, folds, 38 inputs and app score as `ref`; balanced row weights; 40-trial random search each on top-1% weekly
recall (seed 42, trial 0 = defaults, no early stopping); final fit seeds 1-5 averaged. Code `models.comparison --tune`,
run 16 Nov 02:56-05:32 on this Mac (commit b33d763). Winners: XGBoost trial 34 (weekly recall 0.423; 100 trees,
15 leaves, both the smallest values searched), CatBoost trial 38 (0.402). `catch_rules` per fold at the rules'
budget, `ref` 0.473 / 0.450 / 0.440: B1 0.466 / 0.460 / 0.427 (caught 179 of 210, `ref` 180), B2 0.397 / 0.423 /
0.396 (163 of 210). Win rule not applied: it is pooled with month 5 under Holm, at the comparison gate. Outputs:
`outputs/modelling/comparison/v1_full/folds.csv`, `first_flags.csv`, `tuning/<method>_trials.csv` + `_best.json`;
scores in `data/v1_full/comparison/` (not committed).


## 16 Nov 2026 — Fake-mix stress plan closed (no run)

No data, model or result change. The draft plan `outputs/modelling/stress/PLAN.md` (5 Nov, never agreed, never run)
overlapped robustness run 2, which had already scored `in_window_mix__1` once (model 99 vs rules 30 of 124 mules,
lead 0.56, holds). Decision (Kee Chee Pheng, 16 Nov): the plan is closed as answered by that run; `in_window_mix__2`
and `seed__43` are not run. The differences between the two plans are listed in the plan's Amendment 1.

## 16 Nov 2026 — Budget check: rule alerts vs distinct accounts (month 5 only)

No data, model, harness or result change. The harness's weekly budget counts rule alerts; the rules can alert one
account more than once, so the model flags a few more distinct accounts than the rules (month 5, weeks 0-26: 124 vs
119; final test: 280 vs 264). New `python -m evaluation.budget_check` scores month 5 again with the budget capped at
the accounts the rules alerted for the first time each week -> `outputs/modelling/results/v1_full/budget_check_m5/`.
Result: the model catches the same mules under both budgets (65 of 78, weeks 0-26; 79 of 97, weeks 0-77); precision
0.524 -> 0.546, weekly catch mean 0.384 -> 0.379. Test months not read (the script refuses them); the committed
harness and the headline are unchanged. For the report: one sentence in the evaluation section.

## 5 Nov 2026 — Robustness checks (plan approved by Kee Chee Pheng, `outputs/modelling/robustness/PLAN.md`)

No change to the simulator, settings, v1_full or the model of record. Seven sensitivity datasets are rebuilt from
their `run_manifest.json` where needed, each gets its own feature store, cleaned tables and a `robust_avg5` model
(recipe of `frozen_tuned_avg5`, trained on its own months 0-4), and its months 6-7 are scored once
(`results/<name>/final_test/`, locked). Lead = (model caught - rules caught) / mules, weeks 0-26
(`python -m evaluation.robustness`); results in `outputs/modelling/robustness/report.md` and `summary.csv`.
- Run 1 `seed__44` (no rebuild; 10/10 checks, alerts as in its summary): model 114 vs rules 35 of 145 mules, lead
  0.54 (95% 0.47-0.62) vs headline 0.43 -> chance band 0.31-0.55.
- Run 2 `in_window_mix__1` (rebuilt: 10/10 checks, summary identical): model 99 vs rules 30 of 124 mules, lead
  0.56 (95% 0.46-0.66): holds.
- Runs 3-7 (6 Nov; rebuilt, 10/10 checks, summaries identical), lead (95%): repeated bursts 0.46 (0.37-0.54) holds;
  fakes start 150-210 days 0.37 (0.30-0.45) holds; fakes start 15-45 days 0.39 (0.31-0.49) holds; GBP 1,500 transfers
  0.17 (0.10-0.24) shrinks (rules 120 of 163); young fake ages 0.50 (0.42-0.58) holds. No scenario fails.

## 3 Nov 2026 — GraphSAGE on the payment graph: code and tests only (Keith Tan; proposal, not pre-registered)

No data change, no model change, no result. `src/models/gnn.py` + `tests/test_gnn.py` (8 tests on hand-made graphs).
- **What:** a 2-layer GraphSAGE (mean aggregator, plain PyTorch) on account-weeks. Links = payments between two
  accounts of the bank (`features/graph_edges.parquet`) on or before the focal week's cut-off; a neighbour enters as
  its own latest week with a cut-off no later than that (never later). Neighbours may have opened in any month
  (decided 3 Nov 2026); only their public inputs are read, never a label. Node inputs = the 38 frozen inputs;
  fixed settings in `gnn.DEFAULTS` (not tuned). `gnn.method(out)` is the methods comparison's `fit(train, valid)`.
- **Tests:** neighbour rules equal a plain-Python version; payments after day D change no state with a cut-off on or
  before D, at either level; preprocessing fitted on training rows only; learns a signal only the neighbours carry
  (AUC ~0.99 with links, ~0.51 without); same seed gives identical scores; validation labels never read.
- **Plumbing check on `data/v1` (no labels, random-label timing only):** `python -m features graph --out data/v1`
  93 s. 76% of focal account-weeks (months 0-4, weeks 0-26) have at least one neighbour (median 3, max 19); a
  third of neighbour accounts opened in months 5-7. One epoch, one seed, fold-3 size: 75 s, so the full method
  (4 epochs x 5 seeds x 3 folds) is ~1 h on v1 and ~4-5 h on v1_full.
- **Next:** runs on the folds only after the methods comparison adds it as a dated amendment; judged on catch_rules.

## 2 Nov 2026 — Counted re-tests of the test months (decision by Kee Chee Pheng)

No data change, no model change, no change to any result. The test months may be re-used to judge well-justified
improvements, stated as a limitation in the report; the first final test stays the headline.
- `python -m evaluation.score --months 6 7 --final-test --model M --retest "REASON"` scores into a new folder
  `results/<data>/final_test_r<N>/` (never `final_test/`). Before anything about months 6-7 is read it appends a row
  to `results/<data>/final_test_looks.csv` (look, folder, started, score_source, git_commit, reason), so a crashed or
  unhelpful look still counts. Refused before the first final test is locked, without a reason, or with uncommitted
  code. The report and `settings.json` (`retest_reason`) mark the run as a re-test.
- Rules (CLAUDE.md, Phase 5): the change and its months 0-5 evidence are written and committed before the look; one
  look per change; never choose among changes by their months 6-7 scores; report every look.
- `results/v1_full/final_test_looks.csv` starts with look 1 = the final test below. Test:
  `test_retest_is_counted_before_any_read_and_never_overwrites`.

## 2 Nov 2026 — Final test on months 6-7 (run once; Kee Chee Pheng, moved forward from 5 Nov)

No data change, no model change. `python -m evaluation.score --out data/v1_full --months 6 7 --final-test` with the
model of record `frozen_tuned_avg5` at commit 9e748c8 (no uncommitted changes) -> `outputs/modelling/results/v1_full/
final_test/` (`LOCK.json` written: never re-run; later looks are counted re-tests, entry above). Cohort 50,061 accounts.
- **Weeks 0-26** (163 mules by week 26): model 120 caught vs rules 50 (recall 0.736 vs 0.307; precision 0.429 vs
  0.189; 280 model flags vs 264 rule alerts); by the final label 0.667 vs 0.278. Both 43, model only 77, rules only 7,
  neither 36; when both catch a mule the model is first 26 times, the rules 13 (median 2 days earlier); model-only
  catches at least 91 days earlier (median). 2 model flags before laundering started. By type: fake 109/147 vs
  46/147, witting 8/11 vs 3/11, unwitting 3/5 vs 1/5.
- **By opening month:** model recall month 6 0.774, month 7 0.686 (rules 0.323 / 0.286); month 7 holds 43% of the
  mules and 37% of model flags: the drift notebook 11 warned of, smaller than feared.
- **Weeks 0-77** (180 mules, appendix): model 138 vs rules 59 (0.767 vs 0.328).

## 2 Nov 2026 — Model of record: 5-seed average `frozen_tuned_avg5` (decided 30 Oct, confirmed 2 Nov, Kee Chee Pheng)

No data change. New model of record; `frozen_tuned` and its results stay committed for comparison.
- **Why:** notebook 10's pre-registered rule (average 5 seeds if the seed SD of `catch_0.1pct` > 0.005 in any fold;
  it was 0.006-0.008 in all 3). The tuned settings sample 92% of rows and 90% of inputs per tree, so a single seed's
  flags at the rules' small budget depend partly on chance.
- **What:** the tuned settings (tuning step 2) fitted with LightGBM `random_state` 1-5 on the same rows and the same
  application score (out-of-fold split seed 42, as notebook 10 measured); score = mean of the 5 probabilities.
  `python -m models train --name frozen_tuned_avg5 --params .../tuned_params.json --tree-seeds 1 2 3 4 5` (110 s,
  this Mac). Files `lgbm_seed1-5.txt`, `app_logreg.json`, `manifest.json` (`tree_files`, `tree_seeds`,
  `app_score_seed`), `calibration.json` (isotonic, refitted on month 5: out-of-fold Brier 0.00180) in
  `outputs/modelling/models/v1_full/frozen_tuned_avg5/`. `train.MODEL_OF_RECORD` is now the default of `predict`,
  `calibrate` and `evaluation.score`.
- **Code:** `models.train.load` returns a list of boosters and `predict` averages them; a single-model folder
  (`lgbm.txt`) works as before: `frozen_tuned` re-scored on month 5 with the new code reproduces every result file of
  `month5_dryrun_v2`. `load` refuses a folder whose LightGBM files differ from the manifest's. Test:
  `test_seed_average_is_the_mean_of_its_seeds`.
- **Month 5 dry run** (`results/v1_full/month5_dryrun_frozen_tuned_avg5/`), weeks 0-26: model 65 of 78 mules caught
  (recall 0.833, precision 0.524) vs rules 16 (frozen_tuned: 63, 0.508); no flag before laundering starts; weeks
  0-77: 79 of 97 (frozen_tuned 76). Seed spread (`results/v1_full/month5_seed_spread/`): each seed alone catches 63-65
  of 78, so 1-2 mules between single-seed runs is chance.
- **Committed 2 Nov** (built 30 Oct on an older `main`, merged with today's `main`: bank label, by-month table,
  outlier appendix). Checks before the final test, this Mac, same data copy (`run_manifest.json` 4ce1c4fb...):
  retraining with the merged code (`--params .../frozen_tuned/manifest.json --tree-seeds 1 2 3 4 5`, 86 s) gives the
  5 tree files and `app_logreg.json` byte-identical to the committed ones; re-fitting the calibration gives the same
  `calibration.json`; the month-5 dry run with today's harness (`results/v1_full/month5_dryrun_avg5_v2/`, adds
  `by_month_w<W>.csv`) gives every other result file identical to `month5_dryrun_frozen_tuned_avg5`.

## 31 Oct 2026 — Harness: by-opening-month table; final-test rehearsal on data/v1 (Emmy Li)

No data change, no model change, no change to any existing result value.
- **By opening month:** `evaluation.score` writes `by_month_w<W>.csv` and a report section (per policy and opening
  month: accounts, mules, caught, recall, flags, precision, and each month's share of the cohort's accounts, mules and
  flags). Added before the final test because notebook 11 found month-7 accounts get too few top application scores
  when ranked with month 6 (`velocity_*` drift); a month whose share of flags is far below its share of mules is being
  under-ranked. Month 5 of v1_full re-run: the 7 existing result files are identical to `month5_dryrun_v2`.
- **Rehearsal of the final test** on `data/v1` (50k, not the main data; v1_full untouched): a stand-in model
  `rehearsal_tuned` trained on v1 months 0-4 with `frozen_tuned`'s settings (`models train --params
  .../frozen_tuned/manifest.json`), then the 5 Nov command `evaluation.score --months 6 7 --final-test` on it.
  It ran end to end in 5 s (1.2 GB): `STARTED.json` before the read, `LOCK.json` after, all files including
  `by_month`; a second run, by model or by `--scores` file, is refused. Records: `outputs/modelling/results/v1/final_test/`,
  `outputs/modelling/models/v1/rehearsal_tuned/`. Numbers there are a code check only (22 mules), not a result.
  For 5 Nov: commit first (`settings.json` records `git_uncommitted_changes`).

## 30 Oct 2026 — Feature selection for the report appendix (notebook 13)

No data change, no feature-store change, **no change to the 38 frozen inputs** (decision 28 Oct 2026). Report-appendix
evidence: does each frozen input earn its place? (Keith Tan)
- `notebooks/13_feature_selection.ipynb` (`python -m features select [--out D]`, helpers `src/models/feature_selection.py`)
  -> `outputs/modelling/feature_selection/`. The tuned model (tuning step 2's `tuned_params.json`), months 0–4, the
  lab's 3 folds: single-feature AUCs, near-duplicate groups (|Spearman| >= 0.8 for every pair, an assumption),
  grouped permutation importance on **weekly recall and catch_rules** (same shuffles, 3 per fold; single inputs,
  near-duplicate groups, families), gain and mean |SHAP|. Label per input: needed (a shuffle costs at least 0.005
  weekly recall or 0.010 catch_rules in all 3 folds; assumptions, catch_rules' line twice as high because its measured
  noise is about twice as large) / covered by a near-copy / mixed / weak.
- v1_full: 15 needed, 9 covered by a near-copy, 14 weak. Most relied on: `app_score` (weekly recall −0.157 when
  shuffled; catch_rules −0.032), `out_1h_share_4wk` (−0.085; **−0.260 at the rules' budget**, where it carries the
  model), `n_payers_cum`, `weeks_since_open`, `internal_out_share_cum`, the running totals; `money_in_4wk` and
  `n_rows_4wk` matter at the rules' budget. Baseline per fold: weekly recall 0.428 / 0.397 / 0.470, catch_rules
  0.464 / 0.455 / 0.436 (the rules' own alerts 0.146 / 0.132 / 0.143).
- Refit checks (`feature_lab --drop ... --together --params tuned_params.json`, v1_full, vs the tuned 38-input model:
  weekly recall 0.426 pooled, catch_rules 0.452, PR-AUC 0.876, first catch within 2 weeks 0.966):
  - without the 14 weak inputs (24 left): weekly recall 0.431 (+0.009 / +0.005 / −0.000), catch_rules 0.452
    (+0.009 / +0.002 / −0.010), both 'no clear change'; first catch within 2 weeks unchanged; PR-AUC 0.838, 'worse'
    (−0.041 / −0.039 / −0.034); one unwitting mule fewer caught at the rules' budget (15 vs 16 of 18).
  - also without 8 spare near-copies (16 left): weekly recall 0.421, 'worse' (−0.001 / −0.001 / −0.006);
    catch_rules 0.446 (no clear change); first catch within 2 weeks 0.942 (−0.016 / −0.057 / 0.000); PR-AUC 0.848.
  - Reading: the 14 weak inputs add nothing to earliness at either budget but carry account-level ranking (PR-AUC);
    the near-copies add early catching. Dropping inputs gains nothing measurable, which supports keeping all 38.
    The weekly-recall and catch_rules differences above are the size of the tuned model's seed spread (5 seeds, SD
    0.004–0.008 and 0.005–0.010 per fold; `outputs/modelling/models/v1_full/stability/exp2_seed_spread.csv`), so
    they are chance-level; only the PR-AUC fall (0.034–0.041 in every fold) is larger. All numbers here are from one
    Windows machine's copy of `data/v1_full` (the stability notebook's advice: compare runs on one machine).
    The analysis uses the tuned single-seed LightGBM (seed 42); the model of record since 2 Nov 2026 averages
    5 seeds (`frozen_tuned_avg5`), which leaves the inputs, and so this appendix's question, unchanged.
- Earlier runs on the untuned model (27 Oct, notebook then numbered 07; trials `drop-weak-v1_full`,
  `drop-weak-and-copies-v1_full` in the ledger) gave the same picture; the 50k copy was not rerun.
- Code: `feature_lab --drop NAME... [--together]` (families or single inputs left out) and `--params FILE` (LightGBM
  settings, as `models train`; defaults unchanged); `feature_selection.permutation_drop` scores several measures on the
  same shuffles; `run_notebook(..., timeout=)` (12 h for `select`; the notebook saves each finished fold under
  `<data>/features/feature_selection_cache/` and resumes); the ledger writer handles CRLF line ends (Windows);
  `tests/test_hidden_files.py` reads files as UTF-8 (Windows). Tests: `tests/test_feature_selection.py`.

## 30 Oct 2026 — Harness gaps closed (Phase 5, approved by Kee Chee Pheng)

No data change, no model change, no change to any existing result value: result files gain columns only. Re-run of
the month-5 dry run (`outputs/modelling/results/v1_full/month5_dryrun_v2/`): every column of the committed
`month5_dryrun_frozen_tuned` comes out identical (launderers.csv byte-identical).
- **Scores from a file:** `python -m models predict --out D [--model M] --months 5 [--weeks 0-77] [--to PATH]` writes
  `<out>/scores/<model>_m<months>.parquet` (account_id, weeks_since_open, score; data, git-ignored);
  `python -m evaluation.score --scores PATH` scores any such file (`score.load_scores` refuses duplicate
  account-weeks, accounts outside the cohort, weeks other than whole numbers 0-W and missing scores; warns on unscored account-weeks).
  Month 5 via the file gives byte-identical result CSVs to the model path. Test months still need `--final-test`.
- **New measures:** `recall_final_label` in `summary_w<W>.csv` (caught / all cohort launderers by the fixed final
  label: month 5, weeks 0-26: model 0.649, rules 0.165, vs recall 0.808 / 0.205 against mules by week 26);
  `median_min_days_earlier_model_only` in the head to head (launderers only the model catches: days from its flag to
  the end of the horizon, "at least this much earlier": 84 days for weeks 0-26, 49 launderers); `tied_at_cut` in
  `weekly_w<W>.csv` (accounts tied at each week's cut line, decided by account id: none on month 5).
- **Any-time policy:** reported for horizons up to week 26 only; past week 26 the report marks it not meaningful
  (the model is trained on weeks 0-26) and no longer calls it an upper bound. Its rows stay in the CSV files. Report
  wording on this and on the budget (124 alerts vs 119 accounts, month 5, weeks 0-26) taken from draft PR #42.
- **Final-test guard:** a final run writes `outputs/modelling/results/<data>/final_test/STARTED.json` before it reads
  anything about months 6-7 and is refused while `STARTED.json` or `LOCK.json` exists (clearing it is a team decision);
  a missing `--scores` file is refused before `STARTED.json` is written.
- **Provenance in settings.json:** `score_source` (`model:<name>` or `file:<path>`), `scores_sha256`,
  `run_manifest_sha256`, `git_commit`, `git_uncommitted_changes`.
- `python -m models verify` compares only the reference run's columns, so the committed reference still verifies.

## 29 Oct 2026 — Share one model file between machines (option B)

No data change, no result change. Li Ann's `frozen_tuned` (Windows, 16 threads) and a retrain on Emmy Li's Mac
(8 threads) differ slightly (63 vs 65 of 78 month-5 mules), but **scoring a given model file is the same on both**:
her `lgbm.txt` + `app_logreg.json`, scored on the Mac, reproduce her committed `month5_dryrun_frozen_tuned` file for
file (summaries, weekly tables, every launderer's flag week). So the team can train once and share the model files.
- `python -m features fingerprint` (`src/features/fingerprint.py`): content fingerprints (row count + exact sum of
  each row's MD5) of the files a model reads, independent of parquet bytes and row order; cached in
  `features/fingerprints.json`. v1_full on the Mac (DuckDB 1.5.6): accounts 51646089, accounts_linear 82994433,
  accounts_tree 18593764, peer_medians 416730365, weekly 3065472.
- `models.train`: new manifests record `data_identity` (seed, `--set`, config and BAF hashes) and
  `input_fingerprints`; `load` accepts a model when the run manifest is the same file, or the fingerprints equal
  the local data's, or (models trained before) a `verified.json` from `python -m models verify` still matches.
- `python -m models verify --model M --reference RUN` (`src/models/verify.py`): rescores a committed harness run of
  the model; only if every result file is identical does it write `verified.json` (local fingerprints + hashes of the
  model files). `frozen_tuned` verified on the Mac against `month5_dryrun_frozen_tuned`.
- `evaluation.score.run`: `check_data=False` / `results=` only for `verify`; the final test refuses both.
- **The model of record is committed:** `outputs/modelling/models/v1_full/frozen_tuned/` now holds Li Ann's `lgbm.txt`
  and `app_logreg.json` beside his manifest, plus `verified.json` (fingerprints of the data it reproduces, hashes of the
  model files with line endings normalised) and `calibration.json`. `models.train.find_model_dir` prefers this
  committed copy; `train` refuses to overwrite a shared model; `evaluation.score` and `models calibrate` default to
  `frozen_tuned`; notebook 09 defaults to `RETRAIN = False`. `.gitattributes` keeps `lgbm.txt` byte-exact. Team
  members no longer train the model: they need the data, its cleaned tables and the feature store, then score.
- Calibration of `frozen_tuned` on month 5: isotonic chosen, out-of-fold Brier 0.0749 -> 0.0018, mean predicted
  0.00235 = observed rate (`outputs/modelling/models/v1_full/frozen_tuned/calibration/report.md`).

## 29 Oct 2026 — Calibration, onboarding value, age breakdown, seed-43 dry run (Phase 5)

No data change, no feature-store change, frozen inputs and Li Ann's tuned settings unchanged. All runs below are on
Emmy Li's Mac and carry the suffix `_macos`: the tuned model does not rebuild identically across machines (Li Ann,
Windows: 63 of 78 mules caught on month 5; this Mac: 65; same data, same settings), so which machine produces the
results of record is a team decision. Li Ann's committed `frozen_tuned` outputs are untouched.
- `python -m models calibrate` (`src/models/calibrate.py`): isotonic and Platt mappings fitted on month 5 (open
  account-weeks, weeks 0-26), checked out of fold over 5 groups of accounts, the lower Brier score chosen and saved to
  `data/<run>/models/<model>/calibration.json`. `frozen_tuned_macos`: raw scores average 0.186 for a 0.235% mule rate
  (class weights); isotonic 0.00235, Brier 0.0748 -> 0.0018, reliability close in every bin. Order-preserving, so the
  harness's results do not change.
- `python -m models train --inputs activity`: the frozen inputs without `app_score`, for the value of onboarding
  information (professor's comment 2). `python -m evaluation.compare`: two harness runs on the same cohort side by
  side. Month 5 at the rules' budget, weeks 0-26: frozen 65 of 78 caught vs activity only 61 (fake 60 vs 55,
  witting 3 vs 4, unwitting 2 vs 2); catch_mean 0.385 vs 0.358; the frozen model ahead in 16 of 27 weeks, behind in
  7. Seed 43 month 5: 56 vs 56 of 65, catch_mean 0.471 vs 0.462. At the rules' budget the application adds a few
  fake accounts, mostly from week 12 on, and no early flags.
- Harness: recall and false-positive rate by age band (under 30 / 30-49 / 50+, `by_age_w<h>.csv`) for Variant II;
  every model, calibration and harness run records its machine (OS, processor, cores).
- Seed 43 (chance yardstick): trained on its months 0-4 with the tuned settings, month 5 at the rules' budget, weeks
  0-26: model 56 of 65 mules (precision 0.35) vs rules 19 (0.13); v1_full month 5: 65 of 78 (0.52) vs 16 (0.13).

## 28 Oct 2026 — Phase 5 harness, dry run on month 5

No data change, no feature-store change, frozen inputs unchanged. New:
- `python -m models train` (`src/models/train.py`, was a stub): the frozen 38-input LightGBM fitted on all of months
  0-4 (weeks 0-26, closed weeks dropped; application score out of fold as in notebook 06). Saved to
  `data/<run>/models/<name>/` (LightGBM text model, logistic coefficients as JSON, manifest); manifest and importances
  copied to `outputs/modelling/models/<run>/<name>/`. Default LightGBM settings until tuning step 2: `--params FILE`.
- `python -m evaluation.score` (`src/evaluation/score.py`): the fixed-cohort comparison of 8 Oct 2026. Each week
  since opening the model flags as many accounts as the rules alerted on the same cohort that week, permanently;
  closed accounts stay in the cohort as caught by the rules. Reports caught / precision / false alarms (also against
  the fixed final label), days from laundering start, catch_mean, head to head, the any-time policy (same total
  flags, upper bound), by type, per week; horizons 26 (main) and 77 (appendix) in one run. Test months 6-7 need
  `--final-test` and are scored once (lock file). `evaluation.budget` reads month 5, and 6-7 only with
  `allow_test`.
- Dry run, month 5 of v1_full (29,120 accounts, 97 launderers; default settings), weeks 0-26: rules' budget 124
  flags. Model caught 62 of 78 mules (precision 0.50), rules 16 (0.13); fake 57/70 vs 13/70, witting 3/5 vs 3/5,
  unwitting 2/3 vs 0/3; catch_mean 0.371 vs 0.095; when both catch a launderer, same median day (model first 6,
  rules first 5). No flag before laundering starts: at ~5 flags a week, fake accounts (median rank ~1,300 of 29,120
  at weeks 0-8) never reach the budget, so at the rules' budget the application buys no head start; the gain is
  catching bursts the rules miss. Weeks 0-77: model 75 of 97, rules 29.
  `outputs/modelling/results/v1_full/month5_dryrun/`. Tests: `tests/test_harness.py`.

## 28 Oct 2026 — Rules-budget measure, measured noise, split application score, graph features (proposal)

No change to the simulated data, the feature store, its 28 features or the adopted features. New derived files in
`data/<run>/features/` (git-ignored): `graph_weekly.parquet`, `graph_edges.parquet`, `graph_manifest.json`,
`graph_nb/`. The 50k store `data/v1/features/weekly.parquet` was rebuilt (it predated the week-78 drop). All of this
is a **proposal for the team** (Emmy Li); defaults are unchanged (`--decide weekly_recall`). Report-appendix work
under the feature freeze of 28 Oct 2026: none of it changes the 38 frozen inputs, and the results agree with them.
- **Rules' budget** (`src/evaluation/budget.py`): the rules raise ~6 alerts a week per validation month (0.017-0.020%
  of accounts per week, months 0-7), against ~300 flags for the lab's top 1%. New measure `catch_rules`: permanent
  flags at the rules' alert count in each week since opening; per week the share of mule accounts (closed ones
  included) flagged so far, averaged over weeks 0-26. The rules' own value on the same scale: **0.141**. Also
  `catch_0.1pct` (0.1% of open accounts per week). `--decide` picks the deciding measure.
- **Noise measured** (`--placebo N`, trial `noise-placebo5`, 5 groups of shuffled columns): 2 x RMS placebo gain =
  catch_rules 0.012, catch_0.1pct 0.005 (set in `NOISE`); weekly_recall 0.006, acc_pr_auc 0.008, caught_2wk 0.023
  (reported only; the agreed 0.02 / 0.04 / 0.05 are left for the team). Bootstrap over each month's mule accounts:
  catch_rules sd 0.026 per fold.
- **roll4 at the rules' budget** (trial `roll4-recheck-rules-budget`, baseline store only): catch_rules 0.381 ->
  0.457 (+0.128 / +0.072 / +0.027), `better`; start_recall up in all folds. The adoption holds.
- **Two application scores** (`tuning.app_score_split`, group `app_split`): catch_rules -0.008 / -0.022 / +0.006 (no
  clear change), catch_0.1pct `worse`, PR-AUC 0.870 -> 0.811, real-customer mules caught not higher. Drop.
- **Graph features** (`python -m features graph`, `src/features/graph.py`: internal money in / out, internal payers,
  forward-within-24h of internal money, neighbours so far, neighbours showing the closure footprint;
  `src/models/graph_nb.py`: neighbours' out-of-fold scores from a two-stage model, no labels of neighbours):
  `graph_struct` catch_rules -0.011 / -0.004 / -0.001 (`worse` by the all-folds rule, every fall below the noise
  level), `graph_nb` -0.008 / +0.006 / +0.038 (no clear change), both together +0.001 / +0.004 / +0.029 (no clear
  change). start_recall rises in every fold for every graph group (+0.02 to +0.04), PR-AUC 0.870 -> 0.895
  (`graph_nb`); real-customer mules caught at the rules' budget with `graph_nb`: +1 in fold 1, -1 in fold 2, +1 in
  fold 3. Not a promotion candidate at the rules' budget.
- `--scratch DIR` for development runs (no ledger row). The ledger gained 10 columns; earlier lines are byte for
  byte as before plus empty fields (`append_ledger` no longer re-writes old values). 29 ledger rows on v1_full now
  (5 of them placebos).
- **roll4 confirmed on fresh data (seed 43, one look):** `data/sensitivity/seed__43` rebuilt from its committed
  manifest (same BAF hash and setting values; data card identical to the committed one, 10/10 checks), then preprocess
  (`outputs/modelling/preprocess/seed__43/`), store and trial `roll4-confirm-seed43`: catch_rules 0.382 -> 0.452
  (+0.076 / +0.079 / +0.055, `better`; rules 0.162), weekly recall +0.047 / +0.048 / +0.045, PR-AUC 0.691 -> 0.859.
  Seed 44 not run (disk).
- `outputs/modelling/feature_lab/PLAN.md`: the planned trials, their results and the seed-43 check.

## 28 Oct 2026 — Importance of the frozen inputs

No data, feature-store or model-input change. `python -m models.frozen_importance` refits the frozen 38-input model
exactly as the feature lab's baseline (same 3 folds on months 0–4, seed 42, LightGBM settings; it reproduces the lab's
weekly recall, 0.407 / 0.366 / 0.453 on v1_full) and writes each input's share of split gain per fold and on average
to `outputs/modelling/models/v1_full/frozen_importance/importance.csv`. On v1_full: application score 51.0%,
`out_1h_share_4wk` 11.5%, `money_in_4wk` 6.7%, `n_payers_cum` 6.7%, `internal_out_share_cum` 4.1%; the top 5 carry
80%, the top 10 89%; the 28 store features together 24%, the 8 four-week windows 23%. Gain share shows what the
trees lean on, not what the model could do without (inputs that measure the same thing share the credit). Selects
nothing, so it is not another look at the folds. `tests/test_feature_lab.py` now pins the 38 inputs. Used in the
decision-record doc's "Feature engineering" tab (section "The final feature list: 38 inputs").

## 28 Oct 2026 — Feature list frozen

No data, feature-store or code change. Decision (28 Oct 2026, Kee Chee Pheng, lead): the model inputs are frozen
for tuning step 2, calibration on month 5 and scoring of test months 6–7: the 28 store features, the 8 `roll4`
features (`features.candidates.ADOPTED`), `weeks_since_open` and the application score (`app_score`), 38 in all for
the LightGBM activity + application model (the feature lab's baseline). Groups tried and not taken: `lag1`, `roll2`,
`roll4_core`, `running_max`, `new_cp4`, `self4`, `speed_cum`, `max_out_hist`, `internal_out`. From now on feature-lab
trials and `/feature-round` run only on explicit request, as report-appendix work. Re-checking `roll4` on Variants II
and IV is a robustness check and does not reopen the list.

## 28 Oct 2026 — `self4` not adopted

No data, feature-store or code change. Decision (28 Oct 2026, Kee Chee Pheng, lead): the `self4` group (last 4 weeks
vs the account's own earlier 4-week average: money in, money out, payments in) is **not** added to the model inputs,
which stay store + `roll4` (`features.candidates.ADOPTED` unchanged). On v1_full against the adopted model its weekly
recall gain (+0.030 / +0.037 / +0.022) is mostly re-flagging mules already found (later recall +0.053 / +0.077 /
+0.061; start-week recall +0.008 / +0.029 / +0.013), first catch within 2 weeks is unchanged (0.957) and it loses 1
unwitting mule from the top 1% in fold 1. A flag is permanent, so re-flagging earns nothing. The group stays in
`candidates.py` as a tried candidate.

## 28 Oct 2026 — Feature round r01: real-customer mules

No data change, no feature-store change, no change to the adopted features. First `/feature-round`, focus
real-customer mules (66 witting + 69 unwitting in months 0–4 of v1_full). Report-appendix work.
- EDA (`notebooks/07_eda_agent_r01.ipynb`, `outputs/modelling/eda_agent/r01/`, 669 AUCs listed in `checks.csv`):
  for real customers no signal before laundering starts (21 of 376 checks in the 2 weeks before differ, ~19 expected by
  chance); the Phase 1 hint (more rows before the start) disappears when compared at the same week since opening
  (AUC 0.50). 4 start-week insights in `insights.csv`:
  - r01-1 matched forwarding (pays out 80–100% of a payment just received within 24 h): AUC real 0.88, 58% of real
    mules' start weeks vs 1.3% of normal weeks; needs raw transactions, so a team proposal; size partly an artefact
    (normal accounts never forward a received amount).
  - r01-2 largest payment out beats the account's earlier maximum: real 0.81 (store version 0.79).
  - r01-3 same payee 2+ times a week: artefact (the simulator never repeats a normal payee within a week); recorded
    so nobody trials it.
  - r01-4 weekly share of money out to accounts inside the bank: real 0.75 vs fake 0.63.
- Trials (new groups `max_out_hist`, `internal_out` in `features.candidates`, with hand-computed tests), vs store +
  `roll4`, per fold on v1_full: `max_out_hist` weekly recall −0.006 / +0.003 / +0.012, no clear change (status
  `tried`); `internal_out` −0.017 / +0.005 / −0.004, PR-AUC worse in all folds (status `dropped`). Start-week recall
  and first catch within 2 weeks unchanged within fold noise; real-customer mules in the top 1% unchanged (27 of 32).
  No promotion candidate, so seed 43 is still unused.
- Looks: 34 ledger rows, 19 on v1_full.
- `feature-engineer` prompt: the real-mule figure updated to the current model (27 of 32; 19 of 32 was before
  `roll4`).

## 27 Oct 2026 — EDA -> feature loop (report appendix)

No data change, no feature-store change, no change to the adopted features or the frozen feature list. New:
- `eda-explorer` agent (`.claude/agents/eda-explorer.md`): one round explores months 0–4 of v1_full through `amldata`
  (store, raw transactions in DuckDB, labels with launderer type), data first and only then the simulator code, and
  writes up to 5 insights with evidence (AUC with 95% bootstrap interval for all / fake / real-customer mules, within
  income and age bands, against the closest store feature, before vs after the start), the simulator setting and its
  `strength`, and an artefact verdict. Evidence notebook `notebooks/07_eda_agent_<round>.ipynb`.
- `outputs/modelling/eda_agent/insights.csv`: append-only ledger (empty); `tests/test_eda_agent.py` checks it.
- `/feature-round` skill: EDA agent -> the user picks insights -> `feature-engineer` (at most 3 trials) -> report.
- `feature-engineer` agent: takes approved insight ids, updates their status, and judges a v1_full promotion
  candidate once on `data/sensitivity/seed__43` (same settings as v1_full, seed 43, rules frozen at 1.516, unused by any
  trial so far; store and cleaned table built on first use) against the multiple-looks risk.

## 27 Oct 2026 — Feature lab splits gains by phase; agent trials merged

No data change, no feature-store change, no change to the adopted features. Merged from the `feature-engineer` agent's
worktree (trials of 26 Oct 2026):
- `python -m models.feature_lab` also reports, with no verdict, where a gain comes from: `pre_start_recall` (fake
  accounts before they launder), `start_recall` (start week and the next), `later_recall` (2+ weeks after), and
  `first_caught_2wk` (as `caught_2wk`, but a flag is permanent: a mule flagged once leaves the pool).
  `--baseline store` re-checks the adopted features against the store-only model. `NOISE`, folds, the existing
  measures and verdicts are unchanged; the ledger gains columns, earlier rows are kept as they were.
- Finding: `weekly_recall` also rewards flagging the same mule again in later weeks, worth nothing with a permanent flag.
  `roll4` (re-check, v1_full): `start_recall` 0.703 -> 0.781 in all folds, so its gain is partly earlier catching;
  `first_caught_2wk` 0.958 -> 0.957.
- New candidate groups in `features.candidates` (with hand-computed tests): `new_cp4`, `self4`, `speed_cum`. On
  v1_full against the adopted model: `self4` weekly recall +0.030 (+0.030 / +0.037 / +0.022), `start_recall` +0.008 /
  +0.029 / +0.013, `first_caught_2wk` unchanged, loses 1 unwitting mule in fold 1: team decision open. `speed_cum`
  +0.131, almost all in `later_recall` (+0.34 / +0.33 / +0.20): dropped. `new_cp4` (v1 only) no clear change: dropped.
- 17 looks on v1_full against the same folds so far (ledger).
- `.claude/agents/feature-engineer.md`: promotion also needs `start_recall` and `first_caught_2wk` not to fall;
  clearer lab-editing rule, foreground v1_full runs, worktree data paths, report lists changed files and the
  top-1%-vs-rules'-budget caveat.

## 26 Oct 2026 — Four-week-window features adopted into the model inputs

No data change, no feature-store change. The 8 features of the feature lab's `roll4` group (`n_rows_4wk`, `n_in_4wk`,
`money_in_4wk`, `money_out_4wk`, `n_payers_4wk`, `out_1h_share_4wk`, `out_24h_share_4wk`, `passthrough_4wk`: this week
and the three before) are adopted (decision 26 Oct 2026, Kee Chee Pheng, lead). Option A: they are computed at load
time, `models.lgbm_baseline.load_table(..., adopted=True)` (`features.candidates.ADOPTED`), not written to the store,
since they are sums of store columns; no store rebuild, manifest unchanged. `load_table` without the flag is
unchanged, so notebooks 05 and 06 stay the records of the store-only runs. The feature lab's baseline now includes
them (ledger column `baseline`), so later trials must beat the model as it now stands; on v1_full that baseline
reproduces the earlier `+roll4` result exactly (weekly recall 0.403 pooled).
- Smaller set tried first (trial `roll4-core-vs-full`, v1_full): the three 4-week ratios plus `n_in_4wk` reach weekly
  recall 0.393 (−0.03 / +0.02 / −0.03 per fold against all eight) but PR-AUC 0.826 against 0.871 (lower in every
  fold) and 23 against 27 of 32 real-customer mules in the top 1%; all eight kept.
- Still to do: confirm on Variants II and IV once their feature stores exist; tuning step 2 uses `adopted=True`.

## 26 Oct 2026 — Feature lab scores the tuning measure on the tuned model

No data change, no feature-store change. `python -m models.feature_lab` now follows the tuning decision of 26 Oct
2026: its default view is activity + application score, built exactly as `notebooks/06_lgbm_tuning.ipynb`, and the
verdict that decides is `weekly_recall` (share of each week's mules in that week's top 1% of open accounts, mean over
weeks 0–26; 'better' = all 3 folds up and mean gain >= 0.02, an assumption). Account-level PR-AUC and `caught_2wk`
are reported beside it; `early_recall` (weeks 0–8) is gone. `--views activity` keeps the store-only model. The ledger
keeps earlier rows when columns change. New `tests/test_feature_lab.py` checks the measures by hand and against
`lgbm_baseline.by_week`. The feature-engineer agent's promotion rule now uses `weekly_recall`.
- Trial `item1-history-tuned-measure`, v1_full: baseline reproduces notebook 06 (weekly recall 0.345 pooled,
  PR-AUC 0.695). 4-week windows: weekly recall 0.403 (+0.073 / +0.041 / +0.059 per fold, 'better'), PR-AUC 0.871
  ('better'), `caught_2wk` no clear change, real-customer mules in the account-level top 1% 19 -> 27 of 32 (up or
  equal in every fold): the only group that meets every condition of the promotion rule. Running max raises weekly
  recall (0.413) but is worse on PR-AUC and `caught_2wk`; last-week values and 2-week windows: no clear change.

## 26 Oct 2026 — Feature lab: candidate features, trial runner, feature-engineer agent

No data change, no feature-store change. New `src/features/candidates.py`: candidate weekly features built from the
store, using only the same and earlier weeks of each account (groups `lag1`, `roll2`, `roll4`, `running_max`;
`tests/test_feature_candidates.py` checks no look-ahead and no mixing between accounts). New `python -m
models.feature_lab`: refits the activity LightGBM of `models.lgbm_baseline` (same rows, folds, seed, months 0–4 only)
with each group added; measures account-level PR-AUC and `caught_2wk` (launderers in that week's top 1% in their
start week or the next); verdict 'better' only if all 3 folds improve by at least 0.04 PR-AUC (team noise rule) /
0.05 `caught_2wk` (assumption). Reports under `outputs/modelling/feature_lab/<data>/<trial>/`, every trial appended
to `outputs/modelling/feature_lab/ledger.csv`. New agent `.claude/agents/feature-engineer.md` runs propose ->
implement -> verify -> evaluate trials; it never changes the store (promotion is a team decision).
- First trial `item1-history`, v1_full (baseline reproduces the published activity PR-AUC 0.730): 2-week windows
  0.822 (+0.13 / +0.08 / +0.07 per fold), 4-week windows 0.865 (+0.21 / +0.13 / +0.07), both 'better' on PR-AUC;
  `caught_2wk` unchanged (baseline 0.943); running max worse on both measures (0.659). The windows reduce normal
  accounts' one-week spikes (precision), not time to catch. Witting mules in the top 1% fell in one fold (6 -> 4 of 7
  with 2-week windows), so no group is proposed for the store yet.

## 25 Oct 2026 — Logistic baseline: share features clipped to [0, 1]

No data change, no feature-store change. `notebooks/04_logreg_baseline.ipynb` now clips the eight share features to
[0, 1] before standardising them (section 2). The two speed shares divide money paid out this week by this week's
money in, so they pass 1 when money from the week before leaves this week (up to 222 on v1_full, 99th percentile
0.52); unclipped, those rows set the scaler. The store keeps the agreed definition (decision 15 Oct 2026); LightGBM
is unaffected (clipping keeps the order trees split on).
- v1_full, logistic account-level PR-AUC (mean of 3 folds): activity 0.038 -> 0.122, combined 0.112 -> 0.274,
  application 0.025 (unchanged, no shares). Combined logistic now edges past untuned combined LightGBM (0.256);
  activity LightGBM (0.730) still leads by about 6x, not 19x.
- Same check on data/v1 (50k), activity view: 0.051 -> 0.136.

## 22 Oct 2026 — Phase 4 tuning, step 1: equal account weight and the application as one score

No data change. New `notebooks/06_lgbm_tuning.ipynb` (helpers `src/models/tuning.py`, tests
`tests/test_models_tuning.py`) -> `outputs/modelling/models/v1_full/lgbm_tuning/`. Same rows, folds, metrics and
LightGBM defaults as the baseline; deterministic. Two fixes for the combined model's memorising:
- **Equal weight per account** (each account's weeks share one unit of weight, classes balanced): barely helps;
  combined account-level PR-AUC 0.256 -> 0.279, training-minus-validation gap 0.74 -> 0.72.
- **The application as one score**: a logistic regression on the 56 `accounts_linear` columns, one row per account,
  label "mule by the end of week 26" (team choice 22 Oct 2026), scored 5-fold out of fold for training accounts.
  Activity + app score: 0.695, gap 0.18. Both ideas together: 0.699.
- Activity alone still has the best account-level PR-AUC (0.730). But week by week, activity + app score is higher in
  27 of 27 weeks, and in weeks 0–8 it puts 15% of the mules into each week's top 1% against 4%: the application buys
  earliness, which the account-level measure (an account's best week) does not reward. It catches fewer real-customer
  mules in the account-level top 1% (witting 6/14 and unwitting 13/18, vs 9/14 and 16/18 for activity alone).

## 22 Oct 2026 — Phase 4 baselines re-run, now reproducible

No data change. The two baselines re-run on v1_full after the feature-store changes (weeks 0–26 unchanged).
- `notebooks/05_lgbm_baseline.ipynb` imported `models.lgbm_baseline`, but the module was committed as
  `src/models/lightGBM.py`, so the notebook could not run from the repo; renamed to `lgbm_baseline.py` (its own
  docstring and command line already used that name).
- **Not reproducible before:** three runs with the same seed gave combined PR-AUC 0.216 / 0.248 / 0.258. Rows came
  from an unsorted DuckDB join, and LightGBM's threads add in no fixed order. Now both notebooks read the store with
  `weekly.load(..., months=...)` (sorted rows) and LightGBM uses `deterministic=True, force_row_wise=True`: two runs
  of each notebook give identical metrics.
- v1_full, account-level PR-AUC (mean of 3 folds), LightGBM / logistic: activity 0.730 / 0.038, application
  0.011 / 0.025, combined 0.256 / 0.112. Logistic numbers moved by at most 0.002 (row order only).
- Finding for tuning: combined LightGBM overfits. Last fold: account-level PR-AUC 1.00 on training vs 0.40 on
  validation (activity only: 0.83 vs 0.77), with 87% of its gain from application columns. Fake accounts are labelled
  mules in every week, so the trees learn to recognise individual training fakes by their application values.

## 22 Oct 2026 — Feature store: weeks 0–77 (week 78 dropped)

No change to the simulated data. Every account's data ends 547 days after opening, so week 78 (days 546–552) held only
2 of its 7 days: 2.2 rows on average against 5.5 at week 77, an artificial drop in activity at the end of the 0–78
appendix horizon. The store now holds weeks 0–77 (`weekly.LAST_WEEK`); `build()` refuses later weeks and
`manifest.check()` refuses a store that still holds week 78. Rebuilt on v1_full (19,032,000 account-weeks) and v1
(3,900,000): exactly the old store and peer medians without week 78, row for row. Notebook 03's gate re-run on both
(passes); its end-of-window check and `test_whole_store_invariants` now compare week 77's running totals with the
transactions up to that week's cut-off. Appendix horizon in CLAUDE.md: weeks 0–77 (team decision 22 Oct 2026).

## 22 Oct 2026 — Feature store: code check in the manifest, simpler code (no result changes)

No data change; both stores rebuilt and byte-identical to before (`weekly.parquet` and `peer_medians.parquet`, v1_full and v1).
- **Code check:** the manifest now stores `code_sha256`, a fingerprint of the feature SQL, and `manifest.check()`
  refuses a store built by different feature code. Before, `check()` compared data, feature list, weeks and peer
  medians but not code, although its docstring said so, so an edited `weekly.py` silently reused the old store.
  Stores built before this change are refused once; rebuild with `python -m features weekly --out <folder> --force`.
- `load()` takes `months=` and `columns=` (rows now sorted by account and week); no private `amldata` import.
- The zero-fill of empty weeks is generated from one list (`ZERO_FILL`) instead of 20 hand-written lines.
- Docstring: the speed numbers match the report (1 h AUC 0.772 vs 0.951 for cash patterns); the two meanings of
  "new payer" are written down.
- Tests: a store built by other feature code is refused; `HIGH_RISK` equals `configs/sim.yaml`; `load()` filters.

## 21 Oct 2026 — EDA: simpler code (no result changes)

No data change. `notebooks/01_eda_train.ipynb` cleanups, re-run on v1_full and v1 (50k); every number in the reports
is unchanged apart from known float-sum noise (~1e-6) and the two items below.
- No global warning filters (they hid nothing: a run without them prints no warnings); the report path is two plain lines.
- §2: the Welch t-test p-value (computed, never shown; Mann-Whitney already tests the numeric columns) is dropped;
  information gain, which the plan lists, is now shown for the categorical columns.
- §3: the closure table is one `GROUP BY` instead of correlated subqueries (same table).
- §6: no redundant `lab_` query; `x` / `s` renamed `share_accounts` / `share_ends`; `two_xy()` takes its inputs instead
  of reading globals. Names no longer reused across cells (`lab_`, `s`).
- §6 shuffle test: the account list is sorted before shuffling, so it gives the same numbers every run (DuckDB returns
  rows in no fixed order). v1_full: 163 launderer–launderer links vs 9.6 on average (the 21 Oct run said 9.3), mixed
  links 5,663 vs 6,843; p = 0.001 as before.

## 21 Oct 2026 — EDA: claims tested directly (pre-start weeks, graph timing, shuffle test, missing flags)

No data change. `notebooks/01_eda_train.ipynb`, re-run on v1_full and v1 (50k). v1_full numbers:
- **Before laundering starts (§3).** The claim "activity carries nothing before a burst" is now tested: weeks 0–7
  (no fake starts before week 8), each launderer's weeks before its start vs normal accounts, one mean per account so
  the interval is honest. Counts, payers and speed match. Fakes' money features are higher (money in AUC 0.58) only
  through BAF income: 31% of fakes are in the top income band vs 20% of normal accounts, normal money scales with income
  (`src/sim/normal.py`), and inside an income band the AUC is 0.51. The weekly table now uses open weeks only and says
  which columns are medians and which are means.
- **Graph (§6).** Label-shuffle test (labels moved between accounts, each keeps its links, 1,000 shuffles): 163
  launderer–launderer links vs 9.3 on average, p = 0.001; mixed links 5,663 vs 6,845, p = 0.001. Only 1 of the 163
  links exists before both ends start laundering (4 before at least one): graph features can find network partners
  once a burst starts, not give a head start.
- **Missing flags (§2).** BAF's missing codes are scored as 0/1 flags: fakes `prev_address` 0.60, `intended_balcon`
  0.58, `bank_months` 0.57; real mules `intended_balcon_amount_missing` 0.45.
- **Text:** §1 `velocity_6h` note computed (0 negative rows in months 0–4), skew table without 0/1 columns, Phase 2
  decisions quoted for log and correlated pairs; §5 says what fixed weeks hide and points to Phase 3's first-week view;
  §8 hard-coded "~1.6% abroad" removed.
- **Bootstrap intervals** now sort the placement values first, so they no longer depend on the order DuckDB returns
  rows (run-to-run differences fall from ~0.01 to the known ~2e-6 float-sum noise). Point AUCs unchanged.

## 19 Oct 2026 — EDA tidy: closure filter, keep/drop rule with intervals, age allowed

No data change. `notebooks/01_eda_train.ipynb`, re-run on v1_full and v1 (50k); `notebooks/03_feature_store.ipynb`
re-run on both (gate (A) still within 1e-5).
- **Age decision (19 Oct 2026):** `customer_age` is allowed as a model input; Variant II tests fairness.
- **Closure filter:** the feature screen (§5) kept account-weeks with any rows (`n_rows > 0`); it now uses
  `labels()["open_by_day"] == 1`, as CLAUDE.md requires (normal accounts have 82 zero-row weeks in months 0–4). Notebook 03
  uses the same filter so its gate still reproduces the screen. v1_full started launderers at week 12: 167 -> 157 (10
  closed during that week).
- **§3 text:** the stale "decision needed: open at week w" note is replaced (`open_by_day` exists since 10 Oct); the
  closure numbers are printed from the data.
- **§5 / §8:** one AUC helper with a 95% interval (resampling the launderers) for §2 and §5. A candidate is kept when,
  at some screened week, |AUC − 0.5| ≥ 0.05 for `mule_by_day` or `started_by_day` and its interval excludes 0.5; the old
  rule had no interval. v1_full: drop cash / abroad / high-risk shares (as the team decided on 15 Oct); `night_share` and
  `internal_share` pass in 1 of 8 looks (weak). No change to the feature store.

## 18 Oct 2026 — EDA fixes: missing values rank lowest in the AUC; real mules separate on age

No data change. Two corrections to `notebooks/01_eda_train.ipynb`, re-run on v1_full and v1 (50k):
- **AUC helper.** `auc()` used pandas `rank(na_option="bottom")`, which gives NaN the *highest* rank, while its docstring
  said lowest. Share features are NaN in weeks with no money in (about half of normal weeks), so those weeks ranked above
  every launderer and the shares looked like noise. Now `na_option="top"` (NaN lowest, as the Phase 3 bootstrap already
  did). v1_full, best |AUC − 0.5| against started launderers: `out_1h_share` 0.02 -> 0.28, `out_24h_share` 0.05 -> 0.25,
  `new_payer_share` 0.11 -> 0.21, `passthrough_wk` 0.11 -> 0.20, self-vs-past 0.14 -> 0.17. The Phase 1 proposal to
  redefine the speed shares came from this bug; the store already keeps the EDA's definition (decision 15 Oct 2026).
  The same helper in `notebooks/03_feature_store.ipynb` (gate comparison and screen; its first-week bootstrap was
  correct and is unchanged) and `src/sim/eda/eda_sim_v1.py` is fixed too. Notebook 03 re-run on v1_full (store rebuilt,
  deterministic) and v1: gate (A) still within 1e-5. `eda_sim_v1` re-run on v1_full: no AUC changed (no NaN in its
  features), so its report was left as committed.
- **§2 application columns by type.** The table was sorted by the all-launderer AUC and cut at 16 rows, which hid
  `customer_age`: AUC 0.65 for fake accounts but 0.25 for real-customer mules (about 65% under 30 vs 27% of normal
  accounts, from `profiles.real_mule_age_weights`), 0.53 for all. §2 now sorts by the largest of the three separations,
  shows every column, and gives each AUC a 95% interval (resampling the launderers). Real mules: 8 columns' intervals
  exclude 0.5 on v1_full (age, housing_status, keep_alive_session, income, phone_home_valid, has_other_cards,
  bank_months_count, phone_mobile_valid); 1 on v1 (age, 20 real mules). The "real-customer mules do not separate at
  opening" finding is corrected in CLAUDE.md / AGENTS.md and the decision-record doc. Whether age may be a model input
  is open (fairness).

## 16 Oct 2026 — EDA §6: the homophily test is now the r < 2xy test

No data change. `notebooks/01_eda_train.ipynb` §6 called a lift (how often a launderer's payees are launderers vs the
base rate) "the L8 homophily test"; it was not that test. §6 now runs the homophily test itself on the payment network
inside the bank (one undirected link per pair of accounts that paid each other, both ends opened in months 0–4): with x the
launderer share of accounts, homophily means the share of launderer–normal links r is clearly below 2xy (one-sided z-test).
A second row allows for how many links each account has (x = launderer share of link ends). v1_full: r = 0.450% vs 2xy =
0.545% (r / 2xy 0.83, z −14.3); allowing for links per account 0.95, z −4.0; 163 launderer–launderer links vs 9 expected
by chance (17x). The lift (20x) is kept as the measure of strength. r / 2xy looks modest only because launderers are 0.3%
of accounts. v1 (50k): 0.86, z −5.2; 0.95, z −1.9. Re-running the notebook also moved a few weekly money AUCs and
correlations in the 7th–8th digit (DuckDB sums in parallel, in no fixed order); nothing else changed.

## 15 Oct 2026 — Phase 3 speed shares: back to the EDA's definition (team decision 15 Oct 2026)

No change to the simulated data. `out_1h_share_wk` / `out_24h_share_wk` replace `fwd_1h_share_wk` / `fwd_24h_share_wk`:
money paid out (any kind) within 1 h / 24 h of the latest payment in (any kind), over the week's money in, exactly as
in the Phase 1 EDA (Kee Chee Pheng, `notebooks/01_eda_train.ipynb`); it can exceed 1. The transfers-only, capped
redefinition (Phase 3 commit 9fb3caf) is dropped. Evidence, v1_full months 0–4, each launderer's first laundering week
(361) vs normal account-weeks:
- 1 h: EDA definition AUC 0.954 vs 0.919 for the redefinition; paired account-level bootstrap difference +0.035
  (95% interval +0.021 to +0.050). 24 h: no difference (+0.002 the other way, interval crosses 0).
- Why (`python -m evaluation.speed_by_pattern`, hidden pattern labels, training months only): for launderers who use
  transfers only (297) both definitions are equal (1 h AUC 0.955 vs 0.951). For the 64 whose pattern moves cash, the
  redefinition is blind: 0.951 vs 0.772 (Cash_Withdrawal 0.963 vs 0.727, reads 0 for all 9; Deposit-Send 0.944 vs
  0.809; Smurfing 0.994 vs 0.487). It ignores cash deposits as money in and cash withdrawals as money out. A
  launderer's pattern is the label on most of its laundering rows (rows forwarded from the previous chain member
  carry that member's label).
- The Phase 1 report's "swamped by everyday outflows" was right for the 24 h share (normal weeks average 0.59) but not
  for the 1 h share (only 2.5% of normal weeks have any money out within 1 h of money in). The EDA screen showed no
  signal because it scored weekly features at fixed weeks against `started_by_day`, not because of the definition.
Both speed shares now join the value-by-value gate (16 shared features). Tests updated: the synthetic test adds a cash
deposit followed by a cash withdrawal; the pandas re-implementation and whole-store checks follow the EDA definition
(speed shares may exceed 1; 0 ≤ 1 h ≤ 24 h still holds).

## 15 Oct 2026 — Modelling Phase 3: weekly feature store (28 features), gate passed on v1_full and v1

No change to the simulated data (`data/v1` was rebuilt from BAF Base: identical to the team's copy, 0 rows differ in
`accounts_truth`, `aml_alerts`, `aml_outcomes`). `python -m features weekly` builds the feature list fixed at the Phase 1
gate: volume, counterparties (distinct and first-time payers, distinct payees, cumulative distinct counts),
pass-through, speed, self vs past (money in, payers, rows), peer ratio of money in (medians frozen from months 0–4 in
`features/peer_medians.parquet`, hashed in the manifest), cumulative internal / cash / abroad / high-risk shares. Speed as
the gate asked: transfers out (ACH, Cross-border) within 1 h / 24 h of the latest transfer in, each inflow passed on at
most once. Money is summed as exact pence (DECIMAL), so totals do not depend on the order DuckDB adds them in.
One opening month at a time: v1_full weeks 0–78 = 19,276,000 account-weeks in ~4 min, 4.2 GB peak.

Gate (`python -m features store-check` -> `notebooks/03_feature_store.ipynb`, report `outputs/modelling/features/`):
- Value by value, the 14 features the EDA screened equal the EDA's own query (copied verbatim, rerun) on all 4,450,113
  account-weeks of months 0–4 (v1_full; relative difference ≤ 8.2e-14, identical NULL pattern); v1 likewise (912,627).
  The EDA's float sums are not bit-reproducible run to run (its AUCs move by up to 7e-7 on v1_full, 4e-6 on v1); the
  store's exact sums remove that noise.
- First laundering week vs normal account-weeks, 95% account-level (Poisson) bootstrap, 1,000 replicates, v1_full:
  25 of 28 features exclude AUC 0.5; strongest `fwd_1h_share_wk` 0.919 (0.902–0.936), `n_in_wk` 0.915, `fwd_24h_share_wk`
  0.909, `n_rows_wk` 0.906; no signal for `self_vs_past_payers`, `n_payees_cum`, `abroad_out_share_cum`.
- **Correction:** the redefined 1 h speed share is *not* better than the EDA's (any payment out after the latest payment
  in): paired bootstrap gain −0.035 (−0.050 to −0.021); 24 h: +0.002 (−0.012 to +0.016). Resolved in the entry above:
  the EDA's definition is restored.

Tests: `tests/test_feature_store.py` (real data, 3 seeded samples of 300 random accounts + 60 launderers, weeks 0–78):
all 28 features equal an independent pandas re-implementation; cutting test-month accounts' transactions at a random
week leaves every earlier value bit-identical; rebuilds are byte-identical; whole-store invariants (complete keys,
shares in [0, 1], 1 h ≤ 24 h, running totals never fall, week-78 totals equal the transactions file, peer medians equal
a recomputation). `tests/test_features.py` adds the speed cap, card rows out of speed, a week without a transfer in
(NULL, not 1.0), payers counted once, self vs past waiting 4 weeks, peer medians ignoring non-training months.
30 tests pass on v1 and v1_full. Two bugs were caught on the way: DuckDB's `least(1, NULL)` returning 1, and its median
of a DECIMAL rounding to 2 places.

## 10 Oct 2026 — Modelling Phase 2 (in progress): `open_by_day`, cleaning notebook `notebooks/02_preprocess.ipynb`

No change to the simulated data. New derived files per data folder: `<out>/features/accounts_linear.parquet`,
`accounts_tree.parquet` and `preprocess_manifest.json`, written by `python -m features preprocess` (all Phase 2 code is in
the notebook, team decision 10 Oct 2026); committed report and fitted numbers in `outputs/modelling/preprocess/`.
- `amldata.labels()` returns `open_by_day` with any cut-off for months 0–5 (0 once the bank has closed the account;
  only confirmed launderers are closed); withheld when test months are requested. Phase 3 drops training account-weeks
  with 0.
- Recipe fitted per dataset on its own months 0–4 (team decision 10 Oct 2026): BAF negative codes -> NaN + flag in 6
  columns, `velocity_6h` clipped at 0 (its negative rows are all in months 5–7), categories frozen from months 0–4;
  `linear` mode (median fill, log, one-hot, standardise) and `tree` mode (NaN kept, raw, `category` dtype).
- **Log change (team decision 10 Oct 2026):** the Phase 2 plan logged 9 columns in `linear` mode; the log made 4 of them
  more lopsided on v1_full months 0–4 (skew `intended_balcon_amount` 1.34 -> −1.15, `velocity_6h` 0.34 -> −1.20,
  `velocity_24h` 0.32 -> −0.34, `velocity_4w` 0.11 -> −0.45), so they are no longer logged. By the same rule
  `current_address_months_count` (1.41 -> −0.54) was added. Logged now: `days_since_request`, `prev_address_months_count`,
  `current_address_months_count`, `session_length_in_minutes`, `bank_branch_count_8w`, `zip_count_4w`. The notebook
  asserts that every logged column is less skewed after the log.
- Run on v1_full, v1, variant_II and variant_IV (15 Oct 2026): all 25 notebook checks pass on each; v1_full and v1 match
  the EDA report §1 exactly; 56 `linear` / 35 `tree` features. Both notebooks now find the repo root themselves, so
  "Run All" in VS Code works without `PYTHONPATH`.

## 9 Oct 2026 — Modelling Phase 1: EDA on the training months (`python -m features eda`)

No data change. `notebooks/01_eda_train.ipynb` (executed by `python -m features eda`) reads months 0–4 through `amldata` only (month 5 untouched, test months
closed) and writes `outputs/modelling/eda/` (report, 8 figures, `univariate_tests.csv`, `feature_screen.csv`; 50k copy in
`eda/v1_50k/`). Full-size findings: only fake accounts separate at opening; fakes start in weeks 8–17, real customers across
the window; cumulative volume, weekly rows/payers and the median in->out delay carry signal once a burst exists; weekly
abroad / high-risk / cash shares do not; homophily 20x the base rate. Found that a zero-activity week means the bank
closed the account (only confirmed launderers are closed): post-closure weeks must be dropped from training.

## 9 Oct 2026 — Modelling Phase 0: `labels(profile=True)`, feature-store skeleton with manifest, leak tests

No data change. `amldata.labels(profile=True)` returns each launderer's hidden type (fake / witting / unwitting, None for
everyone else) for months 0–5 only, for EDA breakdowns; it refuses test months even with `allow_test=True`. New packages
`src/features` (weekly feature store `python -m features weekly`, `features_manifest.json` recording the feature list, the
cut-off rule `day <= open_day + 7w + 6`, the code commit and a hash of the data's `run_manifest.json`; `load()` refuses a stale
store) and `src/models` (CLI stub). `tests/test_features.py` checks on a synthetic dataset that week-w features ignore later
rows, that rebuilds are byte-identical and that stale manifests are refused. Added lightgbm, networkx, torch to requirements.
Phased plan: doc tab "Modelling: phased plan".

## 9 Oct 2026 — `amldata.labels()`: the agreed weekly label and a weeks-since-opening cut-off

`labels()` now also returns `mule_by_day`, the main label agreed on 8 Oct: a fake account counts as a mule from
the day it opens, a real customer from the day they start laundering. A new `weeks_since_open=w` cut-off ends at
each account's own week w (open_day + 7w + 6), the clock of the fixed-cohort comparison; `as_of_day=` still gives
one calendar day. `is_launderer` remains the fixed final label. On the full-size training accounts:
`mule_by_day` 391 at week 0, 411 at week 8, 552 by week 78 (`started_by_day` 1, 34, 552). Data unchanged; new tests
check fakes count from week 0, started implies mule, and both labels reach `is_launderer` by the end.
## 8 Oct 2026 — R6 waits 8 weeks before judging a new account (team decision); all data regenerated

R6 ("sudden change") compared money in against the average of the previous weeks after only 4 weeks of history.
For many new accounts those weeks hold no salary yet, so the first monthly salary looked like a sudden change:
3,837 alerts at 244k (65% of all the rules' alerts), none on a launderer, almost all in an account's 4th–5th week.
They also put two-thirds of the test cohort's weekly alert budget into a single week. `rules.R6_history_weeks` is
now [8, 8] (was [4, 8]). At 50k with the scale held fixed: alerts 1,592 -> 756, the same 45 launderers caught,
false alarms 97.2% -> 94.0%. Checked on every early R6 alert at 50k: 835 of 840 fell in the week of the account's
first salary (the simulator pays it at a random point in the first pay period), the salary being all the money in.

Regenerated (9 Oct 2026, code 23fc46a; all datasets pass the 10 checks):
- `data/v1` (50k): 756 alerts, 94.0% false alarms, 45 of 150 caught (30%), median 7 days; scale 1.516.
- `data/v1_full` (244k): rules re-tuned to scale **1.516** (was 1.741): 3,614 alerts, 240 true, **93.4%** false
  alarms (inside 90–95% for the first time), **237 of 732 caught (32%)** (was 25%), median 9 days; weekly budget
  mean 33.2 / median 34 / max 95 (was 54.4 / 28 / 170). Test cohort alerts in week 4 after opening: 10 (was 1,006).
- Variants II / IV (frozen at 1.516): 93.2% / 93.1% false alarms, 34% / 33% caught.
- 42 sensitivity runs (frozen at 1.516): seeds 93.1–93.4% / 32–33%; transfers £1,500 75% caught, repeated bursts
  76%; prevalence 1% 81.3%, 0.1% 97.8% false alarms; doubled cash 98.4%. See `outputs/sensitivity/FINDINGS.md`.
- Rough baseline (application-only model, same number of flags as the rules on the test cohort, now 662): model
  19% vs rules 33%; together 44%. The rules are a stronger benchmark after the fix.
## 8 Oct 2026 — `amldata` reads the full-size dataset by default

`amldata.public()`, `labels()` and `evaluation()` now default to `data/v1_full` (244k, the main modelling dataset)
instead of `data/v1` (50k), so model code can't train on the small set by accident. Pass `out="data/v1"` for quick
experiments, or a variant folder. Data unchanged.

## 8 Oct 2026 — sensitivity results (42 runs, `outputs/sensitivity/`)

All 42 runs pass the 10 checks. Seeds 43/44 put chance at 96.7–96.9% false alarms and 24–26% caught. Large effects:
laundering transfers of £1,500 (71% caught) and repeated bursts (67% caught); prevalence 1% (90.8% false alarms)
and 0.1% (99.0%); doubled cash deposits (98.9%, R2 ~13,000 alerts); 15–22-payer group collections (R3 2,178
alerts). Everything else stays near the seed range. Details: `outputs/sensitivity/FINDINGS.md`.

## 8 Oct 2026 — repeated bursts and window-scaled start bands (team decisions 8 Oct 2026)

- `timing.bursts_per_launderer = repeat_until_closed` is now built: a new burst starts `timing.repeat_gap_days`
  (30, new setting, assumption) after each burst ends, until the window ends; the bank's closure removes the rest.
- `size.observe_days` shorter than 548: existing customers' start bands shrink in proportion, so every burst and
  its forwarding still end inside the window (365 days: starts up to day ~343). 548 and longer: unchanged.
- The sensitivity runner now includes `observe_days` (365, 730) and repeated bursts: 42 runs.
- Default unchanged: rebuilding `data/v1` is identical. 6,000-account smoke runs of all three pass 10/10 checks.
- Bug fix: every simulator process shared one DuckDB scratch folder (`/tmp/sim_duckdb`); two runs at the same time
  could corrupt each other's temporary files (a sensitivity run crashed with SIGBUS). Each process now uses its own.
- Bug fix: `finalize` settled closures in at most 4 passes; with repeated bursts they had not settled, leaving 219
  rows after closure (check 3 failed). It now repeats until settled (up to 20 passes) and stops with an error
  rather than write inconsistent files. Runs that settled within 4 passes (all others) are unaffected.
- DuckDB's memory cap can be raised with `SIM_DUCKDB_MEMORY` (default 1500MB); the 732k run needs ~8GB.

## 7 Oct 2026 — sensitivity runner, young-weighted fake ages, guard on unread settings

- `python -m sim.sensitivity`: one run per `test` value in the config (244k, seed 42, rules frozen at the
  main run's scale), plus seeds 43/44 and prevalence 0.1% (732k) / 1% (244k): 39 runs. Large files are
  deleted after the checks; summaries go to `outputs/sensitivity/`. Resumes where it stopped.
- `profiles.fake_age_rule = young_weighted` is now built (default unchanged: rebuilt accounts identical).
- `--set` refuses settings the code does not read (`sim.config.NOT_READ`), and `tests/test_config.py` fails
  if any setting is neither read nor listed there.

## 7 Oct 2026 — BAF Variants II and IV (`data/variant_II`, `data/variant_IV`)

No code change. 244k accounts, seed 42, rules frozen (`--set rules.fixed_scale=1.741`), BAF Variant II / IV files;
all 10 checks pass on both. Rules: 96.9% / 96.8% false alarms, 25% / 26% of launderers caught, median 8 days,
weekly budget 54.3 / 55.3. Launderer rate age 50+ vs under 50: Variant II 0.34% vs 0.23% (train) and 0.47% vs
0.20% (test); Variant IV 0.40% vs 0.21% (train) and 0.26% vs 0.32% (test), the planted drift. EDA reports in
`outputs/eda/variant_II/` and `outputs/eda/variant_IV/`.
## 7 Oct 2026 — frozen rules option (`rules.fixed_scale`)

Team decision: the bank's rules are frozen for variant and sensitivity runs. New setting `rules.fixed_scale`
(null = tune as before; a number = use that scale and skip tuning). Variant and sensitivity runs use
`--set rules.fixed_scale=1.741`, the scale tuned on `data/v1_full`. The data card states the scale and whether it
was frozen. Check: the 50k run with the scale fixed at its tuned value (1.516) reproduces `data/v1` exactly.

## 7 Oct 2026 — 23 hidden numbers moved into the config; R6 window bug fixed

An audit of the simulator code found 23 numbers that change results but were written into the code instead of
`configs/sim.yaml`. All are now settings with a source note (most honestly `modelling` or `assumption`: our
choice, no published figure), so they can be cited in the report and changed with `--set`:
- income: `anchor_points` (0.1/0.5/0.9); the average weekly spend now reads `spend_weekly_household` instead of a copy.
- normal: `card_split_exponent`, `card_week_sigma`, `dd_split_gamma_shape`, `transfer_in_sigma`, `cheque_amount`,
  `cash_withdrawal_sigma`, `cash_deposit_sigma`, `large_cash_amount`, `abroad_sigma`, `group_collection`.
- laundering: `piece_sigma`, `split_max_n_in`, `half_cash_share`, `layered_internal_multiplier`,
  `cash_out_piece_max`, `forward_delay_bands_minutes`.
- rules: `R2_window_weeks`, `R5_window_weeks`.

**Bug fixed:** `rules.R6_history_weeks` = [4, 8] was read, but the 8 (weeks averaged for R6's "usual week") was
ignored because the SQL had 8 written in. Changing it did nothing; now it works (at 6,000 accounts, 6 weeks
instead of 8 gives 251 alerts instead of 91).

**Effect on results: none.** Same values: rebuilding `data/v1` gives identical files, rows, labels, alerts and
tuning table. 10 checks and 5 tests pass.

**Test values and sources (approved 7 Oct 2026; main values unchanged):**
- `group_collection`: 8–15 payers matches Collection Pot's leaving collections (11.4 contributors). Tests: 15–22 payers
  (retirement size, 18.3), 4–8 payers, median £11 (source's £12.89 average) and £40. Main median stays £20 (team
  decision). Strength now `partly_sourced`. These collections cause 328 of the 329 R3 alerts at 244k.
- `large_cash_amount`: tests £10k–15k and £10k–30k; upper end consistent with Barclays/HSBC £20k-a-year caps.
- `cheque_amount`: tests median £50 and £200; Pay.UK's all-cheque average (£1,431, 2025) includes business cheques,
  so no personal figure exists.

## 7 Oct 2026 — rule-tuning scales moved into the config

The list of scales tried when tuning R3–R6 was fixed in `rules.py` (`np.geomspace(0.25, 8, 26)`). It is now
`rules.tune_scales` in `configs/sim.yaml` (low 0.25, high 8, 26 steps) with its source note, so it can be cited
and changed with `--set`. Same values: rebuilding `data/v1` gives identical files, tuning table and chosen
scale (1.516); 10 checks and 5 tests pass.

## 7 Oct 2026 — first full-size run (`data/v1_full`)

No code change. `sim.run all --out data/v1_full --set size.n_accounts=244000` at commit `e81d984` (seed 42):
all 10 checks pass; 732 launderers (180 in test months 6–7); 108.7M transactions; rules tuned to scale 1.741
(50k: 1.516) give 5,930 alerts, 96.9% false alarms, 25% of launderers alerted (median 9 days after start),
weekly alert budget mean 54.4 / median 28. Activity-model AUC 0.755, application-only 0.734. 11 min, 7.2 GB.
Also confirmed: rebuilding `data/v1` from scratch on Python 3.12 reproduces it exactly.

## 7 Oct 2026 — `--set` overrides and run manifests

**Change.**
- `sim.run` takes `--set key=value` (repeatable; value read as YAML) to change a setting for one run without
  editing `configs/sim.yaml`. Unknown keys and malformed values are refused before anything is written.
- The `accounts` step writes `<out>/run_manifest.json`: config file + hash, `--set` values, seed, BAF file +
  hash, git commit (and whether there were uncommitted changes), Python and package versions. Later steps refuse
  to run with different settings. `sim.checks`, the data card and `tests/test_data.py` re-apply the overrides.
- The data card shows the overrides, code version and BAF file, and its tables have a fixed order.
- The too-easy check is now repeatable (seeded model, rows sorted). It read 0.714 / 0.721 on earlier runs of
  the same data; it now reads AUC 0.741, average precision 0.103 every time on `data/v1`.
- `pytest` added to `requirements.txt`.

**Effect on results: none.** The generated data does not change; `data/v1` was made before manifests, so its
data card says "overrides unknown". All 10 checks and 5 tests pass on `data/v1` and on 2,000- and 6,000-account
test runs made with `--set`.

## 7 Oct 2026 — anonymous transaction ids (fixes a label leak)

**Problem.** `txn_id` in the public `transactions` file started with `L_` for every laundering transfer and
`N###_` for normal ones, so anyone reading the column could see which rows were laundering. Laundering rows
also sat together at the start of the file, so a row's position gave the label away too. Flagged in the EDA
report (§12); fix approved 7 Oct 2026.

**Change.**
- `finalize` now gives every transfer a new id: `T` + 16 hex characters of md5(provisional id + seed).
  Both rows of an internal transfer still share one id. Same config + seed still gives identical data.
- `transactions` is written sorted by `day`, `time` (ties by `txn_id`, `account_id`).
- The provisional `N###_` / `L_` ids remain only in the hidden working files under `_internal/`.
- New check 10 (`anonymous ids`) fails if any id is not `T` + 16 hex, if laundering ids are not spread
  evenly (mean position must be within 0.45–0.55), or if rows are out of time order.

**Effect on results: none.** Rebuilding `data/v1` (50,000 accounts, seed 42) left `accounts`,
`accounts_truth`, `aml_alerts` and `aml_outcomes` byte-identical; every transaction row and label is
unchanged (22,276,022 rows, 21,741,821 distinct ids, no collisions). Only `txn_id` values and row order
changed. All 10 checks and 5 tests pass.

**Action for the team.** Re-generate or re-run `finalize` on any local copy of `data/v1` made before this
change; old copies still carry the leak. Never build features from `txn_id`; use it only to join the two
rows of a transfer.
