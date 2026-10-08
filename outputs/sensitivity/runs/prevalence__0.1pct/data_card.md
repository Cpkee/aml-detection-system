# Data card

Run: v1, seed 42, 732,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=732000, rules.fixed_scale=1.516, profiles.launderer_share=0.001. Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

## Accounts by profile

| profile        |      n |   fraud_rows |
|:---------------|-------:|-------------:|
| normal         | 723796 |            0 |
| app_fraud_only |   7472 |         7472 |
| fake           |    537 |          537 |
| witting        |     98 |            0 |
| unwitting      |     97 |            0 |

## Activity per account (medians)

| profile        |   rows_per_month |   payments_per_month |   money_in_per_month |   money_out_per_month |   out_over_in |
|:---------------|-----------------:|---------------------:|---------------------:|----------------------:|--------------:|
| app_fraud_only |             24.5 |                 64.4 |                 5308 |                  3881 |          0.74 |
| fake           |             24.5 |                 62.4 |                 4961 |                  3680 |          0.75 |
| normal         |             24.5 |                 60.9 |                 4243 |                  3283 |          0.78 |
| unwitting      |             24.7 |                 55.8 |                 3330 |                  2873 |          0.82 |
| witting        |             24.4 |                 58.3 |                 3897 |                  3158 |          0.81 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 98728089 |     30.292 |          129.56 |
| Normal_DirectDebit     | 96266930 |     29.537 |           42.2  |
| Normal_Card            | 57890751 |     17.762 |          260.82 |
| Normal_CashWithdrawal  | 26351251 |      8.085 |          140    |
| Normal_Salary          | 19131726 |      5.87  |         1947.86 |
| Normal_TransferIn      | 13182850 |      4.045 |          100.04 |
| Normal_StandingOrder   | 10549441 |      3.237 |           54.21 |
| Normal_CashDeposit     |  1580486 |      0.485 |          149.95 |
| Normal_Cheque          |  1317844 |      0.404 |          100.12 |
| Normal_Abroad          |   462403 |      0.142 |          449.61 |
| Normal_Bonus           |   313814 |      0.096 |         1241.88 |
| Normal_GroupCollection |   125414 |      0.038 |           20    |
| Structuring            |     6033 |      0.002 |          288.43 |
| Normal_LargeCash       |     2239 |      0.001 |        15146.6  |
| Deposit-Send           |     1309 |      0     |          420.01 |
| Layered_Fan_Out        |     1080 |      0     |          436.3  |
| Layered_Fan_In         |      913 |      0     |          725.33 |
| Behavioural_Change_1   |      640 |      0     |          212.1  |
| Behavioural_Change_2   |      634 |      0     |          224.21 |
| Stacked Bipartite      |      553 |      0     |          503.55 |
| Fan_In                 |      535 |      0     |          626.44 |
| Cycle                  |      490 |      0     |         1298.34 |
| Gather-Scatter         |      453 |      0     |          554.89 |
| Scatter-Gather         |      292 |      0     |          558.32 |
| Fan_Out                |      260 |      0     |          614.64 |
| Cash_Withdrawal        |      225 |      0     |          284.77 |
| Bipartite              |      214 |      0     |          476.9  |
| Smurfing               |      166 |      0     |          163.21 |

## Laundering start (days after opening)

| profile   |   n |   min_rel |   median_rel |   max_rel |   pct_year1 |
|:----------|----:|----------:|-------------:|----------:|------------:|
| fake      | 537 |        60 |           90 |       120 |       100   |
| unwitting |  97 |         3 |          352 |       525 |        53.6 |
| witting   |  98 |         4 |          273 |       524 |        66.3 |

## Launderer networks

| net         |   n |
|:------------|----:|
| big network | 183 |
| chain       | 549 |

## Outgoing rows: abroad, high-risk, internal (%)

|   is_laundering |   pct_abroad |   pct_high_risk |   pct_internal |
|----------------:|-------------:|----------------:|---------------:|
|               0 |         0.16 |            0.03 |           2.75 |
|               1 |         1.44 |            0.43 |          24.48 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5019 |         4580 |      2.98826e+06 |
| unwitting |        4016 |         3593 | 452751           |
| witting   |        4089 |         3623 | 466645           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 10,474; true 227 -> false alarm share 97.8% (target 90-95%)
- Launderers alerted after their start: 222 of 732 (30%); accounts closed: 174

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |     2238 |             1 |
| R2     |     2290 |             6 |
| R3     |     2609 |             8 |
| R4     |     3645 |           209 |
| R5     |       11 |             0 |
| R6     |     3091 |            15 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          1 |        451 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   93.5 |              99.5 |            269 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          214 |        71 |       56 |
| Deposit-Send         |           92 |        28 |       19 |
| Layered_Fan_Out      |           68 |        15 |        8 |
| Layered_Fan_In       |           54 |        28 |       26 |
| Behavioural_Change_1 |           50 |         3 |        3 |
| Fan_In               |           45 |        16 |       14 |
| Behavioural_Change_2 |           43 |         2 |        1 |
| Gather-Scatter       |           31 |         8 |        7 |
| Cycle                |           28 |        23 |       19 |
| Stacked Bipartite    |           28 |         7 |        5 |
| Scatter-Gather       |           22 |         7 |        5 |
| Fan_Out              |           21 |         7 |        7 |
| Bipartite            |           15 |         2 |        0 |
| Cash_Withdrawal      |           12 |         4 |        3 |
| Smurfing             |            9 |         1 |        1 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.681 (average precision 0.088, base rate 0.0010)
- Application-only logistic AUC: 0.731
- Single-feature AUC: n_rows 0.458, money_in 0.502, money_out 0.500, max_in 0.587, n_senders 0.556, share_abroad 0.563, n_internal 0.598, spike 0.470
