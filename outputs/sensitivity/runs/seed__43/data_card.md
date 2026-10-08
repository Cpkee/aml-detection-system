# Data card

Run: v1, seed 43, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.741, meta.seed=43. Code: bb5b24e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

## Accounts by profile

| profile        |      n |   fraud_rows |
|:---------------|-------:|-------------:|
| normal         | 241070 |            0 |
| app_fraud_only |   2198 |         2198 |
| fake           |    537 |          537 |
| witting        |     98 |            0 |
| unwitting      |     97 |            0 |

## Activity per account (medians)

| profile        |   rows_per_month |   payments_per_month |   money_in_per_month |   money_out_per_month |   out_over_in |
|:---------------|-----------------:|---------------------:|---------------------:|----------------------:|--------------:|
| app_fraud_only |             24.7 |                 64.3 |                 5209 |                  3815 |          0.74 |
| fake           |             24.5 |                 62.3 |                 4788 |                  3646 |          0.76 |
| normal         |             24.5 |                 61   |                 4252 |                  3290 |          0.78 |
| unwitting      |             24.6 |                 58.8 |                 3771 |                  3113 |          0.82 |
| witting        |             24.1 |                 57.3 |                 3658 |                  3029 |          0.8  |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32901195 |     30.264 |          129.65 |
| Normal_DirectDebit     | 32162110 |     29.584 |           42.13 |
| Normal_Card            | 19291673 |     17.745 |          261.21 |
| Normal_CashWithdrawal  |  8783157 |      8.079 |          140    |
| Normal_Salary          |  6387418 |      5.875 |         1937.32 |
| Normal_TransferIn      |  4390009 |      4.038 |          100    |
| Normal_StandingOrder   |  3517905 |      3.236 |           54.33 |
| Normal_CashDeposit     |   525864 |      0.484 |          150.11 |
| Normal_Cheque          |   439664 |      0.404 |          100.06 |
| Normal_Abroad          |   154692 |      0.142 |          452.21 |
| Normal_Bonus           |   104231 |      0.096 |         1237.43 |
| Normal_GroupCollection |    42155 |      0.039 |           19.93 |
| Structuring            |     5469 |      0.005 |          288.76 |
| Deposit-Send           |     1589 |      0.001 |          462.21 |
| Layered_Fan_In         |      958 |      0.001 |          703.83 |
| Normal_LargeCash       |      763 |      0.001 |        14978    |
| Cycle                  |      723 |      0.001 |         1382.7  |
| Layered_Fan_Out        |      714 |      0.001 |          451.17 |
| Behavioural_Change_1   |      659 |      0.001 |          225.93 |
| Behavioural_Change_2   |      655 |      0.001 |          233    |
| Gather-Scatter         |      624 |      0.001 |          547.83 |
| Fan_In                 |      566 |      0.001 |          569.89 |
| Stacked Bipartite      |      450 |      0     |          527    |
| Cash_Withdrawal        |      383 |      0     |          271.68 |
| Fan_Out                |      283 |      0     |          605.74 |
| Scatter-Gather         |      275 |      0     |          544.78 |
| Bipartite              |      252 |      0     |          588.8  |
| Smurfing               |      106 |      0     |          169.05 |

## Laundering start (days after opening)

| profile   |   n |   min_rel |   median_rel |   max_rel |   pct_year1 |
|:----------|----:|----------:|-------------:|----------:|------------:|
| fake      | 537 |        60 |           90 |       120 |       100   |
| unwitting |  97 |         1 |          315 |       519 |        54.6 |
| witting   |  98 |         2 |          298 |       508 |        63.3 |

## Launderer networks

| net         |   n |
|:------------|----:|
| big network | 183 |
| chain       | 549 |

## Outgoing rows: abroad, high-risk, internal (%)

|   is_laundering |   pct_abroad |   pct_high_risk |   pct_internal |
|----------------:|-------------:|----------------:|---------------:|
|               0 |         0.16 |            0.03 |           2.75 |
|               1 |         1.33 |            0.39 |          23.49 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5067 |         4656 |      3.12595e+06 |
| unwitting |        4817 |         4362 | 524138           |
| witting   |        4505 |         4043 | 540622           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 5,940; true 197 -> false alarm share 96.7% (target 90-95%)
- Launderers alerted after their start: 193 of 732 (26%); accounts closed: 161

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      761 |             3 |
| R2     |      793 |            20 |
| R3     |      326 |             0 |
| R4     |      754 |           174 |
| R5     |        2 |             0 |
| R6     |     4396 |            14 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      8 |          0 |        424 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                     54 |                26 |            185 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        30 |       26 |
| Deposit-Send         |          111 |        31 |       25 |
| Layered_Fan_In       |           53 |        25 |       20 |
| Behavioural_Change_1 |           50 |         5 |        5 |
| Gather-Scatter       |           46 |        12 |       10 |
| Cycle                |           45 |        26 |       26 |
| Layered_Fan_Out      |           44 |         9 |        8 |
| Behavioural_Change_2 |           41 |         5 |        3 |
| Fan_In               |           37 |        14 |       13 |
| Stacked Bipartite    |           30 |         8 |        6 |
| Fan_Out              |           22 |         8 |        7 |
| Cash_Withdrawal      |           20 |         6 |        4 |
| Scatter-Gather       |           20 |         3 |        2 |
| Bipartite            |           18 |         6 |        6 |
| Smurfing             |            5 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.770 (average precision 0.212, base rate 0.0030)
- Application-only logistic AUC: 0.729
- Single-feature AUC: n_rows 0.469, money_in 0.516, money_out 0.513, max_in 0.601, n_senders 0.591, share_abroad 0.552, n_internal 0.615, spike 0.475
