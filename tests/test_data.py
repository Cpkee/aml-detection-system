"""Run with: PYTHONPATH=src BAF_PATH=... pytest -q   (needs a finished run in data/v1)"""
import os
import pytest
from sim.config import Cfg
from sim.checks import connect, run_checks

OUT = os.environ.get("SIM_OUT", "data/v1")
pytestmark = pytest.mark.skipif(not os.path.exists(os.path.join(OUT, "transactions.parquet")),
                                reason="no simulator output yet")


@pytest.fixture(scope="module")
def results():
    cfg = Cfg("configs/sim.yaml")
    return run_checks(connect(OUT), cfg, os.environ.get("BAF_PATH"))


def test_all_checks(results):
    failed = [f"{name}: {detail}" for name, ok, detail in results if not ok]
    assert not failed, failed
