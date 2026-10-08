# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.741, profiles.launderer_share=0.01. Code: 136967e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

## Accounts by profile

| profile        |      n |   fraud_rows |
|:---------------|-------:|-------------:|
| normal         | 240592 |            0 |
| fake           |   1789 |         1789 |
| app_fraud_only |    968 |          968 |
| witting        |    326 |            0 |
| unwitting      |    325 |            0 |

## Activity per account (medians)

| profile        |   rows_per_month |   payments_per_month |   money_in_per_month |   money_out_per_month |   out_over_in |
|:---------------|-----------------:|---------------------:|---------------------:|----------------------:|--------------:|
| app_fraud_only |             24.6 |                 64.6 |                 5267 |                  3851 |          0.74 |
| fake           |             24.6 |                 62.5 |                 4877 |                  3627 |          0.76 |
| normal         |             24.5 |                 60.9 |                 4238 |                  3278 |          0.78 |
| unwitting      |             24.9 |                 58.2 |                 3847 |                  3157 |          0.8  |
| witting        |             24.6 |                 58.4 |                 3859 |                  3211 |          0.79 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32850619 |     30.255 |          129.44 |
| Normal_DirectDebit     | 32090654 |     29.555 |           42.05 |
| Normal_Card            | 19274196 |     17.751 |          260.61 |
| Normal_CashWithdrawal  |  8777439 |      8.084 |          140    |
| Normal_Salary          |  6373181 |      5.87  |         1943.72 |
| Normal_TransferIn      |  4385185 |      4.039 |          100.04 |
| Normal_StandingOrder   |  3518247 |      3.24  |           54.17 |
| Normal_CashDeposit     |   525272 |      0.484 |          149.89 |
| Normal_Cheque          |   439981 |      0.405 |          100.17 |
| Normal_Abroad          |   153411 |      0.141 |          450.53 |
| Normal_Bonus           |   104148 |      0.096 |         1242.24 |
| Normal_GroupCollection |    40870 |      0.038 |           20.02 |
| Structuring            |    18042 |      0.017 |          290.75 |
| Deposit-Send           |     4572 |      0.004 |          416.7  |
| Layered_Fan_Out        |     3044 |      0.003 |          442.79 |
| Layered_Fan_In         |     2308 |      0.002 |          715.54 |
| Cycle                  |     2243 |      0.002 |         1390.84 |
| Fan_In                 |     2015 |      0.002 |          571.12 |
| Behavioural_Change_1   |     1933 |      0.002 |          207.58 |
| Behavioural_Change_2   |     1887 |      0.002 |          221.9  |
| Gather-Scatter         |     1736 |      0.002 |          552.28 |
| Stacked Bipartite      |     1649 |      0.002 |          517.75 |
| Fan_Out                |     1362 |      0.001 |          625.06 |
| Bipartite              |     1229 |      0.001 |          577.27 |
| Scatter-Gather         |     1122 |      0.001 |          510.42 |
| Smurfing               |      919 |      0.001 |          164.18 |
| Cash_Withdrawal        |      811 |      0.001 |          273.5  |
| Normal_LargeCash       |      778 |      0.001 |        14751.2  |

## Laundering start (days after opening)

| profile   |    n |   min_rel |   median_rel |   max_rel |   pct_year1 |
|:----------|-----:|----------:|-------------:|----------:|------------:|
| fake      | 1789 |        60 |           90 |       120 |       100   |
| unwitting |  325 |         1 |          288 |       525 |        62.8 |
| witting   |  326 |         0 |          322 |       526 |        57.4 |

## Launderer networks

| net         |    n |
|:------------|-----:|
| big network |  610 |
| chain       | 1830 |

## Outgoing rows: abroad, high-risk, internal (%)

|   is_laundering |   pct_abroad |   pct_high_risk |   pct_internal |
|----------------:|-------------:|----------------:|---------------:|
|               0 |         0.16 |            0.03 |           2.75 |
|               1 |         1.54 |            0.39 |          23.94 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |    total_in |
|:----------|------------:|-------------:|------------:|
| fake      |        5060 |         4628 | 1.01995e+07 |
| unwitting |        4379 |         3953 | 1.58784e+06 |
| witting   |        4273 |         3821 | 1.59713e+06 |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 6,315; true 581 -> false alarm share 90.8% (target 90-95%)
- Launderers alerted after their start: 577 of 2440 (24%); accounts closed: 482

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      778 |             5 |
| R2     |      818 |            33 |
| R3     |      327 |             3 |
| R4     |     1028 |           523 |
| R5     |        5 |             0 |
| R6     |     4526 |            43 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      8 |          0 |        435 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   57.9 |                29 |            185 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          642 |       112 |      104 |
| Deposit-Send         |          335 |        77 |       63 |
| Layered_Fan_Out      |          172 |        35 |       26 |
| Layered_Fan_In       |          149 |        45 |       38 |
| Fan_In               |          145 |        39 |       30 |
| Behavioural_Change_1 |          143 |         6 |        5 |
| Behavioural_Change_2 |          137 |         6 |        5 |
| Cycle                |          136 |        98 |       91 |
| Gather-Scatter       |          127 |        31 |       24 |
| Stacked Bipartite    |          103 |        25 |       21 |
| Fan_Out              |           94 |        38 |       28 |
| Bipartite            |           88 |        28 |       23 |
| Scatter-Gather       |           79 |        18 |       16 |
| Cash_Withdrawal      |           46 |         8 |        7 |
| Smurfing             |           44 |         1 |        1 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.877 (average precision 0.361, base rate 0.0100)
- Application-only logistic AUC: 0.740
- Single-feature AUC: n_rows 0.486, money_in 0.518, money_out 0.517, max_in 0.600, n_senders 0.583, share_abroad 0.560, n_internal 0.622, spike 0.496
