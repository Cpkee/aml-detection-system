# Feature lab: self-vs-own-month

data `v1_full`, groups self4, views app, seed 42, commit bf43eac-dirty

Hypothesis: Confirm on the main dataset: last 4 weeks vs the account's own 4-week average before them (money in / out, payments in); the store's self_vs_past_money_in is NaN for ~68% of account-weeks because weekly money in is mostly 0 between paydays

## View `app`: baseline vs baseline + candidates (3 folds, months 0-4)

### weekly_recall (decides)

| variant   |   n_features |   weekly_recall_pooled |   weekly_recall |   d_weekly_recall | d_weekly_recall_folds    | weekly_recall_verdict   |
|:----------|-------------:|-----------------------:|----------------:|------------------:|:-------------------------|:------------------------|
| baseline  |           38 |                  0.403 |           0.409 |             0.000 | +0.000 / +0.000 / +0.000 |                         |
| +self4    |           41 |                  0.437 |           0.438 |             0.030 | +0.030 / +0.037 / +0.022 | better                  |

### acc_pr_auc

| variant   |   n_features |   acc_pr_auc |   d_acc_pr_auc | d_acc_pr_auc_folds       | acc_pr_auc_verdict   |
|:----------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline  |           38 |        0.871 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +self4    |           41 |        0.897 |          0.026 | +0.039 / +0.007 / +0.032 | no clear change      |

### caught_2wk

| variant   |   n_features |   caught_2wk |   d_caught_2wk | d_caught_2wk_folds       | caught_2wk_verdict   |
|:----------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline  |           38 |        0.899 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +self4    |           41 |        0.899 |          0.000 | +0.000 / +0.000 / +0.000 | no clear change      |

- weekly_recall: share of each week's mules in that week's top 1% of open accounts, mean over weeks 0-26 (the tuning measure, decision 26 Oct 2026). `weekly_recall_pooled` pools the 3 validation months per week, as notebook 06 reports it; the per-fold column and the verdict use each fold alone.
- acc_pr_auc: account-level PR-AUC (an account's best week). caught_2wk: launderers starting in weeks 0-25 flagged in their start week or the next.
- verdict 'better' = all 3 folds improve and the mean gain is at least the noise level: weekly_recall 0.02, acc_pr_auc 0.04, caught_2wk 0.05 (PR-AUC: team rule; the others: assumptions).
- Real-customer mules in the account-level top 1% per fold (witting / unwitting) are in folds.csv.

## Screen: AUC vs started launderers (95% interval over launderers)

| feature         | week 8            | week 12           | week 26           |
|:----------------|:------------------|:------------------|:------------------|
| self4_money_in  | 0.690 (0.55-0.81) | 0.848 (0.80-0.89) | 0.332 (0.30-0.37) |
| self4_money_out | 0.671 (0.53-0.79) | 0.847 (0.81-0.89) | 0.362 (0.33-0.40) |
| self4_n_in      | 0.632 (0.52-0.73) | 0.839 (0.81-0.87) | 0.424 (0.39-0.46) |

