# CLAUDE.md — aml-detection-system

BT4102 group project (NUS). Question: can account-opening data plus early activity catch money-laundering
(mule) accounts **earlier** than a bank's existing rules? No public data links applications to later
transactions, so we **simulate** one: real BAF applications -> hidden profiles -> 18 months of simulated UK
banking -> laundering planted from published evidence -> the bank's 6 rules as the benchmark.

## Working style (read first)
- **Never assume when unsure.** Ask the user clarifying questions until ~95% confident before changing
  anything that affects results. State assumptions explicitly.
- Explain in plain, simple language (the team includes non-specialists). Prefer small, verifiable steps.
- **Never change an approved setting silently.** Every number in `configs/sim.yaml` was approved by the team.
  Propose the change, say why, get a yes, then update the value AND its `source` note (add "changed <date>").
- Ground new numbers in a source (published figure, our arithmetic on one, SAML-D measurement) or label
  them `assumption` with `test` values. Never invent a statistic.

## Commands
```bash
pip install -r requirements.txt
# BAF Base file -> data/raw/BAF_Base.csv (or pass --baf PATH). data/ is git-ignored.
PYTHONPATH=src python -m sim.run all --baf data/raw/BAF_Base.csv        # full pipeline -> data/v1/
PYTHONPATH=src python -m sim.checks --baf data/raw/BAF_Base.csv         # 10 checks + data/v1/data_card.md
PYTHONPATH=src BAF_PATH=data/raw/BAF_Base.csv python -m pytest -q tests  # must pass before any commit
```
Modelling (plan: "Modelling: phased plan" tab of the decision-record doc; Phases 0–3 done):
`PYTHONPATH=src python -m features weekly --out data/v1_full --weeks 0-77` builds `<out>/features/weekly.parquet` (28 features
from the Phase 1 gate list, see `src/features/weekly.py`; money summed as exact pence; weeks 0–77, since week 78 holds only 2 days of data; 19.0M
account-weeks, ~4 min, ~4.2 GB) +
`peer_medians.parquet` (frozen from months 0–4) + `features_manifest.json` (feature list, cut-off rule, code commit, hash of the
data's `run_manifest.json` and of the peer medians, and a fingerprint of the feature SQL; `features.weekly.load()` and
`features.manifest.check()` refuse a stale store, including one built by different feature code).
`python -m features store-check [--out D]` runs `notebooks/03_feature_store.ipynb` (Phase 3 gate: store equals the EDA's query
value by value, first-week AUCs with account-level bootstrap intervals, whole-store checks) -> `outputs/modelling/features[/<run>]`.
`tests/test_feature_store.py` checks the store on real data (independent pandas re-implementation, no-peek cut test,
byte-identical rebuild, whole-store invariants); run it with `SIM_OUT` = a folder whose store is built. `python -m features eda [--out data/v1 --report DIR]` executes `notebooks/01_eda_train.ipynb`;
`python -m features preprocess [--out data/v1_full --report DIR]` executes `notebooks/02_preprocess.ipynb` (Phase 2: all its
code is in the notebook) -> `<out>/features/accounts_{linear,tree}.parquet` + `preprocess_manifest.json`, `<report>/params.json`
+ `report.md` (default `outputs/modelling/preprocess[/<run>]`); `python -m models train` fits and saves the frozen model
(`src/models/train.py`); model code refuses cleaned tables whose `preprocess_manifest.json` does not match the data run
(`features.manifest.check_preprocess`).
Feature lab: candidate features live in `src/features/candidates.py` (built from the store, same and earlier weeks only;
`tests/test_feature_candidates.py`); `python -m models.feature_lab --out data/v1 --groups G... --name N` refits the tuned
LightGBM (activity + application score, as notebook 06; `--views activity` for store features only) with each group added
(baseline folds, months 0–4 only) and judges it on the tuning measure, weekly earliness (decision 26 Oct 2026) ->
`outputs/modelling/feature_lab/<data>/<name>/` and an append-only `ledger.csv`. **Adopted (26 Oct 2026, Kee Chee Pheng):**
the 8 four-week-window features (`candidates.ADOPTED`, group `roll4`), added at load time with
`lgbm_baseline.load_table(..., adopted=True)` (not stored; weeks must start at 0).
**Feature list frozen (28 Oct 2026, Kee Chee Pheng):** for tuning step 2, calibration (month 5) and the test months the
LightGBM inputs are the 28 store features + the 8 `roll4` features + `weeks_since_open` + the application score
(`app_score`): 38, the lab's baseline. Changed only by team decision. Feature-lab trials and `/feature-round` run only on
explicit request and are report-appendix work; re-checking `roll4` on Variant II / IV is a robustness check, not a
reopening of the list. Tuning step 2 and later models use them;
the lab's baseline includes them (`--baseline store` to re-check them). Notebooks 05/06 stay the records of the store-only
runs. The lab also splits each gain by phase (`pre_start_recall`, `start_recall`, `later_recall`) and reports
`first_caught_2wk` with permanent flags: weekly recall rewards re-flagging mules already found (26 Oct 2026 finding). The `feature-engineer` agent (`.claude/agents/`) runs propose -> implement -> verify -> evaluate
trials; it never changes the store, which stays a team decision.
Agent trials 26 Oct 2026 (v1_full, vs the adopted model; groups `new_cp4`, `self4`, `speed_cum` in `candidates.py`,
merged from the agent worktree 27 Oct 2026): `self4` (last 4 weeks vs the account's own earlier average)
weekly recall +0.03, better in all folds, mostly later weeks, loses 1 unwitting mule in fold 1: **not adopted (decision
28 Oct 2026, Kee Chee Pheng)**: the gain is re-flagging (later recall +0.05 to +0.08; start recall +0.008 to +0.029;
first catch within 2 weeks unchanged), worth nothing with a permanent flag; stays a candidate group, not in `ADOPTED`;
`speed_cum` +0.13 but almost all repeat flags: dropped; `new_cp4` (v1 only) no clear change: dropped. Finding: weekly
recall rewards re-flagging mules already found, worth nothing with a permanent flag. Split by phase, `roll4` still lifts the
start-week flag rate (0.703 -> 0.781, all folds), but first catch within 2 weeks with permanent flags stays 0.958 / 0.957.
17 looks on v1_full against the same folds so far (multiple-looks risk).
**EDA -> feature loop (decided 27 Oct 2026, report appendix only; never changes the frozen feature list):** `/feature-round`
(`.claude/skills/feature-round/`) runs the `eda-explorer` agent (months 0–4 of v1_full via `amldata`: store, raw
transactions, labels with type; explores the data first, then audits each finding against `src/sim/` / `sim.yaml`) ->
up to 5 insights in `outputs/modelling/eda_agent/insights.csv` (append-only; only `status` / `trial` / `note` change;
`tests/test_eda_agent.py`) with `notebooks/07_eda_agent_<round>.ipynb` as evidence -> the user picks -> the
`feature-engineer` runs at most 3 trials -> a v1_full promotion candidate is judged **once** on `data/sensitivity/seed__43`
(same settings as v1_full, seed 43, rules frozen at 1.516; never used by a trial before), its store and cleaned table built
on first use. **Round r01 (28 Oct 2026, focus real-customer mules):** for real customers no signal before the start (21 of
376 checks in the 2 weeks before, ~19 expected by chance); 4 start-week insights: r01-1 matched forwarding (strongest, AUC
0.88 real, needs raw transactions: team proposal), r01-3 repeat payee (artefact: normal accounts never repeat a payee),
r01-2 `max_out_hist` and r01-4 `internal_out` trialled: no gain on v1_full (r01-4 PR-AUC worse in all folds), so seed 43
unused. The current model already flags 0.78 of mule weeks in the start week and the next, first catch within 2 weeks
0.957, 27 of 32 real-customer mules in the top 1%. 19 looks on v1_full so far.
Phase 4 baselines (untuned, 3 temporal folds, months 0–4, weeks 0–26): `notebooks/05_lgbm_baseline.ipynb` (helpers in
`src/models/lgbm_baseline.py`) and `notebooks/04_logreg_baseline.ipynb` -> `outputs/modelling/models/<run>/`; both
reproducible run to run (sorted rows via `weekly.load(months=)`, LightGBM `deterministic=True`, since 22 Oct 2026).
v1_full account-level PR-AUC, LightGBM / logistic: activity 0.730 / 0.122, application 0.011 / 0.025, combined
0.256 / 0.274 (logistic since 25 Oct 2026: share features clipped to [0, 1] in notebook 04; unclipped speed shares
reach 222 and gave 0.038 / 0.112). Combined LightGBM overfits: train 1.00 vs validation 0.40 on the last fold, 87% of its gain from
application columns (fake accounts are mules in every week, so it learns to recognise them).
Tuning step 1 (`notebooks/06_lgbm_tuning.ipynb`, helpers `src/models/tuning.py`, 22 Oct 2026): equal weight per account
barely helps (combined 0.256 -> 0.279); the application as one out-of-fold logistic score (label: mule by week 26)
fixes the memorising (gap 0.74 -> 0.18; 0.695). Activity alone still leads on account level (0.730), but activity +
app score wins in 27 of 27 weeks and puts 15% of mules in each week's top 1% in weeks 0-8 vs 4%: earliness, which
the account-level measure does not reward. It catches fewer real mules in the account top 1% (19/32 vs 25/32).
Stability + 1:20 undersampling (`notebooks/10_stability_undersampling.ipynb`, helpers `src/models/stability.py`, 29 Oct
2026, draft PR, this Mac's v1_full copy, months 0-4): the lab baseline is reproducible on one machine (two runs identical;
equals 26 Oct); 0.4086 / 0.4023 / 0.4123 came from three machines and data copies (an app-score nudge of 1e-6 moves it as
much). Tuned seed SD of `catch_0.1pct` 0.006-0.008 > 0.005, so the pre-registered rule recommends a 5-seed average (adopted:
`frozen_tuned_avg5`, below); tuning's lead beats seed spread on weekly recall only. 1:20 whole-account undersampling: same
earliness, weekly recall -0.007, PR-AUC -0.020, 2-4x faster; class weights stay. -> `outputs/modelling/models/v1_full/stability/`.
Feature lab (`python -m models.feature_lab`, `src/features/candidates.py`, ledger `outputs/modelling/feature_lab/ledger.csv`,
26-27 Oct 2026): candidate groups judged on the tuned model; `roll4` (8 four-week-window features) adopted 26 Oct, computed
at load time (`load_table(..., adopted=True)`). **Proposal 28 Oct 2026, pending the team** (plan:
`outputs/modelling/feature_lab/PLAN.md`): `--decide catch_rules` = permanent flags at the rules' own weekly alert count
(`src/evaluation/budget.py`; ~0.02% of accounts a week vs the top 1%'s ~60x), the rules' own value beside it;
`--placebo N` measures refit noise; special groups `app_split` (two application scores, `tuning.app_score_split`),
`graph_struct` (`python -m features graph` -> `<out>/features/graph_weekly.parquet` + `graph_edges.parquet`, own
manifest, store untouched) and `graph_nb` (neighbours' scores from a two-stage model, `src/models/graph_nb.py`, cached in
`<out>/features/graph_nb/`); `--scratch DIR` for development runs that skip the ledger. Report-appendix work under the
freeze: v1_full results (catch_rules: rules 0.141, frozen model 0.457; `roll4` holds at the rules' budget, `app_split` and the
graph groups no clear gain) agree with the frozen 38 inputs; measured refit noise 0.012 (catch_rules), 0.006 (weekly recall).
Phase 5 (28 Oct 2026): `python -m models train [--out D --params FILE]` fits the frozen model on months 0-4 ->
`data/<run>/models/frozen/`; `python -m evaluation.score [--months 5]` runs the fixed-cohort harness at the rules' weekly
budget -> `outputs/modelling/results/<run>/month5_dryrun/`; test months only with `--final-test`, once (lock file).
Dry run, month 5 of v1_full, weeks 0-26: model 62 of 78 mules caught vs rules 16 (precision 0.50 vs 0.13), no flag before
laundering starts (the budget is ~5 flags a week).
29 Oct: `python -m models calibrate` (month 5, isotonic, out-of-fold check), `train --inputs activity` + `python -m evaluation.compare` (onboarding value: month 5 frozen 65 vs activity-only 61 of 78; seed 43 56 vs 56), age-band breakdown, machine recorded. Tuned model differs by machine (63 Windows vs 65 Mac): machine of record undecided; local runs `_macos`.
Option B (29 Oct): train once, share the model files (`lgbm.txt`, `app_logreg.json`, `manifest.json`, later `calibration.json`) in `data/<run>/models/<name>/`; scoring a file is identical across machines. `python -m features fingerprint` compares data by content; `python -m models verify --model M --reference RUN` accepts an older shared model once by reproducing a committed run.
**Model of record: `frozen_tuned_avg5` (decision 30 Oct 2026, confirmed 2 Nov, Kee Chee Pheng), committed in `outputs/modelling/models/v1_full/frozen_tuned_avg5/`** (lgbm_seed1-5.txt, app_logreg.json, manifest, calibration.json): the tuned settings fitted with LightGBM random_state 1-5 on the same rows and the same application score (seed 42), score = mean of the 5 probabilities (`train --tree-seeds 1 2 3 4 5`, `train.MODEL_OF_RECORD`). Why: notebook 10's pre-registered rule (seed SD of `catch_0.1pct` 0.006-0.008 > 0.005); trained on this Mac. Found there first by `models.train.load`, never retrained (`train` refuses the name). Do not retrain it: score with `python -m evaluation.score` (default model). Retraining on another machine gives slightly different trees. The previous model of record `frozen_tuned` (Li Ann, seed 42, 28 Oct) stays committed for comparison.
30 Oct 2026 (harness gaps): `python -m models predict --out D [--model M] --months 5 [--weeks 0-77] [--to PATH]` writes
`<out>/scores/<model>_m<months>.parquet` (account_id, weeks_since_open, score); `python -m evaluation.score --scores PATH`
scores any such file (checked by `score.load_scores`; byte-identical results to the model path on month 5). New
measures: `recall_final_label` (caught / all cohort launderers by the final label; month 5 weeks 0-26: model 0.649, rules
0.165), `median_min_days_earlier_model_only` (model-only catches, flag to horizon end: 84 days), weekly `tied_at_cut`
(none on month 5). `model_anytime` is reported for horizons <= 26 only (not meaningful past the training weeks 0-26; not
an upper bound). A final run writes `final_test/STARTED.json` before reading months 6-7 and is refused while
`STARTED.json` or `LOCK.json` exists (clearing it is a team decision). settings.json records `score_source`,
`scores_sha256`, `run_manifest_sha256`, `git_commit`. Re-run: `results/v1_full/month5_dryrun_v2/` (existing columns
identical to `month5_dryrun_frozen_tuned`).
31 Oct 2026 (Emmy Li): the harness also writes `by_month_w<W>.csv` (catches and flag shares per opening month, the
calendar-drift check for the 6+7 cohort). Final-test rehearsal on `data/v1` with stand-in `rehearsal_tuned` passed
(`results/v1/final_test/`, locked; a code check, not a result). Commit before the 5 Nov run.
**Outlier appendix (30 Oct 2026, Kee Chee Pheng; plan `outputs/modelling/outlier/PLAN.md`, team doc
https://claude.ai/artifact/MVKuDNLsRt74YdfLkygXZg):** can label-free detectors beat the rules, and do they find the 543
mules the bank never confirmed (189 of 732 confirmed)? Decided: month 5 only, never 6-7 (D1); bank label = closed by
the bank at any time (D2), from the true start (D3); no `amldata` change (D5). Methods: M3 rarity score (per input the
tail share in its suspicious direction, high except fast forwarding; mean of the 3 rarest; one reference per week
since opening), M3s `rarity_sum` (ECOD's sum, side-by-side only) and M4 Isolation Forest on ranks (`python -m models
outlier --method rarity|rarity_sum|iforest`, `src/models/outlier.py`); settings reviewed by label-free checks
30 Oct (plan, "Review of the judgment calls"); M2 `bank_label` = the frozen recipe
trained on bank-confirmed mules only (`models train --label bank`, `train.bank_confirmed` from `open_by_day`); M1b
`truth_macos` = the frozen recipe retrained on this Mac, M2's yardstick. `python -m evaluation.hidden_mules --scores
NAME=PATH ...` -> caught for bank-confirmed vs never confirmed, by type and pattern, top false alarms, bootstrap.
`python -m evaluation.outlier_look freeze | check | look` (look refuses unless the committed frozen settings equal the
code and model files, and runs once). D4 (31 Oct): no autoencoder. Frozen 31 Oct (PR #49); **the one look ran 31 Oct
2026** (planned 6 Nov; PR #50; spent: never re-run, settings never change). Month 5, 78 mules, 124 flags: rules 16,
M1 63, M1b 63, M2 54, M3 16, M3s 39, M4 16; never-confirmed (62): rules 3, M1 50, M2 42. Write-up:
`notebooks/12_outlier_detection.ipynb` (reads only the committed look outputs) -> `outputs/modelling/outlier/v1_full/
report.md`; draft appendix text `outputs/modelling/outlier/APPENDIX.md`. On this Mac run commands with `venv/bin/python`.
Sensitivity runs (rules frozen, 244k, one `test` value each): `python -m sim.sensitivity --list | --run [--only NAME]
| --summarise` -> `data/sensitivity/<name>/` (large files deleted) and `outputs/sensitivity/summary.csv`.
Single steps: `accounts`, `normal --batches 3-3`, `laundering`, `rules`, `finalize`. Use `--out` for another
output folder (e.g. `--out data/variant_II --baf data/raw/Variant_II.csv`). Run `sim.checks` after every run.
Change a setting for one run with `--set key=value` (repeatable, value read as YAML), never by editing the YAML:
`--out data/v1_full --set size.n_accounts=244000`. The `accounts` step writes `<out>/run_manifest.json`
(config hash, overrides, BAF hash, git commit, package versions); later steps refuse different `--set` values;
`sim.checks`, the data card and `tests/test_data.py` re-apply the manifest's overrides automatically.

## Repo map
- `configs/sim.yaml` — **single source of truth** for every number: `value`, `source`, `strength`
  (sourced / derived / samld / assumption / modelling / design), `test` (values for sensitivity runs).
- `src/sim/` — simulator: `accounts.py` (BAF rows, profiles, start days, networks) -> `normal.py`
  (everyday UK banking) -> `laundering.py` (15 SAML-D shapes) -> `rules.py` (R1–R6) -> `run.py` (CLI,
  batching, closure removal) -> `checks.py` (checks + data card). `src/sim/eda/` — EDA scripts.
- `src/amldata/` — **the only way model code reads data** (see Data rules).
- `src/evaluation/` — scoring code; the only place besides `sim` allowed to read hidden files.
- `src/features/` — preprocessing and the weekly feature store (`weekly.py`, `manifest.py`); reads via `amldata` only.
- `notebooks/` — **analysis notebooks are the standard for EDA and modelling write-ups** (`01_eda_train.ipynb`, ...); reusable
  code (features, preprocessing, models, scoring) stays in `src/` packages so tests cover it. `python -m features eda` executes
  the EDA notebook on a data folder; the hidden-file guard scans notebook code cells too.
- `src/models/` — training and calibration (Phase 4). `outputs/modelling/` — committed modelling results (see its README).
- `tests/` — `test_data.py` (runs the 10 checks), `test_hidden_files.py` (blocks hidden-file leaks).
- `outputs/` — committed results (e.g. `outputs/eda/`). `data/` — generated data, never committed.

## Data rules (non-negotiable)
- 6 files in `data/v1/`. **Model inputs:** `accounts` (32 cols: id, open_month, open_day, 29 BAF features)
  and `transactions` (11 cols; card spending = one row per account per week, `item_count` = purchases).
  **Hidden:** `accounts_truth`, `aml_alerts`, `aml_outcomes`, `transactions_truth`.
- Model/feature code uses `amldata.public()` and `amldata.labels(...)` only. Default folder is
  `data/v1_full` (main dataset); pass `out=` for others (`data/v1` 50k, `data/variant_II`, `data/variant_IV`). `labels()` returns
  `is_launderer` (fixed final label) for months 0–5 and refuses test months 6–7; with a cut-off
  (`as_of_day=` one calendar day, or `weeks_since_open=w` = end of each account's week w) it adds
  `started_by_day` and `mule_by_day` (main label: fake accounts count from opening, real customers from start), and
  for months 0–5 `open_by_day` (0 once the bank has closed the account, i.e. `aml_exit_day <=` cut-off; only confirmed
  launderers are closed, so drop account-weeks with 0 from training; withheld when test months are requested).
  `labels(profile=True)` adds each launderer's hidden type (fake / witting / unwitting; None otherwise) for EDA on
  months 0–5 only; it refuses test months even with `allow_test`. Never a model input (decision 9 Oct 2026).
  Scoring code uses `amldata.evaluation()`. Never read hidden parquet files directly elsewhere.
- `txn_id` is anonymous (`T` + 16 hex of md5(provisional id + seed)); rows sorted by `day`, `time`. Provisional
  `N###_`/`L_` ids exist only in `_internal/parts` and must never reach public files (check 10).
- Time split by `open_month`: train 0–4, calibrate 5, test 6–7.
- Weekly scoring: features for week w use only rows with `day <= ` that week's cut-off. No peeking ahead.
- `transactions` is ~22M rows (50k accounts) / ~109M (244k, 7.2 GB on disk). Query it with **DuckDB**, never load it
  whole into pandas. Each 5,000-account batch peaks ~2.7 GB RAM; `run` uses one process per batch.

## How the simulator works (short)
- 0.3% launderers inside the 18-month window: fake 73% (BAF `fraud_bool=1` rows, own ages), witting 13.5%,
  unwitting 13.5% (clean rows weighted to Cifas mule ages). Start: fake ~90 days; existing customers RUSI
  bands. ~25% in one big network, rest short chains (Vocalink).
- Normal banking from UK Finance / Pay.UK / ONS; amounts scale with BAF `income` (ONS spending fifths).
- Laundering: one ~2-week burst, 15 SAML-D shapes (SAML-D account weights), amounts anchored to RUSI
  £532, forwarded at RUSI speed; abroad share = 3.15× normal (SAML-D ratio on the UK rate).
- Rules (weekly): R1 cash ≥ £10,000; R2 >£1,000 cash/day on 2+ days in 2 weeks or 12-month cash crosses
  £10,000; R3 many payers; R4 pass-through; R5 high-risk country; R6 sudden change. 28-day pause, 3–30 day
  review, 80% of true alerts confirmed, closure removes later activity. R3–R6 tuned together.
- Results below are after the R6 fix (8 Oct 2026: R6 waits 8 weeks; before it, 65% of alerts were R6 firing on
  new accounts' first salary, none true, and false alarms were 96.9–97.2%).
- v1 result (50k, seed 42): 94.0% false alarms (inside the 90–95% target), 30% of launderers alerted, median 7
  days after start; weekly alert budget mean 7.3.
- v1_full result (244k, seed 42, `--set size.n_accounts=244000`, 11 min): 93.4% false alarms (3,614 alerts,
  240 true); 32% of 732 launderers alerted (237), median 9 days; weekly alert budget mean 33.2 / median 34;
  rule scale 1.516 (same at 50k); 180 launderers in test months 6–7. **This is the main dataset for modelling.**
- Variants (244k, seed 42, rules frozen at 1.516): `data/variant_II` (fairness: age 50+ launderer rate higher in
  all months) and `data/variant_IV` (drift: 50+ about 2x under-50 in train months, gap reversed in test months).
  Rules: 93.2% / 93.1% false alarms, 34% / 33% caught; 169 / 171 test launderers. Use each variant for training
  AND testing with the same split as the main data (IV's bias exists only in training months by design);
  train-on-main / test-on-variant is an optional extra robustness check.
- Sensitivity (42 runs, rules frozen at 1.516; `outputs/sensitivity/FINDINGS.md`): the rules' catch rate moves
  only with launderer behaviour (£1,500 transfers: 75%, repeated bursts: 76%, vs 32–33%); false alarms move with
  prevalence (1%: 81.3%, 0.1%: 97.8%), normal cash use (98.4%) and group-collection size (R3). Seeds 43/44:
  93.1–93.4% / 32–33%. Re-check models on those scenarios.
- Everything is seeded and deterministic: same config + seed = identical data.

## Known limits / gotchas
- No SAML-D rows are copied; SAML-D supplies labels, shapes and a few shares only. BAF's country is unstated;
  the simulation is UK-calibrated. Results are relative comparisons, not real detection times.
- Laundering card spending is deferred (single card rows would stand out next to weekly card rows).
- EDA: `src/sim/eda/eda_sim_v0.py` + `outputs/eda/eda_report.md` are the v0 record; leave them unchanged.
  `src/sim/eda/eda_sim_v1.py` (heavy parts in DuckDB; 244k: 82 s, 11.9 GB peak) reads `data/v1_full` -> `outputs/eda/v1_full/`;
  other runs via `EDA_DATA=data/v1 EDA_OUT=outputs/eda/v1_50k`. Needs matplotlib.
- On Windows set `PYTHONPATH=src` with `set` / `$env:`; paths in DuckDB SQL work with forward slashes.

## Git
- Record every change to the generated data in `CHANGELOG.md` (newest first) and the decision-record docs.
- Branch per change, PR into `main`. Never commit `data/`. Run checks + pytest before committing.

## Next tasks
**Status 27 Oct 2026** (team plan: doc tab "Team plan: final 3 weeks"): Phases 0–3 done; Phase 4 baselines, tuning step 1
and feature adoption (`roll4`) done. Feature engineering is closing: `self4` not adopted (28 Oct; the agent worktree's lab code,
phase split, `--baseline store` and trial outputs were merged 27 Oct), so the model inputs stay store + `roll4`; feature list
frozen 28 Oct (see the Modelling commands above). Gate 28 Oct: tuning
grid done (Li Ann, with `adopted=True`), ~~harness dry run on month 5 (Emmy Li)~~ done 28 Oct (`evaluation.score`), stress-test datasets and Variant II / IV
stores built (teammate 4; then re-check `roll4` there). 4 Nov: models calibrated on month 5 and frozen. 5 Nov: test
months 6–7 scored once. 11 Nov report final, 12 Nov submit (date to confirm). Caution: the lab and the tuning measure use
each week's top 1% (~300–500 accounts a week); the rules flag ~7–9 cohort accounts a week in weeks 0–12 (111 of 50,061),
about 60x fewer, so only the Phase 5 harness at the rules' budget shows whether the features help.
1. ~~`--set key=value` override~~ done 7 Oct 2026 (with run manifest).
2. ~~Full-size run~~ done 7 Oct 2026, regenerated 8 Oct after the R6 fix: rules at 93.4% (see above).
3. Modelling. **Decisions 9 Oct 2026** (phased plan in the doc tab "Modelling: phased plan"): one pooled account-week
   model (row per account per week since opening, label `mule_by_day`, `weeks_since_open` a feature); horizon weeks 0–26 main,
   0–77 appendix (week 78 holds only 2 days, dropped 22 Oct 2026); a model flag is permanent (caught at first flag, leaves the pool); class weights main + one 1:20 undersampling
   ablation, no SMOTE; features precomputed to `data/<run>/features/` with a manifest; lightgbm + torch (CPU) + networkx.
   Phases: 0 setup ~~done 9 Oct~~ -> 1 EDA ~~done 9 Oct~~ (`notebooks/01_eda_train.ipynb`, run by `python -m features eda`; months 0–4 only, month 5 untouched;
   `outputs/modelling/eda/report.md` + `univariate_tests.csv` + `feature_screen.csv`; 50k copy under `eda/v1_50k/`) -> 2 cleaning
   (BAF −1 codes -> NaN + flag; `credit_risk_score` negatives are real) -> 3 feature store -> 4 models -> 5 harness (dry-run on
   month 5 first) -> 6 extensions (fake-mix stress test first). Dropped as un-rewardable by the simulator: round/under-limit
   amounts, quiet-then-active. **EDA findings 9 Oct 2026, corrected 18 Oct (244k, months 0–4, 455 launderers):** at opening
   fake accounts separate (housing_status, device_os, keep_alive_session, address months, credit score; AUC 0.60–0.69 vs
   0.5); real-customer mules separate mainly on age (customer_age AUC 0.25: ~65% under 30 vs 27% of normal accounts, from
   the simulator's Cifas age weights `profiles.real_mule_age_weights`; fakes skew older, so the all-launderer AUC of 0.53
   hid it), weakly on housing_status (0.57) and income (0.45); age is allowed as a model input (decision 19 Oct 2026;
   Variant II tests fairness).
   Fakes start laundering in weeks 8–17 (median 13), real customers
   spread over weeks 1–75; 361 of 455 start inside the 26-week horizon. Activity screen (open weeks only): cumulative rows and
   money in, rows and payers this week, median in->out delay and the 1 h / 24 h speed shares carry signal once a burst
   exists (AUC 0.70–0.86 vs started; speed 0.78 / 0.75 at week 8); weekly abroad / high-risk / cash shares carry none.
   Before the start (weeks 0–7, tested 21 Oct) activity adds nothing beyond the application: fakes' money in is higher
   (AUC 0.58) only through their higher BAF income (31% top band vs 20%); inside an income band 0.51.
   (Correction 18 Oct: the EDA's AUC helper ranked missing values highest, which hid the share features and led to a
   wrong "redefine the speed shares" proposal; `notebooks/03_feature_store.ipynb` and `eda_sim_v1.py` had the same helper.)
   Homophily (payment links inside the bank, both ends months 0–4): mixed launderer–normal links r = 0.450% vs 2xy = 0.545%
   (z −14; 0.95 of expected, z −4.0, allowing for links per account); 163 launderer–launderer links vs ~9 by chance; a
   launderer's payees are launderers 5.4% of the time, 20x the base rate -> graph features worthwhile. Label-shuffle test
   (1,000 shuffles) p = 0.001. Only 1 of the 163 links exists before both ends start laundering, so graph features find
   network partners after a burst starts, not before (21 Oct 2026).
   **Closure footprint (decided 15 Oct 2026):** every open account has a weekly card row, so a zero-row week = closed by the
   bank = a confirmed launderer (116 of 455 training launderers stop early, 1 normal account). Post-closure account-weeks
   are dropped from training and the scoring pool via `labels(...)["open_by_day"]` (months 0–5). Do not use a zero-row week
   as the closure test: it also drops ~420 normal account-weeks (months 0–5, weeks 0–26).
   **Phase 2 — cleaning and preprocessing (plan revised 10 Oct 2026; built and run 15 Oct, PR open; gate: team agrees the 3 proposals below).** Goal: one fixed,
   tested recipe that turns the 32-column `accounts` table into model inputs. **All Phase 2 code lives in
   `notebooks/02_preprocess.ipynb`** (decision 10 Oct 2026, Phase 2 only; Phases 3–5 not decided). Later phases read the
   notebook's output *files*, never import notebook code. The data has no NaN, duplicates or broken keys by construction
   (10 checks), so "cleaning" means BAF's codes and encodings. **Fit per dataset (decision 10 Oct 2026):** the recipe is the
   same everywhere; medians, levels and scaler numbers are fitted on each dataset's own months 0–4 (v1_full, v1, variant_II,
   variant_IV, a sensitivity run when used); train-on-main / test-on-variant reuses the main fit.
   - *Unavoidable code outside the notebook (3 small pieces):* (1) `open_by_day` in `src/amldata/loaders.py` (only amldata
     may read hidden `aml_outcomes`); (2) `python -m features preprocess [--out D --report R]` in `src/features/__main__.py`
     runs the notebook through the existing `run_notebook` (generalise its default report folder per notebook);
     (3) `tests/test_preprocess.py` executes the notebook on `data/v1` (skipped without data).
   - *Step 0, the open decision first:* ~~done 10 Oct 2026~~ `labels()` returns `open_by_day` with any cut-off (1 unless
     `aml_exit_day <=` the cut-off; a bank knows which accounts it closed), months 0–5 only; withheld (column left out) when
     the request includes test months, even with `allow_test`. Tests in `tests/test_hidden_files.py`: closed accounts are
     launderers only; never rises again once 0 (weeks 0–78); 1 for every account at week 0 (earliest closure is day 55);
     total closures match `aml_outcomes`. v1_full months 0–4: 0 / 1 / 19 / 84 / 118 of 455 launderers closed by weeks
     0 / 8 / 12 / 26 / 78. Phase 3 drops training account-weeks with `open_by_day = 0`; the harness already counts closed
     cohort accounts as caught.
   - *Notebook sections (a plain-language markdown cell each, like `01_eda_train.ipynb`; reads `EDA_DATA` / `EDA_REPORT`,
     which `run_notebook` sets):* 0 setup; 1 the recipe as one Python dict per column (the report's column table is printed
     from this dict, so they cannot drift); 2 before: months 0–4 via `amldata.public()`, same table as EDA §1 for comparison;
     3 `fit(train) -> params` (pure function, months 0–4 only); 4 `transform(df, params, mode)` (pure function, `linear` /
     `tree`); 5 apply to all months 0–7 (accounts are public; no labels touched) and write files; 6 after: before/after per
     column, missing-flag rate launderers vs normal (labels months 0–4 only); 7 checks as `assert` cells (execution fails if
     one breaks); 8 write the report.
   - *Outputs:* `data/<run>/features/accounts_linear.parquet` and `accounts_tree.parquet` (keys `account_id`, `open_month`
     plus features, every account, months 0–7) + `preprocess_manifest.json` (recipe, fitted params, input/output columns per
     mode, months fitted, sha256 of `run_manifest.json`, git commit + dirty flag, package versions); committed copy
     `outputs/modelling/preprocess/params.json` + `report.md` (other datasets under `preprocess/<run>/`). JSON, not joblib:
     readable, diffable, no pickled notebook classes. Phase 4 refuses a file whose manifest hash differs from the data run.
   - *Column recipe (from the EDA, `outputs/modelling/eda/report.md` §1; 29 BAF columns):* (a) negative codes -> NaN +
     `<col>_missing` flag (both modes): `intended_balcon_amount` (73% negative), `prev_address_months_count` (69% at −1),
     `bank_months_count` (25%), `current_address_months_count` (0.4%), `session_length_in_minutes` (0.2%),
     `device_distinct_emails_8w` (0.04%); (b) `credit_risk_score` −165 to 385: real values, keep; (c) `velocity_6h`: fixed
     rule clip at 0 (0 negative rows in months 0–4, 9 in months 5–7 of v1_full, 5–12 in the other datasets), before any log;
     (d) categoricals `payment_type` (5), `employment_status` (7), `housing_status` (7), `source` (2), `device_os` (5):
     levels frozen from months 0–4; `linear` one-hot (unseen level -> all zeros), `tree` `category` dtype with the frozen
     levels (unseen -> NaN); (e) `income`, `customer_age`, `proposed_credit_limit` already binned: keep numeric; 6 binary
     columns (`email_is_free`, `phone_home_valid`, `phone_mobile_valid`, `has_other_cards`, `foreign_request`,
     `keep_alive_session`) stay 0/1; (f) `linear` only: `log1p` on `days_since_request`, `prev_address_months_count`,
     `session_length_in_minutes`, `bank_branch_count_8w`, `zip_count_4w`, `current_address_months_count` (**changed 10 Oct
     2026**, team decision: log only where it brings the skew closer to 0; `intended_balcon_amount` 1.34 -> −1.15 and
     `velocity_6h/24h/4w` 0.34 / 0.32 / 0.11 -> −1.20 / −0.34 / −0.45 on v1_full months 0–4 got worse, so they are no longer
     logged; by the same rule `current_address_months_count` 1.41 -> −0.54 was added; not logged: `proposed_credit_limit`
     (binned) and `device_distinct_emails_8w` (values 0–2); the notebook's section 6
     shows the skew with and without the log, section 7 asserts each logged column improves); (g) `open_month`, `open_day`, `account_id` never features; (h) `linear` = NaN step, clip, log, impute
     month 0–4 median, one-hot, standardise continuous columns (0/1 columns left as 0/1); `tree` = NaN step, clip, raw scale,
     NaN kept, category dtype. Proposals for the team: keep both columns of the 3 pairs with |Spearman| > 0.5 (Phase 4's
     regularisation handles them); flags in both modes; standardise continuous only.
   - *Transactions:* no cleaning needed; the feature store parses `time` to seconds, derives `counterparty_kind`
     (`EXT_*`, `CARD_MERCHANTS`, `CASH`, `A*`), counts the £0.00 rows and keeps them. Recorded here so the report's
     preprocessing section is complete.
   - *Checks (assert cells in section 7, run by pytest via the notebook):* `linear` has no NaN; `tree` NaN exactly where
     codes were; output column lists identical for months 0–4 / 5 / 6–7; `fit` twice gives equal params, and changing
     month 5–7 rows leaves them unchanged (a pure function of months 0–4); `linear` continuous columns mean ≈ 0, sd ≈ 1 on
     months 0–4; row count and `account_id` order preserved; an invented unseen level gives all-zero one-hot / NaN category;
     manifest hash equals the data's `run_manifest.json`. The hidden-file guard already scans notebook cells.
   - *Progress:* 10 Oct 2026 branch `preprocess` created; Step 0 done; notebook + CLI + `tests/test_preprocess.py` built.
     15 Oct: both notebooks find the repo root themselves (VS Code "Run All" works without `PYTHONPATH`); notebook run on
     v1_full (executed copy in `notebooks/`, report `outputs/modelling/preprocess/`), v1 (`preprocess/v1_50k/`),
     variant_II, variant_IV (`preprocess/<run>/`): all 25 checks pass on each, v1_full and v1 match EDA §1; 56 `linear` /
     35 `tree` features. Variant IV has 148,992 accounts in months 0–4 (its BAF file spreads accounts differently over the
     months; Variant II matches Base). Missing flags carry fake-account signal (v1_full months 0–4, normal / fake / real
     mule: `prev_address` 69% / 89% / 67%, `intended_balcon` 73% / 88% / 63%, `bank_months` 25% / 40% / 21%). Then
     pytest + `sim.checks` passed, commit + PR into `main`. Still open: decision-record doc, team agreement on the 3 proposals.
   - *Order:* branch `preprocess` from `eda-train` (PR #16 still open) -> Step 0 + tests -> notebook on `data/v1` (fast) ->
     `data/v1_full` -> v1 / variant_II / variant_IV copies -> pytest + `sim.checks` -> CHANGELOG + decision-record doc -> PR.
   - *Gate:* tests pass; the notebook's section 2 table matches EDA §1; team agrees the 3 proposals above; then the team
     fixes the Phase 3 feature list from the doc's "Phase 1 findings".
   - *Out of scope:* resampling (Phase 4, class weights), scaling of weekly activity features (Phase 3 computes them; the
     `linear` scaler is extended there), any look at months 6–7 labels.
   **Phase 3 — weekly feature store (done 15 Oct 2026, branch `phase3-features`).** 28 features from the Phase 1 gate list
   (`src/features/weekly.py`); stores built for v1_full and v1. Gate passed (`outputs/modelling/features/report.md`): the 14
   shared features equal the EDA's query value by value on every account-week; 25 of 28 features separate a launderer's
   first laundering week from normal weeks (95% account-level bootstrap); 30 tests pass on v1 and v1_full. **Speed shares
   (decision 15 Oct 2026):** `out_1h_share_wk` / `out_24h_share_wk` use the EDA's definition (any payment out after the
   latest payment in). A transfers-only redefinition was tried and dropped: it misses laundering through cash (1 h AUC
   0.772 vs 0.951 for cash patterns; equal for transfer-only patterns), 0.035 AUC worse overall (paired 95% interval
   0.021–0.050). Evidence: `outputs/modelling/features/report.md`, `python -m evaluation.speed_by_pattern`.
   **Decisions 8 Oct 2026:** weekly label = "mule account by this week" (a fake account
   counts from the day it opens; a real customer — witting/unwitting — from `launder_start_day`); alert budget
   = the rules' own alert count in each week. **Fixed cohort (8 Oct 2026):** main comparison = the 50,061 test
   accounts (opened months 6-7, 180 launderers), clock = weeks since each account opened (0-78), weekly budget =
   the rules' alerts on these accounts in that week of their life (after the R6 fix: 29 in weeks 0-3, 111 in
   weeks 0-12, 731 in total); secondary = same total of 731 flags under one score threshold over the horizon (a
   secondary policy, not an upper bound on the head start: weeks 27+ are outside the model's training weeks 0-26).
   This answers comment 2 of the professor's feedback (verbatim in `docs/professor_feedback.md`). Accounts closed
   by the bank stay in the cohort as caught; report accounts still open per week.
   1. ~~Add that label to `amldata.labels()`~~ done 9 Oct 2026: `mule_by_day`, with `weeks_since_open=` cut-offs.
   2. **Baseline to beat** (rough check, untuned application-only logistic model, train months 0-4, same number
      of flags as the rules on the test cohort; after the R6 fix the rules flag 662 test accounts): model 35/180
      (19%, precision 5.3%) vs rules 59 (33%, precision 8.9%) — the rules win on count; the model flags at
      opening, ~98 days *before* start vs rules 9 days *after*; together 80 (44%), overlap 14. (Before the fix,
      with 1,462 flags: model 31% vs rules 27%.)
   3. **Stress test the fake-account assumption**: 73% of launderers are fakes from BAF fraud rows and the
      baseline catches almost only fakes (34 of 35). Rebuild with `in_window_mix` tests (53% / 56% fake) and report
      how much the advantage shrinks — the main threat to the result.
   4. Weekly features via `amldata` (rows up to each week only); application-only / activity-only / combined
      models; score months 6-7 against the rules: caught within budget, days earlier, false alarms, precision.
   5. **Value of onboarding information (professor comment 2):** at each week since opening, on the same cohort
      and the same transactions, compare activity-only vs application + activity; the gap is the onboarding
      value, so data availability and cohort changes cannot explain it.
   6. **Label maturity (comment 2):** also score against a fixed final label (mule at any point in the window);
      report per week how many cohort launderers have started and how many accounts are still open.
   7. **Imbalance (comment 1):** model vs rules false-alarm share and precision at 0.1% / 0.3% / 1% prevalence
      (datasets exist under `data/sensitivity/`). The test set is never rebalanced; resample training data only.
   8. **Report checklist (professor):** justify dataset choice; size and variables; preprocessing; feature
      engineering; why each model suits the task. State that the test set is at the natural 0.3% rate.
4. Week 3: ~~BAF Variants II and IV~~ done 7 Oct 2026 (see above). Sensitivity runs from `test` values;
   professor's feedback: `docs/professor_feedback.md` (imbalance, cohort/data/label changes, report detail).
   **Decisions 7 Oct 2026:** (a) freeze the bank's rules: variant and sensitivity runs use
   `--set rules.fixed_scale=1.516` (the v1_full scale after the R6 fix; 1.741 before), never re-tuned; (b) sensitivity runs at 244k, keeping
   summaries and deleting large files (rebuildable from the manifest); (c) 0.1% prevalence run at ~732k accounts
   so the test set keeps ~180 launderers, 1% at 244k; (d) build repeated bursts and young-weighted fake ages,
   drop hijacked accounts (state as a limitation); (e) main run repeated with seeds 43 and 44 as the
   chance yardstick, one seed per sensitivity run.

## Decision records
- Logic, assumptions, full schema: https://claude.ai/artifact/LchcqbsutNLSHWKESoWWQL
- Schema doc: https://claude.ai/artifact/SEEF2YPKNohZMGEitcwcj5
