# Feature lab: item1-history-tuned-measure

data `v1_full`, groups lag1, roll2, roll4, running_max, views app, seed 42, commit a2728c4-dirty

Hypothesis: Re-score item1 on the tuning measure (weekly earliness, decision 26 Oct) with the tuned model (activity + application score)

## View `app`: baseline vs baseline + candidates (3 folds, months 0-4)

### weekly_recall (decides)

| variant      |   n_features |   weekly_recall_pooled |   weekly_recall |   d_weekly_recall | d_weekly_recall_folds    | weekly_recall_verdict   |
|:-------------|-------------:|-----------------------:|----------------:|------------------:|:-------------------------|:------------------------|
| baseline     |           30 |                  0.345 |           0.351 |             0.000 | +0.000 / +0.000 / +0.000 |                         |
| +lag1        |           38 |                  0.355 |           0.366 |             0.016 | +0.030 / +0.002 / +0.014 | no clear change         |
| +roll2       |           38 |                  0.358 |           0.362 |             0.012 | +0.023 / +0.010 / +0.001 | no clear change         |
| +roll4       |           38 |                  0.403 |           0.409 |             0.058 | +0.073 / +0.041 / +0.059 | better                  |
| +running_max |           34 |                  0.413 |           0.415 |             0.064 | +0.077 / +0.058 / +0.057 | better                  |
| +all         |           58 |                  0.431 |           0.435 |             0.084 | +0.096 / +0.074 / +0.083 | better                  |

### acc_pr_auc

| variant      |   n_features |   acc_pr_auc |   d_acc_pr_auc | d_acc_pr_auc_folds       | acc_pr_auc_verdict   |
|:-------------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline     |           30 |        0.695 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +lag1        |           38 |        0.752 |          0.058 | +0.042 / +0.081 / +0.050 | better               |
| +roll2       |           38 |        0.768 |          0.073 | +0.126 / +0.083 / +0.011 | better               |
| +roll4       |           38 |        0.871 |          0.177 | +0.267 / +0.223 / +0.040 | better               |
| +running_max |           34 |        0.649 |         -0.045 | -0.016 / -0.037 / -0.083 | worse                |
| +all         |           58 |        0.838 |          0.143 | +0.219 / +0.179 / +0.032 | better               |

### caught_2wk

| variant      |   n_features |   caught_2wk |   d_caught_2wk | d_caught_2wk_folds       | caught_2wk_verdict   |
|:-------------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline     |           30 |        0.884 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +lag1        |           38 |        0.881 |         -0.003 | +0.047 / -0.029 / -0.027 | no clear change      |
| +roll2       |           38 |        0.906 |          0.022 | +0.094 / +0.000 / -0.027 | no clear change      |
| +roll4       |           38 |        0.899 |          0.016 | +0.078 / -0.057 / +0.027 | no clear change      |
| +running_max |           34 |        0.807 |         -0.076 | -0.047 / -0.129 / -0.053 | worse                |
| +all         |           58 |        0.881 |         -0.002 | +0.062 / -0.043 / -0.027 | no clear change      |

