# aml-detection-system

Early detection of money-laundering accounts from account-opening and early-activity signals (BT4102).

## Simulator (v0)

Builds a linked dataset: real BAF applications -> hidden profiles -> 18 months of simulated UK banking,
with laundering planted where published evidence says it happens. Every number lives in `configs/sim.yaml`
with its source and strength (sourced / derived / samld / assumption / modelling / design).

```bash
pip install -r requirements.txt
# put BAF Base at data/raw/BAF_Base.csv, or pass --baf
PYTHONPATH=src python -m sim.run all --baf data/raw/BAF_Base.csv     # ~2 min for 50,000 accounts
PYTHONPATH=src python -m sim.checks --baf data/raw/BAF_Base.csv      # 8 checks + data card
```
Low on memory (under ~4 GB)? Run `normal` one batch per process: `--batches 3-3`, or lower `size.batch_size`.

Output in `data/v0/`:

| File | Who may read it |
|---|---|
| `accounts.parquet` | models and rules |
| `transactions.parquet` | models and rules (only rows up to the scoring week) |
| `accounts_truth.parquet` | training label `is_launderer`; everything else evaluation only |
| `aml_alerts.parquet`, `aml_outcomes.parquet` | benchmark + alert budget (empty until the rules module exists) |
| `transactions_truth.parquet` | data checks only |
| `data_card.md` | summary of the run; read it before training |

v0 limits: one laundering pattern (Fan_In), no bank rules yet, laundering card spending deferred.
