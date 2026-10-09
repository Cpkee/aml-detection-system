# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, profiles.in_window_mix={"fake": 0.53, "witting": 0.235, "unwitting": 0.235}. Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

## Accounts by profile

| profile        |      n |   fraud_rows |
|:---------------|-------:|-------------:|
| normal         | 240899 |            0 |
| app_fraud_only |   2369 |         2369 |
| fake           |    388 |          388 |
| unwitting      |    172 |            0 |
| witting        |    172 |            0 |

## Activity per account (medians)

| profile        |   rows_per_month |   payments_per_month |   money_in_per_month |   money_out_per_month |   out_over_in |
|:---------------|-----------------:|---------------------:|---------------------:|----------------------:|--------------:|
| app_fraud_only |             24.5 |                 64.7 |                 5294 |                  3868 |          0.74 |
| fake           |             24.1 |                 60.8 |                 4493 |                  3379 |          0.75 |
| normal         |             24.5 |                 60.9 |                 4238 |                  3278 |          0.78 |
| unwitting      |             24.9 |                 58.2 |                 3646 |                  3020 |          0.81 |
| witting        |             24.9 |                 58.6 |                 3780 |                  3273 |          0.81 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32884980 |     30.267 |          129.46 |
| Normal_DirectDebit     | 32118578 |     29.562 |           42.05 |
| Normal_Card            | 19291455 |     17.756 |          260.66 |
| Normal_CashWithdrawal  |  8785235 |      8.086 |          140    |
| Normal_Salary          |  6380250 |      5.872 |         1942.84 |
| Normal_TransferIn      |  4389102 |      4.04  |          100.04 |
| Normal_StandingOrder   |  3521415 |      3.241 |           54.18 |
| Normal_CashDeposit     |   525674 |      0.484 |          149.89 |
| Normal_Cheque          |   440397 |      0.405 |          100.16 |
| Normal_Abroad          |   153608 |      0.141 |          450.51 |
| Normal_Bonus           |   104235 |      0.096 |         1243.01 |
| Normal_GroupCollection |    40934 |      0.038 |           20.01 |
| Structuring            |     5659 |      0.005 |          297.55 |
| Deposit-Send           |     1263 |      0.001 |          410.28 |
| Layered_Fan_In         |      969 |      0.001 |          701.7  |
| Layered_Fan_Out        |      898 |      0.001 |          437.83 |
| Normal_LargeCash       |      781 |      0.001 |        14770    |
| Behavioural_Change_2   |      557 |      0.001 |          212.19 |
| Cycle                  |      541 |      0     |         1247.12 |
| Gather-Scatter         |      539 |      0     |          559.6  |
| Fan_In                 |      533 |      0     |          605.98 |
| Stacked Bipartite      |      515 |      0     |          464.43 |
| Behavioural_Change_1   |      455 |      0     |          220.68 |
| Scatter-Gather         |      417 |      0     |          502.31 |
| Bipartite              |      358 |      0     |          575.11 |
| Fan_Out                |      253 |      0     |          635.77 |
| Cash_Withdrawal        |      212 |      0     |          277.29 |
| Smurfing               |      133 |      0     |          168.43 |

## Laundering start (days after opening)

| profile   |   n |   min_rel |   median_rel |   max_rel |   pct_year1 |
|:----------|----:|----------:|-------------:|----------:|------------:|
| fake      | 388 |        60 |           92 |       120 |       100   |
| unwitting | 172 |         0 |          297 |       526 |        59.3 |
| witting   | 172 |         7 |          307 |       519 |        59.3 |

## Launderer networks

| net         |   n |
|:------------|----:|
| big network | 183 |
| chain       | 549 |

## Outgoing rows: abroad, high-risk, internal (%)

|   is_laundering |   pct_abroad |   pct_high_risk |   pct_internal |
|----------------:|-------------:|----------------:|---------------:|
|               0 |         0.16 |            0.03 |           2.75 |
|               1 |         1.6  |            0.41 |          24.11 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5038 |         4562 |      2.18609e+06 |
| unwitting |        4715 |         4089 | 876479           |
| witting   |        4580 |         4080 | 875107           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 3,587; true 211 -> false alarm share 94.1% (target 90-95%)
- Launderers alerted after their start: 210 of 732 (29%); accounts closed: 173

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      781 |             0 |
| R2     |      801 |             8 |
| R3     |      809 |             3 |
| R4     |     1280 |           183 |
| R5     |        8 |             0 |
| R6     |     1109 |            28 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          0 |        427 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   32.9 |                33 |             93 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          199 |        49 |       44 |
| Deposit-Send         |           95 |        24 |       20 |
| Layered_Fan_In       |           60 |        25 |       18 |
| Layered_Fan_Out      |           58 |         8 |        6 |
| Fan_In               |           46 |        18 |       16 |
| Behavioural_Change_2 |           41 |         1 |        1 |
| Gather-Scatter       |           38 |        12 |       10 |
| Behavioural_Change_1 |           34 |         7 |        7 |
| Cycle                |           34 |        26 |       25 |
| Stacked Bipartite    |           31 |         8 |        4 |
| Scatter-Gather       |           29 |        10 |        7 |
| Bipartite            |           28 |         7 |        6 |
| Fan_Out              |           17 |         8 |        6 |
| Cash_Withdrawal      |           14 |         6 |        3 |
| Smurfing             |            8 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.737 (average precision 0.158, base rate 0.0030)
- Application-only logistic AUC: 0.662
- Single-feature AUC: n_rows 0.460, money_in 0.476, money_out 0.479, max_in 0.584, n_senders 0.577, share_abroad 0.554, n_internal 0.617, spike 0.504
