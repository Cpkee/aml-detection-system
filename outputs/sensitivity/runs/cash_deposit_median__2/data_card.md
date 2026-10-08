# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.741, normal.cash_deposit_median=300. Code: bb5b24e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| fake           |             24.6 |                 62   |                 4711 |                  3667 |          0.77 |
| normal         |             24.5 |                 60.9 |                 4258 |                  3278 |          0.78 |
| unwitting      |             24.9 |                 58.1 |                 3637 |                  3002 |          0.81 |
| witting        |             25.6 |                 57.1 |                 3501 |                  2845 |          0.78 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32885486 |     30.267 |          129.46 |
| Normal_DirectDebit     | 32119416 |     29.562 |           42.05 |
| Normal_Card            | 19291811 |     17.756 |          260.66 |
| Normal_CashWithdrawal  |  8785303 |      8.086 |          140    |
| Normal_Salary          |  6380391 |      5.872 |         1942.81 |
| Normal_TransferIn      |  4389172 |      4.04  |          100.04 |
| Normal_StandingOrder   |  3521505 |      3.241 |           54.18 |
| Normal_CashDeposit     |   525423 |      0.484 |          299.78 |
| Normal_Cheque          |   440415 |      0.405 |          100.17 |
| Normal_Abroad          |   153598 |      0.141 |          450.5  |
| Normal_Bonus           |   104239 |      0.096 |         1243.09 |
| Normal_GroupCollection |    40934 |      0.038 |           20.01 |
| Structuring            |     5501 |      0.005 |          285.31 |
| Deposit-Send           |     1681 |      0.002 |          410.45 |
| Layered_Fan_Out        |      949 |      0.001 |          415.76 |
| Layered_Fan_In         |      851 |      0.001 |          709.51 |
| Normal_LargeCash       |      781 |      0.001 |        14770    |
| Cycle                  |      694 |      0.001 |         1468.21 |
| Behavioural_Change_1   |      627 |      0.001 |          205.27 |
| Behavioural_Change_2   |      596 |      0.001 |          223.69 |
| Gather-Scatter         |      577 |      0.001 |          552.25 |
| Fan_In                 |      439 |      0     |          565.09 |
| Fan_Out                |      402 |      0     |          661.17 |
| Scatter-Gather         |      376 |      0     |          505.16 |
| Cash_Withdrawal        |      325 |      0     |          270.87 |
| Stacked Bipartite      |      291 |      0     |          483.86 |
| Bipartite              |      281 |      0     |          685.84 |
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
|               1 |         1.36 |            0.48 |          24.65 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5087 |         4602 |      3.09288e+06 |
| unwitting |        4419 |         3706 | 499427           |
| witting   |        4148 |         3913 | 490693           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 18,882; true 209 -> false alarm share 98.9% (target 90-95%)
- Launderers alerted after their start: 203 of 732 (28%); accounts closed: 166

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      777 |             2 |
| R2     |    13721 |            39 |
| R3     |      327 |             1 |
| R4     |      678 |           164 |
| R5     |        5 |             0 |
| R6     |     4530 |            14 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                     11 |          1 |        492 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                  168.6 |             161.5 |            351 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        34 |       32 |
| Deposit-Send         |          111 |        30 |       25 |
| Behavioural_Change_1 |           50 |         7 |        6 |
| Layered_Fan_Out      |           50 |        12 |       11 |
| Layered_Fan_In       |           46 |        19 |       15 |
| Behavioural_Change_2 |           44 |         6 |        4 |
| Gather-Scatter       |           43 |        10 |        9 |
| Cycle                |           40 |        28 |       25 |
| Fan_In               |           33 |        12 |        8 |
| Scatter-Gather       |           27 |         9 |        6 |
| Fan_Out              |           25 |        11 |       10 |
| Bipartite            |           24 |         8 |        6 |
| Stacked Bipartite    |           22 |         1 |        1 |
| Cash_Withdrawal      |           18 |        10 |        8 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.765 (average precision 0.157, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.485, money_in 0.504, money_out 0.505, max_in 0.588, n_senders 0.573, share_abroad 0.547, n_internal 0.636, spike 0.475
