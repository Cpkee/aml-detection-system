# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.741, normal.cash_withdrawals_per_month=4.0. Code: bb5b24e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             26.5 |                 66.6 |                 5286 |                  3927 |          0.75 |
| fake           |             26.8 |                 64.4 |                 4736 |                  3705 |          0.77 |
| normal         |             26.5 |                 62.9 |                 4221 |                  3319 |          0.79 |
| unwitting      |             27.2 |                 60.6 |                 3641 |                  3095 |          0.82 |
| witting        |             27.4 |                 60.3 |                 3485 |                  2833 |          0.8  |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32886370 |     28.005 |          106    |
| Normal_DirectDebit     | 32120297 |     27.353 |           32.9  |
| Normal_Card            | 19292266 |     16.429 |          260.66 |
| Normal_CashWithdrawal  | 17567213 |     14.96  |          140    |
| Normal_Salary          |  6380519 |      5.434 |         1942.82 |
| Normal_TransferIn      |  4389281 |      3.738 |          100.04 |
| Normal_StandingOrder   |  3521615 |      2.999 |           45.34 |
| Normal_CashDeposit     |   516655 |      0.44  |          149.99 |
| Normal_Cheque          |   440423 |      0.375 |          100.17 |
| Normal_Abroad          |   153848 |      0.131 |          448.43 |
| Normal_Bonus           |   104239 |      0.089 |         1243.1  |
| Normal_GroupCollection |    41114 |      0.035 |           19.93 |
| Structuring            |     5519 |      0.005 |          285.31 |
| Deposit-Send           |     1671 |      0.001 |          408.2  |
| Layered_Fan_Out        |      949 |      0.001 |          415.76 |
| Layered_Fan_In         |      848 |      0.001 |          710.53 |
| Normal_LargeCash       |      752 |      0.001 |        14804    |
| Cycle                  |      721 |      0.001 |         1438.04 |
| Behavioural_Change_1   |      639 |      0.001 |          205.27 |
| Behavioural_Change_2   |      596 |      0.001 |          223.69 |
| Gather-Scatter         |      577 |      0     |          552.25 |
| Fan_In                 |      451 |      0     |          557.51 |
| Fan_Out                |      402 |      0     |          661.17 |
| Scatter-Gather         |      376 |      0     |          505.16 |
| Cash_Withdrawal        |      325 |      0     |          270.87 |
| Bipartite              |      285 |      0     |          687.69 |
| Stacked Bipartite      |      276 |      0     |          479.95 |
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
|               0 |         0.15 |            0.02 |           2.52 |
|               1 |         1.36 |            0.48 |          24.78 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5106 |         4611 |      3.10399e+06 |
| unwitting |        4419 |         3803 | 499427           |
| witting   |        4148 |         3868 | 488091           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 5,578; true 182 -> false alarm share 96.7% (target 90-95%)
- Launderers alerted after their start: 179 of 732 (24%); accounts closed: 147

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      752 |             1 |
| R2     |      777 |            13 |
| R3     |      351 |             3 |
| R4     |      619 |           162 |
| R5     |        2 |             0 |
| R6     |     4195 |            11 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          0 |        434 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   50.3 |                26 |            160 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        31 |       27 |
| Deposit-Send         |          111 |        28 |       24 |
| Behavioural_Change_1 |           50 |         3 |        2 |
| Layered_Fan_Out      |           50 |        12 |       11 |
| Layered_Fan_In       |           46 |        19 |       15 |
| Behavioural_Change_2 |           44 |         5 |        3 |
| Gather-Scatter       |           43 |         9 |        8 |
| Cycle                |           40 |        29 |       25 |
| Fan_In               |           33 |         9 |        6 |
| Scatter-Gather       |           27 |         4 |        3 |
| Fan_Out              |           25 |        11 |       11 |
| Bipartite            |           24 |         7 |        5 |
| Stacked Bipartite    |           22 |         1 |        1 |
| Cash_Withdrawal      |           18 |         8 |        6 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.737 (average precision 0.120, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.497, money_in 0.509, money_out 0.510, max_in 0.586, n_senders 0.587, share_abroad 0.550, n_internal 0.645, spike 0.476
