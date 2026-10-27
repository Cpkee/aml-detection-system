# Feature lab: new-counterparties-4wk

data `v1`, groups new_cp4, views app, seed 42, commit bf43eac-dirty

Hypothesis: Every laundering shape pays in from 1-4 (or all-new) never-seen payers and out to 1-8 never-seen receivers within ~2 weeks, while a real customer's employer and direct-debit payees repeat; the store has new payers only as a weekly share and as cumulative counts a tree cannot difference, so counting payers and payees first seen in the last 4 weeks should lift real-customer mules (rests on laundering.shapes senders/recipients vs normal.transfers_in_per_month / transfers_out_per_month)

## View `app`: baseline vs baseline + candidates (3 folds, months 0-4)

### weekly_recall (decides)

| variant   |   n_features |   weekly_recall_pooled |   weekly_recall |   d_weekly_recall | d_weekly_recall_folds    | weekly_recall_verdict   |
|:----------|-------------:|-----------------------:|----------------:|------------------:|:-------------------------|:------------------------|
| baseline  |           38 |                  0.300 |           0.314 |             0.000 | +0.000 / +0.000 / +0.000 |                         |
| +new_cp4  |           40 |                  0.309 |           0.317 |             0.003 | -0.017 / +0.029 / -0.002 | no clear change         |

### acc_pr_auc

| variant   |   n_features |   acc_pr_auc |   d_acc_pr_auc | d_acc_pr_auc_folds       | acc_pr_auc_verdict   |
|:----------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline  |           38 |        0.731 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +new_cp4  |           40 |        0.770 |          0.039 | +0.084 / +0.064 / -0.031 | no clear change      |

### caught_2wk

| variant   |   n_features |   caught_2wk |   d_caught_2wk | d_caught_2wk_folds       | caught_2wk_verdict   |
|:----------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline  |           38 |        0.866 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +new_cp4  |           40 |        0.866 |          0.000 | +0.000 / +0.000 / +0.000 | no clear change      |

- weekly_recall: share of each week's mules in that week's top 1% of open accounts, mean over weeks 0-26 (the tuning measure, decision 26 Oct 2026). `weekly_recall_pooled` pools the 3 validation months per week, as notebook 06 reports it; the per-fold column and the verdict use each fold alone.
- acc_pr_auc: account-level PR-AUC (an account's best week). caught_2wk: launderers starting in weeks 0-25 flagged in their start week or the next.
- verdict 'better' = all 3 folds improve and the mean gain is at least the noise level: weekly_recall 0.02, acc_pr_auc 0.04, caught_2wk 0.05 (PR-AUC: team rule; the others: assumptions).
- Real-customer mules in the account-level top 1% per fold (witting / unwitting) are in folds.csv.

## Screen: AUC vs started launderers (95% interval over launderers)

| feature        | week 8        | week 12           | week 26           |
|:---------------|:--------------|:------------------|:------------------|
| new_payees_4wk | nan (nan-nan) | 0.661 (0.58-0.74) | 0.579 (0.50-0.65) |
| new_payers_4wk | nan (nan-nan) | 0.888 (0.83-0.93) | 0.542 (0.47-0.61) |

