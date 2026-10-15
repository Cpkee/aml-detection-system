DATA   : data/v1
REPORT : outputs/modelling/preprocess/v1_50k
fitted on months (0, 1, 2, 3, 4); applied to months 0-7
pandas 3.0.6 | python 3.12.15

==============================================================================
1. THE RECIPE (one entry per application column)
==============================================================================
| column                           | kind        | missing   | clip   | log   | note                                                                                            |
|:---------------------------------|:------------|:----------|:-------|:------|:------------------------------------------------------------------------------------------------|
| income                           | binned      | False     | False  | False | BAF deciles 0.1-0.9                                                                             |
| name_email_similarity            | continuous  | False     | False  | False | 0-1 score                                                                                       |
| prev_address_months_count        | continuous  | True      | False  | True  | -1 = unknown; skewed                                                                            |
| current_address_months_count     | continuous  | True      | False  | True  | -1 = unknown; log added: skew 1.4 -> -0.5 (changed 10 Oct 2026)                                 |
| customer_age                     | binned      | False     | False  | False | BAF decades 10-90                                                                               |
| days_since_request               | continuous  | False     | False  | True  | very skewed                                                                                     |
| intended_balcon_amount           | continuous  | True      | False  | False | negative = no amount given; no log: it turns skew 1.3 into -1.2 (changed 10 Oct 2026)           |
| payment_type                     | categorical | False     | False  | False |                                                                                                 |
| zip_count_4w                     | continuous  | False     | False  | True  | skewed count                                                                                    |
| velocity_6h                      | continuous  | False     | True   | False | never negative in months 0-4; clip is a fixed rule; no log: barely skewed (changed 10 Oct 2026) |
| velocity_24h                     | continuous  | False     | False  | False | no log: barely skewed (changed 10 Oct 2026)                                                     |
| velocity_4w                      | continuous  | False     | False  | False | no log: barely skewed (changed 10 Oct 2026)                                                     |
| bank_branch_count_8w             | continuous  | False     | False  | True  | skewed count                                                                                    |
| date_of_birth_distinct_emails_4w | continuous  | False     | False  | False | count                                                                                           |
| employment_status                | categorical | False     | False  | False |                                                                                                 |
| credit_risk_score                | continuous  | False     | False  | False | negative values are real scores: keep                                                           |
| email_is_free                    | binary      | False     | False  | False |                                                                                                 |
| housing_status                   | categorical | False     | False  | False |                                                                                                 |
| phone_home_valid                 | binary      | False     | False  | False |                                                                                                 |
| phone_mobile_valid               | binary      | False     | False  | False |                                                                                                 |
| bank_months_count                | continuous  | True      | False  | False | -1 = unknown                                                                                    |
| has_other_cards                  | binary      | False     | False  | False |                                                                                                 |
| proposed_credit_limit            | binned      | False     | False  | False | 12 BAF bands                                                                                    |
| foreign_request                  | binary      | False     | False  | False |                                                                                                 |
| source                           | categorical | False     | False  | False |                                                                                                 |
| session_length_in_minutes        | continuous  | True      | False  | True  | -1 = unknown; skewed                                                                            |
| device_os                        | categorical | False     | False  | False |                                                                                                 |
| keep_alive_session               | binary      | False     | False  | False |                                                                                                 |
| device_distinct_emails_8w        | continuous  | True      | False  | False | -1 = unknown; count 0-2                                                                         |

29 columns: continuous 15, binary 6, categorical 5, binned 3; missing code in 6, log1p (linear only) on 6

==============================================================================
2. BEFORE: THE APPLICATION TABLE AS IT ARRIVES
==============================================================================
accounts: 50,000 in months 0-7; 33,801 in months 0-4 (the recipe learns from these only)
true NaN in the application columns: 0 (BAF writes unknown as a negative code)

share of rows with a negative value, by split (BAF missing codes; credit_risk_score is a real score):
|                              |   months 0-4 |   month 5 |   months 6-7 |   min (months 0-4) |   negative rows, all months | recipe            |
|:-----------------------------|-------------:|----------:|-------------:|-------------------:|----------------------------:|:------------------|
| intended_balcon_amount       |       0.7284 |    0.7751 |       0.7676 |           -11.0921 |                       37099 | NaN + flag        |
| prev_address_months_count    |       0.6947 |    0.8226 |       0.7044 |            -1.0000 |                       35604 | NaN + flag        |
| bank_months_count            |       0.2563 |    0.2252 |       0.2632 |            -1.0000 |                       12698 | NaN + flag        |
| credit_risk_score            |       0.0174 |    0.0076 |       0.0050 |          -164.0000 |                         686 | keep (real score) |
| current_address_months_count |       0.0042 |    0.0005 |       0.0070 |            -1.0000 |                         217 | NaN + flag        |
| session_length_in_minutes    |       0.0017 |    0.0013 |       0.0027 |            -1.0000 |                          91 | NaN + flag        |
| device_distinct_emails_8w    |       0.0003 |    0.0002 |       0.0000 |            -1.0000 |                          12 | NaN + flag        |
| velocity_6h                  |       0.0000 |    0.0002 |       0.0004 |           136.1220 |                           5 | clip at 0         |

