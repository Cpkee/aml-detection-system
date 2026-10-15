# outputs/modelling

Committed results of the modelling phases (plan: the "Modelling: phased plan" tab of the decision-record doc).

| Folder | Written by | Phase |
|---|---|---|
| `eda/` | `python -m features eda` (runs `notebooks/01_eda_train.ipynb`) | 1: EDA on training months (report, figures, `univariate_tests.csv`, `feature_screen.csv`) |
| `preprocess/` | `python -m features preprocess` (runs `notebooks/02_preprocess.ipynb`) | 2: cleaning recipe fitted on months 0-4 (`params.json`, `report.md`, figure); the cleaned tables go to `data/<run>/features/accounts_{linear,tree}.parquet` |
| `models/<run>/` | `python -m models train` | 4: models, calibrators, importances, model cards |
| `results/<run>/` | `python -m evaluation.score` | 5: weekly scoring against the rules on the test cohort |

Feature stores themselves are data (`data/<run>/features/`, git-ignored); only their manifests are described here.
