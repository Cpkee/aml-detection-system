# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.741, timing.fake_start_days=[15, 45]. Code: bb5b24e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             24.5 |                 64.7 |                 5311 |                  3889 |          0.74 |
| fake           |             24.6 |                 61.4 |                 4537 |                  3505 |          0.77 |
| normal         |             24.5 |                 60.9 |                 4238 |                  3278 |          0.78 |
| unwitting      |             24.8 |                 59.2 |                 3866 |                  3098 |          0.8  |
| witting        |             25.4 |                 58.7 |                 3625 |                  2931 |          0.78 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32882685 |     30.267 |          129.46 |
| Normal_DirectDebit     | 32116661 |     29.562 |           42.05 |
| Normal_Card            | 19290444 |     17.756 |          260.65 |
| Normal_CashWithdrawal  |  8784538 |      8.086 |          140    |
| Normal_Salary          |  6379524 |      5.872 |         1942.99 |
| Normal_TransferIn      |  4388870 |      4.04  |          100.04 |
| Normal_StandingOrder   |  3521199 |      3.241 |           54.17 |
| Normal_CashDeposit     |   525493 |      0.484 |          149.9  |
| Normal_Cheque          |   440378 |      0.405 |          100.16 |
| Normal_Abroad          |   153573 |      0.141 |          450.53 |
| Normal_Bonus           |   104238 |      0.096 |         1243.07 |
| Normal_GroupCollection |    40901 |      0.038 |           20.02 |
| Structuring            |     5470 |      0.005 |          289.09 |
| Deposit-Send           |     1394 |      0.001 |          454.5  |
| Layered_Fan_Out        |      834 |      0.001 |          438.17 |
| Normal_LargeCash       |      780 |      0.001 |        14761.8  |
| Layered_Fan_In         |      750 |      0.001 |          674.89 |
| Cycle                  |      653 |      0.001 |         1396.05 |
| Stacked Bipartite      |      649 |      0.001 |          517.77 |
| Behavioural_Change_1   |      607 |      0.001 |          204.46 |
| Fan_In                 |      598 |      0.001 |          571.43 |
| Behavioural_Change_2   |      467 |      0     |          227.28 |
| Gather-Scatter         |      434 |      0     |          608.63 |
| Bipartite              |      410 |      0     |          661.01 |
| Fan_Out                |      382 |      0     |          625.69 |
| Scatter-Gather         |      334 |      0     |          518.48 |
| Cash_Withdrawal        |      325 |      0     |          272.32 |
| Smurfing               |      182 |      0     |          193.52 |

## Laundering start (days after opening)

| profile   |   n |   min_rel |   median_rel |   max_rel |   pct_year1 |
|:----------|----:|----------:|-------------:|----------:|------------:|
| fake      | 537 |        15 |           31 |        45 |       100   |
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
|               1 |         1.3  |            0.28 |          24.65 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5067 |         4652 |      3.09081e+06 |
| unwitting |        4429 |         3970 | 474902           |
| witting   |        4197 |         3649 | 484190           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 5,930; true 189 -> false alarm share 96.8% (target 90-95%)
- Launderers alerted after their start: 186 of 732 (25%); accounts closed: 155

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      780 |             1 |
| R2     |      801 |            10 |
| R3     |      331 |             3 |
| R4     |      670 |           161 |
| R5     |        5 |             0 |
| R6     |     4501 |            23 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      8 |          0 |        507 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   54.4 |                27 |            169 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          191 |        35 |       31 |
| Deposit-Send         |          104 |        26 |       17 |
| Layered_Fan_Out      |           46 |        12 |       11 |
| Behavioural_Change_1 |           43 |         5 |        4 |
| Fan_In               |           43 |        10 |        9 |
| Layered_Fan_In       |           43 |        14 |       11 |
| Cycle                |           42 |        28 |       26 |
| Stacked Bipartite    |           41 |        12 |        9 |
| Behavioural_Change_2 |           34 |         5 |        5 |
| Gather-Scatter       |           34 |         6 |        5 |
| Fan_Out              |           30 |        13 |       12 |
| Bipartite            |           26 |        12 |        9 |
| Scatter-Gather       |           26 |         5 |        3 |
| Cash_Withdrawal      |           19 |         3 |        3 |
| Smurfing             |           10 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.771 (average precision 0.173, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.478, money_in 0.485, money_out 0.487, max_in 0.581, n_senders 0.567, share_abroad 0.550, n_internal 0.624, spike 0.461