matches the EDA report §1 (outputs/modelling/eda/v1_50k/report.md): all 8 rows, share and minimum

categorical levels in months 0-4, and rows in months 5-7 with a level not seen there:
|                   |   levels | values                                |   unseen rows, months 5-7 |
|:------------------|---------:|:--------------------------------------|--------------------------:|
| payment_type      |        5 | AA, AB, AC, AD, AE                    |                         0 |
| employment_status |        7 | CA, CB, CC, CD, CE, CF, CG            |                         0 |
| housing_status    |        7 | BA, BB, BC, BD, BE, BF, BG            |                         0 |
| source            |        2 | INTERNET, TELEAPP                     |                         0 |
| device_os         |        5 | linux, macintosh, other, windows, x11 |                         0 |


==============================================================================
5. APPLY TO MONTHS 0-7 AND SAVE
==============================================================================
linear: 50,000 accounts x 56 features -> data/v1/features/accounts_linear.parquet
tree  : 50,000 accounts x 35 features -> data/v1/features/accounts_tree.parquet
manifest -> data/v1/features/preprocess_manifest.json
params   -> outputs/modelling/preprocess/v1_50k/params.json
fitted on 33,801 accounts in months [0, 1, 2, 3, 4]

==============================================================================
6. AFTER: THE COLUMN TABLE (months 0-4) AND THE MISSING FLAGS
==============================================================================
| column                           | kind        | linear                                   | tree               |   missing share |   fill median |   skew before |   skew if log1p |   skew after (linear) |
|:---------------------------------|:------------|:-----------------------------------------|:-------------------|----------------:|--------------:|--------------:|----------------:|----------------------:|
| income                           | binned      | standardise                              | raw                |         nan     |       nan     |        -0.294 |          -0.453 |                -0.294 |
| name_email_similarity            | continuous  | standardise                              | raw                |         nan     |       nan     |        -0.036 |          -0.257 |                -0.036 |
| prev_address_months_count        | continuous  | NaN -> median + flag, log1p, standardise | NaN kept + flag    |           0.695 |         3.497 |         2.362 |           0.394 |                 1.514 |
| current_address_months_count     | continuous  | NaN -> median + flag, log1p, standardise | NaN kept + flag    |           0.004 |         3.951 |         1.409 |          -0.537 |                -0.539 |
| customer_age                     | binned      | standardise                              | raw                |         nan     |       nan     |         0.496 |          -0.336 |                 0.496 |
| days_since_request               | continuous  | log1p, standardise                       | raw                |         nan     |       nan     |         8.873 |           3.463 |                 3.463 |
| intended_balcon_amount           | continuous  | NaN -> median + flag, standardise        | NaN kept + flag    |           0.728 |        32.025 |         1.355 |          -1.126 |                 3.266 |
| payment_type                     | categorical | one-hot, 5 columns                       | category, 5 levels |         nan     |       nan     |       nan     |         nan     |               nan     |
| zip_count_4w                     | continuous  | log1p, standardise                       | raw                |         nan     |       nan     |         1.364 |          -0.231 |                -0.231 |
| velocity_6h                      | continuous  | clip at 0, standardise                   | clip at 0          |         nan     |       nan     |         0.340 |          -1.190 |                 0.340 |
| velocity_24h                     | continuous  | standardise                              | raw                |         nan     |       nan     |         0.321 |          -0.340 |                 0.321 |
| velocity_4w                      | continuous  | standardise                              | raw                |         nan     |       nan     |         0.130 |          -0.409 |                 0.130 |
| bank_branch_count_8w             | continuous  | log1p, standardise                       | raw                |         nan     |       nan     |         2.712 |           0.882 |                 0.882 |
| date_of_birth_distinct_emails_4w | continuous  | standardise                              | raw                |         nan     |       nan     |         0.552 |          -0.722 |                 0.552 |
| employment_status                | categorical | one-hot, 7 columns                       | category, 7 levels |         nan     |       nan     |       nan     |         nan     |               nan     |
| credit_risk_score                | continuous  | standardise                              | raw                |         nan     |       nan     |         0.333 |         nan     |                 0.333 |
| email_is_free                    | binary      | 0/1 as is                                | 0/1 as is          |         nan     |       nan     |       nan     |         nan     |               nan     |
| housing_status                   | categorical | one-hot, 7 columns                       | category, 7 levels |         nan     |       nan     |       nan     |         nan     |               nan     |
| phone_home_valid                 | binary      | 0/1 as is                                | 0/1 as is          |         nan     |       nan     |       nan     |         nan     |               nan     |
| phone_mobile_valid               | binary      | 0/1 as is                                | 0/1 as is          |         nan     |       nan     |       nan     |         nan     |               nan     |
| bank_months_count                | continuous  | NaN -> median + flag, standardise        | NaN kept + flag    |           0.256 |        15.000 |         0.015 |          -0.514 |                 0.020 |
| has_other_cards                  | binary      | 0/1 as is                                | 0/1 as is          |         nan     |       nan     |       nan     |         nan     |               nan     |
| proposed_credit_limit            | binned      | standardise                              | raw                |         nan     |       nan     |         1.169 |           0.801 |                 1.169 |
| foreign_request                  | binary      | 0/1 as is                                | 0/1 as is          |         nan     |       nan     |       nan     |         nan     |               nan     |
| source                           | categorical | one-hot, 2 columns                       | category, 2 levels |         nan     |       nan     |       nan     |         nan     |               nan     |
| session_length_in_minutes        | continuous  | NaN -> median + flag, log1p, standardise | NaN kept + flag    |           0.002 |         1.845 |         3.226 |           0.545 |                 0.547 |
| device_os                        | categorical | one-hot, 5 columns                       | category, 5 levels |         nan     |       nan     |       nan     |         nan     |               nan     |
| keep_alive_session               | binary      | 0/1 as is                                | 0/1 as is          |         nan     |       nan     |       nan     |         nan     |               nan     |
| device_distinct_emails_8w        | continuous  | NaN -> median + flag, standardise        | NaN kept + flag    |           0.000 |         1.000 |         2.874 |          -0.763 |                 2.875 |

