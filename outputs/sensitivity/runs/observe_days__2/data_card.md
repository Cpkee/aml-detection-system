# Data card

Run: v1, seed 42, 244,000 accounts, 730 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.741, size.observe_days=730. Code: bb5b24e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| fake           |             24   |                 60.2 |                 4367 |                  3360 |          0.76 |
| normal         |             24.6 |                 60.8 |                 4244 |                  3278 |          0.78 |
| unwitting      |             24.3 |                 57.5 |                 3780 |                  3175 |          0.82 |
| witting        |             24.1 |                 55.7 |                 3291 |                  2693 |          0.8  |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 43971244 |     30.369 |          129.45 |
| Normal_DirectDebit     | 42741487 |     29.519 |           42.09 |
| Normal_Card            | 25626656 |     17.699 |          260.62 |
| Normal_CashWithdrawal  | 11699506 |      8.08  |          140    |
| Normal_Salary          |  8502047 |      5.872 |         1942.98 |
| Normal_TransferIn      |  5849779 |      4.04  |          100.08 |
| Normal_StandingOrder   |  4683324 |      3.235 |           54.2  |
| Normal_CashDeposit     |   709408 |      0.49  |          149.91 |
| Normal_Cheque          |   583575 |      0.403 |           99.97 |
| Normal_Abroad          |   205885 |      0.142 |          451.56 |
| Normal_Bonus           |   146415 |      0.101 |         1246.79 |
| Normal_GroupCollection |    57420 |      0.04  |           19.98 |
| Structuring            |     5885 |      0.004 |          289.01 |
| Deposit-Send           |     1563 |      0.001 |          427.82 |
| Layered_Fan_In         |      998 |      0.001 |          723.6  |
| Layered_Fan_Out        |      947 |      0.001 |          450.02 |
| Normal_LargeCash       |      918 |      0.001 |        14900.2  |
| Cycle                  |      881 |      0.001 |         1375.01 |
| Behavioural_Change_1   |      802 |      0.001 |          221.94 |
| Stacked Bipartite      |      527 |      0     |          593.69 |
| Gather-Scatter         |      500 |      0     |          585.48 |
| Fan_Out                |      447 |      0     |          654    |
| Behavioural_Change_2   |      408 |      0     |          235.32 |
| Bipartite              |      294 |      0     |          611    |
| Fan_In                 |      293 |      0     |          573.56 |
| Scatter-Gather         |      260 |      0     |          521.43 |
| Smurfing               |      219 |      0     |          138.94 |
| Cash_Withdrawal        |      210 |      0     |          268.93 |

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
|               1 |         1.28 |            0.41 |          26.15 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5378 |         4911 |      3.40469e+06 |
| unwitting |        4231 |         3710 | 474751           |
| witting   |        4159 |         3784 | 482542           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 6,459; true 213 -> false alarm share 96.7% (target 90-95%)
- Launderers alerted after their start: 210 of 732 (29%); accounts closed: 175

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      917 |             2 |
| R2     |      972 |            15 |
| R3     |      483 |             2 |
| R4     |      791 |           185 |
| R5     |        2 |             0 |
| R6     |     4632 |            19 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          0 |        518 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   47.1 |                24 |            175 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          205 |        38 |       32 |
| Deposit-Send         |          101 |        33 |       27 |
| Behavioural_Change_1 |           56 |         7 |        4 |
| Layered_Fan_In       |           55 |        27 |       23 |
| Layered_Fan_Out      |           55 |         9 |       10 |
| Cycle                |           45 |        36 |       28 |
| Gather-Scatter       |           35 |        11 |       11 |
| Stacked Bipartite    |           34 |         7 |        4 |
| Fan_Out              |           28 |        11 |        9 |
| Behavioural_Change_2 |           27 |         3 |        3 |
| Bipartite            |           23 |         7 |        5 |
| Fan_In               |           23 |         6 |        5 |
| Scatter-Gather       |           21 |         8 |        8 |
| Cash_Withdrawal      |           13 |         5 |        5 |
| Smurfing             |           11 |         1 |        1 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.769 (average precision 0.221, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.431, money_in 0.465, money_out 0.464, max_in 0.589, n_senders 0.530, share_abroad 0.548, n_internal 0.564, spike 0.488
