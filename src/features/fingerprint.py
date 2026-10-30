"""Content fingerprints of the files a trained model reads, so a model file can be shared between machines.

    PYTHONPATH=src python -m features fingerprint --out data/v1_full

Two team members' data folders are the same when these fingerprints are equal, even though their run_manifest.json
files differ (the manifest records the BAF path, the git commit the data was generated at and package versions,
which differ per machine). Each fingerprint is the row count and an exact integer sum of the MD5 of every row written
out as text, so it ignores the parquet file's bytes (compression, writer version) and the row order. Rows are written
out by DuckDB, so compare fingerprints made with the same DuckDB version (printed alongside).

A model trained since 29 Oct 2026 stores these in its manifest; models.train.load compares them with the local
data instead of the manifest's file hash (option B, 29 Oct 2026: train once, share the model file).
"""
from __future__ import annotations
import json
import os

import amldata

FILES = ["accounts.parquet", "features/accounts_linear.parquet", "features/accounts_tree.parquet",
         "features/peer_medians.parquet", "features/weekly.parquet"]
CACHE = "features/fingerprints.json"


def _stat(path: str) -> list:
    s = os.stat(path)
    return [s.st_size, int(s.st_mtime)]


def fingerprints(out: str = amldata.DEFAULT_OUT, use_cache: bool = True) -> dict:
    """{file: {"rows": n, "fingerprint": h}} plus "duckdb": version. Cached next to the store and recomputed for a
    file whose size or modification time changed."""
    import duckdb
    cache_path = os.path.join(out, CACHE)
    cache = json.load(open(cache_path)) if use_cache and os.path.exists(cache_path) else {}
    con = duckdb.connect()
    con.execute("PRAGMA memory_limit='4GB'")
    con.execute("PRAGMA disable_progress_bar")
    res, changed = {"duckdb": duckdb.__version__}, False
    for f in FILES:
        path = os.path.join(out, f)
        if not os.path.exists(path):
            raise FileNotFoundError(f"{path} not found")
        hit = cache.get(f)
        if hit and hit.get("stat") == _stat(path) and cache.get("duckdb") == duckdb.__version__:
            res[f] = {"rows": hit["rows"], "fingerprint": hit["fingerprint"]}
            continue
        # lower 64 bits of each row's MD5, summed as an exact 128-bit integer (19M rows x 2^64 < 2^89): a plain
        # sum of md5_number is a DOUBLE in DuckDB, inexact and not stable under parallel addition
        n, h = con.execute(f"SELECT count(*), CAST(sum(CAST(md5_number_lower(CAST(t AS VARCHAR)) AS HUGEINT)) "
                           f"% 1000000007 AS BIGINT) "
                           f"FROM read_parquet('{path.replace(os.sep, '/')}') t").fetchone()
        res[f] = {"rows": int(n), "fingerprint": int(h)}
        cache[f] = {**res[f], "stat": _stat(path)}
        changed = True
    if changed and use_cache:
        cache["duckdb"] = duckdb.__version__
        with open(cache_path, "w") as fh:
            json.dump(cache, fh, indent=2)
    return res


def differences(a: dict, b: dict) -> list[str]:
    """Files whose fingerprint differs between two fingerprint dicts (and a DuckDB version note)."""
    out = [f for f in FILES if a.get(f) != b.get(f)]
    if out and a.get("duckdb") != b.get("duckdb"):
        out.append(f"(DuckDB {a.get('duckdb')} vs {b.get('duckdb')}: the text form of rows may differ by version)")
    return out


def main(out: str) -> None:
    fp = fingerprints(out)
    print(f"DuckDB {fp['duckdb']}")
    for f in FILES:
        print(f"{f:36s} rows {fp[f]['rows']:>12,}  fingerprint {fp[f]['fingerprint']}")
