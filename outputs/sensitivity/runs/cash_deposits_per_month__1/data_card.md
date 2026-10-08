# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.741, normal.cash_deposits_per_month=1.0. Code: bb5b24e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             24.5 |                 64.7 |                 5298 |                  3901 |          0.74 |
| fake           |             24.7 |                 62.4 |                 4730 |                  3672 |          0.77 |
| normal         |             24.5 |                 60.8 |                 4226 |                  3278 |          0.78 |
| unwitting      |             24.9 |                 58.3 |                 3641 |                  3026 |          0.81 |
| witting        |             25.6 |                 58.3 |                 3486 |                  2932 |          0.78 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32886223 |     30.34  |          129.46 |
| Normal_DirectDebit     | 32120159 |     29.633 |           42.05 |
| Normal_Card            | 19292215 |     17.799 |          260.66 |
| Normal_CashWithdrawal  |  8785497 |      8.105 |          140    |
| Normal_Salary          |  6380491 |      5.887 |         1942.83 |
| Normal_TransferIn      |  4389267 |      4.049 |          100.04 |
| Normal_StandingOrder   |  3521588 |      3.249 |           54.18 |
| Normal_Cheque          |   440418 |      0.406 |          100.17 |
| Normal_CashDeposit     |   262820 |      0.242 |          149.47 |
| Normal_Abroad          |   152592 |      0.141 |          451.27 |
| Normal_Bonus           |   104241 |      0.096 |         1243.1  |
| Normal_GroupCollection |    41561 |      0.038 |           19.94 |
| Structuring            |     5501 |      0.005 |          285.31 |
| Deposit-Send           |     1681 |      0.002 |          410.45 |
| Layered_Fan_Out        |      949 |      0.001 |          415.76 |
| Layered_Fan_In         |      851 |      0.001 |          709.51 |
| Normal_LargeCash       |      757 |      0.001 |        14922.9  |
| Cycle                  |      694 |      0.001 |         1468.21 |
| Behavioural_Change_1   |      627 |      0.001 |          205.27 |
| Behavioural_Change_2   |      596 |      0.001 |          223.69 |
| Gather-Scatter         |      577 |      0.001 |          552.25 |
| Fan_In                 |      439 |      0     |          565.09 |
| Fan_Out                |      402 |      0     |          661.17 |
| Scatter-Gather         |      376 |      0     |          505.16 |
| Cash_Withdrawal        |      325 |      0     |          270.87 |
| Stacked Bipartite      |      291 |      0     |          483.86 |
| Bipartite              |      285 |      0     |          687.69 |
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
| fake      |        5087 |         4602 |      3.09374e+06 |
| unwitting |        4419 |         3706 | 499427           |
| witting   |        4148 |         3913 | 490693           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 5,671; true 185 -> false alarm share 96.7% (target 90-95%)
- Launderers alerted after their start: 182 of 732 (25%); accounts closed: 147

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      757 |             0 |
| R2     |      770 |            13 |
| R3     |      338 |             4 |
| R4     |      660 |           163 |
| R5     |        1 |             0 |
| R6     |     4278 |            13 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          1 |        420 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   51.6 |                26 |            162 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        30 |       26 |
| Deposit-Send         |          111 |        28 |       24 |
| Behavioural_Change_1 |           50 |         3 |        2 |
| Layered_Fan_Out      |           50 |        11 |       10 |
| Layered_Fan_In       |           46 |        19 |       15 |
| Behavioural_Change_2 |           44 |         4 |        2 |
| Gather-Scatter       |           43 |        10 |        9 |
| Cycle                |           40 |        28 |       24 |
| Fan_In               |           33 |        10 |        6 |
| Scatter-Gather       |           27 |         7 |        5 |
| Fan_Out              |           25 |        13 |       12 |
| Bipartite            |           24 |         7 |        5 |
| Stacked Bipartite    |           22 |         1 |        1 |
| Cash_Withdrawal      |           18 |         8 |        6 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.781 (average precision 0.155, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.498, money_in 0.509, money_out 0.511, max_in 0.587, n_senders 0.583, share_abroad 0.552, n_internal 0.642, spike 0.474
