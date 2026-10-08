# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, rules.confirm_share=0.6. Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| fake           |             24.8 |                 62.2 |                 4730 |                  3670 |          0.77 |
| normal         |             24.5 |                 60.9 |                 4238 |                  3278 |          0.78 |
| unwitting      |             24.9 |                 58.3 |                 3637 |                  3100 |          0.81 |
| witting        |             25.7 |                 57.7 |                 3702 |                  2845 |          0.79 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32885451 |     30.266 |          129.47 |
| Normal_DirectDebit     | 32120156 |     29.562 |           42.06 |
| Normal_Card            | 19291872 |     17.755 |          260.67 |
| Normal_CashWithdrawal  |  8785313 |      8.086 |          140    |
| Normal_Salary          |  6380422 |      5.872 |         1942.84 |
| Normal_TransferIn      |  4389217 |      4.04  |          100.04 |
| Normal_StandingOrder   |  3521488 |      3.241 |           54.18 |
| Normal_CashDeposit     |   525669 |      0.484 |          149.89 |
| Normal_Cheque          |   440396 |      0.405 |          100.17 |
| Normal_Abroad          |   153598 |      0.141 |          450.51 |
| Normal_Bonus           |   104239 |      0.096 |         1243.16 |
| Normal_GroupCollection |    40934 |      0.038 |           20.01 |
| Structuring            |     5403 |      0.005 |          283.75 |
| Deposit-Send           |     1687 |      0.002 |          411.01 |
| Layered_Fan_Out        |      925 |      0.001 |          424.85 |
| Layered_Fan_In         |      794 |      0.001 |          715.49 |
| Normal_LargeCash       |      780 |      0.001 |        14761.8  |
| Cycle                  |      691 |      0.001 |         1438.04 |
| Behavioural_Change_1   |      639 |      0.001 |          205.27 |
| Behavioural_Change_2   |      575 |      0.001 |          227.4  |
| Gather-Scatter         |      553 |      0.001 |          567.84 |
| Fan_In                 |      439 |      0     |          565.09 |
| Fan_Out                |      408 |      0     |          692.05 |
| Scatter-Gather         |      394 |      0     |          512.94 |
| Cash_Withdrawal        |      325 |      0     |          270.87 |
| Stacked Bipartite      |      282 |      0     |          454.1  |
| Bipartite              |      279 |      0     |          682    |
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
|               1 |         1.36 |            0.49 |          24.22 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        4945 |         4508 |      3.08231e+06 |
| unwitting |        4419 |         3561 | 494591           |
| witting   |        4085 |         3567 | 474111           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 3,622; true 248 -> false alarm share 93.2% (target 90-95%)
- Launderers alerted after their start: 242 of 732 (33%); accounts closed: 152

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      780 |             1 |
| R2     |      804 |            13 |
| R3     |      810 |             4 |
| R4     |     1317 |           220 |
| R5     |        8 |             0 |
| R6     |     1103 |            24 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          0 |        426 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   33.2 |                34 |             95 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        48 |       34 |
| Deposit-Send         |          111 |        42 |       25 |
| Behavioural_Change_1 |           50 |         3 |        1 |
| Layered_Fan_Out      |           50 |        13 |        9 |
| Layered_Fan_In       |           46 |        22 |       16 |
| Behavioural_Change_2 |           44 |         7 |        3 |
| Gather-Scatter       |           43 |        16 |       12 |
| Cycle                |           40 |        32 |       20 |
| Fan_In               |           33 |        11 |        4 |
| Scatter-Gather       |           27 |        13 |        7 |
| Fan_Out              |           25 |        15 |       11 |
| Bipartite            |           24 |         7 |        3 |
| Stacked Bipartite    |           22 |         3 |        3 |
| Cash_Withdrawal      |           18 |         9 |        4 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.755 (average precision 0.133, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.499, money_in 0.508, money_out 0.509, max_in 0.586, n_senders 0.574, share_abroad 0.545, n_internal 0.626, spike 0.472
