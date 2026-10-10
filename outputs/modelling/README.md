# outputs/modelling

Committed results of the modelling phases (plan: the "Modelling: phased plan" tab of the decision-record doc).

| Folder | Written by | Phase |
|---|---|---|
| `eda/` | `python -m features eda` (runs `notebooks/01_eda_train.ipynb`) | 1: EDA on training months (report, figures, `univariate_tests.csv`, `feature_screen.csv`) |
| `preprocessor.joblib` | `python -m features preprocess` | 2: cleaning recipe fitted on months 0-4 |
| `models/<run>/` | `python -m models train` | 4: models, calibrators, importances, model cards |
| `results/<run>/` | `python -m evaluation.score` | 5: weekly scoring against the rules on the test cohort |

Feature stores themselves are data (`data/<run>/features/`, git-ignored); only their manifests are described here.
