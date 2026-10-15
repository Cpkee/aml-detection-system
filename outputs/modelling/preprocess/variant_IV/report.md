DATA   : data/variant_IV
REPORT : outputs/modelling/preprocess/variant_IV
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
accounts: 244,000 in months 0-7; 148,992 in months 0-4 (the recipe learns from these only)
true NaN in the application columns: 0 (BAF writes unknown as a negative code)

share of rows with a negative value, by split (BAF missing codes; credit_risk_score is a real score):
|                              |   months 0-4 |   month 5 |   months 6-7 |   min (months 0-4) |   negative rows, all months | recipe            |
|:-----------------------------|-------------:|----------:|-------------:|-------------------:|----------------------------:|:------------------|
| prev_address_months_count    |       0.7443 |    0.8520 |       0.7549 |            -1.0000 |                      186100 | NaN + flag        |
| intended_balcon_amount       |       0.7430 |    0.7772 |       0.7542 |           -14.9817 |                      183185 | NaN + flag        |
| bank_months_count            |       0.2519 |    0.2175 |       0.2489 |            -1.0000 |                       60050 | NaN + flag        |
| credit_risk_score            |       0.0156 |    0.0088 |       0.0047 |          -154.0000 |                        2923 | keep (real score) |
| current_address_months_count |       0.0037 |    0.0015 |       0.0046 |            -1.0000 |                         871 | NaN + flag        |
| session_length_in_minutes    |       0.0023 |    0.0022 |       0.0025 |            -1.0000 |                         571 | NaN + flag        |
| device_distinct_emails_8w    |       0.0003 |    0.0003 |       0.0002 |            -1.0000 |                          64 | NaN + flag        |
| velocity_6h                  |       0.0000 |    0.0001 |       0.0002 |            23.7767 |                          12 | clip at 0         |

no EDA report for variant_IV: comparison with EDA §1 skipped

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
linear: 244,000 accounts x 56 features -> data/variant_IV/features/accounts_linear.parquet
tree  : 244,000 accounts x 35 features -> data/variant_IV/features/accounts_tree.parquet
manifest -> data/variant_IV/features/preprocess_manifest.json
params   -> outputs/modelling/preprocess/variant_IV/params.json
fitted on 148,992 accounts in months [0, 1, 2, 3, 4]

