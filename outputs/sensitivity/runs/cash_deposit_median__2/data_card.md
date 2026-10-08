# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, normal.cash_deposit_median=300. Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             24.5 |                 64.7 |                 5334 |                  3890 |          0.74 |
| fake           |             24.3 |                 60.4 |                 4395 |                  3347 |          0.77 |
| normal         |             24.5 |                 60.9 |                 4258 |                  3278 |          0.78 |
| unwitting      |             24.1 |                 56.9 |                 3544 |                  2937 |          0.81 |
| witting        |             25.7 |                 57   |                 3589 |                  2820 |          0.78 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32880696 |     30.266 |          129.46 |
| Normal_DirectDebit     | 32116062 |     29.562 |           42.05 |
| Normal_Card            | 19289429 |     17.756 |          260.66 |
| Normal_CashWithdrawal  |  8784210 |      8.086 |          140    |
| Normal_Salary          |  6379701 |      5.872 |         1942.73 |
| Normal_TransferIn      |  4388648 |      4.04  |          100.04 |
| Normal_StandingOrder   |  3521059 |      3.241 |           54.18 |
| Normal_CashDeposit     |   525358 |      0.484 |          299.78 |
| Normal_Cheque          |   440355 |      0.405 |          100.17 |
| Normal_Abroad          |   153570 |      0.141 |          450.51 |
| Normal_Bonus           |   104230 |      0.096 |         1243.05 |
| Normal_GroupCollection |    40934 |      0.038 |           20.01 |
| Structuring            |     5303 |      0.005 |          284.72 |
| Deposit-Send           |     1687 |      0.002 |          411.01 |
| Layered_Fan_Out        |      925 |      0.001 |          424.85 |
| Layered_Fan_In         |      794 |      0.001 |          715.49 |
| Normal_LargeCash       |      780 |      0.001 |        14761.8  |
| Cycle                  |      661 |      0.001 |         1436.55 |
| Behavioural_Change_1   |      627 |      0.001 |          205.27 |
| Behavioural_Change_2   |      563 |      0.001 |          227.71 |
| Gather-Scatter         |      553 |      0.001 |          567.84 |
| Fan_In                 |      439 |      0     |          565.09 |
| Fan_Out                |      390 |      0     |          678.69 |
| Scatter-Gather         |      376 |      0     |          505.16 |
| Cash_Withdrawal        |      325 |      0     |          270.87 |
| Bipartite              |      275 |      0     |          680.3  |
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
| fake      |        4914 |         4426 |      3.03182e+06 |
| unwitting |        4419 |         3512 | 492897           |
| witting   |        4085 |         3567 | 474111           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 16,543; true 261 -> false alarm share 98.4% (target 90-95%)
- Launderers alerted after their start: 254 of 732 (35%); accounts closed: 206

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      776 |             1 |
| R2     |    13716 |            34 |
| R3     |      807 |             4 |
| R4     |     1322 |           211 |
| R5     |        8 |             0 |
| R6     |     1111 |            24 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          0 |        492 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                  147.7 |             119.5 |            364 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        49 |       43 |
| Deposit-Send         |          111 |        43 |       36 |
| Behavioural_Change_1 |           50 |         8 |        5 |
| Layered_Fan_Out      |           50 |        14 |       13 |
| Layered_Fan_In       |           46 |        22 |       18 |
| Behavioural_Change_2 |           44 |         9 |        7 |
| Gather-Scatter       |           43 |        16 |       12 |
| Cycle                |           40 |        29 |       25 |
| Fan_In               |           33 |        13 |        8 |
| Scatter-Gather       |           27 |        13 |       10 |
| Fan_Out              |           25 |        14 |       12 |
| Bipartite            |           24 |         8 |        6 |
| Stacked Bipartite    |           22 |         2 |        2 |
| Cash_Withdrawal      |           18 |        11 |        9 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.759 (average precision 0.202, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.456, money_in 0.476, money_out 0.475, max_in 0.586, n_senders 0.533, share_abroad 0.545, n_internal 0.586, spike 0.468
