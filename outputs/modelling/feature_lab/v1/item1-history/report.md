# Feature lab: item1-history

data `v1`, groups lag1, roll2, roll4, running_max, seed 42, commit b11389c-dirty

Hypothesis: A ~2-week burst crosses week boundaries and the pooled model sees past weeks only through running totals; recent-history features should catch it sooner

## Model: activity LightGBM, baseline vs baseline + candidates (3 folds, months 0-4)

### acc_pr_auc

| variant      |   n_features |   acc_pr_auc |   d_acc_pr_auc | d_acc_pr_auc_folds       | acc_pr_auc_verdict   |
|:-------------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline     |           29 |        0.490 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +lag1        |           37 |        0.570 |          0.080 | +0.121 / +0.108 / +0.012 | better               |
| +roll2       |           37 |        0.678 |          0.188 | +0.213 / +0.184 / +0.168 | better               |
| +roll4       |           37 |        0.832 |          0.342 | +0.348 / +0.396 / +0.281 | better               |
| +running_max |           33 |        0.463 |         -0.027 | -0.129 / +0.156 / -0.109 | no clear change      |
| +all         |           57 |        0.791 |          0.301 | +0.311 / +0.418 / +0.174 | better               |

### caught_2wk

| variant      |   n_features |   caught_2wk |   d_caught_2wk | d_caught_2wk_folds       | caught_2wk_verdict   |
|:-------------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline     |           29 |        0.887 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +lag1        |           37 |        0.849 |         -0.038 | -0.059 / -0.056 / +0.000 | no clear change      |
| +roll2       |           37 |        0.942 |          0.056 | +0.000 / +0.111 / +0.056 | no clear change      |
| +roll4       |           37 |        0.924 |          0.037 | +0.000 / +0.056 / +0.056 | no clear change      |
| +running_max |           33 |        0.714 |         -0.173 | -0.353 / -0.056 / -0.111 | worse                |
| +all         |           57 |        0.886 |         -0.001 | -0.059 / +0.000 / +0.056 | no clear change      |

### early_recall

| variant      |   n_features |   early_recall |   d_early_recall | d_early_recall_folds     |
|:-------------|-------------:|---------------:|-----------------:|:-------------------------|
| baseline     |           29 |          0.022 |            0.000 | +0.000 / +0.000 / +0.000 |
| +lag1        |           37 |          0.019 |           -0.002 | +0.000 / -0.013 / +0.006 |
| +roll2       |           37 |          0.011 |           -0.011 | +0.000 / -0.039 / +0.006 |
| +roll4       |           37 |          0.004 |           -0.018 | +0.000 / -0.059 / +0.006 |
| +running_max |           33 |          0.013 |           -0.009 | +0.000 / -0.026 / +0.000 |
| +all         |           57 |          0.011 |           -0.011 | +0.000 / -0.033 / +0.000 |

- acc_pr_auc: account-level PR-AUC, weeks 0-26. caught_2wk: launderers starting in weeks 0-25 flagged (weekly top 1%) in their start week or the next. early_recall: share of each week's mules in that week's top 1%, weeks 0-8 (mostly fakes not yet laundering; no verdict).
- verdict 'better' = all 3 folds improve and the mean gain is at least 0.04 (PR-AUC, the team's fold-noise rule) / 0.05 (caught_2wk, an assumption).
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

