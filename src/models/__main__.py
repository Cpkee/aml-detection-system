"""Command line: python -m models <command> [options]."""
from __future__ import annotations
import sys


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] in ("-h", "--help"):
        print("usage: python -m models train [--out D] [--name N] [--params FILE] [--seed S]\n\n"
              "  train   fit the frozen 38-input LightGBM on months 0-4 and save it (models.train)")
        return
    if argv[0] == "train":
        from .train import main as train_main
        train_main(argv[1:])
    else:
        raise SystemExit(f"unknown command `{argv[0]}` (known: train)")


if __name__ == "__main__":
    main()
