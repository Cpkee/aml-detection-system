# outputs/modelling

Committed results of the modelling phases (plan: the "Modelling: phased plan" tab of the decision-record doc).

| Folder | Written by | Phase |
|---|---|---|
| `eda/` | `python -m features eda` (runs `notebooks/01_eda_train.ipynb`) | 1: EDA on training months (report, figures, `univariate_tests.csv`, `feature_screen.csv`) |
| `preprocess/` | `python -m features preprocess` (runs `notebooks/02_preprocess.ipynb`) | 2: cleaning recipe fitted on months 0-4 (`params.json`, `report.md`, figure); the cleaned tables go to `data/<run>/features/accounts_{linear,tree}.parquet` |
| `features/` | `python -m features store-check` (runs `notebooks/03_feature_store.ipynb` on a built store) | 3: gate record for the weekly feature store (`report.md`; `gate_values.csv` store vs EDA value by value, `gate_auc.csv`, `feature_screen.csv` for all 28 features, `first_week_auc_ci.csv` with 95% account-level bootstrap intervals, `speed_definitions.csv` kept vs dropped speed definition) and `speed_by_pattern.csv` (`python -m evaluation.speed_by_pattern`, by hidden laundering pattern); `v1/` = the 50k run |
| `feature_selection/` | `python -m features select` (runs `notebooks/07_feature_selection.ipynb`) | 4: which of the tuned model's 38 inputs earn their place (`report.md`, `summary.csv` label per input, `families.csv`, `near_copy_groups.csv`, `spearman.csv`, `permutation.csv`, 2 figures); `v1/` = the 50k run |
| `models/<run>/` | `python -m models train` | 4: models, calibrators, importances, model cards |
| `results/<run>/` | `python -m evaluation.score` | 5: weekly scoring against the rules on the test cohort |

Feature stores themselves are data (`data/<run>/features/`, git-ignored); only their manifests are described here.
