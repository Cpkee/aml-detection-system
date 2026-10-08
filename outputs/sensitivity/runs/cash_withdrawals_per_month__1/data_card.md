# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, normal.cash_withdrawals_per_month=1.0. Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             23.6 |                 63.7 |                 5325 |                  3853 |          0.73 |
| fake           |             23.5 |                 60   |                 4421 |                  3304 |          0.76 |
| normal         |             23.6 |                 59.9 |                 4247 |                  3260 |          0.77 |
| unwitting      |             23.6 |                 56.4 |                 3570 |                  2908 |          0.79 |
| witting        |             24.6 |                 56.3 |                 3581 |                  2816 |          0.79 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32881290 |     31.541 |          141.39 |
| Normal_DirectDebit     | 32116615 |     30.808 |           46.6  |
| Normal_Card            | 19289733 |     18.504 |          260.66 |
| Normal_Salary          |  6379803 |      6.12  |         1942.63 |
| Normal_CashWithdrawal  |  4393262 |      4.214 |          140    |
| Normal_TransferIn      |  4388734 |      4.21  |          100.04 |
| Normal_StandingOrder   |  3521099 |      3.378 |           58.6  |
| Normal_CashDeposit     |   523632 |      0.502 |          149.77 |
| Normal_Cheque          |   440364 |      0.422 |          100.17 |
| Normal_Abroad          |   153034 |      0.147 |          449.55 |
| Normal_Bonus           |   104229 |      0.1   |         1243.05 |
| Normal_GroupCollection |    42209 |      0.04  |           20.02 |
| Structuring            |     5321 |      0.005 |          284.72 |
| Deposit-Send           |     1690 |      0.002 |          411.49 |
| Layered_Fan_Out        |      925 |      0.001 |          424.85 |
| Layered_Fan_In         |      794 |      0.001 |          715.49 |
| Normal_LargeCash       |      725 |      0.001 |        15173.1  |
| Cycle                  |      655 |      0.001 |         1439.45 |
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
|               0 |         0.17 |            0.03 |           2.88 |
|               1 |         1.4  |            0.5  |          23.76 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        4940 |         4431 |      3.03276e+06 |
| unwitting |        4419 |         3512 | 492897           |
| witting   |        4085 |         3611 | 474111           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 3,635; true 243 -> false alarm share 93.3% (target 90-95%)
- Launderers alerted after their start: 240 of 732 (33%); accounts closed: 193

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      725 |             2 |
| R2     |      746 |            14 |
| R3     |      840 |             5 |
| R4     |     1374 |           214 |
| R5     |        4 |             0 |
| R6     |     1031 |            23 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          0 |        468 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   32.7 |                34 |             97 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        49 |       40 |
| Deposit-Send         |          111 |        46 |       39 |
| Behavioural_Change_1 |           50 |         4 |        2 |
| Layered_Fan_Out      |           50 |        12 |       11 |
| Layered_Fan_In       |           46 |        22 |       18 |
| Behavioural_Change_2 |           44 |         7 |        5 |
| Gather-Scatter       |           43 |        18 |       14 |
| Cycle                |           40 |        30 |       24 |
| Fan_In               |           33 |        10 |        6 |
| Scatter-Gather       |           27 |         9 |        6 |
| Fan_Out              |           25 |        14 |       13 |
| Bipartite            |           24 |         8 |        6 |
| Stacked Bipartite    |           22 |         2 |        2 |
| Cash_Withdrawal      |           18 |         9 |        7 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.780 (average precision 0.199, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.465, money_in 0.479, money_out 0.479, max_in 0.586, n_senders 0.541, share_abroad 0.538, n_internal 0.590, spike 0.474
