# Weekly feature store: Phase 3 gate

data data/v1_full -> report outputs/modelling/features; EDA screen outputs/modelling/eda/feature_screen.csv
## 1. Store

19,276,000 account-weeks = 244,000 accounts x 79 weeks; 28 features; code f8777d2; cut-off rule: rows with day <= open_day + 7*w + 6 (end of each account's week w, as amldata.labels)

Share of account-weeks where a feature is undefined (e.g. no money in that week, fewer than 4 earlier weeks):

|                       |   share_null |
|:----------------------|-------------:|
| new_payer_share_wk    |       0.4643 |
| passthrough_wk        |       0.4542 |
| out_1h_share_wk       |       0.4542 |
| out_24h_share_wk      |       0.4542 |
| med_in_out_minutes_wk |       0.0126 |
| self_vs_past_money_in |       0.6547 |
| self_vs_past_payers   |       0.7255 |
| self_vs_past_rows     |       0.0577 |
| peer_ratio_money_in   |       0.0163 |
| cash_in_share_cum     |       0.0103 |

## 2. Gate: Phase 1 screen reproduced

(A) EDA query rerun vs published screen (64 AUCs, mule_by_day): max |difference| 5.6e-17 for count features, 1.4e-06 for the eight float-sum money features
(B) store vs EDA panel, value by value over 4,450,113 account-weeks (months 0-4, weeks 0-26):

| feature               | eda_name            |   account_weeks | null_pattern_equal   |   max_rel_diff |
|:----------------------|:--------------------|----------------:|:---------------------|---------------:|
| n_rows_wk             | n_rows              |         4450113 | True                 |        0.0e+00 |
| money_in_wk           | money_in            |         4450113 | True                 |        4.2e-16 |
| money_out_wk          | money_out           |         4450113 | True                 |        4.7e-16 |
| max_in_wk             | max_in              |         4450113 | True                 |        0.0e+00 |
| n_payers_wk           | n_payers            |         4450113 | True                 |        0.0e+00 |
| n_payees_wk           | n_payees            |         4450113 | True                 |        0.0e+00 |
| new_payer_share_wk    | new_payer_share     |         4450113 | True                 |        0.0e+00 |
| passthrough_wk        | passthrough_wk      |         4450113 | True                 |        4.4e-16 |
| out_1h_share_wk       | out_1h_share        |         4450113 | True                 |        3.9e-16 |
| out_24h_share_wk      | out_24h_share       |         4450113 | True                 |        5.5e-16 |
| med_in_out_minutes_wk | med_delay_min       |         4450113 | True                 |        0.0e+00 |
| money_in_cum          | money_in_cum        |         4450113 | True                 |        8.1e-16 |
| n_rows_cum            | n_rows_cum          |         4450113 | True                 |        0.0e+00 |
| self_vs_past_money_in | self_vs_past_in     |         4450113 | True                 |        8.2e-14 |
| self_vs_past_payers   | self_vs_past_payers |         4450113 | True                 |        0.0e+00 |
| peer_ratio_money_in   | peer_ratio_in       |         4450113 | True                 |        4.4e-16 |

Store AUC vs published AUC: max |difference| 1.6e-05 (largest for self_vs_past_money_in, week 8); differences come only from float ties, since (B) shows the values agree.

GATE PASSED: (A) and (B) hold for all 16 shared features.

## 3. First-laundering-week signal

361 launderers start inside weeks 0-26 (of 455 training launderers); 540,000 normal account-weeks from 20,000 normal accounts.

AUC of each feature, first laundering week vs normal account-weeks, 95% account-level bootstrap interval:

| feature                 |   auc |   ci_low |   ci_high | excludes_0.5   |
|:------------------------|------:|---------:|----------:|:---------------|
| out_1h_share_wk         | 0.954 |    0.944 |     0.964 | True           |
| n_in_wk                 | 0.915 |    0.904 |     0.927 | True           |
| out_24h_share_wk        | 0.907 |    0.900 |     0.914 | True           |
| n_rows_wk               | 0.906 |    0.889 |     0.922 | True           |
| money_out_wk            | 0.903 |    0.885 |     0.921 | True           |
| self_vs_past_rows       | 0.877 |    0.853 |     0.898 | True           |
| n_payers_wk             | 0.853 |    0.835 |     0.872 | True           |
| max_out_wk              | 0.848 |    0.828 |     0.868 | True           |
| money_in_wk             | 0.839 |    0.829 |     0.849 | True           |
| peer_ratio_money_in     | 0.825 |    0.812 |     0.837 | True           |
| new_payer_share_wk      | 0.819 |    0.805 |     0.832 | True           |
| med_in_out_minutes_wk   | 0.183 |    0.159 |     0.205 | True           |
| n_out_wk                | 0.809 |    0.785 |     0.834 | True           |
| passthrough_wk          | 0.795 |    0.783 |     0.806 | True           |
| max_in_wk               | 0.791 |    0.781 |     0.802 | True           |
| n_payees_wk             | 0.700 |    0.673 |     0.728 | True           |
| n_payers_cum            | 0.643 |    0.621 |     0.663 | True           |
| money_in_cum            | 0.635 |    0.614 |     0.657 | True           |
| money_out_cum           | 0.626 |    0.604 |     0.648 | True           |
| internal_out_share_cum  | 0.595 |    0.562 |     0.628 | True           |
| cash_in_share_cum       | 0.564 |    0.546 |     0.582 | True           |
| self_vs_past_money_in   | 0.546 |    0.516 |     0.579 | True           |
| card_items_wk           | 0.535 |    0.507 |     0.566 | True           |
| n_rows_cum              | 0.520 |    0.506 |     0.535 | True           |
| self_vs_past_payers     | 0.518 |    0.492 |     0.544 | False          |
| n_payees_cum            | 0.516 |    0.499 |     0.533 | False          |
| abroad_out_share_cum    | 0.512 |    0.499 |     0.526 | False          |
| high_risk_out_share_cum | 0.509 |    0.501 |     0.518 | True           |

25 of 28 features have an interval that excludes 0.5 (no signal).

Speed shares, kept vs dropped definition (same account-weeks, 95% account-level bootstrap):

| feature          | definition                      |   auc |   ci_low |   ci_high |   mean_first_week |   mean_normal_week |
|:-----------------|:--------------------------------|------:|---------:|----------:|------------------:|-------------------:|
| out_1h_share_wk  | kept: EDA (any payment)         | 0.954 |    0.944 |     0.964 |             0.404 |              0.031 |
| tried_1h         | dropped: transfers only, capped | 0.919 |    0.902 |     0.936 |             0.366 |              0.007 |
| out_24h_share_wk | kept: EDA (any payment)         | 0.907 |    0.900 |     0.913 |             0.731 |              0.588 |
| tried_24h        | dropped: transfers only, capped | 0.909 |    0.895 |     0.923 |             0.544 |              0.109 |

Paired bootstrap of the AUC difference, kept minus dropped (same resampled accounts for both):

| comparison                   |   auc_gain |   ci_low |   ci_high |   share_of_replicates_kept_better |
|:-----------------------------|-----------:|---------:|----------:|----------------------------------:|
| out_1h_share_wk - tried_1h   |      0.035 |    0.021 |     0.050 |                             1.000 |
| out_24h_share_wk - tried_24h |     -0.002 |   -0.016 |     0.012 |                             0.368 |
- out_1h_share_wk - tried_1h: kept better (difference +0.035, 95% interval +0.021 to +0.050)
- out_24h_share_wk - tried_24h: no clear difference (difference -0.002, 95% interval -0.016 to +0.012)

## 4. Consistency checks

- PASS: keys unique and complete
- PASS: shares inside [0, 1]
- PASS: speed shares: 0 <= 1 h <= 24 h
- PASS: running totals never fall
- PASS: week-78 totals equal the transactions file

done in 186s