==============================================================================
6. AFTER: THE COLUMN TABLE (months 0-4) AND THE MISSING FLAGS
==============================================================================
| column                           | kind        | linear                                   | tree               |   missing share |   fill median |   skew before |   skew if log1p |   skew after (linear) |
|:---------------------------------|:------------|:-----------------------------------------|:-------------------|----------------:|--------------:|--------------:|----------------:|----------------------:|
| income                           | binned      | standardise                              | raw                |         nan     |       nan     |        -0.339 |          -0.499 |                -0.339 |
| name_email_similarity            | continuous  | standardise                              | raw                |         nan     |       nan     |        -0.015 |          -0.225 |                -0.015 |
| prev_address_months_count        | continuous  | NaN -> median + flag, log1p, standardise | NaN kept + flag    |           0.744 |         3.526 |         2.188 |           0.341 |                 1.734 |
| current_address_months_count     | continuous  | NaN -> median + flag, log1p, standardise | NaN kept + flag    |           0.004 |         4.159 |         1.172 |          -0.664 |                -0.667 |
| customer_age                     | binned      | standardise                              | raw                |         nan     |       nan     |        -0.191 |          -0.870 |                -0.191 |
| days_since_request               | continuous  | log1p, standardise                       | raw                |         nan     |       nan     |         9.219 |           3.580 |                 3.580 |
| intended_balcon_amount           | continuous  | NaN -> median + flag, standardise        | NaN kept + flag    |           0.743 |        33.354 |         1.310 |          -1.232 |                 3.275 |
| payment_type                     | categorical | one-hot, 5 columns                       | category, 5 levels |         nan     |       nan     |       nan     |         nan     |               nan     |
| zip_count_4w                     | continuous  | log1p, standardise                       | raw                |         nan     |       nan     |         1.412 |          -0.154 |                -0.154 |
| velocity_6h                      | continuous  | clip at 0, standardise                   | clip at 0          |         nan     |       nan     |         0.361 |          -1.203 |                 0.361 |
| velocity_24h                     | continuous  | standardise                              | raw                |         nan     |       nan     |         0.423 |          -0.275 |                 0.423 |
| velocity_4w                      | continuous  | standardise                              | raw                |         nan     |       nan     |         0.147 |          -0.454 |                 0.147 |
| bank_branch_count_8w             | continuous  | log1p, standardise                       | raw                |         nan     |       nan     |         2.538 |           0.799 |                 0.799 |
| date_of_birth_distinct_emails_4w | continuous  | standardise                              | raw                |         nan     |       nan     |         0.839 |          -0.449 |                 0.839 |
| employment_status                | categorical | one-hot, 7 columns                       | category, 7 levels |         nan     |       nan     |       nan     |         nan     |               nan     |
| credit_risk_score                | continuous  | standardise                              | raw                |         nan     |       nan     |         0.311 |         nan     |                 0.311 |
| email_is_free                    | binary      | 0/1 as is                                | 0/1 as is          |         nan     |       nan     |       nan     |         nan     |               nan     |
| housing_status                   | categorical | one-hot, 7 columns                       | category, 7 levels |         nan     |       nan     |       nan     |         nan     |               nan     |
| phone_home_valid                 | binary      | 0/1 as is                                | 0/1 as is          |         nan     |       nan     |       nan     |         nan     |               nan     |
| phone_mobile_valid               | binary      | 0/1 as is                                | 0/1 as is          |         nan     |       nan     |       nan     |         nan     |               nan     |
| bank_months_count                | continuous  | NaN -> median + flag, standardise        | NaN kept + flag    |           0.252 |        15.000 |         0.005 |          -0.570 |                 0.028 |
| has_other_cards                  | binary      | 0/1 as is                                | 0/1 as is          |         nan     |       nan     |       nan     |         nan     |               nan     |
| proposed_credit_limit            | binned      | standardise                              | raw                |         nan     |       nan     |         1.046 |           0.681 |                 1.046 |
| foreign_request                  | binary      | 0/1 as is                                | 0/1 as is          |         nan     |       nan     |       nan     |         nan     |               nan     |
| source                           | categorical | one-hot, 2 columns                       | category, 2 levels |         nan     |       nan     |       nan     |         nan     |               nan     |
| session_length_in_minutes        | continuous  | NaN -> median + flag, log1p, standardise | NaN kept + flag    |           0.002 |         1.868 |         3.081 |           0.500 |                 0.502 |
| device_os                        | categorical | one-hot, 5 columns                       | category, 5 levels |         nan     |       nan     |       nan     |         nan     |               nan     |
| keep_alive_session               | binary      | 0/1 as is                                | 0/1 as is          |         nan     |       nan     |       nan     |         nan     |               nan     |
| device_distinct_emails_8w        | continuous  | NaN -> median + flag, standardise        | NaN kept + flag    |           0.000 |         1.000 |         2.654 |          -0.615 |                 2.654 |

linear mode: 56 feature columns
tree mode: 35 feature columns

share of accounts with each missing flag, by group (months 0-4; group sizes normal 148,536, fake 335, real mule 121):
|                                      |   normal |   fake |   real mule |   accounts flagged |
|:-------------------------------------|---------:|-------:|------------:|-------------------:|
| prev_address_months_count_missing    |   0.7439 | 0.9194 |      0.6860 |            110,891 |
| current_address_months_count_missing |   0.0037 | 0.0000 |      0.0083 |                545 |
| intended_balcon_amount_missing       |   0.7427 | 0.8716 |      0.7355 |            110,702 |
| bank_months_count_missing            |   0.2518 | 0.3015 |      0.2645 |             37,528 |
| session_length_in_minutes_missing    |   0.0023 | 0.0000 |      0.0000 |                342 |
| device_distinct_emails_8w_missing    |   0.0003 | 0.0000 |      0.0000 |                 42 |

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
  ok  velocity_6h is never negative after cleaning (tree mode) (12 rows clipped, all in months [5, 6, 7])
  ok  every logged column is less lopsided after log1p on months 0-4 (decision 10 Oct 2026) (6 logged)
  ok  binary columns hold only 0 and 1
  ok  linear: each categorical has at most one level set per account
  ok  linear: standardised columns have mean 0 and spread 1 on months 0-4 (worst |mean| 6.7e-16, worst |sd - 1| 2.2e-16)
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

done in 4s