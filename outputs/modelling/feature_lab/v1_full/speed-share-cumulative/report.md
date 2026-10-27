# Feature lab: speed-share-cumulative

data `v1_full`, groups speed_cum, views app, seed 42, commit bf43eac-dirty

Hypothesis: Confirm on the main dataset: share of all money in so far paid out within 1 h / 24 h of a payment in (keeps the burst visible after it ends, dilutes normal accounts' one-off fast weeks)

## View `app`: baseline vs baseline + candidates (3 folds, months 0-4)

### weekly_recall (decides)

| variant    |   n_features |   weekly_recall_pooled |   weekly_recall |   d_weekly_recall | d_weekly_recall_folds    | weekly_recall_verdict   |
|:-----------|-------------:|-----------------------:|----------------:|------------------:|:-------------------------|:------------------------|
| baseline   |           38 |                  0.403 |           0.409 |             0.000 | +0.000 / +0.000 / +0.000 |                         |
| +speed_cum |           40 |                  0.535 |           0.539 |             0.131 | +0.168 / +0.142 / +0.081 | better                  |

### acc_pr_auc

| variant    |   n_features |   acc_pr_auc |   d_acc_pr_auc | d_acc_pr_auc_folds       | acc_pr_auc_verdict   |
|:-----------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline   |           38 |        0.871 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +speed_cum |           40 |        0.886 |          0.015 | +0.030 / +0.007 / +0.007 | no clear change      |

### caught_2wk

| variant    |   n_features |   caught_2wk |   d_caught_2wk | d_caught_2wk_folds       | caught_2wk_verdict   |
|:-----------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline   |           38 |        0.899 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +speed_cum |           40 |        0.879 |         -0.020 | -0.047 / +0.000 / -0.013 | no clear change      |

- weekly_recall: share of each week's mules in that week's top 1% of open accounts, mean over weeks 0-26 (the tuning measure, decision 26 Oct 2026). `weekly_recall_pooled` pools the 3 validation months per week, as notebook 06 reports it; the per-fold column and the verdict use each fold alone.
- acc_pr_auc: account-level PR-AUC (an account's best week). caught_2wk: launderers starting in weeks 0-25 flagged in their start week or the next.
- verdict 'better' = all 3 folds improve and the mean gain is at least the noise level: weekly_recall 0.02, acc_pr_auc 0.04, caught_2wk 0.05 (PR-AUC: team rule; the others: assumptions).
- Real-customer mules in the account-level top 1% per fold (witting / unwitting) are in folds.csv.

## Screen: AUC vs started launderers (95% interval over launderers)

| feature           | week 8            | week 12           | week 26           |
|:------------------|:------------------|:------------------|:------------------|
| out_1h_share_cum  | 0.976 (0.96-0.99) | 0.961 (0.94-0.98) | 0.975 (0.96-0.98) |
| out_24h_share_cum | 0.923 (0.86-0.97) | 0.915 (0.89-0.94) | 0.919 (0.90-0.93) |

