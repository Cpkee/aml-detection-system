# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.741, normal.bonus_share=0.15. Code: bb5b24e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

## Accounts by profile

| profile        |      n |   fraud_rows |
|:---------------|-------:|-------------:|
| normal         | 241048 |            0 |
| app_fraud_only |   2220 |         2220 |
| fake           |    537 |          537 |
| witting        |     98 |            0 |
| unwitting      |     97 |            0 |

## Activity per account (medians)

| profile        |   rows_per_month |   payments_per_month |   money_in_per_month |   money_out_per_month |   out_over_in |
|:---------------|-----------------:|---------------------:|---------------------:|----------------------:|--------------:|
| app_fraud_only |             24.5 |                 64.4 |                 5303 |                  3891 |          0.74 |
| fake           |             24.4 |                 61.8 |                 4835 |                  3647 |          0.76 |
| normal         |             24.5 |                 60.9 |                 4216 |                  3281 |          0.78 |
| unwitting      |             24.3 |                 59.6 |                 3872 |                  3010 |          0.81 |
| witting        |             24.5 |                 56.4 |                 3292 |                  2760 |          0.82 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32902516 |     30.29  |          129.47 |
| Normal_DirectDebit     | 32127573 |     29.577 |           42.07 |
| Normal_Card            | 19292384 |     17.761 |          260.57 |
| Normal_CashWithdrawal  |  8781918 |      8.085 |          140    |
| Normal_Salary          |  6380458 |      5.874 |         1942.65 |
| Normal_TransferIn      |  4391571 |      4.043 |          100.05 |
| Normal_StandingOrder   |  3518076 |      3.239 |           54.24 |
| Normal_CashDeposit     |   525787 |      0.484 |          149.92 |
| Normal_Cheque          |   439905 |      0.405 |           99.96 |
| Normal_Abroad          |   154478 |      0.142 |          448.98 |
| Normal_Bonus           |    52412 |      0.048 |         1237.72 |
| Normal_GroupCollection |    41898 |      0.039 |           19.87 |
| Structuring            |     5580 |      0.005 |          285.03 |
| Deposit-Send           |     1654 |      0.002 |          410.9  |
| Layered_Fan_Out        |      955 |      0.001 |          415.76 |
| Layered_Fan_In         |      839 |      0.001 |          707.49 |
| Normal_LargeCash       |      771 |      0.001 |        14956    |
| Cycle                  |      703 |      0.001 |         1436.55 |
| Behavioural_Change_1   |      630 |      0.001 |          203.15 |
| Gather-Scatter         |      582 |      0.001 |          542.39 |
| Behavioural_Change_2   |      566 |      0.001 |          228.87 |
| Fan_In                 |      451 |      0     |          557.51 |
| Fan_Out                |      402 |      0     |          661.17 |
| Scatter-Gather         |      376 |      0     |          505.16 |
| Cash_Withdrawal        |      325 |      0     |          270.87 |
| Bipartite              |      285 |      0     |          687.69 |
| Stacked Bipartite      |      276 |      0     |          479.95 |
| Smurfing               |      165 |      0     |          141.66 |

## Laundering start (days after opening)

| profile   |   n |   min_rel |   median_rel |   max_rel |   pct_year1 |
|:----------|----:|----------:|-------------:|----------:|------------:|
| fake      | 537 |        60 |           92 |       120 |       100   |
| unwitting |  97 |        10 |          299 |       521 |        58.8 |
| witting   |  98 |         1 |          297 |       526 |        61.2 |

## Launderer networks

| net         |   n |
|:------------|----:|
| big network | 183 |
| chain       | 549 |

## Outgoing rows: abroad, high-risk, internal (%)

|   is_laundering |   pct_abroad |   pct_high_risk |   pct_internal |
|----------------:|-------------:|----------------:|---------------:|
|               0 |         0.16 |            0.03 |           2.75 |
|               1 |         1.36 |            0.48 |          24.7  |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5122 |         4605 |      3.09659e+06 |
| unwitting |        4419 |         3803 | 499711           |
| witting   |        4111 |         3868 | 486987           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 5,779; true 187 -> false alarm share 96.8% (target 90-95%)
- Launderers alerted after their start: 184 of 732 (25%); accounts closed: 150

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      771 |             3 |
| R2     |      803 |            17 |
| R3     |      334 |             1 |
| R4     |      644 |           169 |
| R5     |        1 |             0 |
| R6     |     4385 |            10 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                     10 |          0 |        436 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                     54 |                26 |            172 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        31 |       25 |
| Deposit-Send         |          111 |        30 |       26 |
| Behavioural_Change_1 |           50 |         3 |        2 |
| Layered_Fan_Out      |           50 |        13 |       13 |
| Layered_Fan_In       |           46 |        20 |       16 |
| Behavioural_Change_2 |           44 |         4 |        2 |
| Gather-Scatter       |           43 |        11 |       10 |
| Cycle                |           40 |        31 |       25 |
| Fan_In               |           33 |        10 |        7 |
| Scatter-Gather       |           27 |         3 |        3 |
| Fan_Out              |           25 |        11 |       10 |
| Bipartite            |           24 |         5 |        3 |
| Stacked Bipartite    |           22 |         2 |        2 |
| Cash_Withdrawal      |           18 |         8 |        6 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.757 (average precision 0.131, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.470, money_in 0.507, money_out 0.509, max_in 0.588, n_senders 0.576, share_abroad 0.554, n_internal 0.640, spike 0.477
