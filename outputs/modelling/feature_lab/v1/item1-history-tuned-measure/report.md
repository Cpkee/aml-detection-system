# Feature lab: item1-history-tuned-measure

data `v1`, groups lag1, roll2, roll4, running_max, views app, seed 42, commit a2728c4-dirty

Hypothesis: Re-score item1 on the tuning measure (weekly earliness, decision 26 Oct) with the tuned model (activity + application score)

## View `app`: baseline vs baseline + candidates (3 folds, months 0-4)

### weekly_recall (decides)

| variant      |   n_features |   weekly_recall_pooled |   weekly_recall |   d_weekly_recall | d_weekly_recall_folds    | weekly_recall_verdict   |
|:-------------|-------------:|-----------------------:|----------------:|------------------:|:-------------------------|:------------------------|
| baseline     |           30 |                  0.226 |           0.230 |             0.000 | +0.000 / +0.000 / +0.000 |                         |
| +lag1        |           38 |                  0.236 |           0.242 |             0.012 | +0.029 / +0.010 / -0.002 | no clear change         |
| +roll2       |           38 |                  0.246 |           0.256 |             0.026 | +0.035 / +0.032 / +0.011 | better                  |
| +roll4       |           38 |                  0.300 |           0.314 |             0.085 | +0.153 / +0.007 / +0.093 | better                  |
| +running_max |           34 |                  0.342 |           0.360 |             0.131 | +0.140 / +0.155 / +0.097 | better                  |
| +all         |           58 |                  0.382 |           0.404 |             0.175 | +0.215 / +0.153 / +0.156 | better                  |

### acc_pr_auc

| variant      |   n_features |   acc_pr_auc |   d_acc_pr_auc | d_acc_pr_auc_folds       | acc_pr_auc_verdict   |
|:-------------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline     |           30 |        0.411 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +lag1        |           38 |        0.427 |          0.016 | +0.016 / +0.053 / -0.022 | no clear change      |
| +roll2       |           38 |        0.482 |          0.071 | +0.008 / +0.120 / +0.084 | better               |
| +roll4       |           38 |        0.731 |          0.320 | +0.417 / +0.306 / +0.236 | better               |
| +running_max |           34 |        0.482 |          0.071 | +0.110 / +0.163 / -0.060 | no clear change      |
| +all         |           58 |        0.710 |          0.299 | +0.325 / +0.382 / +0.188 | better               |

### caught_2wk

| variant      |   n_features |   caught_2wk |   d_caught_2wk | d_caught_2wk_folds       | caught_2wk_verdict   |
|:-------------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline     |           30 |        0.582 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +lag1        |           38 |        0.638 |          0.057 | +0.059 / +0.111 / +0.000 | no clear change      |
| +roll2       |           38 |        0.753 |          0.171 | +0.235 / +0.167 / +0.111 | better               |
| +roll4       |           38 |        0.866 |          0.284 | +0.353 / +0.167 / +0.333 | better               |
| +running_max |           34 |        0.696 |          0.114 | +0.176 / +0.111 / +0.056 | better               |
| +all         |           58 |        0.809 |          0.228 | +0.294 / +0.111 / +0.278 | better               |

