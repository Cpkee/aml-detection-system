# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, normal.internal_share_of_transfers=0.05. Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             24.3 |                 64.5 |                 5276 |                  3875 |          0.75 |
| fake           |             24.3 |                 61.1 |                 4513 |                  3484 |          0.78 |
| normal         |             24.3 |                 60.6 |                 4187 |                  3278 |          0.79 |
| unwitting      |             24.2 |                 57.7 |                 3521 |                  3102 |          0.83 |
| witting        |             25.4 |                 57   |                 3484 |                  2775 |          0.81 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_DirectDebit     | 32116842 |     29.92  |           42.06 |
| Normal_Transfer        | 31581310 |     29.421 |          129.47 |
| Normal_Card            | 19290065 |     17.97  |          260.66 |
| Normal_CashWithdrawal  |  8783063 |      8.182 |          140    |
| Normal_Salary          |  6379915 |      5.943 |         1942.73 |
| Normal_TransferIn      |  4390247 |      4.09  |          100.05 |
| Normal_StandingOrder   |  3521181 |      3.28  |           54.18 |
| Normal_CashDeposit     |   526616 |      0.491 |          150.13 |
| Normal_Cheque          |   439841 |      0.41  |          100.13 |
| Normal_Abroad          |   154548 |      0.144 |          450.47 |
| Normal_Bonus           |   104230 |      0.097 |         1243.03 |
| Normal_GroupCollection |    41097 |      0.038 |           20.09 |
| Structuring            |     5375 |      0.005 |          284.58 |
| Deposit-Send           |     1681 |      0.002 |          412.5  |
| Layered_Fan_Out        |      901 |      0.001 |          427.81 |
| Layered_Fan_In         |      794 |      0.001 |          715.49 |
| Normal_LargeCash       |      768 |      0.001 |        14839.2  |
| Cycle                  |      687 |      0.001 |         1439.45 |
| Behavioural_Change_1   |      627 |      0.001 |          205.27 |
| Behavioural_Change_2   |      566 |      0.001 |          227.56 |
| Gather-Scatter         |      556 |      0.001 |          557.01 |
| Fan_In                 |      433 |      0     |          571.35 |
| Fan_Out                |      378 |      0     |          678.69 |
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
|               0 |         0.16 |            0.03 |           1.37 |
|               1 |         1.37 |            0.47 |          23.83 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        4940 |         4375 |      3.02467e+06 |
| unwitting |        4419 |         3479 | 493017           |
| witting   |        4111 |         3809 | 493903           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 3,660; true 238 -> false alarm share 93.5% (target 90-95%)
- Launderers alerted after their start: 235 of 732 (32%); accounts closed: 188

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      768 |             1 |
| R2     |      800 |            15 |
| R3     |      800 |             5 |
| R4     |     1290 |           212 |
| R5     |        5 |             0 |
| R6     |     1164 |            17 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          1 |        459 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                     33 |                33 |             98 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        49 |       41 |
| Deposit-Send         |          111 |        42 |       34 |
| Behavioural_Change_1 |           50 |         4 |        1 |
| Layered_Fan_Out      |           50 |        13 |       12 |
| Layered_Fan_In       |           46 |        23 |       19 |
| Behavioural_Change_2 |           44 |         7 |        5 |
| Gather-Scatter       |           43 |        17 |       13 |
| Cycle                |           40 |        30 |       25 |
| Fan_In               |           33 |         9 |        6 |
| Scatter-Gather       |           27 |        10 |        8 |
| Fan_Out              |           25 |        12 |       10 |
| Bipartite            |           24 |         7 |        5 |
| Stacked Bipartite    |           22 |         2 |        2 |
| Cash_Withdrawal      |           18 |         9 |        7 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.752 (average precision 0.180, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.472, money_in 0.486, money_out 0.487, max_in 0.585, n_senders 0.569, share_abroad 0.552, n_internal 0.682, spike 0.536
