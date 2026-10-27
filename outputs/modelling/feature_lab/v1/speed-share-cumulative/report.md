# Feature lab: speed-share-cumulative

data `v1`, groups speed_cum, views app, seed 42, commit bf43eac-dirty

Hypothesis: Mules forward money at RUSI speed (53% within 1 h, 85% within 24 h) and stay mules after their ~2-week burst, but the weekly and 4-week speed shares fall back once the burst ends (screen AUC ~0.57 at week 26) and running_max kept normal accounts' one-off fast weeks forever (hurt PR-AUC and caught_2wk); the share of all money in so far paid out within 1 h / 24 h keeps the burst visible while diluting one-off coincidences (rests on laundering.forward_delay_shares vs normal accounts with no in->out link)

## View `app`: baseline vs baseline + candidates (3 folds, months 0-4)

### weekly_recall (decides)

| variant    |   n_features |   weekly_recall_pooled |   weekly_recall |   d_weekly_recall | d_weekly_recall_folds    | weekly_recall_verdict   |
|:-----------|-------------:|-----------------------:|----------------:|------------------:|:-------------------------|:------------------------|
| baseline   |           38 |                  0.300 |           0.314 |             0.000 | +0.000 / +0.000 / +0.000 |                         |
| +speed_cum |           40 |                  0.546 |           0.565 |             0.251 | +0.234 / +0.291 / +0.226 | better                  |

### acc_pr_auc

| variant    |   n_features |   acc_pr_auc |   d_acc_pr_auc | d_acc_pr_auc_folds       | acc_pr_auc_verdict   |
|:-----------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline   |           38 |        0.731 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +speed_cum |           40 |        0.921 |          0.190 | +0.265 / +0.174 / +0.131 | better               |

### caught_2wk

| variant    |   n_features |   caught_2wk |   d_caught_2wk | d_caught_2wk_folds       | caught_2wk_verdict   |
|:-----------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline   |           38 |        0.866 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +speed_cum |           40 |        0.925 |          0.059 | +0.176 / +0.000 / +0.000 | no clear change      |

- weekly_recall: share of each week's mules in that week's top 1% of open accounts, mean over weeks 0-26 (the tuning measure, decision 26 Oct 2026). `weekly_recall_pooled` pools the 3 validation months per week, as notebook 06 reports it; the per-fold column and the verdict use each fold alone.
- acc_pr_auc: account-level PR-AUC (an account's best week). caught_2wk: launderers starting in weeks 0-25 flagged in their start week or the next.
- verdict 'better' = all 3 folds improve and the mean gain is at least the noise level: weekly_recall 0.02, acc_pr_auc 0.04, caught_2wk 0.05 (PR-AUC: team rule; the others: assumptions).
- Real-customer mules in the account-level top 1% per fold (witting / unwitting) are in folds.csv.

## Screen: AUC vs started launderers (95% interval over launderers)

| feature           | week 8        | week 12           | week 26           |
|:------------------|:--------------|:------------------|:------------------|
| out_1h_share_cum  | nan (nan-nan) | 0.952 (0.90-0.99) | 0.995 (0.99-1.00) |
| out_24h_share_cum | nan (nan-nan) | 0.943 (0.92-0.96) | 0.950 (0.93-0.96) |

