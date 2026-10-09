# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, laundering.out_transfer_mean=1500. Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| fake           |              7.5 |                 17.6 |                 2353 |                  1871 |          0.79 |
| normal         |             24.5 |                 60.9 |                 4238 |                  3278 |          0.78 |
| unwitting      |             21.9 |                 50.7 |                 3494 |                  2807 |          0.8  |
| witting        |             23.2 |                 51.7 |                 3237 |                  2701 |          0.79 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32850764 |     30.264 |          129.45 |
| Normal_DirectDebit     | 32090292 |     29.564 |           42.05 |
| Normal_Card            | 19274404 |     17.757 |          260.63 |
| Normal_CashWithdrawal  |  8777213 |      8.086 |          140    |
| Normal_Salary          |  6374769 |      5.873 |         1942.46 |
| Normal_TransferIn      |  4385224 |      4.04  |          100.04 |
| Normal_StandingOrder   |  3518452 |      3.241 |           54.17 |
| Normal_CashDeposit     |   525001 |      0.484 |          149.9  |
| Normal_Cheque          |   439991 |      0.405 |          100.16 |
| Normal_Abroad          |   153415 |      0.141 |          450.54 |
| Normal_Bonus           |   104147 |      0.096 |         1242.92 |
| Normal_GroupCollection |    40909 |      0.038 |           20.02 |
| Structuring            |     4399 |      0.004 |          819.71 |
| Deposit-Send           |     1419 |      0.001 |         1260.33 |
| Normal_LargeCash       |      779 |      0.001 |        14753.6  |
| Cash_Withdrawal        |      730 |      0.001 |          289.43 |
| Fan_In                 |      684 |      0.001 |         1674.15 |
| Layered_Fan_In         |      667 |      0.001 |         2035.13 |
| Behavioural_Change_1   |      614 |      0.001 |          537.64 |
| Behavioural_Change_2   |      568 |      0.001 |          686.88 |
| Layered_Fan_Out        |      500 |      0     |         1233.72 |
| Cycle                  |      449 |      0     |         3829.43 |
| Gather-Scatter         |      378 |      0     |         1774.85 |
| Fan_Out                |      306 |      0     |         1657.24 |
| Scatter-Gather         |      296 |      0     |         1590.54 |
| Stacked Bipartite      |      238 |      0     |         1608.84 |
| Smurfing               |      181 |      0     |          380.45 |
| Bipartite              |      145 |      0     |         1701.03 |

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
|               1 |         1.42 |            0.36 |          18.02 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |    total_in |
|:----------|------------:|-------------:|------------:|
| fake      |       12374 |         9815 | 7.47999e+06 |
| unwitting |       10822 |         8023 | 1.2295e+06  |
| witting   |       10492 |         7489 | 1.22296e+06 |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 3,947; true 574 -> false alarm share 85.5% (target 90-95%)
- Launderers alerted after their start: 552 of 732 (75%); accounts closed: 458

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      780 |             1 |
| R2     |      834 |            43 |
| R3     |      809 |             3 |
| R4     |     1583 |           486 |
| R5     |        8 |             0 |
| R6     |     1170 |            92 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      7 |          0 |        394 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   36.2 |                37 |             94 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          180 |       147 |      123 |
| Deposit-Send         |          114 |        91 |       74 |
| Layered_Fan_In       |           53 |        42 |       37 |
| Fan_In               |           50 |        44 |       35 |
| Behavioural_Change_1 |           49 |        19 |       19 |
| Behavioural_Change_2 |           47 |        27 |       24 |
| Layered_Fan_Out      |           39 |        24 |       21 |
| Gather-Scatter       |           37 |        30 |       24 |
| Cycle                |           36 |        30 |       25 |
| Stacked Bipartite    |           29 |        16 |       11 |
| Scatter-Gather       |           28 |        23 |       19 |
| Fan_Out              |           26 |        23 |       18 |
| Cash_Withdrawal      |           20 |        18 |       15 |
| Bipartite            |           14 |        11 |        9 |
| Smurfing             |           10 |         7 |        4 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.862 (average precision 0.514, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.237, money_in 0.351, money_out 0.335, max_in 0.723, n_senders 0.295, share_abroad 0.547, n_internal 0.313, spike 0.491
