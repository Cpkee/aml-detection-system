DATA   : data/v1
REPORT : outputs/modelling/eda/v1_50k
months : (0, 1, 2, 3, 4) (training); month 5 kept for calibration, 6-7 closed
pandas 3.0.6 | python 3.12.15

==============================================================================
1. APPLICATION TABLE (input to Phase 2 cleaning)
==============================================================================
accounts in months (0, 1, 2, 3, 4): 33,801; launderers 92 (0.272%); by type: {'fake': 72, 'unwitting': 10, 'witting': 10}
24 numeric and 5 categorical application columns; true NaN: 0

BAF codes: share of rows with a negative value (BAF writes missing as -1 or a negative amount):
|                              |   share_negative |       min | note                                                |
|:-----------------------------|-----------------:|----------:|:----------------------------------------------------|
| intended_balcon_amount       |           0.7284 |  -11.0921 | missing code -> NaN + flag                          |
| prev_address_months_count    |           0.6947 |   -1.0000 | missing code -> NaN + flag                          |
| bank_months_count            |           0.2563 |   -1.0000 | missing code -> NaN + flag                          |
| credit_risk_score            |           0.0174 | -164.0000 | real values: the score runs negative; keep as is    |
| current_address_months_count |           0.0042 |   -1.0000 | missing code -> NaN + flag                          |
| session_length_in_minutes    |           0.0017 |   -1.0000 | missing code -> NaN + flag                          |
| device_distinct_emails_8w    |           0.0003 |   -1.0000 | missing code -> NaN + flag                          |
| velocity_6h                  |           0.0000 |  136.1220 | 9 rows of generator noise at full size -> clip at 0 |

categorical levels:
|                   |   levels | values                                |
|:------------------|---------:|:--------------------------------------|
| payment_type      |        5 | AA, AB, AC, AD, AE                    |
| employment_status |        7 | CA, CB, CC, CD, CE, CF, CG            |
| housing_status    |        7 | BA, BB, BC, BD, BE, BF, BG            |
| source            |        2 | INTERNET, TELEAPP                     |
| device_os         |        5 | linux, macintosh, other, windows, x11 |

skew of numeric columns (|skew| > 2 -> log1p for logistic regression and the autoencoder):
|                              |    skew |   distinct |
|:-----------------------------|--------:|-----------:|
| days_since_request           |  8.8728 | 33792.0000 |
| foreign_request              |  5.8182 |     2.0000 |
| prev_address_months_count    |  3.9902 |   326.0000 |
| session_length_in_minutes    |  3.2229 | 33743.0000 |
| bank_branch_count_8w         |  2.7123 |  1889.0000 |
| intended_balcon_amount       |  2.4292 | 33800.0000 |
| device_distinct_emails_8w    |  2.3752 |     4.0000 |
| phone_mobile_valid           | -2.3743 |     2.0000 |
| current_address_months_count |  1.4123 |   397.0000 |
| zip_count_4w                 |  1.3635 |  4832.0000 |
| has_other_cards              |  1.3493 |     2.0000 |
| proposed_credit_limit        |  1.1695 |    12.0000 |

application columns with |Spearman| > 0.5 (candidates to drop one of, for logistic regression):
| a                         | b                            |   spearman |
|:--------------------------|:-----------------------------|-----------:|
| prev_address_months_count | current_address_months_count |    -0.6637 |
| credit_risk_score         | proposed_credit_limit        |     0.6424 |
| bank_branch_count_8w      | bank_months_count            |     0.5122 |


