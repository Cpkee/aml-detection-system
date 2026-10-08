# Data card

Run: v1, seed 44, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.741, meta.seed=44. Code: bb5b24e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

## Accounts by profile

| profile        |      n |   fraud_rows |
|:---------------|-------:|-------------:|
| normal         | 241067 |            0 |
| app_fraud_only |   2201 |         2201 |
| fake           |    537 |          537 |
| witting        |     98 |            0 |
| unwitting      |     97 |            0 |

## Activity per account (medians)

| profile        |   rows_per_month |   payments_per_month |   money_in_per_month |   money_out_per_month |   out_over_in |
|:---------------|-----------------:|---------------------:|---------------------:|----------------------:|--------------:|
| app_fraud_only |             24.7 |                 64.6 |                 5314 |                  3883 |          0.74 |
| fake           |             24.8 |                 62.6 |                 5038 |                  3732 |          0.75 |
| normal         |             24.5 |                 60.9 |                 4256 |                  3286 |          0.78 |
| unwitting      |             24.5 |                 59.2 |                 3952 |                  3181 |          0.8  |
| witting        |             23.9 |                 57.9 |                 3578 |                  2891 |          0.81 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32899864 |     30.285 |          129.81 |
| Normal_DirectDebit     | 32095440 |     29.544 |           42.3  |
| Normal_Card            | 19292629 |     17.759 |          261.37 |
| Normal_CashWithdrawal  |  8782687 |      8.085 |          140    |
| Normal_Salary          |  6381242 |      5.874 |         1946.59 |
| Normal_TransferIn      |  4392132 |      4.043 |           99.95 |
| Normal_StandingOrder   |  3513728 |      3.234 |           54.25 |
| Normal_CashDeposit     |   524157 |      0.482 |          149.83 |
| Normal_Cheque          |   438359 |      0.404 |          100.15 |
| Normal_Abroad          |   152619 |      0.14  |          449.8  |
| Normal_Bonus           |   104587 |      0.096 |         1241.08 |
| Normal_GroupCollection |    42282 |      0.039 |           20.12 |
| Structuring            |     6073 |      0.006 |          294.27 |
| Deposit-Send           |     1390 |      0.001 |          411.16 |
| Layered_Fan_In         |     1163 |      0.001 |          711.97 |
| Layered_Fan_Out        |      967 |      0.001 |          436.64 |
| Normal_LargeCash       |      742 |      0.001 |        14892    |
| Behavioural_Change_1   |      591 |      0.001 |          188.27 |
| Cycle                  |      579 |      0.001 |         1387.55 |
| Gather-Scatter         |      562 |      0.001 |          619.26 |
| Fan_In                 |      549 |      0.001 |          507.21 |
| Behavioural_Change_2   |      506 |      0     |          219.56 |
| Stacked Bipartite      |      457 |      0     |          527.5  |
| Fan_Out                |      353 |      0     |          596.03 |
| Cash_Withdrawal        |      328 |      0     |          283.82 |
| Bipartite              |      281 |      0     |          614.7  |
| Smurfing               |      247 |      0     |          139.38 |
| Scatter-Gather         |      187 |      0     |          608.4  |

## Laundering start (days after opening)

| profile   |   n |   min_rel |   median_rel |   max_rel |   pct_year1 |
|:----------|----:|----------:|-------------:|----------:|------------:|
| fake      | 537 |        60 |           90 |       120 |       100   |
| unwitting |  97 |         0 |          306 |       525 |        55.7 |
| witting   |  98 |         8 |          263 |       526 |        63.3 |

## Launderer networks

| net         |   n |
|:------------|----:|
| big network | 183 |
| chain       | 549 |

## Outgoing rows: abroad, high-risk, internal (%)

|   is_laundering |   pct_abroad |   pct_high_risk |   pct_internal |
|----------------:|-------------:|----------------:|---------------:|
|               0 |         0.16 |            0.03 |           2.75 |
|               1 |         1.24 |            0.32 |          25.39 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5197 |         4788 |      3.11967e+06 |
| unwitting |        4423 |         3954 | 515097           |
| witting   |        4579 |         4158 | 495347           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 5,792; true 180 -> false alarm share 96.9% (target 90-95%)
- Launderers alerted after their start: 178 of 732 (24%); accounts closed: 136

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      741 |             1 |
| R2     |      767 |            11 |
| R3     |      355 |             1 |
| R4     |      648 |           158 |
| R5     |        3 |             0 |
| R6     |     4395 |            17 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          0 |        473 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   53.1 |                26 |            178 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          200 |        31 |       21 |
| Deposit-Send         |          102 |        26 |       16 |
| Layered_Fan_In       |           66 |        24 |       22 |
| Layered_Fan_Out      |           56 |        14 |       14 |
| Behavioural_Change_1 |           45 |         2 |        2 |
| Fan_In               |           40 |         7 |        5 |
| Gather-Scatter       |           39 |        12 |       11 |
| Behavioural_Change_2 |           36 |         6 |        4 |
| Cycle                |           32 |        19 |       16 |
| Stacked Bipartite    |           28 |         6 |        5 |
| Fan_Out              |           25 |         8 |        7 |
| Bipartite            |           18 |         8 |        7 |
| Cash_Withdrawal      |           18 |         5 |        3 |
| Scatter-Gather       |           14 |         5 |        2 |
| Smurfing             |           13 |         1 |        1 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.746 (average precision 0.141, base rate 0.0030)
- Application-only logistic AUC: 0.714
- Single-feature AUC: n_rows 0.492, money_in 0.523, money_out 0.521, max_in 0.582, n_senders 0.596, share_abroad 0.555, n_internal 0.637, spike 0.472
