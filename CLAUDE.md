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
- Model/feature code uses `amldata.public()` and `amldata.labels(as_of_day=...)` only. `labels()` returns
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
3. Modelling (week 2): decide the weekly label ("ever launders" vs `started_by_day`), build weekly
   features via `amldata`, application-only / activity-only / combined models, same weekly alert budget.
4. Week 3: BAF Variants II (fairness) and IV (drift) with identical settings; sensitivity runs from
   `test` values; professor comments (fixed-cohort same-week comparison; 0.1/0.3/1% prevalence).

## Decision records
- Logic, assumptions, full schema: https://claude.ai/artifact/LchcqbsutNLSHWKESoWWQL
- Schema doc: https://claude.ai/artifact/SEEF2YPKNohZMGEitcwcj5
