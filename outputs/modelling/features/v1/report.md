# Weekly feature store: Phase 3 gate

data data/v1 -> report outputs/modelling/features/v1; EDA screen outputs/modelling/eda/v1_50k/feature_screen.csv
## 1. Store

3,950,000 account-weeks = 50,000 accounts x 79 weeks; 28 features; code f8777d2; cut-off rule: rows with day <= open_day + 7*w + 6 (end of each account's week w, as amldata.labels)

Share of account-weeks where a feature is undefined (e.g. no money in that week, fewer than 4 earlier weeks):

|                         |   share_null |
|:------------------------|-------------:|
| new_payer_share_wk      |       0.4643 |
| passthrough_wk          |       0.4539 |
| out_1h_share_wk         |       0.4539 |
| out_24h_share_wk        |       0.4539 |
| med_in_out_minutes_wk   |       0.0126 |
| self_vs_past_money_in   |       0.649  |
| self_vs_past_payers     |       0.7216 |
| self_vs_past_rows       |       0.0575 |
| peer_ratio_money_in     |       0.0319 |
| internal_out_share_cum  |       0      |
| cash_in_share_cum       |       0.0104 |
| abroad_out_share_cum    |       0      |
| high_risk_out_share_cum |       0      |

## 2. Gate: Phase 1 screen reproduced

(A) EDA query rerun vs published screen (64 AUCs, mule_by_day): max |difference| 5.6e-17 for count features, 8.2e-07 for the eight float-sum money features
(B) store vs EDA panel, value by value over 912,627 account-weeks (months 0-4, weeks 0-26):

| feature               | eda_name            |   account_weeks | null_pattern_equal   |   max_rel_diff |
|:----------------------|:--------------------|----------------:|:---------------------|---------------:|
| n_rows_wk             | n_rows              |          912627 | True                 |        0.0e+00 |
| money_in_wk           | money_in            |          912627 | True                 |        3.6e-16 |
| money_out_wk          | money_out           |          912627 | True                 |        5.0e-16 |
| max_in_wk             | max_in              |          912627 | True                 |        0.0e+00 |
| n_payers_wk           | n_payers            |          912627 | True                 |        0.0e+00 |
| n_payees_wk           | n_payees            |          912627 | True                 |        0.0e+00 |
| new_payer_share_wk    | new_payer_share     |          912627 | True                 |        0.0e+00 |
| passthrough_wk        | passthrough_wk      |          912627 | True                 |        4.4e-16 |
| out_1h_share_wk       | out_1h_share        |          912627 | True                 |        3.8e-16 |
| out_24h_share_wk      | out_24h_share       |          912627 | True                 |        5.0e-16 |
| med_in_out_minutes_wk | med_delay_min       |          912627 | True                 |        0.0e+00 |
| money_in_cum          | money_in_cum        |          912627 | True                 |        8.9e-16 |
| n_rows_cum            | n_rows_cum          |          912627 | True                 |        0.0e+00 |
| self_vs_past_money_in | self_vs_past_in     |          912627 | True                 |        8.0e-14 |
| self_vs_past_payers   | self_vs_past_payers |          912627 | True                 |        0.0e+00 |
| peer_ratio_money_in   | peer_ratio_in       |          912627 | True                 |        4.9e-16 |

Store AUC vs published AUC: max |difference| 1.5e-03 (largest for self_vs_past_money_in, week 4); differences come only from float ties, since (B) shows the values agree.

GATE PASSED: (A) and (B) hold for all 16 shared features.

## 3. First-laundering-week signal

77 launderers start inside weeks 0-26 (of 92 training launderers); 540,000 normal account-weeks from 20,000 normal accounts.

AUC of each feature, first laundering week vs normal account-weeks, 95% account-level bootstrap interval:

| feature                 |   auc |   ci_low |   ci_high | excludes_0.5   |
|:------------------------|------:|---------:|----------:|:---------------|
| out_1h_share_wk         | 0.956 |    0.934 |     0.975 | True           |
| n_in_wk                 | 0.906 |    0.874 |     0.933 | True           |
| money_out_wk            | 0.904 |    0.863 |     0.937 | True           |
| out_24h_share_wk        | 0.901 |    0.884 |     0.915 | True           |
| self_vs_past_rows       | 0.883 |    0.838 |     0.924 | True           |
| n_rows_wk               | 0.877 |    0.821 |     0.920 | True           |
| n_payers_wk             | 0.863 |    0.818 |     0.905 | True           |
| peer_ratio_money_in     | 0.850 |    0.824 |     0.874 | True           |
| money_in_wk             | 0.843 |    0.817 |     0.869 | True           |
| max_out_wk              | 0.833 |    0.786 |     0.876 | True           |
| max_in_wk               | 0.800 |    0.775 |     0.825 | True           |
| n_out_wk                | 0.794 |    0.730 |     0.850 | True           |
| new_payer_share_wk      | 0.794 |    0.762 |     0.822 | True           |
| passthrough_wk          | 0.780 |    0.754 |     0.806 | True           |
| med_in_out_minutes_wk   | 0.250 |    0.182 |     0.324 | True           |
| n_payees_wk             | 0.712 |    0.649 |     0.766 | True           |
| n_payers_cum            | 0.675 |    0.626 |     0.723 | True           |
| money_in_cum            | 0.641 |    0.594 |     0.685 | True           |
| internal_out_share_cum  | 0.634 |    0.572 |     0.703 | True           |
| money_out_cum           | 0.630 |    0.587 |     0.670 | True           |
| self_vs_past_money_in   | 0.587 |    0.522 |     0.656 | True           |
| cash_in_share_cum       | 0.579 |    0.539 |     0.626 | True           |
| card_items_wk           | 0.572 |    0.513 |     0.628 | True           |
| self_vs_past_payers     | 0.545 |    0.488 |     0.608 | False          |
| abroad_out_share_cum    | 0.533 |    0.500 |     0.573 | False          |
| n_rows_cum              | 0.516 |    0.486 |     0.550 | False          |
| high_risk_out_share_cum | 0.506 |    0.492 |     0.526 | False          |
| n_payees_cum            | 0.504 |    0.470 |     0.542 | False          |

23 of 28 features have an interval that excludes 0.5 (no signal).

Speed shares, kept vs dropped definition (same account-weeks, 95% account-level bootstrap):

| feature          | definition                      |   auc |   ci_low |   ci_high |   mean_first_week |   mean_normal_week |
|:-----------------|:--------------------------------|------:|---------:|----------:|------------------:|-------------------:|
| out_1h_share_wk  | kept: EDA (any payment)         | 0.956 |    0.934 |     0.976 |             0.380 |              0.033 |
| tried_1h         | dropped: transfers only, capped | 0.924 |    0.886 |     0.959 |             0.350 |              0.006 |
| out_24h_share_wk | kept: EDA (any payment)         | 0.901 |    0.885 |     0.914 |             0.696 |              0.588 |
| tried_24h        | dropped: transfers only, capped | 0.899 |    0.865 |     0.930 |             0.500 |              0.111 |

Paired bootstrap of the AUC difference, kept minus dropped (same resampled accounts for both):

| comparison                   |   auc_gain |   ci_low |   ci_high |   share_of_replicates_kept_better |
|:-----------------------------|-----------:|---------:|----------:|----------------------------------:|
| out_1h_share_wk - tried_1h   |      0.032 |    0.005 |     0.064 |                             0.987 |
| out_24h_share_wk - tried_24h |      0.002 |   -0.026 |     0.035 |                             0.508 |
- out_1h_share_wk - tried_1h: kept better (difference +0.032, 95% interval +0.005 to +0.064)
- out_24h_share_wk - tried_24h: no clear difference (difference +0.002, 95% interval -0.026 to +0.035)

## 4. Consistency checks

- PASS: keys unique and complete
- PASS: shares inside [0, 1]
- PASS: speed shares: 0 <= 1 h <= 24 h
- PASS: running totals never fall
- PASS: week-78 totals equal the transactions file

done in 139s
