"""Load configs/sim.yaml and expose plain values.

Every setting in the YAML is a dict with a `value` key (plus source/strength/test).
`Cfg.get("normal.card_per_month")` returns just the value.

Runs can override settings without editing the YAML: `--set size.n_accounts=244000`. The overrides are
recorded in <out>/run_manifest.json, and `Cfg.for_run(out)` re-applies them for later steps and checks.
"""
from __future__ import annotations
import copy
import hashlib
import json
import os
import subprocess
import yaml

MANIFEST = "run_manifest.json"


class Cfg:
    def __init__(self, path: str, overrides: dict | None = None, set_args: list[str] | None = None):
        """`set_args` are raw '--set key=value' strings; they are what the run manifest records."""
        self.path = path
        with open(path) as f:
            self.raw = yaml.safe_load(f)
        self.set_args = list(set_args or []) + [f"{k}={json.dumps(v)}" for k, v in (overrides or {}).items()]
        self.overrides = parse_overrides(self.set_args)
        for key, val in self.overrides.items():
            self.set(key, val)

    def _node(self, dotted: str):
        node = self.raw
        for part in dotted.split("."):
            node = node[part]
        return node

    def get(self, dotted: str):
        node = self._node(dotted)
        if isinstance(node, dict) and "value" in node:
            return copy.deepcopy(node["value"])
        return copy.deepcopy(node)

    def set(self, dotted: str, value):
        parts = dotted.split(".")
        node = self.raw
        try:
            for part in parts[:-1]:
                node = node[part]
            leaf = node[parts[-1]]
        except (KeyError, TypeError):
            raise KeyError(f"unknown setting '{dotted}' (not in {self.path})") from None
        if isinstance(leaf, dict) and "value" in leaf:
            leaf["value"] = value
        else:
            node[parts[-1]] = value

    @classmethod
    def for_run(cls, out: str, path: str = "configs/sim.yaml"):
        """The config a finished run in `out` was made with (YAML + the overrides in its manifest)."""
        m = read_manifest(out)
        return cls(m["config"] if m else path, set_args=m["set"] if m else None)


def parse_overrides(items: list[str] | None) -> dict:
    """['size.n_accounts=244000', 'timing.fake_start_days=[15, 45]'] -> dict; values are read as YAML."""
    out = {}
    for item in items or []:
        key, sep, val = item.partition("=")
        if not sep or not key.strip():
            raise ValueError(f"--set needs key=value, got '{item}'")
        out[key.strip()] = yaml.safe_load(val)
    return out


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _git(*args) -> str | None:
    try:
        return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def read_manifest(out: str) -> dict | None:
    path = os.path.join(out, MANIFEST)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def write_manifest(cfg: Cfg, out: str, baf_path: str):
    """Record how this run was made. Written when the run starts (the `accounts` step)."""
    import duckdb, numpy, pandas, sys
    dirty = _git("status", "--porcelain", "--untracked-files=no")
    m = {
        "version": cfg.get("meta.version"),
        "seed": cfg.get("meta.seed"),
        "config": cfg.path,
        "config_sha256": _sha256(cfg.path),
        "set": cfg.set_args,
        "baf_file": baf_path,
        "baf_sha256": _sha256(baf_path),
        "git_commit": _git("rev-parse", "HEAD"),
        "git_uncommitted_changes": bool(dirty) if dirty is not None else None,
        "python": sys.version.split()[0],
        "packages": {"numpy": numpy.__version__, "pandas": pandas.__version__, "duckdb": duckdb.__version__},
    }
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, MANIFEST), "w") as f:
        json.dump(m, f, indent=2)
    return m


def check_manifest(cfg: Cfg, out: str):
    """Later steps must use the same config and overrides as the run's first step."""
    m = read_manifest(out)
    if m is None:
        print(f"note: {out} has no {MANIFEST} (run made before manifests); not checking settings")
        return
    problems = []
    if parse_overrides(m["set"]) != cfg.overrides:
        problems.append(f"--set {cfg.set_args} differs from the run's {m['set']}")
    if m["config_sha256"] != _sha256(cfg.path):
        problems.append(f"{cfg.path} changed since the run started")
    if problems:
        raise SystemExit(f"{out} was started with different settings: " + "; ".join(problems)
                         + ". Rerun from the `accounts` step, or pass the same --set values.")
