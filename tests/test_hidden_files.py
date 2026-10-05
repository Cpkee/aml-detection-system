"""Guards for the honesty rule: hidden answers never become model inputs."""
import os
import pathlib
import pytest

from amldata import HIDDEN, labels, public

ALLOWED = {"sim", "amldata", "evaluation"}          # only these packages may name hidden files
SRC = pathlib.Path(__file__).resolve().parents[1] / "src"
OUT = os.environ.get("SIM_OUT", "data/v1")


def test_no_hidden_files_outside_allowed_code():
    offenders = []
    for py in SRC.rglob("*.py"):
        if py.relative_to(SRC).parts[0] in ALLOWED:
            continue
        text = py.read_text()
        offenders += [f"{py.relative_to(SRC)} names {h}" for h in HIDDEN if h in text]
    assert not offenders, offenders


needs_data = pytest.mark.skipif(not os.path.exists(os.path.join(OUT, "accounts.parquet")), reason="no simulator output")


@needs_data
def test_public_has_only_inputs():
    tables = {r[0] for r in public(OUT).execute("SHOW TABLES").fetchall()}
    assert tables == {"accounts", "transactions"}


@needs_data
def test_labels_refuse_test_months():
    with pytest.raises(ValueError):
        labels(OUT, months=(6, 7))


@needs_data
def test_labels_only_train_months_and_label_columns():
    y = labels(OUT, as_of_day=300)
    assert set(y["open_month"]) <= set(range(6))
    assert list(y.columns) == ["account_id", "open_month", "is_launderer", "started_by_day"]
