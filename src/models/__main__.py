"""Command line: python -m models <command> [options]."""
from __future__ import annotations
import sys


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] in ("-h", "--help"):
        print("usage: python -m models train [--out D] [--name N] [--params FILE] [--inputs frozen|activity] [--seed S]\n"
              "       python -m models calibrate [--out D] [--model N]\n"
              "       python -m models verify [--out D] --model N --reference RUN\n\n"
              "  train      fit the frozen 38-input LightGBM on months 0-4 and save it (models.train)\n"
              "  calibrate  map a trained model's scores to probabilities on month 5 (models.calibrate)\n"
              "  verify     accept a model file from another machine by reproducing a committed run (models.verify)")
        return
    if argv[0] == "train":
        from .train import main as train_main
        train_main(argv[1:])
    elif argv[0] == "calibrate":
        from .calibrate import main as calibrate_main
        calibrate_main(argv[1:])
    elif argv[0] == "verify":
        from .verify import main as verify_main
        verify_main(argv[1:])
    else:
        raise SystemExit(f"unknown command `{argv[0]}` (known: train, calibrate, verify)")


if __name__ == "__main__":
    main()
