# aml-detection-system

Early detection of money-laundering accounts from account-opening and early-activity signals (BT4012).

**Question.** With the same weekly number of alerts as a bank's rules, does a model on account-opening data plus
weekly account activity catch mule accounts more often and sooner? No public dataset links applications to later
transactions, so we simulate one from real BAF applications. **Headline (final test, months 6-7, weeks 0-26):**
the model caught 120 of 163 mule accounts, the rules 50 (precision 42.9% vs 18.9%).

## Reproducing the results

Tested with Python 3.12 on macOS (where the model of record was trained) and Python 3.13 on Windows 11. Commands
are written for bash; on Windows PowerShell set the path once with `$env:PYTHONPATH="src"` and drop the
`PYTHONPATH=src` prefix.

**0. Setup.**

```bash
pip install -r requirements.txt
```

Download the Bank Account Fraud dataset suite (Jesus et al., NeurIPS 2022) from Kaggle:
<https://www.kaggle.com/datasets/sgpjesus/bank-account-fraud-dataset-neurips-2022>, and save `Base.csv` as
`data/raw/BAF_Base.csv`. Generated data goes under `data/` and is never committed.

**1. Check the results without rebuilding anything** (reads only committed files, seconds):

```bash
PYTHONPATH=src python -m evaluation.robustness     # robustness table (report 4.4.1), McNemar test and false-alarm ratios by age
```