==============================================================================
2. APPLICATION COLUMNS VS is_launderer (months 0-4), BY HIDDEN TYPE
==============================================================================
univariate AUC vs the label (0.5 = none) with a 95% interval, for all launderers, fake accounts and real-customer
mules, with Mann-Whitney (numeric) or chi-square + Cramer's V (categorical). Categorical AUC uses the level's
launderer rate as the score. Sorted by the largest of the three separations. A small p is support, not proof.
| feature                          | kind        | auc_all             | auc_fake_vs_normal   | auc_real_vs_normal   |   mann_whitney_p |   chi2_p |   cramers_v |
|:---------------------------------|:------------|:--------------------|:---------------------|:---------------------|-----------------:|---------:|------------:|
| housing_status                   | categorical | 0.684 (0.624-0.739) | 0.745 (0.686-0.799)  | 0.463 (0.348-0.570)  |         nan      |   0.0000 |      0.0476 |
| device_os                        | categorical | 0.672 (0.619-0.723) | 0.734 (0.680-0.777)  | 0.450 (0.331-0.570)  |         nan      |   0.0000 |      0.0356 |
| customer_age                     | numeric     | 0.566 (0.505-0.629) | 0.635 (0.574-0.701)  | 0.316 (0.211-0.438)  |           0.0245 | nan      |    nan      |
| credit_risk_score                | numeric     | 0.623 (0.558-0.686) | 0.674 (0.606-0.734)  | 0.443 (0.305-0.592)  |           0.0000 | nan      |    nan      |
| keep_alive_session               | numeric     | 0.371 (0.327-0.420) | 0.343 (0.295-0.392)  | 0.468 (0.368-0.568)  |           0.0000 | nan      |    nan      |
| current_address_months_count     | numeric     | 0.619 (0.572-0.667) | 0.642 (0.593-0.695)  | 0.536 (0.440-0.644)  |           0.0001 | nan      |    nan      |
| date_of_birth_distinct_emails_4w | numeric     | 0.397 (0.336-0.457) | 0.363 (0.296-0.423)  | 0.518 (0.427-0.617)  |           0.0006 | nan      |    nan      |
| income                           | numeric     | 0.590 (0.527-0.649) | 0.634 (0.574-0.697)  | 0.429 (0.305-0.561)  |           0.0026 | nan      |    nan      |
| proposed_credit_limit            | numeric     | 0.604 (0.541-0.653) | 0.634 (0.569-0.702)  | 0.494 (0.395-0.606)  |           0.0001 | nan      |    nan      |
| name_email_similarity            | numeric     | 0.396 (0.344-0.451) | 0.374 (0.307-0.442)  | 0.474 (0.355-0.583)  |           0.0006 | nan      |    nan      |
| prev_address_months_count        | numeric     | 0.411 (0.377-0.445) | 0.401 (0.369-0.437)  | 0.446 (0.369-0.539)  |           0.0003 | nan      |    nan      |
| employment_status                | categorical | 0.554 (0.511-0.601) | 0.590 (0.548-0.633)  | 0.424 (0.330-0.518)  |         nan      |   0.3080 |      0.0145 |
| payment_type                     | categorical | 0.572 (0.521-0.626) | 0.576 (0.516-0.636)  | 0.556 (0.434-0.682)  |         nan      |   0.1583 |      0.0140 |
| phone_home_valid                 | numeric     | 0.447 (0.404-0.496) | 0.438 (0.389-0.493)  | 0.481 (0.381-0.581)  |           0.0373 | nan      |    nan      |
| has_other_cards                  | numeric     | 0.444 (0.411-0.477) | 0.445 (0.410-0.480)  | 0.440 (0.390-0.515)  |           0.0097 | nan      |    nan      |
| bank_branch_count_8w             | numeric     | 0.449 (0.389-0.513) | 0.440 (0.370-0.514)  | 0.482 (0.350-0.606)  |           0.0896 | nan      |    nan      |
| velocity_6h                      | numeric     | 0.497 (0.438-0.559) | 0.482 (0.419-0.549)  | 0.554 (0.420-0.673)  |           0.9334 | nan      |    nan      |
| velocity_24h                     | numeric     | 0.503 (0.452-0.557) | 0.491 (0.432-0.554)  | 0.546 (0.416-0.656)  |           0.9188 | nan      |    nan      |
| phone_mobile_valid               | numeric     | 0.477 (0.434-0.515) | 0.482 (0.441-0.524)  | 0.459 (0.359-0.534)  |           0.1754 | nan      |    nan      |
| email_is_free                    | numeric     | 0.536 (0.487-0.585) | 0.539 (0.476-0.594)  | 0.526 (0.426-0.626)  |           0.1667 | nan      |    nan      |
| device_distinct_emails_8w        | numeric     | 0.522 (0.484-0.559) | 0.517 (0.469-0.565)  | 0.538 (0.489-0.613)  |           0.0296 | nan      |    nan      |
| zip_count_4w                     | numeric     | 0.523 (0.465-0.582) | 0.536 (0.465-0.603)  | 0.476 (0.361-0.587)  |           0.4500 | nan      |    nan      |
| days_since_request               | numeric     | 0.490 (0.426-0.554) | 0.496 (0.428-0.567)  | 0.466 (0.295-0.625)  |           0.7326 | nan      |    nan      |
| intended_balcon_amount           | numeric     | 0.484 (0.434-0.535) | 0.482 (0.431-0.538)  | 0.491 (0.384-0.593)  |           0.5878 | nan      |    nan      |
| velocity_4w                      | numeric     | 0.488 (0.436-0.539) | 0.486 (0.427-0.548)  | 0.494 (0.391-0.602)  |           0.6834 | nan      |    nan      |
| session_length_in_minutes        | numeric     | 0.488 (0.433-0.544) | 0.486 (0.424-0.547)  | 0.492 (0.371-0.617)  |           0.6800 | nan      |    nan      |
| foreign_request                  | numeric     | 0.503 (0.486-0.524) | 0.507 (0.486-0.535)  | 0.486 (nan-nan)      |           0.7475 | nan      |    nan      |
| bank_months_count                | numeric     | 0.505 (0.433-0.572) | 0.510 (0.431-0.584)  | 0.488 (0.342-0.635)  |           0.8692 | nan      |    nan      |
| source                           | categorical | 0.507 (0.496-0.524) | 0.510 (0.496-0.531)  | 0.496 (nan-nan)      |         nan      |   0.3103 |      0.0055 |

