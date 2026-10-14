"""Command line: python -m models <command> [options]."""
from __future__ import annotations
import argparse


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m models", description="Train and calibrate the models (Phase 4).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("train", help="train one model on months 0-4, calibrate on month 5 (not built yet)")
    t.add_argument("--view", choices=["application", "activity", "combined"], default="combined")
    t.add_argument("--model", choices=["logreg", "lgbm"], default="lgbm")
    t.add_argument("--out", default="data/v1_full")
    a = ap.parse_args(argv)
    raise SystemExit(f"`{a.cmd}` is not built yet (Phase 4 of the modelling plan)")


if __name__ == "__main__":
    main()
