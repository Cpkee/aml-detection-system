# Feature lab: self-vs-own-month

data `v1`, groups self4, views app, seed 42, commit bf43eac-dirty

Hypothesis: A real customer already has a steady monthly pattern (salary scaled by BAF income, ~1 transfer in), and a burst of 3-15 payments in at GBP 532 x amount_rel per piece multiplies it; the store's self_vs_past_money_in is NaN for ~68% of account-weeks (weekly money in is mostly 0 between paydays, so the MAD is 0) and peer_ratio compares with other accounts, so the last 4 weeks vs the account's own 4-week average should lift real-customer mules (rests on laundering.out_transfer_mean x shape amount_rel and n_in vs normal salary / transfers_in_per_month)

## View `app`: baseline vs baseline + candidates (3 folds, months 0-4)

### weekly_recall (decides)

| variant   |   n_features |   weekly_recall_pooled |   weekly_recall |   d_weekly_recall | d_weekly_recall_folds    | weekly_recall_verdict   |
|:----------|-------------:|-----------------------:|----------------:|------------------:|:-------------------------|:------------------------|
| baseline  |           38 |                  0.300 |           0.314 |             0.000 | +0.000 / +0.000 / +0.000 |                         |
| +self4    |           41 |                  0.353 |           0.357 |             0.043 | +0.028 / +0.094 / +0.008 | better                  |

### acc_pr_auc

| variant   |   n_features |   acc_pr_auc |   d_acc_pr_auc | d_acc_pr_auc_folds       | acc_pr_auc_verdict   |
|:----------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline  |           38 |        0.731 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +self4    |           41 |        0.800 |          0.069 | +0.142 / +0.097 / -0.032 | no clear change      |

### caught_2wk

| variant   |   n_features |   caught_2wk |   d_caught_2wk | d_caught_2wk_folds       | caught_2wk_verdict   |
|:----------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline  |           38 |        0.866 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +self4    |           41 |        0.905 |          0.039 | +0.118 / +0.000 / +0.000 | no clear change      |

- weekly_recall: share of each week's mules in that week's top 1% of open accounts, mean over weeks 0-26 (the tuning measure, decision 26 Oct 2026). `weekly_recall_pooled` pools the 3 validation months per week, as notebook 06 reports it; the per-fold column and the verdict use each fold alone.
- acc_pr_auc: account-level PR-AUC (an account's best week). caught_2wk: launderers starting in weeks 0-25 flagged in their start week or the next.
- verdict 'better' = all 3 folds improve and the mean gain is at least the noise level: weekly_recall 0.02, acc_pr_auc 0.04, caught_2wk 0.05 (PR-AUC: team rule; the others: assumptions).
- Real-customer mules in the account-level top 1% per fold (witting / unwitting) are in folds.csv.

## Screen: AUC vs started launderers (95% interval over launderers)

| feature         | week 8        | week 12           | week 26           |
|:----------------|:--------------|:------------------|:------------------|
| self4_money_in  | nan (nan-nan) | 0.922 (0.85-0.98) | 0.335 (0.26-0.41) |
| self4_money_out | nan (nan-nan) | 0.892 (0.83-0.94) | 0.371 (0.28-0.46) |
| self4_n_in      | nan (nan-nan) | 0.903 (0.86-0.93) | 0.395 (0.32-0.47) |