11 of 29 columns significant at p < 0.01 against all launderers.
columns whose 95% interval excludes 0.5, by separation: fake accounts 15: ['housing_status', 'device_os', 'customer_age', 'credit_risk_score', 'keep_alive_session', 'current_address_months_count', 'date_of_birth_distinct_emails_4w', 'income', 'proposed_credit_limit', 'name_email_similarity', 'prev_address_months_count', 'employment_status', 'payment_type', 'phone_home_valid', 'has_other_cards']
real-customer mules 1: ['customer_age']
  -> the two types separate on different columns, sometimes in opposite directions: customer_age has AUC 0.64 for fakes and 0.32 for real mules, 0.57 for all.
     Real mules' age signal comes from the simulator setting profiles.real_mule_age_weights (Cifas mule ages): an
     assumption the report must name. Age is allowed as a model input (decision 19 Oct 2026); Variant II tests fairness.

==============================================================================
3. A WEEK OF ACTIVITY, BY WEEK SINCE OPENING (weeks 0-26) + LABEL MATURITY
==============================================================================
account-week panel for months (0, 1, 2, 3, 4), weeks 0-26: 912,627 rows in 2s
medians per account-week, launderers (1) vs normal (0), weeks 0, 1, 4, 8, 12, 26:
|         |        n |   rows_med |   in_med |   out_med |   payers_avg |   payees_med |   cash_avg |   internal_avg |   abroad_avg |   new_payer_avg |   out_24h_avg |
|:--------|---------:|-----------:|---------:|----------:|-------------:|-------------:|-----------:|---------------:|-------------:|----------------:|--------------:|
| (0, 0)  | 33709.00 |       6.00 |    34.04 |    665.96 |         0.63 |         3.00 |       0.08 |           0.01 |         0.00 |            1.00 |          0.57 |
| (0, 1)  |    92.00 |       5.00 |    67.87 |    694.62 |         0.64 |         3.00 |       0.08 |           0.00 |         0.01 |            1.00 |          0.64 |
| (1, 0)  | 33709.00 |       6.00 |    34.20 |    662.90 |         0.63 |         3.00 |       0.08 |           0.01 |         0.00 |            0.78 |          0.59 |
| (1, 1)  |    92.00 |       5.00 |     0.00 |    672.26 |         0.54 |         3.00 |       0.08 |           0.01 |         0.00 |            0.82 |          0.60 |
| (4, 0)  | 33709.00 |       5.00 |    40.30 |    622.68 |         0.65 |         3.00 |       0.09 |           0.01 |         0.00 |            0.53 |          0.58 |
| (4, 1)  |    92.00 |       5.00 |    16.69 |    717.95 |         0.61 |         3.00 |       0.11 |           0.02 |         0.00 |            0.47 |          0.40 |
| (8, 0)  | 33709.00 |       5.00 |    49.60 |    623.44 |         0.67 |         3.00 |       0.09 |           0.02 |         0.00 |            0.45 |          0.56 |
| (8, 1)  |    92.00 |       5.00 |     6.96 |    755.77 |         0.72 |         3.00 |       0.10 |           0.03 |         0.01 |            0.55 |          0.48 |
| (12, 0) | 33709.00 |       5.00 |    57.01 |    607.78 |         0.68 |         3.00 |       0.09 |           0.02 |         0.00 |            0.46 |          0.58 |
| (12, 1) |    92.00 |       5.00 |   163.79 |    702.62 |         1.32 |         2.00 |       0.07 |           0.04 |         0.00 |            0.68 |          0.54 |
| (26, 0) | 33709.00 |       6.00 |    74.89 |    659.46 |         0.73 |         3.00 |       0.08 |           0.03 |         0.00 |            0.49 |          0.61 |
| (26, 1) |    92.00 |       5.00 |     0.00 |    586.38 |         0.62 |         3.00 |       0.06 |           0.03 |         0.01 |            0.46 |          0.33 |

  -> before any laundering starts, launderers' weeks should look like everyone else's: the simulator gives
     every profile the same normal life. Differences in early weeks come from the application side only.

