"""Modelling features: the leak-free EDA (Phase 1), preprocessing (Phase 2) and the weekly feature store (Phase 3).

Everything here reads the data through `amldata.public()` and `amldata.labels()` only. `tests/test_hidden_files.py`
fails if any file in this package names a hidden file.

  PYTHONPATH=src python -m features weekly --out data/v1 --weeks 0-77    # build <out>/features/weekly.parquet
  PYTHONPATH=src python -m features preprocess --out data/v1             # run notebooks/02_preprocess.ipynb (Phase 2)
"""
