"""Command line: python -m features <command> [options]."""
from __future__ import annotations
import argparse

from .weekly import build, parse_weeks


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m features",
                                 description="Modelling features. Reads data only through amldata.public().")
    sub = ap.add_subparsers(dest="cmd", required=True)

    w = sub.add_parser("weekly", help="build the weekly feature store <out>/features/weekly.parquet")
    w.add_argument("--out", default="data/v1_full", help="data folder (default data/v1_full; data/v1 for 50k)")
    w.add_argument("--weeks", default="0-78", help="weeks since opening, e.g. 0-26 (default 0-78)")
    w.add_argument("--force", action="store_true", help="rebuild even if the store exists")

    e = sub.add_parser("eda", help="Phase 1 EDA on the training months -> <report>/report.md, figures, CSVs")
    e.add_argument("--out", default="data/v1_full", help="data folder (default data/v1_full)")
    e.add_argument("--report", default=None,
                   help="report folder (default outputs/modelling/eda, or outputs/modelling/eda/<data folder name>)")
    sub.add_parser("preprocess", help="Phase 2, not built yet")

    a = ap.parse_args(argv)
    if a.cmd == "weekly":
        path, n = build(a.out, parse_weeks(a.weeks), force=a.force)
        print(f"wrote {path}: {n:,} account-weeks")
    elif a.cmd == "eda":
        import os, runpy
        os.environ["EDA_DATA"] = a.out
        if a.report:
            os.environ["EDA_REPORT"] = a.report
        runpy.run_module("features.eda_train", run_name="__main__")
    else:
        raise SystemExit(f"`{a.cmd}` is not built yet (see the modelling plan)")


if __name__ == "__main__":
    main()