activity that stops (weeks 0-77): accounts whose last active week is before week 77, and zero-activity weeks
|   is_launderer |   accounts |   stopped_before_week_77 |   zero_activity_weeks |   account_weeks |
|---------------:|-----------:|-------------------------:|----------------------:|----------------:|
|              0 |      33709 |                        0 |                    15 |         2629302 |
|              1 |         92 |                       23 |                  1123 |            7176 |

  -> 23 of 92 launderers stop early, against 0 normal account(s). Only the bank's rules close accounts, only after a
     confirmed (true) alert, so weeks after a closure are a label giveaway a live model never sees (the harness
     counts closed accounts as caught). A zero-row week is not a clean closure test: normal accounts have 15 too.
     labels() returns open_by_day (decision 10 Oct 2026: 0 once the bank has closed the account; a bank knows its
     closures). The screen below and Phase 3/4 drop account-weeks with open_by_day = 0.

label maturity on training accounts (1s): launderers labelled under each label, by week
|   week |   mule_by_day |   started_by_day |   is_launderer |
|-------:|--------------:|-----------------:|---------------:|
|      0 |            72 |                0 |             92 |
|      1 |            72 |                0 |             92 |
|      4 |            72 |                0 |             92 |
|      8 |            72 |                4 |             92 |
|     12 |            73 |               47 |             92 |
|     17 |            75 |               75 |             92 |
|     26 |            77 |               77 |             92 |
|     39 |            80 |               80 |             92 |
|     52 |            82 |               82 |             92 |
|     78 |            92 |               92 |             92 |


==============================================================================
4. WHEN LAUNDERING STARTS ON THE WEEKLY CLOCK (training launderers)
==============================================================================
| profile   |   count |   min |   10% |   50% |   90% |   max |
|:----------|--------:|------:|------:|------:|------:|------:|
| fake      |      72 |     8 |     9 |    11 |    16 |    17 |
| unwitting |      10 |    10 |    14 |    42 |    70 |    72 |
| witting   |      10 |    15 |    20 |    56 |    71 |    73 |

launderers whose start lies inside the main horizon (week <= 26): 77 of 92; by type: {'fake': 72, 'unwitting': 3, 'witting': 2}
  -> weeks before an account's start week can only be won on application data (fake accounts) or not at all
     (real-customer mules). Report 'days earlier' separately for the two.

