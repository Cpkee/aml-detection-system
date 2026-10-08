# Data card

Run: v1, seed 43, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, meta.seed=43. Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

## Accounts by profile

| profile        |      n |   fraud_rows |
|:---------------|-------:|-------------:|
| normal         | 241070 |            0 |
| app_fraud_only |   2198 |         2198 |
| fake           |    537 |          537 |
| witting        |     98 |            0 |
| unwitting      |     97 |            0 |

## Activity per account (medians)

| profile        |   rows_per_month |   payments_per_month |   money_in_per_month |   money_out_per_month |   out_over_in |
|:---------------|-----------------:|---------------------:|---------------------:|----------------------:|--------------:|
| app_fraud_only |             24.7 |                 64.3 |                 5209 |                  3815 |          0.74 |
| fake           |             24.2 |                 60.7 |                 4468 |                  3425 |          0.76 |
| normal         |             24.5 |                 61   |                 4252 |                  3290 |          0.78 |
| unwitting      |             24.3 |                 57.4 |                 3757 |                  3064 |          0.82 |
| witting        |             23.7 |                 57.1 |                 3575 |                  2929 |          0.79 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32896023 |     30.263 |          129.65 |
| Normal_DirectDebit     | 32157962 |     29.584 |           42.13 |
| Normal_Card            | 19289156 |     17.745 |          261.2  |
| Normal_CashWithdrawal  |  8782039 |      8.079 |          140    |
| Normal_Salary          |  6386479 |      5.875 |         1937.32 |
| Normal_TransferIn      |  4389422 |      4.038 |          100    |
| Normal_StandingOrder   |  3517459 |      3.236 |           54.33 |
| Normal_CashDeposit     |   525745 |      0.484 |          150.1  |
| Normal_Cheque          |   439599 |      0.404 |          100.06 |
| Normal_Abroad          |   154676 |      0.142 |          452.21 |
| Normal_Bonus           |   104220 |      0.096 |         1237.38 |
| Normal_GroupCollection |    42142 |      0.039 |           19.94 |
| Structuring            |     5434 |      0.005 |          289.23 |
| Deposit-Send           |     1568 |      0.001 |          464.29 |
| Layered_Fan_In         |      886 |      0.001 |          698.71 |
| Normal_LargeCash       |      762 |      0.001 |        14976.4  |
| Cycle                  |      722 |      0.001 |         1381.65 |
| Layered_Fan_Out        |      669 |      0.001 |          457.5  |
| Behavioural_Change_1   |      644 |      0.001 |          226.05 |
| Behavioural_Change_2   |      631 |      0.001 |          239.03 |
| Gather-Scatter         |      591 |      0.001 |          541.55 |
| Fan_In                 |      548 |      0.001 |          581.34 |
| Stacked Bipartite      |      438 |      0     |          512.02 |
| Cash_Withdrawal        |      383 |      0     |          271.68 |
| Scatter-Gather         |      275 |      0     |          544.78 |
| Fan_Out                |      259 |      0     |          628.22 |
| Bipartite              |      252 |      0     |          588.8  |
| Smurfing               |      106 |      0     |          169.05 |

## Laundering start (days after opening)

| profile   |   n |   min_rel |   median_rel |   max_rel |   pct_year1 |
|:----------|----:|----------:|-------------:|----------:|------------:|
| fake      | 537 |        60 |           90 |       120 |       100   |
| unwitting |  97 |         1 |          315 |       519 |        54.6 |
| witting   |  98 |         2 |          298 |       508 |        63.3 |

## Launderer networks

| net         |   n |
|:------------|----:|
| big network | 183 |
| chain       | 549 |

## Outgoing rows: abroad, high-risk, internal (%)

|   is_laundering |   pct_abroad |   pct_high_risk |   pct_internal |
|----------------:|-------------:|----------------:|---------------:|
|               0 |         0.16 |            0.03 |           2.75 |
|               1 |         1.31 |            0.36 |          22.82 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        4965 |         4556 |      3.06955e+06 |
| unwitting |        4684 |         4201 | 518264           |
| witting   |        4505 |         3696 | 538062           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 3,689; true 250 -> false alarm share 93.2% (target 90-95%)
- Launderers alerted after their start: 245 of 732 (33%); accounts closed: 204

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      762 |             2 |
| R2     |      793 |            18 |
| R3     |      888 |             4 |
| R4     |     1349 |           222 |
| R5     |        4 |             0 |
| R6     |     1046 |            23 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      8 |          0 |        432 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   33.5 |              33.5 |             83 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        43 |       36 |
| Deposit-Send         |          111 |        45 |       33 |
| Layered_Fan_In       |           53 |        28 |       23 |
| Behavioural_Change_1 |           50 |         6 |        6 |
| Gather-Scatter       |           46 |        13 |       11 |
| Cycle                |           45 |        30 |       29 |
| Layered_Fan_Out      |           44 |        10 |        9 |
| Behavioural_Change_2 |           41 |         5 |        3 |
| Fan_In               |           37 |        16 |       15 |
| Stacked Bipartite    |           30 |        12 |       11 |
| Fan_Out              |           22 |        10 |        9 |
| Cash_Withdrawal      |           20 |         9 |        6 |
| Scatter-Gather       |           20 |         3 |        2 |
| Bipartite            |           18 |        12 |       11 |
| Smurfing             |            5 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.800 (average precision 0.221, base rate 0.0030)
- Application-only logistic AUC: 0.729
- Single-feature AUC: n_rows 0.429, money_in 0.485, money_out 0.479, max_in 0.600, n_senders 0.547, share_abroad 0.549, n_internal 0.565, spike 0.469
