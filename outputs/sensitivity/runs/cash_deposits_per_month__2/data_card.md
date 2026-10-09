# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, normal.cash_deposits_per_month=4.0. Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             24.5 |                 64.8 |                 5335 |                  3884 |          0.74 |
| fake           |             24.3 |                 60.6 |                 4418 |                  3283 |          0.76 |
| normal         |             24.7 |                 61   |                 4258 |                  3279 |          0.78 |
| unwitting      |             24.6 |                 57.2 |                 3565 |                  2956 |          0.8  |
| witting        |             25.7 |                 57.2 |                 3641 |                  2837 |          0.78 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32880920 |     30.121 |          129.46 |
| Normal_DirectDebit     | 32116328 |     29.42  |           42.05 |
| Normal_Card            | 19289552 |     17.67  |          260.66 |
| Normal_CashWithdrawal  |  8784292 |      8.047 |          140    |
| Normal_Salary          |  6379704 |      5.844 |         1942.75 |
| Normal_TransferIn      |  4388667 |      4.02  |          100.04 |
| Normal_StandingOrder   |  3521096 |      3.226 |           54.18 |
| Normal_CashDeposit     |  1051587 |      0.963 |          150.06 |
| Normal_Cheque          |   440354 |      0.403 |          100.17 |
| Normal_Abroad          |   151407 |      0.139 |          449.7  |
| Normal_Bonus           |   104232 |      0.095 |         1243.07 |
| Normal_GroupCollection |    41381 |      0.038 |           19.98 |
| Structuring            |     5324 |      0.005 |          284.09 |
| Deposit-Send           |     1687 |      0.002 |          411.01 |
| Layered_Fan_Out        |      925 |      0.001 |          424.85 |
| Layered_Fan_In         |      794 |      0.001 |          715.49 |
| Normal_LargeCash       |      722 |      0.001 |        14707.6  |
| Cycle                  |      661 |      0.001 |         1436.55 |
| Behavioural_Change_1   |      627 |      0.001 |          205.27 |
| Behavioural_Change_2   |      563 |      0.001 |          227.71 |
| Gather-Scatter         |      544 |      0     |          568.51 |
| Fan_In                 |      439 |      0     |          565.09 |
| Fan_Out                |      390 |      0     |          678.69 |
| Scatter-Gather         |      376 |      0     |          505.16 |
| Cash_Withdrawal        |      325 |      0     |          270.87 |
| Bipartite              |      270 |      0     |          680.46 |
| Stacked Bipartite      |      240 |      0     |          465.5  |
| Smurfing               |      162 |      0     |          139.44 |

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
|               1 |         1.4  |            0.5  |          23.73 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        4914 |         4426 |      3.03023e+06 |
| unwitting |        4419 |         3512 | 492897           |
| witting   |        4085 |         3567 | 474111           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 15,646; true 255 -> false alarm share 98.4% (target 90-95%)
- Launderers alerted after their start: 251 of 732 (34%); accounts closed: 202

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      721 |             0 |
| R2     |    12780 |            29 |
| R3     |      886 |             6 |
| R4     |     1297 |           210 |
| R5     |        5 |             0 |
| R6     |     1033 |            23 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          0 |        412 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                  139.7 |              95.5 |            383 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        51 |       43 |
| Deposit-Send         |          111 |        42 |       37 |
| Behavioural_Change_1 |           50 |         7 |        4 |
| Layered_Fan_Out      |           50 |        16 |       15 |
| Layered_Fan_In       |           46 |        22 |       18 |
| Behavioural_Change_2 |           44 |         9 |        7 |
| Gather-Scatter       |           43 |        16 |       12 |
| Cycle                |           40 |        29 |       24 |
| Fan_In               |           33 |        12 |        6 |
| Scatter-Gather       |           27 |        12 |        9 |
| Fan_Out              |           25 |        14 |       12 |
| Bipartite            |           24 |         6 |        5 |
| Stacked Bipartite    |           22 |         2 |        2 |
| Cash_Withdrawal      |           18 |        10 |        8 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.768 (average precision 0.187, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.456, money_in 0.478, money_out 0.476, max_in 0.588, n_senders 0.535, share_abroad 0.549, n_internal 0.585, spike 0.470