- weekly_recall: share of each week's mules in that week's top 1% of open accounts, mean over weeks 0-26 (the tuning measure, decision 26 Oct 2026). `weekly_recall_pooled` pools the 3 validation months per week, as notebook 06 reports it; the per-fold column and the verdict use each fold alone.
- acc_pr_auc: account-level PR-AUC (an account's best week). caught_2wk: launderers starting in weeks 0-25 flagged in their start week or the next.
- verdict 'better' = all 3 folds improve and the mean gain is at least the noise level: weekly_recall 0.02, acc_pr_auc 0.04, caught_2wk 0.05 (PR-AUC: team rule; the others: assumptions).
- Real-customer mules in the account-level top 1% per fold (witting / unwitting) are in folds.csv.

## Screen: AUC vs started launderers (95% interval over launderers)

| feature                     | week 8        | week 12           | week 26           |
|:----------------------------|:--------------|:------------------|:------------------|
| money_in_2wk                | nan (nan-nan) | 0.702 (0.63-0.76) | 0.599 (0.52-0.67) |
| money_in_4wk                | nan (nan-nan) | 0.869 (0.82-0.91) | 0.669 (0.60-0.74) |
| money_in_wk_lag1            | nan (nan-nan) | 0.688 (0.61-0.75) | 0.520 (0.46-0.59) |
| money_in_wk_max_so_far      | nan (nan-nan) | 0.710 (0.64-0.77) | 0.738 (0.68-0.79) |
| money_out_2wk               | nan (nan-nan) | 0.814 (0.74-0.88) | 0.582 (0.50-0.65) |
| money_out_4wk               | nan (nan-nan) | 0.886 (0.83-0.93) | 0.628 (0.54-0.71) |
| money_out_wk_lag1           | nan (nan-nan) | 0.741 (0.64-0.82) | 0.577 (0.50-0.65) |
| n_in_2wk                    | nan (nan-nan) | 0.852 (0.78-0.91) | 0.565 (0.50-0.63) |
| n_in_4wk                    | nan (nan-nan) | 0.933 (0.89-0.97) | 0.599 (0.53-0.67) |
| n_in_wk_lag1                | nan (nan-nan) | 0.752 (0.66-0.83) | 0.552 (0.48-0.62) |
| n_payers_2wk                | nan (nan-nan) | 0.798 (0.72-0.86) | 0.542 (0.48-0.61) |
| n_payers_4wk                | nan (nan-nan) | 0.879 (0.82-0.93) | 0.565 (0.50-0.63) |
| n_payers_wk_lag1            | nan (nan-nan) | 0.713 (0.62-0.79) | 0.521 (0.45-0.59) |
| n_payers_wk_max_so_far      | nan (nan-nan) | 0.777 (0.70-0.85) | 0.765 (0.69-0.83) |
| n_rows_2wk                  | nan (nan-nan) | 0.775 (0.68-0.85) | 0.526 (0.45-0.60) |
| n_rows_4wk                  | nan (nan-nan) | 0.918 (0.86-0.96) | 0.572 (0.50-0.65) |
| n_rows_wk_lag1              | nan (nan-nan) | 0.732 (0.63-0.82) | 0.544 (0.47-0.62) |
| out_1h_share_2wk            | nan (nan-nan) | 0.851 (0.78-0.91) | 0.597 (0.55-0.64) |
| out_1h_share_4wk            | nan (nan-nan) | 0.959 (0.91-1.00) | 0.591 (0.54-0.65) |
| out_1h_share_wk_lag1        | nan (nan-nan) | 0.755 (0.66-0.83) | 0.544 (0.48-0.61) |
| out_1h_share_wk_max_so_far  | nan (nan-nan) | 0.899 (0.85-0.94) | 0.884 (0.87-0.89) |
| out_24h_share_2wk           | nan (nan-nan) | 0.808 (0.74-0.86) | 0.616 (0.55-0.68) |
| out_24h_share_4wk           | nan (nan-nan) | 0.948 (0.93-0.96) | 0.582 (0.51-0.65) |
| out_24h_share_wk_lag1       | nan (nan-nan) | 0.721 (0.64-0.79) | 0.558 (0.49-0.63) |
| out_24h_share_wk_max_so_far | nan (nan-nan) | 0.582 (0.53-0.63) | 0.527 (0.47-0.58) |
| passthrough_2wk             | nan (nan-nan) | 0.676 (0.61-0.73) | 0.574 (0.51-0.64) |
| passthrough_4wk             | nan (nan-nan) | 0.520 (0.45-0.58) | 0.433 (0.37-0.50) |
| passthrough_wk_lag1         | nan (nan-nan) | 0.662 (0.59-0.73) | 0.554 (0.48-0.63) |

