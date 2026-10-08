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
- `tests/` — `test_data.py` (runs the 10 checks), `test_hidden_files.py` (blocks hidden-file leaks).
- `outputs/` — committed results (e.g. `outputs/eda/`). `data/` — generated data, never committed.

## Data rules (non-negotiable)
- 6 files in `data/v1/`. **Model inputs:** `accounts` (32 cols: id, open_month, open_day, 29 BAF features)
  and `transactions` (11 cols; card spending = one row per account per week, `item_count` = purchases).
  **Hidden:** `accounts_truth`, `aml_alerts`, `aml_outcomes`, `transactions_truth`.
- Model/feature code uses `amldata.public()` and `amldata.labels(as_of_day=...)` only. Default folder is
  `data/v1_full` (main dataset); pass `out=` for others (`data/v1` 50k, `data/variant_II`, `data/variant_IV`). `labels()` returns
  `is_launderer` (+ `started_by_day`) for months 0–5 and refuses test months 6–7.
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
- v1 result (50k, seed 42): 97.2% false alarms (target 90–95% unreachable; **accepted, report as a
  finding**), 30% of launderers alerted, median 7 days after start; weekly alert budget ~15.
- v1_full result (244k, seed 42, `--set size.n_accounts=244000`, 11 min): 96.9% false alarms; 25% of 732
  launderers alerted, median 9 days; weekly alert budget mean 54.4 / median 28; rule scale 1.741 (50k: 1.516);
  180 launderers in test months 6–7. **This is the main dataset for modelling.**
- Variants (244k, seed 42, rules frozen at 1.741): `data/variant_II` (fairness: age 50+ launderer rate higher in
  all months) and `data/variant_IV` (drift: 50+ about 2x under-50 in train months, gap reversed in test months).
  Rules: 96.9% / 96.8% false alarms, 25% / 26% caught; 169 / 171 test launderers. Use each variant for training
  AND testing with the same split as the main data (IV's bias exists only in training months by design);
  train-on-main / test-on-variant is an optional extra robustness check.
- Sensitivity (42 runs, rules frozen; `outputs/sensitivity/FINDINGS.md`): the rules' catch rate moves only with
  launderer behaviour (transfer size, repeated bursts: 25% -> ~70%); false alarms move with prevalence (1%: 90.8%,
  0.1%: 99.0%) and normal cash use (98.9%). Seeds 43/44: 96.7–96.9% / 24–26%. Re-check models on those scenarios.
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
1. ~~`--set key=value` override~~ done 7 Oct 2026 (with run manifest).
2. ~~Full-size run~~ done 7 Oct 2026: `data/v1_full`, rules at 96.9% (see v1_full result above).
3. Modelling (week 2). **Decisions 8 Oct 2026:** weekly label = "mule account by this week" (a fake account
   counts from the day it opens; a real customer — witting/unwitting — from `launder_start_day`); alert budget
   = the rules' own alert count in each week. **Fixed cohort (8 Oct 2026):** main comparison = the 50,061 test
   accounts (opened months 6-7, 180 launderers), clock = weeks since each account opened (0-78), weekly budget =
   the rules' alerts on these accounts in that week of their life (only 21 in weeks 0-3, 1,130 in weeks 0-12,
   1,501 in total); secondary = same total of 1,501 flags used at any time (upper bound on the head start).
   This answers comment 2 of the professor's feedback (verbatim in `docs/professor_feedback.md`). Accounts closed
   by the bank stay in the cohort as caught; report accounts still open per week.
   1. Add that label to `amldata.labels()` (it now returns only `is_launderer` / `started_by_day`).
   2. **Baseline to beat** (rough check 8 Oct, untuned application-only model, train months 0-4, same number
      of flags as the rules on the test cohort = 1,462): 56/180 caught (31%) vs rules 48 (27%), a tie within
      noise (±6-7 pts); flags at opening, median 98 days *before* start vs rules 10 days *after*; union 84 (47%).
   3. **Stress test the fake-account assumption**: 73% of launderers are fakes from BAF fraud rows and the
      baseline caught almost only fakes (53/56). Rebuild with `in_window_mix` tests (53% / 56% fake) and report
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
   `--set rules.fixed_scale=1.741` (the v1_full scale), never re-tuned; (b) sensitivity runs at 244k, keeping
   summaries and deleting large files (rebuildable from the manifest); (c) 0.1% prevalence run at ~732k accounts
   so the test set keeps ~180 launderers, 1% at 244k; (d) build repeated bursts and young-weighted fake ages,
   drop hijacked accounts (state as a limitation); (e) main run repeated with seeds 43 and 44 as the
   chance yardstick, one seed per sensitivity run.

## Decision records
- Logic, assumptions, full schema: https://claude.ai/artifact/LchcqbsutNLSHWKESoWWQL
- Schema doc: https://claude.ai/artifact/SEEF2YPKNohZMGEitcwcj5