Paths below are under `outputs/modelling/` unless they start with `configs/`. Section numbers refer to the report.
Four rows point to files that are still on open pull requests (#61, #62, #64, #73); they name the branch.

| Result in the report | Committed file |
|---|---|
| Inputs that drive the catches (3.4) | `feature_selection/report.md` |
| Calibration (3.3) | `models/v1_full/frozen_tuned_avg5/calibration/report.md` |
| Tuned settings (4.2) | `models/v1_full/lgbm_tuning_step2/tuned_params.json` |
| Methods comparison (4.2, Table 4.2) | `comparison/v1_full/folds.csv`; paired tests `comparison/v1_full/interim_paired_tests_folds.csv` (the XGBoost and CatBoost rows are on branch `interim-tests-group-b`, PR #73) |
| Month 5 dry run (4.2) | `results/v1_full/month5_dryrun_frozen_tuned_avg5/report.md` |
| Final test, model vs rules (4.3, Table 4.3A) | `results/v1_full/final_test/report.md`, `summary_w26.csv`; weeks 0-77: `summary_w77.csv` |
| Robustness checks (4.4.1, Table 4.4A) | `robustness/report.md`, `summary.csv`, `summary_amendments.csv` (Variant II, patient launderers) |
| Prevalence at 0.1% and 1% (4.4.1) | branch `prevalence-runs` (PR #64): `results/prevalence__0.1pct/final_test/`, `results/prevalence__1pct/final_test/` |
| What the application adds (4.4.2, Table 4.4B) | training folds: `comparison/v1_full/folds.csv` (`ref` against `A1_activity`); the month-5 runs are not committed, and `src/evaluation/compare.py` describes how to rebuild them |
| False alarms by age (4.4.3, Table 4.4C) | `results/v1_full/final_test/by_age_w26.csv` |
| Bank labels and label-free detectors (Appendix C.1) | `outlier/v1_full/report.md` |
| Alert budget check (Appendix C.2) | `results/v1_full/budget_check_m5/report.md` |
| Rule thresholds (Appendix C.3) | branch `budget-curve` (PR #61): `budget_curve/v1_full/curve.csv` |
| Review at account opening (Appendix C.4) | branch `opening-topk` (PR #62): `opening_topk/v1_full/table.csv` |
| Money stopped before it left (Appendix C.5) | `results/v1_full/month5_cost/summary.csv` |
| Stronger rule scorecard (5.2) | `scorecard/PLAN.md`, `results/v1_full/month5_scorecard/report.md` |
| The model of record | `models/v1_full/frozen_tuned_avg5/` (5 tree files, application score, calibration) |
| Simulator settings and their sources | `configs/sim.yaml` |

**2. Rebuild the main dataset** (244,000 accounts, ~11 min, 7.2 GB on disk, ~16 GB RAM recommended):

```bash
PYTHONPATH=src python -m sim.run all --baf data/raw/BAF_Base.csv --out data/v1_full --set size.n_accounts=244000
PYTHONPATH=src python -m sim.checks --baf data/raw/BAF_Base.csv --out data/v1_full    # 10 checks + data card
```

The simulator is seeded: the same settings and BAF file give identical data. `data/v1_full/run_manifest.json`
records the settings, seed, BAF hash and code version.

**3. Build the model inputs.**

```bash
PYTHONPATH=src python -m features weekly --out data/v1_full --weeks 0-77    # weekly feature store, ~4 min, ~4 GB
PYTHONPATH=src python -m features preprocess --out data/v1_full             # cleaned application tables
```

**4. Score the committed model on month 5** (the dry run; it uses the committed model files, no retraining):

```bash
PYTHONPATH=src python -m evaluation.score --months 5 --name repro_check
```

Expected: weeks 0-26, model 65 of 78 mules caught vs rules 16, the same as
`results/v1_full/month5_dryrun_frozen_tuned_avg5/`. Scoring the committed files gives identical results on any
machine; retraining (`python -m models train`) can differ by a mule or two between machines, which is why the
trained model is committed.

The test months 6-7 are locked: they were scored once on 2 Nov 2026 and `evaluation.score --final-test` refuses
to run again (`final_test/LOCK.json`). Their outputs are committed (table above).

**5. Run the tests.**

```bash
PYTHONPATH=src BAF_PATH=data/raw/BAF_Base.csv python -m pytest -q tests
```

231 tests: the data checks, an independent re-computation of the weekly features, a no-look-ahead test, a guard that
no model code reads the hidden label files, and checks on the committed results. Tests that need a built dataset
skip when it is missing.

**6. Re-run a notebook (optional).** The notebooks in `notebooks/` are committed with their outputs (all but 09), so
they can be read on GitHub without running anything. To re-run one, build the data first (steps 2-3); notebook 12
needs only committed files. Four notebooks have a command that runs the whole notebook and saves the executed copy:

```bash
PYTHONPATH=src python -m features eda            # notebooks/01_eda_train.ipynb
PYTHONPATH=src python -m features preprocess     # notebooks/02_preprocess.ipynb (also writes the cleaned tables)
PYTHONPATH=src python -m features store-check    # notebooks/03_feature_store.ipynb
PYTHONPATH=src python -m features select         # notebooks/13_feature_selection.ipynb
```

Each takes `--out` for another data folder (default `data/v1_full`). Run the others with Run All, in Jupyter
(`pip install jupyterlab`, then `jupyter lab`; Jupyter is not in `requirements.txt`) or in VS Code with the Jupyter
extension. Each notebook finds the repository folder itself, so no `PYTHONPATH` is needed. It reads `data/v1_full`
unless the `EDA_DATA` environment variable names another folder (for example `EDA_DATA=data/v1 jupyter lab` for the
50,000-account dataset), and writes to `outputs/modelling/`, where results for another data folder go to a
sub-folder named after it.

- Re-running a notebook on `data/v1_full` overwrites the committed results it wrote; `git diff` shows any change.
- Notebook 09 does not retrain by default (`RETRAIN = False`): it loads the committed single-seed model
  `frozen_tuned` and re-runs its month-5 dry run. The model of record, `frozen_tuned_avg5`, is never retrained
  (`python -m models train` refuses its name).
- The tuning notebooks (06, 08, 15) and the stability notebook (10) refit many models and take much longer than the
  others.

**Where the rest is.** Analysis notebooks in `notebooks/` (01 EDA, 02 preprocessing, 03 feature store, 04-09
models and tuning, 10-13 and 15 appendices); every modelling result in `outputs/modelling/` (see its README);
decisions and data changes in `CHANGELOG.md`.

## Simulator

Builds a linked dataset: real BAF applications -> hidden profiles -> 18 months of simulated UK banking,
with laundering planted where published evidence says it happens. Every number lives in `configs/sim.yaml`
with its source and strength (sourced / derived / samld / assumption / modelling / design).

```bash
pip install -r requirements.txt
# put BAF Base at data/raw/BAF_Base.csv, or pass --baf
PYTHONPATH=src python -m sim.run all --baf data/raw/BAF_Base.csv     # ~2 min for 50,000 accounts
PYTHONPATH=src python -m sim.checks --baf data/raw/BAF_Base.csv      # 10 checks + data card
```
Change a setting for one run without editing the YAML: `--set size.n_accounts=244000 --out data/v1_full`
(repeatable). Each run records its settings in `<out>/run_manifest.json`; `sim.checks` reads them back.

Low on memory (under ~4 GB)? Run `normal` one batch per process: `--batches 3-3`, or lower `size.batch_size`.

Output in `data/v1/`:

| File | Who may read it |
|---|---|
| `accounts.parquet` | models and rules |
| `transactions.parquet` | models and rules (only rows up to the scoring week) |
| `accounts_truth.parquet` | training label `is_launderer`; everything else evaluation only |
| `aml_alerts.parquet`, `aml_outcomes.parquet` | the bank's 6 rules: benchmark + weekly alert budget |
| `transactions_truth.parquet` | data checks only |
| `data_card.md` | summary of the run; read it before training |

Steps: `accounts` -> `normal` -> `laundering` (15 SAML-D shapes) -> `rules` (tune R3-R6, find closures) -> `finalize`
(remove activity after closure, give transactions anonymous ids, write alerts) -> `sim.checks` (10 checks + data card).

`txn_id` is an anonymous id (`T` + 16 hex characters) and `transactions` is sorted by `day`, `time`; neither
says anything about laundering (check 10). Changes to the data are listed in `CHANGELOG.md`.

Full-size run (main modelling dataset): `--out data/v1_full --set size.n_accounts=244000` (~11 min, 7.2 GB,
109M transactions, 732 launderers).

Known limits: laundering card spending deferred; after the R6 fix (8 Oct 2026) the rules reach 93–94% false alarms, inside the 90–95% that practitioners report.

## Using the data in model code

Never open the hidden files directly. Use `amldata`:

```python
from amldata import public, labels
con = public()                                            # data/v1_full by default; public("data/v1") for 50k
                                                          # only `accounts` and `transactions`
tx = con.sql("SELECT * FROM transactions WHERE day <= 377").df()
y = labels(as_of_day=377)                                 # training/calibration accounts (months 0-5) only
```

`labels()` refuses test months 6-7; scoring code in `src/evaluation/` uses `amldata.evaluation()`.
`tests/test_hidden_files.py` fails if any other code names a hidden file.
