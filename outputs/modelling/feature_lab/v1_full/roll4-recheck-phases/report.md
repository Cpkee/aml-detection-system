# Feature lab: roll4-recheck-phases

data `v1_full`, groups roll4, views app, seed 42, commit bf43eac-dirty

Hypothesis: Re-check the adopted 4-week windows: is the weekly-recall gain earlier catching or re-flagging mules already found?

## View `app`: baseline vs baseline + candidates (3 folds, months 0-4)

### weekly_recall (decides)

| variant   |   n_features |   weekly_recall_pooled |   weekly_recall |   d_weekly_recall | d_weekly_recall_folds    | weekly_recall_verdict   |
|:----------|-------------:|-----------------------:|----------------:|------------------:|:-------------------------|:------------------------|
| baseline  |           30 |                  0.345 |           0.351 |             0.000 | +0.000 / +0.000 / +0.000 |                         |
| +roll4    |           38 |                  0.403 |           0.409 |             0.058 | +0.073 / +0.041 / +0.059 | better                  |

### acc_pr_auc

| variant   |   n_features |   acc_pr_auc |   d_acc_pr_auc | d_acc_pr_auc_folds       | acc_pr_auc_verdict   |
|:----------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline  |           30 |        0.695 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +roll4    |           38 |        0.871 |          0.177 | +0.267 / +0.223 / +0.040 | better               |

### caught_2wk

| variant   |   n_features |   caught_2wk |   d_caught_2wk | d_caught_2wk_folds       | caught_2wk_verdict   |
|:----------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline  |           30 |        0.884 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +roll4    |           38 |        0.899 |          0.016 | +0.078 / -0.057 / +0.027 | no clear change      |

### Where the gain comes from (no verdict)

| variant   |   pre_start_recall | d_pre_start_recall_folds   |   start_recall | d_start_recall_folds     |   later_recall | d_later_recall_folds     |   first_caught_2wk | d_first_caught_2wk_folds   |
|:----------|-------------------:|:---------------------------|---------------:|:-------------------------|---------------:|:-------------------------|-------------------:|:---------------------------|
| baseline  |              0.140 | +0.000 / +0.000 / +0.000   |          0.703 | +0.000 / +0.000 / +0.000 |          0.488 | +0.000 / +0.000 / +0.000 |              0.958 | +0.000 / +0.000 / +0.000   |
| +roll4    |              0.136 | +0.001 / -0.020 / +0.007   |          0.781 | +0.173 / +0.007 / +0.053 |          0.603 | +0.129 / +0.102 / +0.114 |              0.957 | -0.016 / -0.014 / +0.027   |

Share of mule weeks in the weekly top 1%, by weeks since the account's laundering start: pre_start (fake accounts before they launder), start (start week and the next), later (2+ weeks after). first_caught_2wk: as caught_2wk, but a flag is permanent (decision 9 Oct 2026), so a mule flagged earlier counts as caught and later re-flags count for nothing.

- weekly_recall: share of each week's mules in that week's top 1% of open accounts, mean over weeks 0-26 (the tuning measure, decision 26 Oct 2026). `weekly_recall_pooled` pools the 3 validation months per week, as notebook 06 reports it; the per-fold column and the verdict use each fold alone.
- acc_pr_auc: account-level PR-AUC (an account's best week). caught_2wk: launderers starting in weeks 0-25 flagged in their start week or the next.
- verdict 'better' = all 3 folds improve and the mean gain is at least the noise level: weekly_recall 0.02, acc_pr_auc 0.04, caught_2wk 0.05 (PR-AUC: team rule; the others: assumptions).
- Real-customer mules in the account-level top 1% per fold (witting / unwitting) are in folds.csv.

## Screen: AUC vs started launderers (95% interval over launderers)

| feature           | week 8            | week 12           | week 26           |
|:------------------|:------------------|:------------------|:------------------|
| money_in_4wk      | 0.714 (0.61-0.80) | 0.830 (0.80-0.86) | 0.596 (0.56-0.63) |
| money_out_4wk     | 0.758 (0.66-0.84) | 0.855 (0.82-0.89) | 0.595 (0.56-0.63) |
| n_in_4wk          | 0.842 (0.77-0.90) | 0.886 (0.86-0.91) | 0.590 (0.56-0.62) |
| n_payers_4wk      | 0.811 (0.73-0.88) | 0.830 (0.80-0.86) | 0.572 (0.54-0.60) |
| n_rows_4wk        | 0.822 (0.73-0.90) | 0.880 (0.85-0.91) | 0.566 (0.53-0.60) |
| out_1h_share_4wk  | 0.901 (0.83-0.96) | 0.934 (0.91-0.96) | 0.572 (0.55-0.60) |
| out_24h_share_4wk | 0.882 (0.82-0.93) | 0.908 (0.88-0.93) | 0.585 (0.55-0.62) |
| passthrough_4wk   | 0.602 (0.52-0.68) | 0.541 (0.51-0.58) | 0.484 (0.45-0.52) |

