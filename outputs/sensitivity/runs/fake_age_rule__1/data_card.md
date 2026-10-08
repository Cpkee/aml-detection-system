# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.741, profiles.fake_age_rule="young_weighted". Code: bb5b24e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| fake           |             24.6 |                 61.8 |                 4443 |                  3447 |          0.77 |
| normal         |             24.5 |                 60.9 |                 4237 |                  3278 |          0.78 |
| unwitting      |             24.3 |                 59.9 |                 4488 |                  3355 |          0.77 |
| witting        |             24.3 |                 58.2 |                 3960 |                  3123 |          0.78 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32884954 |     30.267 |          129.46 |
| Normal_DirectDebit     | 32118650 |     29.562 |           42.05 |
| Normal_Card            | 19291609 |     17.756 |          260.65 |
| Normal_CashWithdrawal  |  8785292 |      8.086 |          140    |
| Normal_Salary          |  6379988 |      5.872 |         1942.84 |
| Normal_TransferIn      |  4389109 |      4.04  |          100.04 |
| Normal_StandingOrder   |  3521397 |      3.241 |           54.18 |
| Normal_CashDeposit     |   525532 |      0.484 |          149.89 |
| Normal_Cheque          |   440396 |      0.405 |          100.16 |
| Normal_Abroad          |   153551 |      0.141 |          450.51 |
| Normal_Bonus           |   104233 |      0.096 |         1242.94 |
| Normal_GroupCollection |    40915 |      0.038 |           20.01 |
| Structuring            |     5259 |      0.005 |          287.3  |
| Deposit-Send           |     1235 |      0.001 |          454.57 |
| Layered_Fan_In         |     1074 |      0.001 |          723.38 |
| Layered_Fan_Out        |      895 |      0.001 |          457.9  |
| Normal_LargeCash       |      781 |      0.001 |        14770    |
| Cycle                  |      645 |      0.001 |         1360.37 |
| Behavioural_Change_2   |      614 |      0.001 |          226.73 |
| Stacked Bipartite      |      549 |      0.001 |          547.67 |
| Fan_In                 |      517 |      0     |          537.62 |
| Gather-Scatter         |      455 |      0     |          557.13 |
| Fan_Out                |      433 |      0     |          616.33 |
| Behavioural_Change_1   |      382 |      0     |          196.19 |
| Smurfing               |      375 |      0     |          160.93 |
| Bipartite              |      361 |      0     |          556.44 |
| Scatter-Gather         |      329 |      0     |          551.16 |
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
|               1 |         1.26 |            0.36 |          23.49 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5043 |         4522 |      3.11572e+06 |
| unwitting |        3834 |         3522 | 472096           |
| witting   |        4125 |         3576 | 475233           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 5,942; true 197 -> false alarm share 96.7% (target 90-95%)
- Launderers alerted after their start: 194 of 732 (27%); accounts closed: 153

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      781 |             2 |
| R2     |      800 |             9 |
| R3     |      328 |             1 |
| R4     |      684 |           176 |
| R5     |        5 |             0 |
| R6     |     4502 |            17 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      8 |          0 |        451 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                     54 |                27 |            167 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          185 |        32 |       24 |
| Deposit-Send         |           92 |        25 |       20 |
| Layered_Fan_In       |           63 |        28 |       23 |
| Layered_Fan_Out      |           57 |        12 |        8 |
| Fan_In               |           41 |        10 |        9 |
| Behavioural_Change_2 |           40 |         3 |        2 |
| Cycle                |           38 |        32 |       26 |
| Gather-Scatter       |           35 |         7 |        6 |
| Stacked Bipartite    |           34 |        10 |        9 |
| Behavioural_Change_1 |           32 |         2 |        2 |
| Fan_Out              |           31 |        11 |        9 |
| Bipartite            |           27 |         9 |        6 |
| Scatter-Gather       |           24 |         7 |        5 |
| Smurfing             |           20 |         2 |        2 |
| Cash_Withdrawal      |           13 |         2 |        2 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.752 (average precision 0.158, base rate 0.0030)
- Application-only logistic AUC: 0.748
- Single-feature AUC: n_rows 0.476, money_in 0.506, money_out 0.508, max_in 0.587, n_senders 0.564, share_abroad 0.551, n_internal 0.610, spike 0.483
