# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, timing.bursts_per_launderer="repeat_until_closed". Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             24.5 |                 64.7 |                 5311 |                  3889 |          0.74 |
| fake           |             14.4 |                 30.5 |                 3098 |                  2424 |          0.78 |
| normal         |             24.5 |                 60.9 |                 4238 |                  3278 |          0.78 |
| unwitting      |             25   |                 56.2 |                 4001 |                  3193 |          0.78 |
| witting        |             26   |                 54.8 |                 3763 |                  2936 |          0.78 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32857484 |     30.253 |          129.45 |
| Normal_DirectDebit     | 32096390 |     29.553 |           42.05 |
| Normal_Card            | 19277651 |     17.75  |          260.63 |
| Normal_CashWithdrawal  |  8778831 |      8.083 |          140    |
| Normal_Salary          |  6375672 |      5.87  |         1942.51 |
| Normal_TransferIn      |  4385957 |      4.038 |          100.04 |
| Normal_StandingOrder   |  3519007 |      3.24  |           54.17 |
| Normal_CashDeposit     |   525080 |      0.483 |          149.89 |
| Normal_Cheque          |   440054 |      0.405 |          100.17 |
| Normal_Abroad          |   153485 |      0.141 |          450.54 |
| Normal_Bonus           |   104160 |      0.096 |         1242.51 |
| Normal_GroupCollection |    40912 |      0.038 |           20.02 |
| Structuring            |    23086 |      0.021 |          291.64 |
| Deposit-Send           |     4448 |      0.004 |          443.66 |
| Behavioural_Change_1   |     4254 |      0.004 |          211.58 |
| Layered_Fan_Out        |     3889 |      0.004 |          471.7  |
| Behavioural_Change_2   |     3711 |      0.003 |          240.05 |
| Fan_In                 |     2076 |      0.002 |          569.21 |
| Gather-Scatter         |     1623 |      0.001 |          574.9  |
| Bipartite              |     1553 |      0.001 |          601.4  |
| Layered_Fan_In         |     1468 |      0.001 |          724.98 |
| Smurfing               |     1347 |      0.001 |          157.03 |
| Stacked Bipartite      |     1170 |      0.001 |          598.13 |
| Scatter-Gather         |     1152 |      0.001 |          538.96 |
| Cash_Withdrawal        |      796 |      0.001 |          276.2  |
| Fan_Out                |      789 |      0.001 |          583.44 |
| Normal_LargeCash       |      779 |      0.001 |        14753.6  |
| Cycle                  |      608 |      0.001 |         1537.38 |

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
|               1 |         1.78 |            0.52 |          15.94 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |    total_in |
|:----------|------------:|-------------:|------------:|
| fake      |       17641 |        14001 | 1.1693e+07  |
| unwitting |       13142 |         8385 | 1.58267e+06 |
| witting   |       12449 |         8632 | 1.55006e+06 |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 4,010; true 637 -> false alarm share 84.1% (target 90-95%)
- Launderers alerted after their start: 558 of 732 (76%); accounts closed: 522

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      779 |             0 |
| R2     |      856 |            65 |
| R3     |      820 |            14 |
| R4     |     1663 |           566 |
| R5     |        8 |             0 |
| R6     |     1090 |            12 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                     60 |          0 |        451 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   36.8 |                38 |             96 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          188 |       142 |      130 |
| Deposit-Send         |          108 |        98 |       96 |
| Layered_Fan_Out      |           65 |        44 |       39 |
| Behavioural_Change_1 |           45 |         9 |        7 |
| Layered_Fan_In       |           45 |        39 |       36 |
| Behavioural_Change_2 |           44 |        13 |       12 |
| Fan_In               |           42 |        37 |       36 |
| Gather-Scatter       |           36 |        31 |       27 |
| Bipartite            |           33 |        31 |       31 |
| Stacked Bipartite    |           33 |        28 |       28 |
| Fan_Out              |           24 |        23 |       23 |
| Scatter-Gather       |           24 |        22 |       22 |
| Cycle                |           22 |        19 |       17 |
| Cash_Withdrawal      |           12 |        12 |       11 |
| Smurfing             |           11 |        10 |        7 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.877 (average precision 0.696, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.358, money_in 0.435, money_out 0.417, max_in 0.599, n_senders 0.508, share_abroad 0.648, n_internal 0.530, spike 0.263
