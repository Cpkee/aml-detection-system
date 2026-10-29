# Feature lab: max-out-vs-hist

data `v1`, groups max_out_hist, views app, seed 42, commit 46e3d35-dirty

Hypothesis: [r01-2] In the start week a mule's largest payment out is bigger than anything the account paid out before (laundering pieces sized from GBP 532 x shape amount_rel, not from income), which holds for real customers with long normal histories; the store has max_out_wk only in absolute terms, so the account's own past is unused

## View `app`: baseline vs baseline + candidates (3 folds, months 0-4)

### weekly_recall (decides)

| variant       |   n_features |   weekly_recall_pooled |   weekly_recall |   d_weekly_recall | d_weekly_recall_folds    | weekly_recall_verdict   |
|:--------------|-------------:|-----------------------:|----------------:|------------------:|:-------------------------|:------------------------|
| baseline      |           38 |                  0.300 |           0.314 |             0.000 | +0.000 / +0.000 / +0.000 |                         |
| +max_out_hist |           39 |                  0.330 |           0.339 |             0.025 | +0.000 / +0.049 / +0.025 | better                  |

### acc_pr_auc

| variant       |   n_features |   acc_pr_auc |   d_acc_pr_auc | d_acc_pr_auc_folds       | acc_pr_auc_verdict   |
|:--------------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline      |           38 |        0.731 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +max_out_hist |           39 |        0.757 |          0.026 | +0.037 / +0.046 / -0.004 | no clear change      |

### caught_2wk

| variant       |   n_features |   caught_2wk |   d_caught_2wk | d_caught_2wk_folds       | caught_2wk_verdict   |
|:--------------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline      |           38 |        0.866 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +max_out_hist |           39 |        0.905 |          0.039 | +0.118 / +0.000 / +0.000 | no clear change      |

### Where the gain comes from (no verdict)

| variant       |   pre_start_recall | d_pre_start_recall_folds   |   start_recall | d_start_recall_folds     |   later_recall | d_later_recall_folds     |   first_caught_2wk | d_first_caught_2wk_folds   |
|:--------------|-------------------:|:---------------------------|---------------:|:-------------------------|---------------:|:-------------------------|-------------------:|:---------------------------|
| baseline      |              0.073 | +0.000 / +0.000 / +0.000   |          0.706 | +0.000 / +0.000 / +0.000 |          0.474 | +0.000 / +0.000 / +0.000 |              0.943 | +0.000 / +0.000 / +0.000   |
| +max_out_hist |              0.080 | -0.035 / +0.056 / +0.000   |          0.734 | +0.029 / +0.056 / +0.000 |          0.513 | +0.026 / +0.040 / +0.050 |              1.000 | +0.059 / +0.111 / +0.000   |

Share of mule weeks in the weekly top 1%, by weeks since the account's laundering start: pre_start (fake accounts before they launder), start (start week and the next), later (2+ weeks after). first_caught_2wk: as caught_2wk, but a flag is permanent (decision 9 Oct 2026), so a mule flagged earlier counts as caught and later re-flags count for nothing.

- weekly_recall: share of each week's mules in that week's top 1% of open accounts, mean over weeks 0-26 (the tuning measure, decision 26 Oct 2026). `weekly_recall_pooled` pools the 3 validation months per week, as notebook 06 reports it; the per-fold column and the verdict use each fold alone.
- acc_pr_auc: account-level PR-AUC (an account's best week). caught_2wk: launderers starting in weeks 0-25 flagged in their start week or the next.
- verdict 'better' = all 3 folds improve and the mean gain is at least the noise level: weekly_recall 0.02, acc_pr_auc 0.04, caught_2wk 0.05 (PR-AUC: team rule; the others: assumptions).
- Real-customer mules in the account-level top 1% per fold (witting / unwitting) are in folds.csv.

## Screen: AUC vs started launderers (95% interval over launderers)

| feature         | week 8        | week 12           | week 26           |
|:----------------|:--------------|:------------------|:------------------|
| max_out_vs_hist | nan (nan-nan) | 0.471 (0.36-0.57) | 0.309 (0.23-0.38) |

