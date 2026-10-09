# Data card

Run: v1, seed 44, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, meta.seed=44. Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| fake           |             24.5 |                 61.3 |                 4792 |                  3545 |          0.75 |
| normal         |             24.5 |                 60.9 |                 4256 |                  3286 |          0.78 |
| unwitting      |             23.4 |                 58.1 |                 3769 |                  2951 |          0.79 |
| witting        |             23.4 |                 55.2 |                 3357 |                  2672 |          0.8  |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32894752 |     30.284 |          129.81 |
| Normal_DirectDebit     | 32091417 |     29.545 |           42.3  |
| Normal_Card            | 19290037 |     17.759 |          261.36 |
| Normal_CashWithdrawal  |  8781492 |      8.085 |          140    |
| Normal_Salary          |  6380319 |      5.874 |         1946.51 |
| Normal_TransferIn      |  4391534 |      4.043 |           99.95 |
| Normal_StandingOrder   |  3513265 |      3.234 |           54.25 |
| Normal_CashDeposit     |   523981 |      0.482 |          149.83 |
| Normal_Cheque          |   438309 |      0.404 |          100.15 |
| Normal_Abroad          |   152585 |      0.14  |          449.81 |
| Normal_Bonus           |   104576 |      0.096 |         1241.11 |
| Normal_GroupCollection |    42282 |      0.039 |           20.12 |
| Structuring            |     5916 |      0.005 |          294.93 |
| Deposit-Send           |     1341 |      0.001 |          415.18 |
| Layered_Fan_In         |     1127 |      0.001 |          717.2  |
| Layered_Fan_Out        |      922 |      0.001 |          433.99 |
| Normal_LargeCash       |      742 |      0.001 |        14892    |
| Behavioural_Change_1   |      591 |      0.001 |          188.27 |
| Cycle                  |      579 |      0.001 |         1387.55 |
| Gather-Scatter         |      556 |      0.001 |          619.26 |
| Fan_In                 |      537 |      0     |          507.21 |
| Behavioural_Change_2   |      470 |      0     |          221.55 |
| Stacked Bipartite      |      457 |      0     |          527.5  |
| Fan_Out                |      350 |      0     |          598.15 |
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
|               1 |         1.26 |            0.32 |          24.69 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5120 |         4726 |      3.08359e+06 |
| unwitting |        4394 |         3880 | 508280           |
| witting   |        4579 |         3947 | 491185           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 3,542; true 244 -> false alarm share 93.1% (target 90-95%)
- Launderers alerted after their start: 242 of 732 (33%); accounts closed: 188

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      741 |             1 |
| R2     |      766 |            10 |
| R3     |      887 |             3 |
| R4     |     1225 |           215 |
| R5     |        5 |             0 |
| R6     |     1073 |            27 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          0 |        473 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   32.2 |                34 |             81 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          200 |        61 |       46 |
| Deposit-Send         |          102 |        30 |       20 |
| Layered_Fan_In       |           66 |        34 |       29 |
| Layered_Fan_Out      |           56 |        18 |       16 |
| Behavioural_Change_1 |           45 |         5 |        5 |
| Fan_In               |           40 |        12 |        8 |
| Gather-Scatter       |           39 |        15 |       14 |
| Behavioural_Change_2 |           36 |         6 |        4 |
| Cycle                |           32 |        23 |       17 |
| Stacked Bipartite    |           28 |         7 |        6 |
| Fan_Out              |           25 |        10 |        8 |
| Bipartite            |           18 |         9 |        8 |
| Cash_Withdrawal      |           18 |         5 |        3 |
| Scatter-Gather       |           14 |         6 |        3 |
| Smurfing             |           13 |         1 |        1 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.786 (average precision 0.200, base rate 0.0030)
- Application-only logistic AUC: 0.714
- Single-feature AUC: n_rows 0.449, money_in 0.492, money_out 0.487, max_in 0.581, n_senders 0.552, share_abroad 0.555, n_internal 0.589, spike 0.464
