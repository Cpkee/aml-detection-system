"""Model training (Phases 4-5 of the modelling plan).

Models read features from the weekly store (`features.weekly.load`), the cleaned application tables (checked with
`features.manifest.check_preprocess`) and labels from `amldata.labels()`. Nothing here may read a hidden file
(`tests/test_hidden_files.py`).

  PYTHONPATH=src python -m models train --out data/v1_full [--params FILE]    # fit and save the frozen 38-input model
  PYTHONPATH=src python -m models.lgbm_baseline --out data/v1                 # Phase 4 untuned baseline, 3 folds
  PYTHONPATH=src python -m models.feature_lab --out data/v1 --groups G --name N   # try candidate feature groups
"""
