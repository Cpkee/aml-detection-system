"""Model training and calibration (Phase 4 of the modelling plan).

Models read features from the weekly store (`features.weekly.load`) and labels from `amldata.labels()`.
Nothing here may read a hidden file (`tests/test_hidden_files.py`).

  PYTHONPATH=src python -m models train --view combined --model lgbm --out data/v1
"""
