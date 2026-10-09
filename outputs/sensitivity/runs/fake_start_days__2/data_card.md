# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, timing.fake_start_days=[150, 210]. Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             24.5 |                 64.7 |                 5311 |                  3890 |          0.74 |
| fake           |             24.4 |                 60.4 |                 4408 |                  3396 |          0.76 |
| normal         |             24.5 |                 60.9 |                 4238 |                  3278 |          0.78 |
| unwitting      |             24.7 |                 57.5 |                 3947 |                  3171 |          0.81 |
| witting        |             25.3 |                 57   |                 3423 |                  2759 |          0.8  |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32884681 |     30.267 |          129.46 |
| Normal_DirectDebit     | 32118824 |     29.562 |           42.05 |
| Normal_Card            | 19291449 |     17.756 |          260.66 |
| Normal_CashWithdrawal  |  8785177 |      8.086 |          140    |
| Normal_Salary          |  6380206 |      5.872 |         1942.95 |
| Normal_TransferIn      |  4389162 |      4.04  |          100.04 |
| Normal_StandingOrder   |  3521443 |      3.241 |           54.18 |
| Normal_CashDeposit     |   525720 |      0.484 |          149.89 |
| Normal_Cheque          |   440393 |      0.405 |          100.16 |
| Normal_Abroad          |   153583 |      0.141 |          450.51 |
| Normal_Bonus           |   104225 |      0.096 |         1243    |
| Normal_GroupCollection |    40934 |      0.038 |           20.01 |
| Structuring            |     5472 |      0.005 |          277.25 |
| Deposit-Send           |     1345 |      0.001 |          422.25 |
| Layered_Fan_Out        |     1101 |      0.001 |          459.89 |
| Layered_Fan_In         |      934 |      0.001 |          704.63 |
| Normal_LargeCash       |      780 |      0.001 |        14761.8  |
| Behavioural_Change_1   |      654 |      0.001 |          217.15 |
| Gather-Scatter         |      603 |      0.001 |          580.89 |
| Stacked Bipartite      |      576 |      0.001 |          562.26 |
| Cycle                  |      562 |      0.001 |         1491.32 |
| Fan_In                 |      555 |      0.001 |          627.01 |
| Behavioural_Change_2   |      512 |      0     |          235.16 |
| Scatter-Gather         |      362 |      0     |          496.76 |
| Fan_Out                |      299 |      0     |          696.13 |
| Bipartite              |      273 |      0     |          623.67 |
| Cash_Withdrawal        |      231 |      0     |          276.62 |
| Smurfing               |      163 |      0     |          152.77 |

## Laundering start (days after opening)

| profile   |   n |   min_rel |   median_rel |   max_rel |   pct_year1 |
|:----------|----:|----------:|-------------:|----------:|------------:|
| fake      | 537 |       150 |          182 |       210 |       100   |
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
|               1 |         1.37 |            0.4  |          24.89 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |        total_in |
|:----------|------------:|-------------:|----------------:|
| fake      |        4986 |         4542 |      3.0706e+06 |
| unwitting |        4853 |         4032 | 526850          |
| witting   |        4191 |         3875 | 482315          |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 3,611; true 238 -> false alarm share 93.4% (target 90-95%)
- Launderers alerted after their start: 234 of 732 (32%); accounts closed: 189

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      780 |             1 |
| R2     |      804 |            13 |
| R3     |      810 |             4 |
| R4     |     1309 |           212 |
| R5     |        8 |             0 |
| R6     |     1092 |            14 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      8 |          0 |        336 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   33.1 |                33 |             99 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          196 |        51 |       39 |
| Deposit-Send         |          101 |        23 |       21 |
| Layered_Fan_Out      |           63 |        17 |       11 |
| Behavioural_Change_1 |           46 |         6 |        4 |
| Layered_Fan_In       |           45 |        24 |       20 |
| Cycle                |           44 |        31 |       25 |
| Gather-Scatter       |           42 |        17 |       13 |
| Fan_In               |           38 |        17 |       13 |
| Behavioural_Change_2 |           36 |         1 |        1 |
| Stacked Bipartite    |           30 |        11 |       10 |
| Scatter-Gather       |           25 |         8 |        7 |
| Fan_Out              |           23 |        11 |        9 |
| Bipartite            |           21 |        10 |       10 |
| Cash_Withdrawal      |           14 |         7 |        6 |
| Smurfing             |            8 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.759 (average precision 0.155, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.460, money_in 0.503, money_out 0.501, max_in 0.588, n_senders 0.550, share_abroad 0.550, n_internal 0.620, spike 0.482
