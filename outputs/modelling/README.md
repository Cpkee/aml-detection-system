# outputs/modelling

Committed results of the modelling phases (plan: the "Modelling: phased plan" tab of the decision-record doc).

| Folder | Written by | Phase |
|---|---|---|
| `eda/` | `python -m features eda` (runs `notebooks/01_eda_train.ipynb`) | 1: EDA on training months (report, figures, `univariate_tests.csv`, `feature_screen.csv`) |
| `preprocess/` | `python -m features preprocess` (runs `notebooks/02_preprocess.ipynb`) | 2: cleaning recipe fitted on months 0-4 (`params.json`, `report.md`, figure); the cleaned tables go to `data/<run>/features/accounts_{linear,tree}.parquet` |
| `features/` | `python -m features store-check` (runs `notebooks/03_feature_store.ipynb` on a built store) | 3: gate record for the weekly feature store (`report.md`; `gate_values.csv` store vs EDA value by value, `gate_auc.csv`, `feature_screen.csv` for all 28 features, `first_week_auc_ci.csv` with 95% account-level bootstrap intervals, `speed_definitions.csv` kept vs dropped speed definition) and `speed_by_pattern.csv` (`python -m evaluation.speed_by_pattern`, by hidden laundering pattern); `v1/` = the 50k run |
| `feature_lab/<data>/<trial>/` | `python -m models.feature_lab` | 4: candidate feature trials (`report.md`, `folds.csv`, `screen.csv`, `summary.csv`) and the append-only `ledger.csv` of every trial (the number of looks) |
| `eda_agent/` | the `eda-explorer` agent, via `/feature-round` | appendix: `insights.csv` (append-only ledger of findings and their status) and `<round>/` figures and CSVs; the evidence notebooks are `notebooks/07_eda_agent_<round>.ipynb` |
| `feature_selection/` | `python -m features select` (runs `notebooks/13_feature_selection.ipynb`) | appendix: how much each of the 38 frozen inputs contributes (`report.md`, `summary.csv` label per input, `families.csv`, `near_copy_groups.csv`, `spearman.csv`, `permutation.csv`, 2 figures) |
| `outlier/` | `PLAN.md`; `python -m evaluation.outlier_look freeze` / `look` -> `v1_full/settings.json`, `LOOK*.json`, one harness folder per method, `hidden_mules.md` + CSVs; `notebooks/12_outlier_detection.ipynb` -> `v1_full/report.md`, figures; `APPENDIX.md` | appendix: label-free detectors and bank labels, one look on month 5 (31 Oct 2026) |
| `models/<run>/` | `python -m models train` | 4: models, calibrators, importances, model cards; model of record `v1_full/frozen_tuned_avg5/` (5 LightGBM seeds averaged, decision 30 Oct 2026) |
| `models/<run>/frozen_importance/` | `python -m models.frozen_importance` | 4: share of split gain per input of the frozen 38-input model (the feature lab's baseline, 3 folds, months 0-4) |
| `results/<run>/` | `python -m evaluation.score` (model of record, or `--scores FILE` from `python -m models predict`) | 5: weekly scoring against the rules on the test cohort (`summary_w<W>.csv`, `weekly_w<W>.csv`, `by_age_w<W>.csv`, `launderers.csv`, `settings.json` with provenance, `report.md`); `final_test/STARTED.json` + `LOCK.json` guard the first final run (the headline); later looks are counted re-tests (`--retest REASON`) in `final_test_r<N>/`, each a row in `final_test_looks.csv` |

Feature stores themselves are data (`data/<run>/features/`, git-ignored); only their manifests are described here.
