"""Command line: python -m features <command> [options]."""
from __future__ import annotations
import argparse
import os
from pathlib import Path

from .weekly import LAST_WEEK, build, parse_weeks

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA = "data/v1_full"


def run_notebook(name: str, out: str, report: str | None, report_root: str = "outputs/modelling/eda") -> None:
    """Execute notebooks/<name> on data folder `out` with EDA_DATA / EDA_REPORT set, and save the executed copy:
    in place for the main dataset, else under the report folder (default <report_root>/<data folder name>)."""
    import nbformat
    from nbclient import NotebookClient

    os.environ["EDA_DATA"] = out
    if report:
        os.environ["EDA_REPORT"] = report
    src = ROOT / "notebooks" / name
    nb = nbformat.read(src, as_version=4)
    NotebookClient(nb, timeout=3600, kernel_name="python3",
                   resources={"metadata": {"path": str(ROOT)}}).execute()
    main = os.path.normpath(out) == os.path.normpath(DEFAULT_DATA) and not report
    dest = src if main else Path(report or f"{report_root}/{os.path.basename(os.path.normpath(out))}") / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nb, dest)
    print(f"executed {src.relative_to(ROOT)} on {out} -> {dest}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m features",
                                 description="Modelling features. Reads data only through amldata.public().")
    sub = ap.add_subparsers(dest="cmd", required=True)

    w = sub.add_parser("weekly", help="build the weekly feature store <out>/features/weekly.parquet")
    w.add_argument("--out", default="data/v1_full", help="data folder (default data/v1_full; data/v1 for 50k)")
    w.add_argument("--weeks", default=f"0-{LAST_WEEK}", help=f"weeks since opening, e.g. 0-26 (default 0-{LAST_WEEK})")
    w.add_argument("--force", action="store_true", help="rebuild even if the store exists")

    e = sub.add_parser("eda", help="Phase 1 EDA: execute notebooks/01_eda_train.ipynb -> <report>/report.md, figures, CSVs")
    e.add_argument("--out", default="data/v1_full", help="data folder (default data/v1_full)")
    e.add_argument("--report", default=None,
                   help="report folder (default outputs/modelling/eda, or outputs/modelling/eda/<data folder name>)")
    p = sub.add_parser("preprocess", help="Phase 2 cleaning: execute notebooks/02_preprocess.ipynb -> "
                                          "<out>/features/accounts_{linear,tree}.parquet + manifest, <report>/report.md")
    p.add_argument("--out", default="data/v1_full", help="data folder (default data/v1_full); fitted on its months 0-4")
    p.add_argument("--report", default=None,
                   help="report folder (default outputs/modelling/preprocess, or .../preprocess/<data folder name>)")
    c = sub.add_parser("store-check", help="Phase 3 gate: execute notebooks/03_feature_store.ipynb on a built store -> "
                                           "<report>/report.md (screen reproduced, first-week AUCs with bootstrap CIs)")
    c.add_argument("--out", default="data/v1_full", help="data folder whose features/weekly.parquet is checked")
    c.add_argument("--report", default=None,
                   help="report folder (default outputs/modelling/features, or .../features/<data folder name>)")

    a = ap.parse_args(argv)
    if a.cmd == "weekly":
        path, n = build(a.out, parse_weeks(a.weeks), force=a.force)
        print(f"wrote {path}: {n:,} account-weeks")
    elif a.cmd == "eda":
        run_notebook("01_eda_train.ipynb", a.out, a.report)
    elif a.cmd == "preprocess":
        run_notebook("02_preprocess.ipynb", a.out, a.report, report_root="outputs/modelling/preprocess")
    elif a.cmd == "store-check":
        run_notebook("03_feature_store.ipynb", a.out, a.report, report_root="outputs/modelling/features")
    else:
        raise SystemExit(f"`{a.cmd}` is not built yet (see the modelling plan)")


if __name__ == "__main__":
    main()