==============================================================================
5. CANDIDATE FEATURE SCREEN AT WEEKS 4, 8, 12, 26 (months 0-4)
==============================================================================
Accounts the bank has not closed (open_by_day = 1); AUCs with fewer than 20 positives shown as NaN.
AUC against mule_by_day (main label) by week since opening; 0.5 = no signal:
| feature             |      4 |      8 |     12 |     26 |   max_sep |
|:--------------------|-------:|-------:|-------:|-------:|----------:|
| n_rows_cum          | 0.5091 | 0.5378 | 0.6723 | 0.7626 |    0.2626 |
| money_in_cum        | 0.6258 | 0.6176 | 0.6904 | 0.6972 |    0.1972 |
| self_vs_past_in     | 0.4769 | 0.5104 | 0.5871 | 0.6925 |    0.1925 |
| med_delay_min       | 0.5298 | 0.4972 | 0.3384 | 0.4804 |    0.1616 |
| self_vs_past_payers | 0.4801 | 0.5138 | 0.5856 | 0.6590 |    0.1590 |
| out_1h_share        | 0.5097 | 0.4813 | 0.6428 | 0.5374 |    0.1428 |
| money_out           | 0.5762 | 0.6307 | 0.6081 | 0.5639 |    0.1307 |
| out_24h_share       | 0.5106 | 0.4917 | 0.6218 | 0.5307 |    0.1218 |
| passthrough_wk      | 0.5010 | 0.4812 | 0.6157 | 0.5093 |    0.1157 |
| new_payer_share     | 0.4935 | 0.4899 | 0.6155 | 0.5241 |    0.1155 |
| n_payers            | 0.5078 | 0.5023 | 0.6136 | 0.5322 |    0.1136 |
| peer_ratio_in       | 0.5450 | 0.5125 | 0.6030 | 0.5693 |    0.1030 |
| income_fit_in       | 0.5226 | 0.4941 | 0.5929 | 0.5690 |    0.0929 |
| money_in            | 0.5222 | 0.4923 | 0.5919 | 0.5690 |    0.0919 |
| max_in              | 0.5224 | 0.4907 | 0.5734 | 0.5652 |    0.0734 |
| n_rows              | 0.5344 | 0.5586 | 0.5409 | 0.4970 |    0.0586 |
| cash_share          | 0.5169 | 0.5151 | 0.4520 | 0.4468 |    0.0532 |
| night_share         | 0.5014 | 0.5069 | 0.5473 | 0.4780 |    0.0473 |
| n_payees            | 0.5157 | 0.5198 | 0.4696 | 0.5104 |    0.0304 |
| abroad_share        | 0.4960 | 0.5174 | 0.5104 | 0.5048 |    0.0174 |
| internal_share      | 0.5056 | 0.5170 | 0.5137 | 0.5035 |    0.0170 |
| hr_share            | 0.4994 | 0.5065 | 0.5065 | 0.4992 |    0.0065 |

AUC against started_by_day (accounts whose laundering has started vs normal):
launderers started by week: {4: 0, 8: 4, 12: 44, 26: 60} (real-customer mules: {4: 0, 8: 0, 12: 1, 26: 4})
| feature             |   4 |   8 |     12 |     26 |
|:--------------------|----:|----:|-------:|-------:|
| n_rows_cum          | nan | nan | 0.8182 | 0.7625 |
| money_in_cum        | nan | nan | 0.7355 | 0.6972 |
| self_vs_past_in     | nan | nan | 0.6697 | 0.6925 |
| med_delay_min       | nan | nan | 0.2260 | 0.4804 |
| self_vs_past_payers | nan | nan | 0.6563 | 0.6590 |
| out_1h_share        | nan | nan | 0.7537 | 0.5374 |
| money_out           | nan | nan | 0.6763 | 0.5639 |
| out_24h_share       | nan | nan | 0.7259 | 0.5307 |
| passthrough_wk      | nan | nan | 0.7069 | 0.5093 |
| new_payer_share     | nan | nan | 0.6930 | 0.5241 |
| n_payers            | nan | nan | 0.7054 | 0.5322 |
| peer_ratio_in       | nan | nan | 0.6855 | 0.5693 |
| income_fit_in       | nan | nan | 0.6763 | 0.5690 |
| money_in            | nan | nan | 0.6748 | 0.5690 |
| max_in              | nan | nan | 0.6450 | 0.5652 |
| n_rows              | nan | nan | 0.6258 | 0.4970 |
| cash_share          | nan | nan | 0.4627 | 0.4468 |
| night_share         | nan | nan | 0.5760 | 0.4780 |
| n_payees            | nan | nan | 0.5113 | 0.5104 |
| abroad_share        | nan | nan | 0.5188 | 0.5048 |
| internal_share      | nan | nan | 0.5191 | 0.5035 |
| hr_share            | nan | nan | 0.5107 | 0.4992 |

  -> mule_by_day counts fake accounts from week 0 even while their activity is still normal, so activity
     features look weak against it in early weeks by construction. started_by_day shows what activity
     can see once a burst exists; with few starts before week 8, those early AUCs are noisy.
