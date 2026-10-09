# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, normal.large_cash_yearly_rate=0.004. Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             24.5 |                 64.7 |                 5311 |                  3888 |          0.74 |
| fake           |             24.4 |                 60.4 |                 4409 |                  3375 |          0.77 |
| normal         |             24.5 |                 60.9 |                 4240 |                  3277 |          0.78 |
| unwitting      |             24.6 |                 57.2 |                 3565 |                  2956 |          0.81 |
| witting        |             25.8 |                 57.7 |                 3641 |                  2860 |          0.78 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32880985 |     30.266 |          129.46 |
| Normal_DirectDebit     | 32116403 |     29.562 |           42.05 |
| Normal_Card            | 19289615 |     17.756 |          260.66 |
| Normal_CashWithdrawal  |  8784302 |      8.086 |          140    |
| Normal_Salary          |  6379760 |      5.872 |         1942.72 |
| Normal_TransferIn      |  4388672 |      4.04  |          100.04 |
| Normal_StandingOrder   |  3521120 |      3.241 |           54.18 |
| Normal_CashDeposit     |   525570 |      0.484 |          149.89 |
| Normal_Cheque          |   440353 |      0.405 |          100.17 |
| Normal_Abroad          |   153311 |      0.141 |          450.54 |
| Normal_Bonus           |   104232 |      0.096 |         1243.07 |
| Normal_GroupCollection |    40816 |      0.038 |           20    |
| Structuring            |     5303 |      0.005 |          284.72 |
| Deposit-Send           |     1687 |      0.002 |          411.01 |
| Normal_LargeCash       |     1528 |      0.001 |        14866    |
| Layered_Fan_Out        |      925 |      0.001 |          424.85 |
| Layered_Fan_In         |      794 |      0.001 |          715.49 |
| Cycle                  |      661 |      0.001 |         1436.55 |
| Behavioural_Change_1   |      627 |      0.001 |          205.27 |
| Behavioural_Change_2   |      563 |      0.001 |          227.71 |
| Gather-Scatter         |      553 |      0.001 |          567.84 |
| Fan_In                 |      439 |      0     |          565.09 |
| Fan_Out                |      390 |      0     |          678.69 |
| Scatter-Gather         |      376 |      0     |          505.16 |
| Cash_Withdrawal        |      325 |      0     |          270.87 |
| Bipartite              |      279 |      0     |          682    |
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
|               1 |         1.4  |            0.5  |          23.72 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        4914 |         4426 |      3.03268e+06 |
| unwitting |        4419 |         3512 | 492897           |
| witting   |        4085 |         3567 | 474111           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 4,477; true 246 -> false alarm share 94.5% (target 90-95%)
- Launderers alerted after their start: 243 of 732 (33%); accounts closed: 194

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |     1528 |             5 |
| R2     |     1552 |            17 |
| R3     |      922 |             6 |
| R4     |     1317 |           212 |
| R5     |        6 |             0 |
| R6     |     1486 |            24 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          0 |        417 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                     40 |              41.5 |            114 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        49 |       41 |
| Deposit-Send         |          111 |        42 |       35 |
| Behavioural_Change_1 |           50 |         4 |        2 |
| Layered_Fan_Out      |           50 |        13 |       12 |
| Layered_Fan_In       |           46 |        21 |       18 |
| Behavioural_Change_2 |           44 |         8 |        6 |
| Gather-Scatter       |           43 |        16 |       12 |
| Cycle                |           40 |        31 |       25 |
| Fan_In               |           33 |        11 |        6 |
| Scatter-Gather       |           27 |        13 |       10 |
| Fan_Out              |           25 |        14 |       12 |
| Bipartite            |           24 |         7 |        5 |
| Stacked Bipartite    |           22 |         3 |        3 |
| Cash_Withdrawal      |           18 |         9 |        7 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.763 (average precision 0.192, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.465, money_in 0.478, money_out 0.478, max_in 0.586, n_senders 0.537, share_abroad 0.552, n_internal 0.589, spike 0.465
