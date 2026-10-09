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
    assert list(y.columns) == ["account_id", "open_month", "is_launderer", "started_by_day", "mule_by_day"]
    assert list(labels(OUT).columns) == ["account_id", "open_month", "is_launderer"]


@needs_data
def test_mule_label_counts_fakes_from_opening():
    from amldata import evaluation
    fakes = evaluation(OUT).execute("""SELECT count(*) FROM accounts a JOIN accounts_truth t USING (account_id)
                                     WHERE t.profile = 'fake' AND a.open_month <= 5""").fetchone()[0]
    y0 = labels(OUT, weeks_since_open=0)
    assert y0["mule_by_day"].sum() >= fakes                      # every fake account is a mule from week 0
    assert (y0["mule_by_day"] >= y0["started_by_day"]).all()     # started always implies mule
    y_end = labels(OUT, weeks_since_open=200)                    # long after every window ends
    assert (y_end["mule_by_day"] == y_end["is_launderer"]).all()
    assert (y_end["started_by_day"] == y_end["is_launderer"]).all()


@needs_data
def test_labels_refuse_two_cutoffs():
    with pytest.raises(ValueError):
        labels(OUT, as_of_day=100, weeks_since_open=4)


@needs_data
def test_profile_only_for_eda_on_training_months():
    assert "profile" not in labels(OUT).columns                    # absent unless asked for
    y = labels(OUT, profile=True)
    assert set(y["profile"].dropna()) <= {"fake", "witting", "unwitting"}
    assert (y["profile"].notna() == (y["is_launderer"] == 1)).all()  # the type is shown for launderers only
    with pytest.raises(ValueError):
        labels(OUT, months=(6, 7), profile=True, allow_test=True)   # never on test months, even for evaluation