candidate pairs with |Spearman| > 0.8 at week 12 (keep one of each for logistic regression):
| a                   | b                   |   spearman |
|:--------------------|:--------------------|-----------:|
| money_in            | income_fit_in       |     0.9996 |
| money_in            | max_in              |     0.9994 |
| max_in              | income_fit_in       |     0.9990 |
| peer_ratio_in       | income_fit_in       |     0.9971 |
| money_in            | peer_ratio_in       |     0.9969 |
| max_in              | peer_ratio_in       |     0.9964 |
| money_in            | self_vs_past_in     |     0.9178 |
| self_vs_past_in     | income_fit_in       |     0.9171 |
| max_in              | self_vs_past_in     |     0.9169 |
| self_vs_past_in     | peer_ratio_in       |     0.9152 |
| n_payers            | self_vs_past_payers |     0.9072 |
| money_in            | n_payers            |     0.8785 |
| n_payers            | income_fit_in       |     0.8784 |
| n_payers            | peer_ratio_in       |     0.8772 |
| self_vs_past_in     | self_vs_past_payers |     0.8754 |
| max_in              | n_payers            |     0.8722 |
| money_in            | passthrough_wk      |    -0.8604 |
| max_in              | passthrough_wk      |    -0.8573 |
| n_payers            | self_vs_past_in     |     0.8532 |
| passthrough_wk      | income_fit_in       |    -0.8502 |
| n_rows              | n_payees            |     0.8386 |
| passthrough_wk      | peer_ratio_in       |    -0.8385 |
| money_in            | self_vs_past_payers |     0.8302 |
| self_vs_past_payers | income_fit_in       |     0.8298 |
| self_vs_past_payers | peer_ratio_in       |     0.8295 |
| max_in              | self_vs_past_payers |     0.8269 |


==============================================================================
6. SIMULATOR-FINGERPRINT AUDIT + HOMOPHILY TEST
==============================================================================
each candidate feature and the simulator setting it rests on; the 42 sensitivity runs test these settings:
| feature(s)                                   | rests on (configs/sim.yaml)                                                                                              |
|:---------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------|
| out_1h_share / out_24h_share / med_delay_min | laundering.forward_delay_shares (RUSI speed bands); normal accounts have no in->out link at all                          |
| passthrough_wk                               | laundering.holder_keeps (0-10% kept) and the same R4 logic the rules use                                                 |
| n_payers / new_payer_share                   | laundering.shapes senders ('all' = every payment from a new payer); normal.transfers_in_per_month = 1.0                  |
| n_payees                                     | laundering.shapes recipients; normal.transfers_out_per_month                                                             |
| cash_share                                   | laundering.shapes in_kind cash / half_cash; normal.cash_depositor_share 0.06                                             |
| internal_share                               | networks.internal_pieces_share 0.5 (x2 for layered shapes) vs normal.internal_share_of_transfers 0.10                    |
| abroad_share / hr_share                      | laundering.abroad_ratio_vs_normal 3.15 x normal.abroad_sender_share 0.07; high_risk_share_of_cross_border                |
| money_in / max_in / self_vs_past_in          | laundering.out_transfer_mean GBP 532 x shape amount_rel vs income-scaled normal amounts                                  |
| peer_ratio_in / income_fit_in                | normal money in scales with BAF income (ONS fifths); laundering amounts do not -> the ratio is partly a fingerprint      |
| night_share                                  | normal.hour_weights only; laundering uses the same hour weights, so no signal is expected                                |
| application columns                          | profiles.in_window_mix (73% of launderers are BAF fraud rows): the whole application signal rests on this one assumption |

