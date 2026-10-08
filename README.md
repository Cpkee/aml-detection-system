# aml-detection-system

Early detection of money-laundering accounts from account-opening and early-activity signals (BT4102).

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

Known limits: laundering card spending deferred; rules reach 96.9-97.2% false alarms at best (target 90-95%); accepted and reported as a finding.

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
