"""Outlier appendix: freeze the settings, then the one look on month 5 (plan: outputs/modelling/outlier/PLAN.md).

    PYTHONPATH=src python -m evaluation.outlier_look freeze --out data/v1_full    # 3 Nov; then commit the files
    PYTHONPATH=src python -m evaluation.outlier_look check --out data/v1_full     # is the look allowed? reads no label
    PYTHONPATH=src python -m evaluation.outlier_look look --out data/v1_full      # 6 Nov, once

freeze writes outputs/modelling/outlier/<data>/settings.json once: the outlier settings (models.outlier.settings) and
the sha256 of each supervised model's files. It first copies the M1b / M2 model files to the shared folder in git
(outputs/modelling/models/<data>/<name>/, as frozen_tuned, option B 29 Oct 2026), so every machine scores the same
trees and `models train` refuses to retrain them.

look refuses unless settings.json is committed and unchanged, still equals the code's settings and the model files,
and no look has started. Before it reads anything about month 5 it writes LOOK_STARTED.json (never cleared: clearing
it is a team decision). It then writes the month-5 scores of the six methods to <out>/scores/outlier_look/, runs the
harness (evaluation.score, weeks 0-26) on each into outputs/modelling/outlier/<data>/<method>/, runs
evaluation.hidden_mules on all six, and writes LOOK.json with the scores' sha256.
"""
from __future__ import annotations
import argparse
import json
import os
import shutil
import time

import amldata
from evaluation import hidden_mules
from evaluation import score as harness
from features import manifest
from models import outlier
from models import train as trainer

MODELS = ("frozen_tuned", "truth_macos", "bank_label")   # M1, M1b, M2
TO_SHARE = ("truth_macos", "bank_label")                  # trained on this Mac 30 Oct 2026
MONTHS = (5,)                                             # decision D1
REPORT = hidden_mules.REPORT


def folder(out: str) -> str:
    return os.path.join(REPORT, os.path.basename(os.path.normpath(out)))


def current(out: str) -> dict:
    """What decides the look's results, as the code and the model files stand now."""
    return {"outlier": outlier.settings(), "months": list(MONTHS), "weeks": [0, hidden_mules.HORIZON],
            "n_boot": hidden_mules.N_BOOT, "n_alarms": hidden_mules.N_ALARMS,
            "models": {m: trainer.model_files_sha256(trainer.find_model_dir(out, m)) for m in MODELS}}


def freeze(out: str) -> str:
    path = os.path.join(folder(out), "settings.json")
    if os.path.exists(path):
        raise SystemExit(f"{path} exists: the settings are frozen once")
    for m in TO_SHARE:
        shared = trainer.shared_dir(out, m)
        os.makedirs(shared, exist_ok=True)
        for f in trainer.MODEL_FILES:
            shutil.copyfile(os.path.join(trainer.model_dir(out, m), f), os.path.join(shared, f))
    os.makedirs(folder(out), exist_ok=True)
    with open(path, "w") as f:
        json.dump({**current(out), "frozen": time.strftime("%Y-%m-%d %H:%M"),
                   "git_commit": manifest._git("rev-parse", "HEAD")}, f, indent=2)
    return path


def problems(out: str) -> list[str]:
    """Why the look may not run (empty = it may). Reads no label."""
    path = os.path.join(folder(out), "settings.json")
    if not os.path.exists(path):
        return [f"{path} not found: freeze the settings first"]
    found = []
    if manifest._git("ls-files", "--error-unmatch", path) is None or manifest._git("status", "--porcelain", path):
        found.append(f"{path} is not committed as it stands")
    saved = json.load(open(path))
    now = current(out)
    found += [f"`{k}` differs from the frozen settings" for k in now if saved.get(k) != now[k]]
    for f in ("LOOK_STARTED.json", "LOOK.json"):
        if os.path.exists(os.path.join(folder(out), f)):
            found.append(f"{f} exists: the look runs once")
    return found


def look(out: str) -> str:
    found = problems(out)
    if found:
        raise SystemExit("the look is not allowed: " + "; ".join(found))
    with open(os.path.join(folder(out), "LOOK_STARTED.json"), "w") as f:
        json.dump({"started": time.strftime("%Y-%m-%d %H:%M"), "git_commit": manifest._git("rev-parse", "HEAD")}, f)
    scores = os.path.join(out, "scores", "outlier_look")
    os.makedirs(scores, exist_ok=True)
    paths = {}
    for m in MODELS:
        paths[m] = os.path.join(scores, f"{m}_m5.parquet")
        trainer.predict(out, MONTHS, (0, hidden_mules.HORIZON), m).to_parquet(paths[m], index=False)
    for m in outlier.METHODS:
        paths[m] = os.path.join(scores, f"outlier_{m}_m5.parquet")
        outlier.run(out, m, MONTHS).to_parquet(paths[m], index=False)
    for m, p in paths.items():
        harness.run(out, MONTHS, [hidden_mules.HORIZON], m, results=REPORT, scores_path=p)
    hidden_mules.run(out, MONTHS, paths, folder(out))
    with open(os.path.join(folder(out), "LOOK.json"), "w") as f:
        json.dump({"done": time.strftime("%Y-%m-%d %H:%M"),
                   "scores": {m: {"path": p, "sha256": manifest._sha256(p)} for m, p in paths.items()}}, f, indent=2)
    return folder(out)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m evaluation.outlier_look", description=__doc__.split("\n")[0])
    ap.add_argument("step", choices=["freeze", "check", "look"])
    ap.add_argument("--out", default=amldata.DEFAULT_OUT)
    a = ap.parse_args(argv)
    if a.step == "freeze":
        print(f"frozen -> {freeze(a.out)} (and the shared model files); commit them before the look")
    elif a.step == "check":
        found = problems(a.out)
        print("the look may run" if not found else "not allowed:\n- " + "\n- ".join(found))
    else:
        print(f"look done -> {look(a.out)}")


if __name__ == "__main__":
    main()