payment network, months 0-4: 258,221 links between 33,801 accounts (92 launderers); mixed links 1,208; launderer-launderer links 35
links per account (the 2xy test assumes these are about equal):
| group     |   link_ends |   accounts |   mean_links |
|:----------|------------:|-----------:|-------------:|
| normal    |      515164 |      33709 |         15.3 |
| launderer |        1278 |         92 |         13.9 |

the homophily test: r clearly below 2xy = launderers link to each other more than chance
|                                                         |   launderer share |   expected mixed share (2xy) |   observed mixed share (r) |   r / 2xy |      z |   p (one-sided, r < 2xy) |   launderer-launderer links expected |   launderer-launderer links found |
|:--------------------------------------------------------|------------------:|-----------------------------:|---------------------------:|----------:|-------:|-------------------------:|-------------------------------------:|----------------------------------:|
| homophily test (x = share of accounts)                  |          0.002722 |                     0.005429 |                   0.004678 |    0.8617 | -5.191 |                1.045e-07 |                                1.913 |                                35 |
| allowing for links per account (x = share of link ends) |          0.002475 |                     0.004937 |                   0.004678 |    0.9476 | -1.877 |                0.03029   |                                1.581 |                                35 |

|   src_l |       edges |   accounts |   launderer_share_of_payees |
|--------:|------------:|-----------:|----------------------------:|
|       0 | 257618.0000 | 33697.0000 |                      0.0023 |
|       1 |    638.0000 |    89.0000 |                      0.0549 |

lift: base launderer rate in months 0-4: 0.2722%. A launderer's internal payees are launderers 5.49% of the time (20x the base rate); a normal account's 0.235%.
  -> homophily test: r = 0.468% vs 2xy = 0.543% (r / 2xy 0.86, z -5.2); allowing for links per account r / expected 0.95, z -1.9.
     r / 2xy looks modest only because launderers are 0.3% of accounts: nearly all their links are mixed links
     either way. The same fact, easier to read: 35 launderer-launderer links vs 2 expected by chance (18x; 22x allowing for links per account), and the 20x lift above.
     So the chains and the big network leave a trace in the public transactions, and graph features (Phase 6)
     have something to find. Only links with both ends in months 0-4 are counted, so no test-month account enters.

==============================================================================
7. BENFORD'S LAW ON ALL AMOUNTS (realism check for comment 1; not a feature)
==============================================================================
|   d |            n |   observed |   benford |
|----:|-------------:|-----------:|----------:|
|   1 | 4755749.0000 |     0.3176 |    0.3010 |
|   2 | 2797316.0000 |     0.1868 |    0.1761 |
|   3 | 1937928.0000 |     0.1294 |    0.1249 |
|   4 | 1362091.0000 |     0.0910 |    0.0969 |
|   5 | 1081320.0000 |     0.0722 |    0.0792 |
|   6 |  907691.0000 |     0.0606 |    0.0669 |
|   7 |  786980.0000 |     0.0525 |    0.0580 |
|   8 |  704703.0000 |     0.0471 |    0.0512 |
|   9 |  642138.0000 |     0.0429 |    0.0458 |

rows 14,975,916; chi-square 64,664 (any large sample rejects); Nigrini MAD 0.0070 (first digit: < 0.006 close, 0.006-0.012 acceptable, 0.012-0.015 marginal, > 0.015 nonconformity)
  -> amounts are lognormal around published medians, so rough conformity is expected; it says the amount
     mix is not absurd, nothing more. Each launderer has 3-15 laundering payments, far too few for Benford.

