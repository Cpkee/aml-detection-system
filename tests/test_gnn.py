"""Runs the GNN tests (tests/gnn_cases.py) in a fresh Python process, so torch never loads into the main test process.

Why: torch and LightGBM each bring their own copy of the OpenMP library (torch's in torch/lib, LightGBM's from Homebrew
on macOS). Both copies export the same weak internal functions (__kmp_suspend_*, __kmp_resume_*, ...), and torch loads
its copy globally (RTLD_GLOBAL). macOS then merges those functions across the two copies, so LightGBM's threads call
into torch's runtime with their own runtime's data and crash (segfault in Dataset construction). Found 19 Nov 2026 on
an Apple M5 Pro: every LightGBM test after test_gnn.py crashed. Setting torch's thread count or the import order does
not help; a separate process does, and changes no result. Run one GNN test directly with
`python -m pytest tests/gnn_cases.py -k NAME`."""
import importlib.util
import os
import subprocess
import sys

import pytest

CASES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gnn_cases.py")


@pytest.mark.skipif(importlib.util.find_spec("torch") is None, reason="torch not installed")
def test_gnn_cases_pass_in_their_own_process():
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", CASES],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-5000:] + r.stderr[-2000:]
    assert " passed" in r.stdout and "skipped" not in r.stdout, r.stdout[-2000:]
