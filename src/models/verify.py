"""Accept a model file trained on another machine, once, by reproducing one of its committed results here.

    PYTHONPATH=src python -m models verify --out data/v1_full --model frozen_tuned \
        --reference month5_dryrun_frozen_tuned

For a shared model trained before models recorded input fingerprints (Li Ann's frozen_tuned, 28 Oct 2026). Its
manifest only holds a hash of the trainer's run_manifest.json, which differs per machine even for identical data. So
the model is rescored here on the reference run's cohort (outputs/modelling/results/<data>/<reference>/) and every
result file present in both runs must come out identical: the summaries, the weekly tables and each launderer's flag
weeks (the reference's columns; columns the harness added since are ignored). Identical results mean identical
inputs and an identical model. Then verified.json records this machine's input fingerprints and the hashes of the
model files, and models.train.load accepts the model while both still hold.
Nothing is written when any file differs.
"""
from __future__ import annotations
import argparse
import datetime
import json
import os
import tempfile

import pandas as pd

import amldata
from evaluation import score as sc
from features import fingerprint
from models import train


def same_columns(ref: pd.DataFrame, new: pd.DataFrame) -> bool:
    """Every column of the reference file comes out identical (columns added to the harness later are ignored)."""
    return set(ref.columns) <= set(new.columns) and new[ref.columns].equals(ref)


def verify(out: str, model: str, reference: str) -> dict:
    data = os.path.basename(os.path.normpath(out))
    ref_dir = os.path.join(sc.RESULTS, data, reference)
    settings = json.load(open(os.path.join(ref_dir, "settings.json")))
    folder = train.find_model_dir(out, model)
    man = train.load(out, model, check_data=False)[2]
    if settings["model"] != model or settings.get("model_git_commit") != man["git_commit"]:
        raise SystemExit(f"{reference} was scored by model {settings['model']} at commit "
                         f"{settings.get('model_git_commit')}, not {model} at {man['git_commit']}")
    with tempfile.TemporaryDirectory() as tmp:
        new = sc.run(out, settings["cohort_months"], settings["horizons"], reference, model,
                     check_data=False, results=tmp)
        files = sorted(f for f in os.listdir(ref_dir) if f.endswith(".csv") and os.path.exists(os.path.join(new, f)))
        if not any(f.startswith("summary_") for f in files):
            raise SystemExit(f"{reference} has no summary files to compare")
        result = {f: same_columns(pd.read_csv(os.path.join(ref_dir, f)), pd.read_csv(os.path.join(new, f)))
                  for f in files}
    record = {"verified": all(result.values()), "reference": ref_dir, "compared": result,
              "date": datetime.date.today().isoformat(), "machine": train.machine()}
    if record["verified"]:
        record |= {"input_fingerprints": fingerprint.fingerprints(out),
                   "model_files_sha256": train.model_files_sha256(folder)}
        with open(os.path.join(folder, train.VERIFIED), "w") as f:
            json.dump(record, f, indent=2)
    return record


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m models verify", description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=amldata.DEFAULT_OUT)
    ap.add_argument("--model", required=True, help="model folder under <out>/models/ (the shared model files)")
    ap.add_argument("--reference", required=True, help="committed harness run of this model, under "
                                                       "outputs/modelling/results/<data>/")
    a = ap.parse_args(argv)
    r = verify(a.out, a.model, a.reference)
    for f, ok in r["compared"].items():
        print(f"  {f:22s} {'identical' if ok else 'DIFFERENT'}")
    if r["verified"]:
        print(f"verified: {a.model} reproduces {a.reference} on this machine -> {train.VERIFIED} written")
    else:
        raise SystemExit(f"NOT verified: {a.model} does not reproduce {a.reference} here; nothing written")


if __name__ == "__main__":
    main()
