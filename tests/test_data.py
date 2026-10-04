"""Run with: PYTHONPATH=src BAF_PATH=... pytest -q   (needs a finished run in data/v0)"""
import os
import pytest
from sim.config import Cfg
from sim.checks import connect, run_checks

OUT = os.environ.get("SIM_OUT", "data/v0")
pytestmark = pytest.mark.skipif(not os.path.exists(os.path.join(OUT, "transactions.parquet")),
                                reason="no simulator output yet")


@pytest.fixture(scope="module")
def results():
    cfg = Cfg("configs/sim.yaml")
    return run_checks(connect(OUT), cfg, os.environ.get("BAF_PATH"))


@pytest.mark.parametrize("i", range(8))
def test_check(results, i):
    if i >= len(results):
        pytest.skip("BAF check needs BAF_PATH")
    name, ok, detail = results[i]
    assert ok, f"{name}: {detail}"
