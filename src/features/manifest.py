"""Manifest for a feature store, so models and scoring never read features built from other code or data.

<out>/features/features_manifest.json records the feature-code commit, a fingerprint of the feature SQL, the
feature list, the cut-off rule, the weeks built, a hash of the data run's run_manifest.json and of the frozen peer
medians. `check(out, features=...)` refuses a store whose code, data or feature list differ from what the caller
expects, the same pattern as the simulator's run manifest.
"""
from __future__ import annotations
import hashlib
import json
import os
import subprocess
import sys

MANIFEST = "features_manifest.json"
CUTOFF_RULE = "rows with day <= open_day + 7*w + 6 (end of each account's week w, as amldata.labels)"


def _git(*args):
    try:
        return subprocess.check_output(["git", *args], text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _sha256(path: str) -> str | None:
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write(out: str, features: list[str], weeks: tuple[int, int], extra: dict | None = None) -> dict:
    import duckdb, numpy, pandas
    dirty = _git("status", "--porcelain", "--untracked-files=no")
    m = {
        "features": list(features),
        "weeks": [int(weeks[0]), int(weeks[1])],
        "cutoff_rule": CUTOFF_RULE,
        "data_folder": str(out),
        "run_manifest_sha256": _sha256(os.path.join(out, "run_manifest.json")),
        "git_commit": _git("rev-parse", "HEAD"),
        "git_uncommitted_changes": bool(dirty) if dirty is not None else None,
        "python": sys.version.split()[0],
        "packages": {"numpy": numpy.__version__, "pandas": pandas.__version__, "duckdb": duckdb.__version__},
    }
    m.update(extra or {})
    folder = os.path.join(out, "features")
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, MANIFEST), "w") as f:
        json.dump(m, f, indent=2)
    return m


def read(out: str) -> dict | None:
    path = os.path.join(out, "features", MANIFEST)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def check(out: str, features: list[str] | None = None, weeks: tuple[int, int] | None = None) -> dict:
    """The store in `out` must match the data run, the expected feature list and cover the weeks asked for."""
    m = read(out)
    if m is None:
        raise FileNotFoundError(f"{out}/features/{MANIFEST} not found - run `python -m features weekly --out {out}`")
    problems = []
    if m["run_manifest_sha256"] != _sha256(os.path.join(out, "run_manifest.json")):
        problems.append("the data run changed since the features were built")
    if features is not None and list(features) != m["features"]:
        problems.append(f"feature list differs: store has {m['features']}, caller expects {list(features)}")
    if weeks is not None and (weeks[0] < m["weeks"][0] or weeks[1] > m["weeks"][1]):
        problems.append(f"store covers weeks {m['weeks']}, caller needs {list(weeks)}")
    from .weekly import code_sha256                 # imported here: weekly imports this module
    if m.get("code_sha256") != code_sha256():
        problems.append("the feature code changed since the store was built (or the store predates the code check)")
    if "peer_medians_sha256" in m and m["peer_medians_sha256"] != _sha256(
            os.path.join(out, "features", "peer_medians.parquet")):
        problems.append("the frozen peer medians changed since the store was built")
    if problems:
        raise ValueError(f"{out}/features is stale: " + "; ".join(problems) + ". Rebuild with --force.")
    return m