linear mode: 56 feature columns
tree mode: 35 feature columns

share of accounts with each missing flag, by group (months 0-4; group sizes normal 33,709, fake 72, real mule 20):
|                                      |   normal |   fake |   real mule |   accounts flagged |
|:-------------------------------------|---------:|-------:|------------:|-------------------:|
| prev_address_months_count_missing    |   0.6942 | 0.8889 |      0.8000 |             23,482 |
| current_address_months_count_missing |   0.0042 | 0.0000 |      0.0000 |                143 |
| intended_balcon_amount_missing       |   0.7280 | 0.8750 |      0.8500 |             24,620 |
| bank_months_count_missing            |   0.2560 | 0.3472 |      0.4000 |              8,663 |
| session_length_in_minutes_missing    |   0.0017 | 0.0000 |      0.0000 |                 56 |
| device_distinct_emails_8w_missing    |   0.0003 | 0.0000 |      0.0000 |                 11 |

  -> a flag whose rate differs between groups carries signal; the flags are kept as features in both modes.

==============================================================================
7. CHECKS (any failure stops the notebook)
==============================================================================
  ok  every account kept once, in input order, keys first
  ok  open_day is never an output; account_id and open_month only as keys
  ok  linear mode has no NaN
  ok  tree mode: NaN exactly where BAF wrote a missing code
  ok  tree mode: no NaN in any other numeric column (categorical NaN from levels unseen in months 0-4: 0)
  ok  missing flags = negative code, identical in both modes
  ok  velocity_6h is never negative after cleaning (tree mode) (5 rows clipped, all in months [5, 6, 7])
  ok  every logged column is less lopsided after log1p on months 0-4 (decision 10 Oct 2026) (6 logged)
  ok  binary columns hold only 0 and 1
  ok  linear: each categorical has at most one level set per account
  ok  linear: standardised columns have mean 0 and spread 1 on months 0-4 (worst |mean| 9.3e-16, worst |sd - 1| 2.2e-16)
  ok  fit is repeatable
  ok  changing every month 5-7 value leaves the fitted numbers unchanged
  ok  linear: months 0-4 cleaned on its own = same columns and values as in the full run
  ok  tree: months 0-4 cleaned on its own = same columns and values as in the full run
  ok  linear: month 5 cleaned on its own = same columns and values as in the full run
  ok  tree: month 5 cleaned on its own = same columns and values as in the full run
  ok  linear: months 6-7 cleaned on its own = same columns and values as in the full run
  ok  tree: months 6-7 cleaned on its own = same columns and values as in the full run
  ok  an unseen level gives all-zero one-hot (linear) and NaN (tree)
  ok  manifest fingerprint matches this data run
  ok  fitted numbers survive the JSON round trip (same cleaned tables)
  ok  linear: saved parquet reads back identical, dtypes included
  ok  tree: saved parquet reads back identical, dtypes included
  ok  saved column lists match the files

done in 1s