==============================================================================
8. PROPOSED FEATURE LIST FOR PHASE 3 (the team fixed it on 15 Oct 2026)
==============================================================================
| feature             |   best_sep_mule |   best_sep_started |   looks_separating |   nonnull | proposal                                                                          |
|:--------------------|----------------:|-------------------:|-------------------:|----------:|:----------------------------------------------------------------------------------|
| n_rows_cum          |          0.2626 |             0.3182 |                  2 |    1.0000 | keep                                                                              |
| med_delay_min       |          0.1616 |             0.2740 |                  1 |    0.9999 | keep                                                                              |
| out_1h_share        |          0.1428 |             0.2537 |                  1 |    0.5251 | keep                                                                              |
| money_in_cum        |          0.1972 |             0.2355 |                  4 |    1.0000 | keep                                                                              |
| out_24h_share       |          0.1218 |             0.2259 |                  1 |    0.5251 | keep                                                                              |
| passthrough_wk      |          0.1157 |             0.2069 |                  1 |    0.5251 | keep                                                                              |
| n_payers            |          0.1136 |             0.2054 |                  1 |    1.0000 | keep                                                                              |
| new_payer_share     |          0.1155 |             0.1930 |                  1 |    0.5145 | keep                                                                              |
| self_vs_past_in     |          0.1925 |             0.1925 |                  2 |    0.3810 | keep                                                                              |
| peer_ratio_in       |          0.1030 |             0.1855 |                  1 |    0.9436 | keep                                                                              |
| money_out           |          0.1307 |             0.1763 |                  3 |    1.0000 | keep                                                                              |
| income_fit_in       |          0.0929 |             0.1763 |                  1 |    1.0000 | keep                                                                              |
| money_in            |          0.0919 |             0.1748 |                  1 |    1.0000 | keep                                                                              |
| self_vs_past_payers |          0.1590 |             0.1590 |                  2 |    0.3115 | keep                                                                              |
| max_in              |          0.0734 |             0.1450 |                  1 |    1.0000 | keep                                                                              |
| n_rows              |          0.0586 |             0.1258 |                  1 |    1.0000 | keep                                                                              |
| night_share         |          0.0473 |             0.0760 |                  1 |    1.0000 | keep; the simulator gives everyone the same hour weights (team dropped it 15 Oct) |
| cash_share          |          0.0532 |             0.0532 |                  0 |    1.0000 | drop (no screened week passes both tests)                                         |
| internal_share      |          0.0170 |             0.0191 |                  0 |    0.9999 | drop (no screened week passes both tests)                                         |
| abroad_share        |          0.0174 |             0.0188 |                  0 |    0.9999 | drop (no screened week passes both tests)                                         |
| n_payees            |          0.0304 |             0.0113 |                  0 |    1.0000 | drop (no screened week passes both tests)                                         |
| hr_share            |          0.0065 |             0.0107 |                  0 |    0.9999 | drop (no screened week passes both tests)                                         |

looks_separating: in how many of up to 8 looks (4 weeks x 2 labels) |AUC - 0.5| >= 0.05 and the 95% interval
excludes 0.5. Both tests are needed: rare-event shares (mostly 0) get narrow intervals around tiny effects.
Speed features separate started launderers: best |AUC - 0.5| vs started_by_day 0.25 (out_1h_share) and 0.23 (out_24h_share).
They are NaN in weeks with no money in (set in only 53% of screened account-weeks), and the AUC ranks NaN lowest. Correction 18 Oct 2026: the first version of
this notebook ranked NaN highest by mistake, which made the speed shares look swamped by everyday outflows and led to
a proposal to redefine them; the store keeps this definition (decision 15 Oct 2026).
abroad_share, hr_share and cash_share are rare events at week level (launderers send ~1.6% of transfers abroad);
keep them cumulative rather than weekly if kept at all.
Application columns: keep all 29 after Phase 2 cleaning; LightGBM ignores useless ones and L1 logistic
regression drops them. Candidate pairs above |0.8| correlation: keep one for the logistic model.

done in 5s