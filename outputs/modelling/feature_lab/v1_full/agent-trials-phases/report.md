# Feature lab: agent-trials-phases

data `v1_full`, groups self4, speed_cum, views app, seed 42, commit bf43eac-dirty

Hypothesis: Same breakdown for the agent's two v1_full candidates (self4, speed_cum), on top of the adopted baseline

## View `app`: baseline vs baseline + candidates (3 folds, months 0-4)

### weekly_recall (decides)

| variant    |   n_features |   weekly_recall_pooled |   weekly_recall |   d_weekly_recall | d_weekly_recall_folds    | weekly_recall_verdict   |
|:-----------|-------------:|-----------------------:|----------------:|------------------:|:-------------------------|:------------------------|
| baseline   |           38 |                  0.403 |           0.409 |             0.000 | +0.000 / +0.000 / +0.000 |                         |
| +self4     |           41 |                  0.437 |           0.438 |             0.030 | +0.030 / +0.037 / +0.022 | better                  |
| +speed_cum |           40 |                  0.535 |           0.539 |             0.131 | +0.168 / +0.142 / +0.081 | better                  |
| +all       |           43 |                  0.536 |           0.544 |             0.135 | +0.169 / +0.150 / +0.087 | better                  |

### acc_pr_auc

| variant    |   n_features |   acc_pr_auc |   d_acc_pr_auc | d_acc_pr_auc_folds       | acc_pr_auc_verdict   |
|:-----------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline   |           38 |        0.871 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +self4     |           41 |        0.897 |          0.026 | +0.039 / +0.007 / +0.032 | no clear change      |
| +speed_cum |           40 |        0.886 |          0.015 | +0.030 / +0.007 / +0.007 | no clear change      |
| +all       |           43 |        0.899 |          0.027 | +0.038 / +0.020 / +0.024 | no clear change      |

### caught_2wk

| variant    |   n_features |   caught_2wk |   d_caught_2wk | d_caught_2wk_folds       | caught_2wk_verdict   |
|:-----------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline   |           38 |        0.899 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +self4     |           41 |        0.899 |          0.000 | +0.000 / +0.000 / +0.000 | no clear change      |
| +speed_cum |           40 |        0.879 |         -0.020 | -0.047 / +0.000 / -0.013 | no clear change      |
| +all       |           43 |        0.879 |         -0.020 | -0.047 / -0.014 / +0.000 | no clear change      |

### Where the gain comes from (no verdict)

| variant    |   pre_start_recall | d_pre_start_recall_folds   |   start_recall | d_start_recall_folds     |   later_recall | d_later_recall_folds     |   first_caught_2wk | d_first_caught_2wk_folds   |
|:-----------|-------------------:|:---------------------------|---------------:|:-------------------------|---------------:|:-------------------------|-------------------:|:---------------------------|
| baseline   |              0.136 | +0.000 / +0.000 / +0.000   |          0.781 | +0.000 / +0.000 / +0.000 |          0.603 | +0.000 / +0.000 / +0.000 |              0.957 | +0.000 / +0.000 / +0.000   |
| +self4     |              0.132 | +0.008 / -0.006 / -0.016   |          0.798 | +0.008 / +0.029 / +0.013 |          0.666 | +0.053 / +0.077 / +0.061 |              0.957 | +0.000 / +0.000 / +0.000   |
| +speed_cum |              0.122 | +0.031 / -0.044 / -0.029   |          0.771 | -0.031 / +0.014 / -0.013 |          0.892 | +0.337 / +0.328 / +0.203 |              0.947 | +0.000 / -0.029 / +0.000   |
| +all       |              0.123 | +0.019 / -0.039 / -0.020   |          0.783 | -0.016 / +0.014 / +0.007 |          0.900 | +0.347 / +0.340 / +0.206 |              0.936 | -0.047 / -0.014 / +0.000   |

Share of mule weeks in the weekly top 1%, by weeks since the account's laundering start: pre_start (fake accounts before they launder), start (start week and the next), later (2+ weeks after). first_caught_2wk: as caught_2wk, but a flag is permanent (decision 9 Oct 2026), so a mule flagged earlier counts as caught and later re-flags count for nothing.

- weekly_recall: share of each week's mules in that week's top 1% of open accounts, mean over weeks 0-26 (the tuning measure, decision 26 Oct 2026). `weekly_recall_pooled` pools the 3 validation months per week, as notebook 06 reports it; the per-fold column and the verdict use each fold alone.
- acc_pr_auc: account-level PR-AUC (an account's best week). caught_2wk: launderers starting in weeks 0-25 flagged in their start week or the next.
- verdict 'better' = all 3 folds improve and the mean gain is at least the noise level: weekly_recall 0.02, acc_pr_auc 0.04, caught_2wk 0.05 (PR-AUC: team rule; the others: assumptions).
- Real-customer mules in the account-level top 1% per fold (witting / unwitting) are in folds.csv.

## Screen: AUC vs started launderers (95% interval over launderers)

| feature           | week 8            | week 12           | week 26           |
|:------------------|:------------------|:------------------|:------------------|
| out_1h_share_cum  | 0.976 (0.96-0.99) | 0.961 (0.94-0.98) | 0.975 (0.96-0.98) |
| out_24h_share_cum | 0.923 (0.86-0.97) | 0.915 (0.89-0.94) | 0.919 (0.90-0.93) |
| self4_money_in    | 0.690 (0.55-0.81) | 0.848 (0.80-0.89) | 0.332 (0.30-0.37) |
| self4_money_out   | 0.671 (0.53-0.79) | 0.847 (0.81-0.89) | 0.362 (0.33-0.40) |
| self4_n_in        | 0.632 (0.52-0.73) | 0.839 (0.81-0.87) | 0.424 (0.39-0.46) |

