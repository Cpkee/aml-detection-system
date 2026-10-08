# Data card

Run: v1, seed 42, 244,000 accounts, 730 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, size.observe_days=730. Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             24.7 |                 64.3 |                 5349 |                  3879 |          0.74 |
| fake           |             23.7 |                 58.3 |                 3970 |                  3120 |          0.76 |
| normal         |             24.6 |                 60.8 |                 4244 |                  3278 |          0.78 |
| unwitting      |             24.1 |                 56.2 |                 3257 |                  2855 |          0.81 |
| witting        |             24   |                 55.6 |                 3227 |                  2617 |          0.8  |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 43965247 |     30.368 |          129.45 |
| Normal_DirectDebit     | 42736146 |     29.519 |           42.09 |
| Normal_Card            | 25623570 |     17.699 |          260.62 |
| Normal_CashWithdrawal  | 11698133 |      8.08  |          140    |
| Normal_Salary          |  8501245 |      5.872 |         1942.73 |
| Normal_TransferIn      |  5849039 |      4.04  |          100.08 |
| Normal_StandingOrder   |  4682795 |      3.235 |           54.2  |
| Normal_CashDeposit     |   709311 |      0.49  |          149.91 |
| Normal_Cheque          |   583499 |      0.403 |           99.97 |
| Normal_Abroad          |   205871 |      0.142 |          451.56 |
| Normal_Bonus           |   146399 |      0.101 |         1246.79 |
| Normal_GroupCollection |    57420 |      0.04  |           19.98 |
| Structuring            |     5784 |      0.004 |          289.49 |
| Deposit-Send           |     1544 |      0.001 |          426.49 |
| Layered_Fan_In         |      941 |      0.001 |          722.85 |
| Layered_Fan_Out        |      935 |      0.001 |          450.02 |
| Normal_LargeCash       |      918 |      0.001 |        14900.2  |
| Cycle                  |      842 |      0.001 |         1375.77 |
| Behavioural_Change_1   |      796 |      0.001 |          229.42 |
| Gather-Scatter         |      500 |      0     |          585.48 |
| Stacked Bipartite      |      491 |      0     |          594.48 |
| Fan_Out                |      432 |      0     |          662.29 |
| Behavioural_Change_2   |      408 |      0     |          235.32 |
| Fan_In                 |      293 |      0     |          573.56 |
| Bipartite              |      290 |      0     |          608.62 |
| Scatter-Gather         |      260 |      0     |          521.43 |
| Cash_Withdrawal        |      210 |      0     |          268.93 |
| Smurfing               |      192 |      0     |          149.8  |

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
|               0 |         0.16 |            0.03 |           2.87 |
|               1 |         1.3  |            0.42 |          25.52 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5282 |         4746 |      3.34714e+06 |
| unwitting |        4055 |         3691 | 468611           |
| witting   |        4186 |         3678 | 479276           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 4,704; true 267 -> false alarm share 94.3% (target 90-95%)
- Launderers alerted after their start: 262 of 732 (36%); accounts closed: 213

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      918 |             2 |
| R2     |      972 |            14 |
| R3     |     1196 |            11 |
| R4     |     1646 |           227 |
| R5     |        4 |             0 |
| R6     |     1357 |            31 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      8 |          0 |        514 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   34.3 |                35 |             98 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          205 |        55 |       44 |
| Deposit-Send         |          101 |        41 |       33 |
| Behavioural_Change_1 |           56 |        10 |        7 |
| Layered_Fan_In       |           55 |        29 |       24 |
| Layered_Fan_Out      |           55 |        16 |       14 |
| Cycle                |           45 |        38 |       31 |
| Gather-Scatter       |           35 |        13 |       13 |
| Stacked Bipartite    |           34 |         8 |        5 |
| Fan_Out              |           28 |        13 |       10 |
| Behavioural_Change_2 |           27 |         2 |        2 |
| Bipartite            |           23 |         9 |        7 |
| Fan_In               |           23 |         7 |        5 |
| Scatter-Gather       |           21 |        12 |       10 |
| Cash_Withdrawal      |           13 |         6 |        6 |
| Smurfing             |           11 |         2 |        2 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.757 (average precision 0.227, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.403, money_in 0.437, money_out 0.434, max_in 0.588, n_senders 0.491, share_abroad 0.547, n_internal 0.517, spike 0.484
