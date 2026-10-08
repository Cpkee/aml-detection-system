# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.741, normal.bonus_share=0.6. Code: bb5b24e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             24.5 |                 64.5 |                 5388 |                  3878 |          0.73 |
| fake           |             24.7 |                 61.9 |                 4871 |                  3605 |          0.76 |
| normal         |             24.5 |                 60.9 |                 4273 |                  3279 |          0.77 |
| unwitting      |             24.3 |                 56.8 |                 3843 |                  3184 |          0.81 |
| witting        |             24.5 |                 56.4 |                 3365 |                  2866 |          0.8  |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32901597 |     30.255 |          129.46 |
| Normal_DirectDebit     | 32108320 |     29.525 |           42.14 |
| Normal_Card            | 19291854 |     17.74  |          260.59 |
| Normal_CashWithdrawal  |  8776527 |      8.07  |          140    |
| Normal_Salary          |  6380450 |      5.867 |         1942.81 |
| Normal_TransferIn      |  4392710 |      4.039 |          100.11 |
| Normal_StandingOrder   |  3520269 |      3.237 |           54.22 |
| Normal_CashDeposit     |   519957 |      0.478 |          150    |
| Normal_Cheque          |   440674 |      0.405 |           99.96 |
| Normal_Bonus           |   208805 |      0.192 |         1248.5  |
| Normal_Abroad          |   151394 |      0.139 |          449.61 |
| Normal_GroupCollection |    41723 |      0.038 |           20.1  |
| Structuring            |     5512 |      0.005 |          284.77 |
| Deposit-Send           |     1645 |      0.002 |          411.46 |
| Layered_Fan_Out        |      934 |      0.001 |          418.44 |
| Layered_Fan_In         |      843 |      0.001 |          715.41 |
| Normal_LargeCash       |      760 |      0.001 |        15047.1  |
| Cycle                  |      655 |      0.001 |         1472.74 |
| Behavioural_Change_1   |      630 |      0.001 |          203.15 |
| Behavioural_Change_2   |      587 |      0.001 |          227.71 |
| Gather-Scatter         |      579 |      0.001 |          548.89 |
| Fan_In                 |      439 |      0     |          565.09 |
| Fan_Out                |      402 |      0     |          661.17 |
| Scatter-Gather         |      377 |      0     |          507.01 |
| Cash_Withdrawal        |      325 |      0     |          270.87 |
| Stacked Bipartite      |      294 |      0     |          479.95 |
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
|               1 |         1.37 |            0.48 |          24.44 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |        total_in |
|:----------|------------:|-------------:|----------------:|
| fake      |        5062 |         4593 |      3.0718e+06 |
| unwitting |        4419 |         3706 | 498713          |
| witting   |        4111 |         3816 | 487228          |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 5,893; true 189 -> false alarm share 96.8% (target 90-95%)
- Launderers alerted after their start: 187 of 732 (26%); accounts closed: 148

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      759 |             3 |
| R2     |      793 |            16 |
| R3     |      369 |             1 |
| R4     |      662 |           166 |
| R5     |        1 |             0 |
| R6     |     4448 |            15 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          0 |        472 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   53.6 |                26 |            170 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        31 |       26 |
| Deposit-Send         |          111 |        28 |       23 |
| Behavioural_Change_1 |           50 |         3 |        2 |
| Layered_Fan_Out      |           50 |        13 |       11 |
| Layered_Fan_In       |           46 |        23 |       18 |
| Behavioural_Change_2 |           44 |         3 |        1 |
| Gather-Scatter       |           43 |        10 |        9 |
| Cycle                |           40 |        24 |       21 |
| Fan_In               |           33 |        10 |        6 |
| Scatter-Gather       |           27 |         7 |        6 |
| Fan_Out              |           25 |        13 |       13 |
| Bipartite            |           24 |         7 |        4 |
| Stacked Bipartite    |           22 |         1 |        1 |
| Cash_Withdrawal      |           18 |         9 |        7 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.752 (average precision 0.143, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.465, money_in 0.507, money_out 0.507, max_in 0.587, n_senders 0.590, share_abroad 0.552, n_internal 0.622, spike 0.482