- weekly_recall: share of each week's mules in that week's top 1% of open accounts, mean over weeks 0-26 (the tuning measure, decision 26 Oct 2026). `weekly_recall_pooled` pools the 3 validation months per week, as notebook 06 reports it; the per-fold column and the verdict use each fold alone.
- acc_pr_auc: account-level PR-AUC (an account's best week). caught_2wk: launderers starting in weeks 0-25 flagged in their start week or the next.
- verdict 'better' = all 3 folds improve and the mean gain is at least the noise level: weekly_recall 0.02, acc_pr_auc 0.04, caught_2wk 0.05 (PR-AUC: team rule; the others: assumptions).
- Real-customer mules in the account-level top 1% per fold (witting / unwitting) are in folds.csv.

## Screen: AUC vs started launderers (95% interval over launderers)

| feature                     | week 8            | week 12           | week 26           |
|:----------------------------|:------------------|:------------------|:------------------|
| money_in_2wk                | 0.688 (0.59-0.77) | 0.743 (0.71-0.78) | 0.524 (0.49-0.56) |
| money_in_4wk                | 0.714 (0.61-0.80) | 0.830 (0.80-0.86) | 0.596 (0.56-0.63) |
| money_in_wk_lag1            | 0.635 (0.54-0.72) | 0.680 (0.64-0.72) | 0.522 (0.49-0.56) |
| money_in_wk_max_so_far      | 0.619 (0.53-0.69) | 0.711 (0.68-0.74) | 0.707 (0.68-0.73) |
| money_out_2wk               | 0.734 (0.62-0.83) | 0.846 (0.81-0.88) | 0.582 (0.55-0.62) |
| money_out_4wk               | 0.758 (0.66-0.84) | 0.855 (0.82-0.89) | 0.595 (0.56-0.63) |
| money_out_wk_lag1           | 0.615 (0.49-0.72) | 0.772 (0.73-0.81) | 0.567 (0.53-0.60) |
| n_in_2wk                    | 0.795 (0.69-0.88) | 0.835 (0.80-0.87) | 0.539 (0.50-0.57) |
| n_in_4wk                    | 0.842 (0.77-0.90) | 0.886 (0.86-0.91) | 0.590 (0.56-0.62) |
| n_in_wk_lag1                | 0.656 (0.55-0.75) | 0.715 (0.67-0.76) | 0.530 (0.50-0.56) |
| n_payers_2wk                | 0.776 (0.68-0.86) | 0.783 (0.74-0.82) | 0.528 (0.50-0.56) |
| n_payers_4wk                | 0.811 (0.73-0.88) | 0.830 (0.80-0.86) | 0.572 (0.54-0.60) |
| n_payers_wk_lag1            | 0.596 (0.50-0.69) | 0.687 (0.64-0.73) | 0.520 (0.49-0.55) |
| n_payers_wk_max_so_far      | 0.818 (0.74-0.88) | 0.749 (0.71-0.78) | 0.735 (0.70-0.77) |
| n_rows_2wk                  | 0.815 (0.72-0.89) | 0.858 (0.83-0.89) | 0.535 (0.50-0.57) |
| n_rows_4wk                  | 0.822 (0.73-0.90) | 0.880 (0.85-0.91) | 0.566 (0.53-0.60) |
| n_rows_wk_lag1              | 0.626 (0.50-0.73) | 0.757 (0.71-0.80) | 0.537 (0.50-0.57) |
| out_1h_share_2wk            | 0.817 (0.72-0.90) | 0.859 (0.82-0.90) | 0.548 (0.52-0.57) |
| out_1h_share_4wk            | 0.901 (0.83-0.96) | 0.934 (0.91-0.96) | 0.572 (0.55-0.60) |
| out_1h_share_wk_lag1        | 0.684 (0.58-0.78) | 0.735 (0.69-0.78) | 0.538 (0.51-0.57) |
| out_1h_share_wk_max_so_far  | 0.943 (0.93-0.95) | 0.912 (0.89-0.93) | 0.875 (0.87-0.88) |
| out_24h_share_2wk           | 0.750 (0.65-0.83) | 0.806 (0.77-0.84) | 0.554 (0.52-0.59) |
| out_24h_share_4wk           | 0.882 (0.82-0.93) | 0.908 (0.88-0.93) | 0.585 (0.55-0.62) |
| out_24h_share_wk_lag1       | 0.660 (0.56-0.75) | 0.711 (0.67-0.75) | 0.534 (0.50-0.57) |
| out_24h_share_wk_max_so_far | 0.652 (0.62-0.69) | 0.636 (0.61-0.66) | 0.560 (0.53-0.59) |
| passthrough_2wk             | 0.661 (0.57-0.73) | 0.651 (0.62-0.68) | 0.549 (0.51-0.58) |
| passthrough_4wk             | 0.602 (0.52-0.68) | 0.541 (0.51-0.58) | 0.484 (0.45-0.52) |
| passthrough_wk_lag1         | 0.637 (0.54-0.72) | 0.658 (0.62-0.70) | 0.542 (0.51-0.58) |

