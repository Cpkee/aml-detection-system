# Data card

Run: v1, seed 42, 732,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=732000, rules.fixed_scale=1.741, profiles.launderer_share=0.001. Code: 136967e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| fake           |             25   |                 63.4 |                 5104 |                  3791 |          0.75 |
| normal         |             24.5 |                 60.9 |                 4243 |                  3283 |          0.78 |
| unwitting      |             24.9 |                 56.8 |                 3356 |                  2888 |          0.82 |
| witting        |             24.8 |                 60.6 |                 4129 |                  3363 |          0.81 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 98732818 |     30.292 |          129.56 |
| Normal_DirectDebit     | 96271005 |     29.537 |           42.2  |
| Normal_Card            | 57893164 |     17.762 |          260.83 |
| Normal_CashWithdrawal  | 26352361 |      8.085 |          140    |
| Normal_Salary          | 19132517 |      5.87  |         1947.86 |
| Normal_TransferIn      | 13183359 |      4.045 |          100.04 |
| Normal_StandingOrder   | 10549911 |      3.237 |           54.21 |
| Normal_CashDeposit     |  1580654 |      0.485 |          149.95 |
| Normal_Cheque          |  1317916 |      0.404 |          100.12 |
| Normal_Abroad          |   462432 |      0.142 |          449.61 |
| Normal_Bonus           |   313819 |      0.096 |         1241.88 |
| Normal_GroupCollection |   125418 |      0.038 |           20    |
| Structuring            |     6121 |      0.002 |          288.39 |
| Normal_LargeCash       |     2239 |      0.001 |        15146.6  |
| Deposit-Send           |     1303 |      0     |          421.34 |
| Layered_Fan_Out        |     1130 |      0     |          435.96 |
| Layered_Fan_In         |      925 |      0     |          725.33 |
| Behavioural_Change_1   |      661 |      0     |          212.48 |
| Behavioural_Change_2   |      655 |      0     |          225.19 |
| Stacked Bipartite      |      595 |      0     |          503.55 |
| Fan_In                 |      565 |      0     |          617.73 |
| Cycle                  |      491 |      0     |         1295.23 |
| Gather-Scatter         |      465 |      0     |          554.89 |
| Scatter-Gather         |      305 |      0     |          557.92 |
| Fan_Out                |      275 |      0     |          612.3  |
| Cash_Withdrawal        |      225 |      0     |          284.77 |
| Bipartite              |      214 |      0     |          476.9  |
| Smurfing               |      178 |      0     |          157.92 |

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
|               1 |         1.46 |            0.42 |          25.12 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5149 |         4806 |      3.03173e+06 |
| unwitting |        4016 |         3647 | 458138           |
| witting   |        4107 |         3817 | 469186           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 17,157; true 164 -> false alarm share 99.0% (target 90-95%)
- Launderers alerted after their start: 162 of 732 (22%); accounts closed: 128

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |     2236 |             1 |
| R2     |     2289 |             7 |
| R3     |      977 |             2 |
| R4     |     1637 |           150 |
| R5     |        6 |             0 |
| R6     |    13321 |             9 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                     10 |          1 |        316 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                  153.2 |                69 |            492 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          214 |        41 |       34 |
| Deposit-Send         |           92 |        16 |       13 |
| Layered_Fan_Out      |           68 |        10 |        4 |
| Layered_Fan_In       |           54 |        22 |       22 |
| Behavioural_Change_1 |           50 |         3 |        3 |
| Fan_In               |           45 |        12 |        9 |
| Behavioural_Change_2 |           43 |         0 |        0 |
| Gather-Scatter       |           31 |         7 |        6 |
| Cycle                |           28 |        21 |       16 |
| Stacked Bipartite    |           28 |         9 |        7 |
| Scatter-Gather       |           22 |         5 |        4 |
| Fan_Out              |           21 |         8 |        8 |
| Bipartite            |           15 |         1 |        0 |
| Cash_Withdrawal      |           12 |         2 |        1 |
| Smurfing             |            9 |         1 |        1 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.689 (average precision 0.069, base rate 0.0010)
- Application-only logistic AUC: 0.731
- Single-feature AUC: n_rows 0.498, money_in 0.531, money_out 0.532, max_in 0.588, n_senders 0.593, share_abroad 0.565, n_internal 0.640, spike 0.478
