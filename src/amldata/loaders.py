"""Safe access to the simulated dataset.

Three doors, so hidden answers never reach a model by accident:

  public(out)               model inputs only: `accounts` and `transactions`
  labels(out, ...)          the training answer `is_launderer`, for training/calibration accounts only
  evaluation(out)           every table; for scoring code in src/evaluation/ only

Feature and model code must only use `public()` and `labels()`. tests/test_hidden_files.py fails if any
code outside src/sim, src/amldata or src/evaluation names a hidden file.

Example
-------
    from amldata import public, labels
    con = public()                                   # DuckDB connection, two views
    week = con.sql("SELECT * FROM transactions WHERE day <= 377").df()
    y = labels(as_of_day=377)                        # months 0-5 only; weekly labels at one calendar day
    y4 = labels(weeks_since_open=4)                  # weekly labels at the end of each account's week 4
"""
from __future__ import annotations
import os

import duckdb
import pandas as pd

PUBLIC = ["accounts", "transactions"]
HIDDEN = ["accounts_truth", "aml_alerts", "aml_outcomes", "transactions_truth"]
TRAIN_MONTHS = (0, 1, 2, 3, 4, 5)   # 0-4 train, 5 calibrate
TEST_MONTHS = (6, 7)                # stay closed until scoring
DEFAULT_OUT = "data/v1_full"       # the main modelling dataset (244k); pass out="data/v1" for quick 50k work


def _file(out: str, name: str) -> str:
    path = os.path.join(out, f"{name}.parquet")
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found - run the simulator first (see README)")
    return path


def _connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute("PRAGMA memory_limit='2GB'")
    return con


def public(out: str = DEFAULT_OUT) -> duckdb.DuckDBPyConnection:
    """Connection with ONLY the model inputs: views `accounts` and `transactions`."""
    con = _connect()
    for name in PUBLIC:
        con.execute(f"CREATE VIEW {name} AS SELECT * FROM read_parquet('{_file(out, name)}')")
    return con


def accounts(out: str = DEFAULT_OUT) -> pd.DataFrame:
    """The application table (32 columns) as a DataFrame."""
    return public(out).execute("SELECT * FROM accounts").df()


def labels(out: str = DEFAULT_OUT, months=TRAIN_MONTHS, as_of_day: int | None = None,
           weeks_since_open: int | None = None, allow_test: bool = False) -> pd.DataFrame:
    """Training answers for accounts opened in `months`.

    Always returns account_id, open_month and is_launderer (the fixed final label: a mule at any point in
    the window). Given a cut-off, it also returns two weekly labels:
      started_by_day  1 if the account's laundering has started by the cut-off
      mule_by_day     1 if the account is a mule account by the cut-off: a fake account counts from the
                      day it opens (it was opened to launder), a real customer from the day they start
                      laundering (the agreed main label, team decision 8 Oct 2026)
    The cut-off is either `as_of_day` (one calendar day for every account) or `weeks_since_open` (the end
    of week w of each account's own life: open_day + 7*w + 6, the clock used for the fixed-cohort
    comparison). Nothing else from the hidden files is returned. Test months (6-7) are refused unless
    allow_test=True, which only evaluation code should use.
    """
    if as_of_day is not None and weeks_since_open is not None:
        raise ValueError("give as_of_day or weeks_since_open, not both")
    months = tuple(int(m) for m in months)
    if not allow_test and set(months) & set(TEST_MONTHS):
        raise ValueError("labels for test months 6-7 stay closed; use amldata.evaluation() in scoring code")
    con = _connect()
    m = ", ".join(str(x) for x in months)
    df = con.execute(f"""
        SELECT a.account_id, a.open_month, a.open_day, t.is_launderer, t.launder_start_day,
               (t.profile = 'fake') AS is_fake
        FROM read_parquet('{_file(out, 'accounts')}') a
        JOIN read_parquet('{_file(out, 'accounts_truth')}') t USING (account_id)
        WHERE a.open_month IN ({m})""").df()
    if as_of_day is not None or weeks_since_open is not None:
        cutoff = as_of_day if as_of_day is not None else df["open_day"] + 7 * int(weeks_since_open) + 6
        start = df["launder_start_day"]
        launders = df["is_launderer"] == 1
        started = launders & start.notna() & (start <= cutoff)
        df["started_by_day"] = started.astype(int)
        df["mule_by_day"] = (started | (launders & df["is_fake"])).astype(int)
    return df.drop(columns=["open_day", "launder_start_day", "is_fake"])


def evaluation(out: str = DEFAULT_OUT) -> duckdb.DuckDBPyConnection:
    """Every table, including hidden answers. ONLY for scoring code in src/evaluation/."""
    con = _connect()
    for name in PUBLIC + HIDDEN:
        con.execute(f"CREATE VIEW {name} AS SELECT * FROM read_parquet('{_file(out, name)}')")
    return con
