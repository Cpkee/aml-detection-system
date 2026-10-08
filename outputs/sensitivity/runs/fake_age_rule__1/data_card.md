# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, profiles.fake_age_rule="young_weighted". Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             24.5 |                 64.7 |                 5293 |                  3869 |          0.74 |
| fake           |             24   |                 59   |                 3967 |                  3166 |          0.77 |
| normal         |             24.5 |                 60.9 |                 4237 |                  3278 |          0.78 |
| unwitting      |             24.1 |                 59.8 |                 4488 |                  3355 |          0.77 |
| witting        |             24.1 |                 56.9 |                 3832 |                  3020 |          0.78 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32879819 |     30.267 |          129.46 |
| Normal_DirectDebit     | 32114294 |     29.562 |           42.05 |
| Normal_Card            | 19289026 |     17.756 |          260.65 |
| Normal_CashWithdrawal  |  8784128 |      8.086 |          140    |
| Normal_Salary          |  6379201 |      5.872 |         1942.81 |
| Normal_TransferIn      |  4388522 |      4.04  |          100.04 |
| Normal_StandingOrder   |  3520913 |      3.241 |           54.17 |
| Normal_CashDeposit     |   525481 |      0.484 |          149.89 |
| Normal_Cheque          |   440330 |      0.405 |          100.16 |
| Normal_Abroad          |   153514 |      0.141 |          450.53 |
| Normal_Bonus           |   104213 |      0.096 |         1242.91 |
| Normal_GroupCollection |    40900 |      0.038 |           20.02 |
| Structuring            |     5194 |      0.005 |          286.28 |
| Deposit-Send           |     1207 |      0.001 |          456.35 |
| Layered_Fan_In         |     1038 |      0.001 |          724.01 |
| Layered_Fan_Out        |      874 |      0.001 |          464.18 |
| Normal_LargeCash       |      781 |      0.001 |        14770    |
| Cycle                  |      632 |      0.001 |         1398.97 |
| Behavioural_Change_2   |      599 |      0.001 |          229.11 |
| Stacked Bipartite      |      534 |      0     |          564.44 |
| Fan_In                 |      487 |      0     |          537.62 |
| Gather-Scatter         |      452 |      0     |          547.3  |
| Fan_Out                |      421 |      0     |          602.33 |
| Behavioural_Change_1   |      379 |      0     |          199.34 |
| Smurfing               |      375 |      0     |          160.93 |
| Bipartite              |      359 |      0     |          553.73 |
| Scatter-Gather         |      308 |      0     |          560.5  |
| Cash_Withdrawal        |      235 |      0     |          275.2  |

## Laundering start (days after opening)

| profile   |   n |   min_rel |   median_rel |   max_rel |   pct_year1 |
|:----------|----:|----------:|-------------:|----------:|------------:|
| fake      | 537 |        60 |           91 |       120 |       100   |
| unwitting |  97 |         0 |          315 |       526 |        53.6 |
| witting   |  98 |         3 |          308 |       525 |        57.1 |

## Launderer networks

| net         |   n |
|:------------|----:|
| big network | 183 |
| chain       | 549 |

## Outgoing rows: abroad, high-risk, internal (%)

|   is_laundering |   pct_abroad |   pct_high_risk |   pct_internal |
|----------------:|-------------:|----------------:|---------------:|
|               0 |         0.16 |            0.03 |           2.75 |
|               1 |         1.28 |            0.37 |          22.96 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5002 |         4381 |      3.07415e+06 |
| unwitting |        3834 |         3522 | 472096           |
| witting   |        4118 |         3556 | 471591           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 3,625; true 258 -> false alarm share 92.9% (target 90-95%)
- Launderers alerted after their start: 254 of 732 (35%); accounts closed: 205

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      781 |             2 |
| R2     |      799 |             8 |
| R3     |      809 |             5 |
| R4     |     1323 |           229 |
| R5     |        8 |             0 |
| R6     |     1105 |            26 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          0 |        446 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                     33 |              32.5 |             94 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          185 |        53 |       43 |
| Deposit-Send         |           92 |        32 |       27 |
| Layered_Fan_In       |           63 |        34 |       28 |
| Layered_Fan_Out      |           57 |        15 |       12 |
| Fan_In               |           41 |        14 |       11 |
| Behavioural_Change_2 |           40 |         7 |        5 |
| Cycle                |           38 |        32 |       26 |
| Gather-Scatter       |           35 |        10 |        8 |
| Stacked Bipartite    |           34 |        12 |       10 |
| Behavioural_Change_1 |           32 |         2 |        2 |
| Fan_Out              |           31 |        15 |       11 |
| Bipartite            |           27 |        12 |        9 |
| Scatter-Gather       |           24 |         8 |        6 |
| Smurfing             |           20 |         3 |        3 |
| Cash_Withdrawal      |           13 |         4 |        4 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.763 (average precision 0.202, base rate 0.0030)
- Application-only logistic AUC: 0.748
- Single-feature AUC: n_rows 0.434, money_in 0.474, money_out 0.472, max_in 0.587, n_senders 0.523, share_abroad 0.549, n_internal 0.562, spike 0.475
