# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, normal.large_cash_yearly_rate=0.001. Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             24.5 |                 64.7 |                 5305 |                  3899 |          0.74 |
| fake           |             24.4 |                 61   |                 4409 |                  3375 |          0.77 |
| normal         |             24.5 |                 60.9 |                 4236 |                  3279 |          0.78 |
| unwitting      |             24.6 |                 57.2 |                 3565 |                  2956 |          0.81 |
| witting        |             25.8 |                 57.7 |                 3641 |                  2977 |          0.79 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32881297 |     30.266 |          129.46 |
| Normal_DirectDebit     | 32116788 |     29.562 |           42.05 |
| Normal_Card            | 19289776 |     17.756 |          260.66 |
| Normal_CashWithdrawal  |  8784374 |      8.086 |          140    |
| Normal_Salary          |  6379757 |      5.872 |         1942.75 |
| Normal_TransferIn      |  4388712 |      4.04  |          100.04 |
| Normal_StandingOrder   |  3521157 |      3.241 |           54.18 |
| Normal_CashDeposit     |   525570 |      0.484 |          149.89 |
| Normal_Cheque          |   440357 |      0.405 |          100.17 |
| Normal_Abroad          |   153742 |      0.142 |          450.51 |
| Normal_Bonus           |   104229 |      0.096 |         1243.05 |
| Normal_GroupCollection |    40996 |      0.038 |           19.98 |
| Structuring            |     5303 |      0.005 |          284.72 |
| Deposit-Send           |     1687 |      0.002 |          411.01 |
| Layered_Fan_Out        |      925 |      0.001 |          424.85 |
| Layered_Fan_In         |      794 |      0.001 |          715.49 |
| Cycle                  |      661 |      0.001 |         1436.55 |
| Behavioural_Change_1   |      621 |      0.001 |          205.27 |
| Behavioural_Change_2   |      563 |      0.001 |          227.71 |
| Gather-Scatter         |      553 |      0.001 |          567.84 |
| Fan_In                 |      439 |      0     |          565.09 |
| Fan_Out                |      390 |      0     |          678.69 |
| Normal_LargeCash       |      383 |      0     |        14901.5  |
| Scatter-Gather         |      376 |      0     |          505.16 |
| Cash_Withdrawal        |      325 |      0     |          270.87 |
| Bipartite              |      279 |      0     |          682    |
| Stacked Bipartite      |      240 |      0     |          465.5  |
| Smurfing               |      174 |      0     |          139.4  |

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
|               1 |         1.4  |            0.5  |          23.74 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        4914 |         4426 |      3.03342e+06 |
| unwitting |        4419 |         3512 | 492564           |
| witting   |        4085 |         3567 | 474111           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 3,241; true 241 -> false alarm share 92.6% (target 90-95%)
- Launderers alerted after their start: 238 of 732 (33%); accounts closed: 189

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      383 |             0 |
| R2     |      407 |            12 |
| R3     |      843 |             6 |
| R4     |     1301 |           211 |
| R5     |        5 |             1 |
| R6     |      883 |            23 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          0 |        412 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                     30 |              28.5 |             94 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        48 |       40 |
| Deposit-Send         |          111 |        44 |       36 |
| Behavioural_Change_1 |           50 |         3 |        1 |
| Layered_Fan_Out      |           50 |        13 |       12 |
| Layered_Fan_In       |           46 |        22 |       18 |
| Behavioural_Change_2 |           44 |         7 |        5 |
| Gather-Scatter       |           43 |        16 |       12 |
| Cycle                |           40 |        30 |       24 |
| Fan_In               |           33 |        11 |        6 |
| Scatter-Gather       |           27 |        12 |        9 |
| Fan_Out              |           25 |        14 |       12 |
| Bipartite            |           24 |         7 |        5 |
| Stacked Bipartite    |           22 |         2 |        2 |
| Cash_Withdrawal      |           18 |         9 |        7 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.762 (average precision 0.184, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.468, money_in 0.480, money_out 0.480, max_in 0.586, n_senders 0.540, share_abroad 0.545, n_internal 0.589, spike 0.469
