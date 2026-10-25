# Feature lab: roll4-core-vs-full

data `v1_full`, groups roll4_core, views app, seed 42, commit c86743e-dirty

Hypothesis: Is the smaller 4-week set (three ratios + payments in) as good as all eight roll4 features?

## View `app`: baseline vs baseline + candidates (3 folds, months 0-4)

### weekly_recall (decides)

| variant     |   n_features |   weekly_recall_pooled |   weekly_recall |   d_weekly_recall | d_weekly_recall_folds    | weekly_recall_verdict   |
|:------------|-------------:|-----------------------:|----------------:|------------------:|:-------------------------|:------------------------|
| baseline    |           30 |                  0.345 |           0.351 |             0.000 | +0.000 / +0.000 / +0.000 |                         |
| +roll4_core |           34 |                  0.393 |           0.398 |             0.047 | +0.047 / +0.062 / +0.031 | better                  |

### acc_pr_auc

| variant     |   n_features |   acc_pr_auc |   d_acc_pr_auc | d_acc_pr_auc_folds       | acc_pr_auc_verdict   |
|:------------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline    |           30 |        0.695 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +roll4_core |           34 |        0.826 |          0.131 | +0.202 / +0.169 / +0.023 | better               |

### caught_2wk

| variant     |   n_features |   caught_2wk |   d_caught_2wk | d_caught_2wk_folds       | caught_2wk_verdict   |
|:------------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline    |           30 |        0.884 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +roll4_core |           34 |        0.885 |          0.001 | +0.047 / -0.057 / +0.013 | no clear change      |

- weekly_recall: share of each week's mules in that week's top 1% of open accounts, mean over weeks 0-26 (the tuning measure, decision 26 Oct 2026). `weekly_recall_pooled` pools the 3 validation months per week, as notebook 06 reports it; the per-fold column and the verdict use each fold alone.
- acc_pr_auc: account-level PR-AUC (an account's best week). caught_2wk: launderers starting in weeks 0-25 flagged in their start week or the next.
- verdict 'better' = all 3 folds improve and the mean gain is at least the noise level: weekly_recall 0.02, acc_pr_auc 0.04, caught_2wk 0.05 (PR-AUC: team rule; the others: assumptions).
- Real-customer mules in the account-level top 1% per fold (witting / unwitting) are in folds.csv.

## Screen: AUC vs started launderers (95% interval over launderers)

| feature           | week 8            | week 12           | week 26           |
|:------------------|:------------------|:------------------|:------------------|
| n_in_4wk          | 0.842 (0.77-0.90) | 0.886 (0.86-0.91) | 0.590 (0.56-0.62) |
| out_1h_share_4wk  | 0.901 (0.83-0.96) | 0.934 (0.91-0.96) | 0.572 (0.55-0.60) |
| out_24h_share_4wk | 0.882 (0.82-0.93) | 0.908 (0.88-0.93) | 0.585 (0.55-0.62) |
| passthrough_4wk   | 0.602 (0.52-0.68) | 0.541 (0.51-0.58) | 0.484 (0.45-0.52) |

