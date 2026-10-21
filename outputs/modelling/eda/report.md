DATA   : data/v1_full
REPORT : outputs/modelling/eda
months : (0, 1, 2, 3, 4) (training); month 5 kept for calibration, 6-7 closed
pandas 3.0.6 | python 3.12.15

==============================================================================
1. APPLICATION TABLE (input to Phase 2 cleaning)
==============================================================================
accounts in months (0, 1, 2, 3, 4): 164,819; launderers 455 (0.276%); by type: {'fake': 320, 'unwitting': 69, 'witting': 66}
24 numeric and 5 categorical application columns; true NaN: 0

BAF codes: share of rows with a negative value (BAF writes missing as -1 or a negative amount):
|                              |   share_negative |       min | note                                                  |
|:-----------------------------|-----------------:|----------:|:------------------------------------------------------|
| intended_balcon_amount       |           0.7299 |  -12.1995 | missing code -> NaN + flag                            |
| prev_address_months_count    |           0.6944 |   -1.0000 | missing code -> NaN + flag                            |
| bank_months_count            |           0.2550 |   -1.0000 | missing code -> NaN + flag                            |
| credit_risk_score            |           0.0181 | -165.0000 | real values: the score runs negative; keep as is      |
| current_address_months_count |           0.0040 |   -1.0000 | missing code -> NaN + flag                            |
| session_length_in_minutes    |           0.0018 |   -1.0000 | missing code -> NaN + flag                            |
| device_distinct_emails_8w    |           0.0004 |   -1.0000 | missing code -> NaN + flag                            |
| velocity_6h                  |           0.0000 |   25.5402 | 0 negative rows here; Phase 2 clips at 0 (fixed rule) |

categorical levels:
|                   |   levels | values                                |
|:------------------|---------:|:--------------------------------------|
| payment_type      |        5 | AA, AB, AC, AD, AE                    |
| employment_status |        7 | CA, CB, CC, CD, CE, CF, CG            |
| housing_status    |        7 | BA, BB, BC, BD, BE, BF, BG            |
| source            |        2 | INTERNET, TELEAPP                     |
| device_os         |        5 | linux, macintosh, other, windows, x11 |

skew of numeric columns with more than 2 values (Phase 2 logs a column for the linear models only where log1p
brings its skew closer to 0):
|                                  |   skew |    distinct |
|:---------------------------------|-------:|------------:|
| days_since_request               | 8.8619 | 164523.0000 |
| prev_address_months_count        | 3.9720 |    355.0000 |
| session_length_in_minutes        | 3.2291 | 164429.0000 |
| bank_branch_count_8w             | 2.6812 |   2202.0000 |
| intended_balcon_amount           | 2.4315 | 164681.0000 |
| device_distinct_emails_8w        | 2.3270 |      4.0000 |
| current_address_months_count     | 1.4118 |    412.0000 |
| zip_count_4w                     | 1.3442 |   5930.0000 |
| proposed_credit_limit            | 1.1978 |     12.0000 |
| date_of_birth_distinct_emails_4w | 0.5516 |     39.0000 |
| customer_age                     | 0.5015 |      9.0000 |
| bank_months_count                | 0.4823 |     33.0000 |

application columns with |Spearman| > 0.5 (Phase 2 proposes keeping both of each pair; regularisation handles them):
| a                         | b                            |   spearman |
|:--------------------------|:-----------------------------|-----------:|
| prev_address_months_count | current_address_months_count |    -0.6600 |
| credit_risk_score         | proposed_credit_limit        |     0.6427 |
| bank_branch_count_8w      | bank_months_count            |     0.5105 |


==============================================================================
2. APPLICATION COLUMNS VS is_launderer (months 0-4), BY HIDDEN TYPE
==============================================================================
univariate AUC vs the label (0.5 = none) with a 95% interval, for all launderers, fake accounts and real-customer
mules, with Mann-Whitney (numeric) or chi-square, Cramer's V and information gain (categorical). Categorical AUC uses the level's
launderer rate as the score. Sorted by the largest of the three separations. A small p is support, not proof.
| feature                              | kind         | auc_all             | auc_fake_vs_normal   | auc_real_vs_normal   |   mann_whitney_p |   chi2_p |   cramers_v |   info_gain_bits |
|:-------------------------------------|:-------------|:--------------------|:---------------------|:---------------------|-----------------:|---------:|------------:|-----------------:|
| customer_age                         | numeric      | 0.529 (0.498-0.557) | 0.649 (0.617-0.678)  | 0.246 (0.206-0.284)  |           0.0263 | nan      |    nan      |         nan      |
| device_os                            | categorical  | 0.639 (0.614-0.662) | 0.688 (0.660-0.714)  | 0.520 (0.477-0.560)  |         nan      |   0.0000 |      0.0284 |           0.0005 |
| housing_status                       | categorical  | 0.642 (0.615-0.667) | 0.673 (0.640-0.702)  | 0.570 (0.532-0.608)  |         nan      |   0.0000 |      0.0332 |           0.0006 |
| current_address_months_count         | numeric      | 0.600 (0.575-0.624) | 0.645 (0.618-0.670)  | 0.493 (0.442-0.540)  |           0.0000 | nan      |    nan      |         nan      |
| date_of_birth_distinct_emails_4w     | numeric      | 0.407 (0.380-0.434) | 0.366 (0.334-0.396)  | 0.505 (0.460-0.549)  |           0.0000 | nan      |    nan      |         nan      |
| keep_alive_session                   | numeric      | 0.398 (0.375-0.420) | 0.373 (0.348-0.398)  | 0.459 (0.418-0.500)  |           0.0000 | nan      |    nan      |         nan      |
| credit_risk_score                    | numeric      | 0.580 (0.552-0.607) | 0.624 (0.589-0.656)  | 0.475 (0.432-0.514)  |           0.0000 | nan      |    nan      |         nan      |
| payment_type                         | categorical  | 0.564 (0.538-0.589) | 0.611 (0.581-0.638)  | 0.454 (0.409-0.499)  |         nan      |   0.0000 |      0.0131 |           0.0001 |
| proposed_credit_limit                | numeric      | 0.570 (0.543-0.596) | 0.606 (0.573-0.635)  | 0.485 (0.449-0.524)  |           0.0000 | nan      |    nan      |         nan      |
| income                               | numeric      | 0.555 (0.528-0.580) | 0.601 (0.571-0.628)  | 0.445 (0.400-0.489)  |           0.0000 | nan      |    nan      |         nan      |
| prev_address_months_count            | numeric      | 0.435 (0.416-0.453) | 0.401 (0.384-0.418)  | 0.517 (0.476-0.557)  |           0.0000 | nan      |    nan      |         nan      |
| prev_address_months_count_missing    | missing flag | 0.566 (0.549-0.582) | 0.598 (0.580-0.614)  | 0.490 (0.453-0.527)  |           0.0000 | nan      |    nan      |         nan      |
| employment_status                    | categorical  | 0.564 (0.545-0.582) | 0.594 (0.573-0.614)  | 0.493 (0.455-0.528)  |         nan      |   0.0000 |      0.0151 |           0.0002 |
| bank_branch_count_8w                 | numeric      | 0.448 (0.421-0.474) | 0.413 (0.380-0.443)  | 0.532 (0.486-0.578)  |           0.0001 | nan      |    nan      |         nan      |
| intended_balcon_amount_missing       | missing flag | 0.538 (0.521-0.555) | 0.576 (0.557-0.591)  | 0.450 (0.413-0.491)  |           0.0002 | nan      |    nan      |         nan      |
| bank_months_count_missing            | missing flag | 0.544 (0.521-0.565) | 0.571 (0.545-0.596)  | 0.480 (0.447-0.510)  |           0.0000 | nan      |    nan      |         nan      |
| name_email_similarity                | numeric      | 0.452 (0.425-0.479) | 0.432 (0.397-0.463)  | 0.499 (0.454-0.542)  |           0.0004 | nan      |    nan      |         nan      |
| phone_home_valid                     | numeric      | 0.442 (0.422-0.462) | 0.443 (0.420-0.467)  | 0.439 (0.406-0.476)  |           0.0000 | nan      |    nan      |         nan      |
| has_other_cards                      | numeric      | 0.449 (0.434-0.464) | 0.442 (0.426-0.459)  | 0.466 (0.436-0.495)  |           0.0000 | nan      |    nan      |         nan      |
| intended_balcon_amount               | numeric      | 0.475 (0.449-0.499) | 0.444 (0.416-0.469)  | 0.548 (0.499-0.594)  |           0.0632 | nan      |    nan      |         nan      |
| device_distinct_emails_8w            | numeric      | 0.536 (0.520-0.553) | 0.552 (0.534-0.572)  | 0.499 (0.488-0.514)  |           0.0000 | nan      |    nan      |         nan      |
| bank_months_count                    | numeric      | 0.497 (0.466-0.525) | 0.474 (0.436-0.507)  | 0.550 (0.503-0.597)  |           0.7938 | nan      |    nan      |         nan      |
| velocity_6h                          | numeric      | 0.506 (0.480-0.531) | 0.491 (0.458-0.520)  | 0.541 (0.495-0.585)  |           0.6662 | nan      |    nan      |         nan      |
| phone_mobile_valid                   | numeric      | 0.480 (0.462-0.495) | 0.461 (0.439-0.482)  | 0.523 (0.501-0.545)  |           0.0074 | nan      |    nan      |         nan      |
| email_is_free                        | numeric      | 0.513 (0.490-0.535) | 0.534 (0.507-0.559)  | 0.463 (0.423-0.504)  |           0.2640 | nan      |    nan      |         nan      |
| days_since_request                   | numeric      | 0.478 (0.450-0.504) | 0.465 (0.430-0.495)  | 0.510 (0.462-0.555)  |           0.1052 | nan      |    nan      |         nan      |
| session_length_in_minutes            | numeric      | 0.523 (0.496-0.550) | 0.532 (0.498-0.562)  | 0.503 (0.454-0.550)  |           0.0840 | nan      |    nan      |         nan      |
| velocity_24h                         | numeric      | 0.514 (0.488-0.538) | 0.506 (0.474-0.534)  | 0.532 (0.485-0.575)  |           0.3133 | nan      |    nan      |         nan      |
| zip_count_4w                         | numeric      | 0.515 (0.489-0.540) | 0.514 (0.481-0.543)  | 0.517 (0.470-0.559)  |           0.2761 | nan      |    nan      |         nan      |
| velocity_4w                          | numeric      | 0.507 (0.479-0.532) | 0.509 (0.477-0.538)  | 0.500 (0.449-0.548)  |           0.6298 | nan      |    nan      |         nan      |
| source                               | categorical  | 0.502 (0.500-0.504) | 0.502 (0.499-0.504)  | 0.504 (nan-nan)      |         nan      |   0.3255 |      0.0024 |           0.0000 |
| foreign_request                      | numeric      | 0.501 (0.495-0.509) | 0.502 (0.495-0.512)  | 0.498 (0.487-0.513)  |           0.7626 | nan      |    nan      |         nan      |
| current_address_months_count_missing | missing flag | 0.498 (nan-nan)     | 0.498 (nan-nan)      | 0.498 (nan-nan)      |           0.1733 | nan      |    nan      |         nan      |
| session_length_in_minutes_missing    | missing flag | 0.499 (nan-nan)     | 0.499 (nan-nan)      | 0.499 (nan-nan)      |           0.3641 | nan      |    nan      |         nan      |
| device_distinct_emails_8w_missing    | missing flag | 0.500 (nan-nan)     | 0.500 (nan-nan)      | 0.500 (nan-nan)      |           0.6620 | nan      |    nan      |         nan      |

17 of 29 BAF columns significant at p < 0.01 against all launderers (6 missing flags not counted).
columns whose 95% interval excludes 0.5, by separation: fake accounts 24: ['customer_age', 'device_os', 'housing_status', 'current_address_months_count', 'date_of_birth_distinct_emails_4w', 'keep_alive_session', 'credit_risk_score', 'payment_type', 'proposed_credit_limit', 'income', 'prev_address_months_count', 'prev_address_months_count_missing', 'employment_status', 'bank_branch_count_8w', 'intended_balcon_amount_missing', 'bank_months_count_missing', 'name_email_similarity', 'phone_home_valid', 'has_other_cards', 'intended_balcon_amount', 'device_distinct_emails_8w', 'phone_mobile_valid', 'email_is_free', 'days_since_request']
real-customer mules 10: ['customer_age', 'housing_status', 'keep_alive_session', 'payment_type', 'income', 'intended_balcon_amount_missing', 'phone_home_valid', 'has_other_cards', 'bank_months_count', 'phone_mobile_valid']
  -> the two types separate on different columns, sometimes in opposite directions: customer_age has AUC 0.65 for fakes and 0.25 for real mules, 0.53 for all.
     Real mules' age signal comes from the simulator setting profiles.real_mule_age_weights (Cifas mule ages): an
     assumption the report must name. Age is allowed as a model input (decision 19 Oct 2026); Variant II tests fairness.

==============================================================================
3. A WEEK OF ACTIVITY, BY WEEK SINCE OPENING (weeks 0-26) + LABEL MATURITY
==============================================================================
account-week panel for months (0, 1, 2, 3, 4), weeks 0-26: 4,450,113 rows in 18s

label maturity on training accounts (4s): launderers labelled under each label, by week
|   week |   mule_by_day |   started_by_day |   is_launderer |
|-------:|--------------:|-----------------:|---------------:|
|      0 |           320 |                0 |            455 |
|      1 |           322 |                2 |            455 |
|      4 |           332 |               12 |            455 |
|      8 |           340 |               32 |            455 |
|     12 |           344 |              176 |            455 |
|     17 |           348 |              348 |            455 |
|     26 |           361 |              361 |            455 |
|     39 |           379 |              379 |            455 |
|     52 |           401 |              401 |            455 |
|     78 |           455 |              455 |            455 |


per open account-week, launderers (1) vs normal (0): medians (_med) and means (_avg), weeks 0, 1, 4, 8, 12, 26.
Launderers mix accounts before and after their start, so this table describes; the test below answers.
|         |         n |   rows_med |   in_med |   out_med |   payers_avg |   payees_med |   cash_avg |   internal_avg |   abroad_avg |   new_payer_avg |   out_24h_avg |
|:--------|----------:|-----------:|---------:|----------:|-------------:|-------------:|-----------:|---------------:|-------------:|----------------:|--------------:|
| (0, 0)  | 164364.00 |       6.00 |    30.44 |    662.59 |         0.63 |         3.00 |       0.08 |           0.01 |         0.00 |            1.00 |          0.56 |
| (0, 1)  |    455.00 |       5.00 |     0.00 |    717.53 |         0.60 |         3.00 |       0.07 |           0.01 |         0.00 |            1.00 |          0.71 |
| (1, 0)  | 164364.00 |       6.00 |    32.39 |    662.61 |         0.63 |         3.00 |       0.08 |           0.01 |         0.00 |            0.78 |          0.58 |
| (1, 1)  |    455.00 |       6.00 |    40.89 |    701.93 |         0.63 |         3.00 |       0.09 |           0.01 |         0.00 |            0.80 |          0.56 |
| (4, 0)  | 164364.00 |       5.00 |    40.59 |    622.47 |         0.65 |         3.00 |       0.09 |           0.01 |         0.00 |            0.53 |          0.55 |
| (4, 1)  |    455.00 |       5.00 |    59.40 |    718.57 |         0.73 |         3.00 |       0.08 |           0.02 |         0.00 |            0.58 |          0.79 |
| (8, 0)  | 164364.00 |       5.00 |    49.20 |    623.22 |         0.66 |         3.00 |       0.09 |           0.02 |         0.00 |            0.44 |          0.57 |
| (8, 1)  |    454.00 |       5.00 |    43.41 |    699.10 |         0.69 |         3.00 |       0.08 |           0.01 |         0.00 |            0.47 |          0.54 |
| (12, 0) | 164364.00 |       5.00 |    55.62 |    605.25 |         0.68 |         3.00 |       0.09 |           0.02 |         0.00 |            0.46 |          0.55 |
| (12, 1) |    436.00 |       5.00 |   322.53 |    757.05 |         1.08 |         3.00 |       0.09 |           0.04 |         0.00 |            0.55 |          0.50 |
| (26, 0) | 164364.00 |       6.00 |    74.10 |    660.91 |         0.73 |         3.00 |       0.08 |           0.03 |         0.00 |            0.49 |          0.62 |
| (26, 1) |    371.00 |       6.00 |    93.73 |    719.05 |         0.81 |         4.00 |       0.07 |           0.02 |         0.00 |            0.55 |          0.60 |


before laundering starts: weeks 0-7, launderers before their start week vs normal accounts, one mean per account (fake 320, real mules 135, normal 164,364)
| feature             | fake                | real mule           |
|:--------------------|:--------------------|:--------------------|
| n_rows              | 0.477 (0.445-0.506) | 0.514 (0.465-0.561) |
| money_in            | 0.583 (0.551-0.612) | 0.462 (0.414-0.507) |
| money_out           | 0.568 (0.536-0.596) | 0.463 (0.413-0.508) |
| max_in              | 0.583 (0.551-0.612) | 0.459 (0.411-0.505) |
| n_payers            | 0.493 (0.462-0.521) | 0.481 (0.430-0.528) |
| n_payees            | 0.481 (0.449-0.508) | 0.529 (0.481-0.577) |
| new_payer_share     | 0.483 (0.451-0.512) | 0.487 (0.439-0.534) |
| passthrough_wk      | 0.462 (0.430-0.491) | 0.457 (0.406-0.504) |
| out_1h_share        | 0.489 (0.470-0.508) | 0.473 (0.441-0.503) |
| out_24h_share       | 0.534 (0.499-0.564) | 0.478 (0.428-0.526) |
| med_delay_min       | 0.522 (0.488-0.552) | 0.474 (0.425-0.520) |
| cash_share          | 0.501 (0.467-0.531) | 0.459 (0.409-0.505) |
| internal_share      | 0.495 (0.466-0.522) | 0.480 (0.440-0.522) |
| abroad_share        | 0.491 (0.484-0.501) | 0.494 (0.483-0.509) |
| hr_share            | 0.497 (0.495-0.500) | 0.506 (0.495-0.521) |
| night_share         | 0.481 (0.448-0.512) | 0.496 (0.446-0.543) |
| money_in_cum        | 0.570 (0.538-0.598) | 0.440 (0.390-0.487) |
| n_rows_cum          | 0.472 (0.440-0.501) | 0.449 (0.397-0.499) |
| self_vs_past_in     | 0.513 (0.480-0.543) | 0.483 (0.441-0.527) |
| self_vs_past_payers | 0.505 (0.474-0.534) | 0.508 (0.464-0.553) |
| peer_ratio_in       | 0.572 (0.538-0.602) | 0.460 (0.411-0.506) |
| income_fit_in       | 0.578 (0.546-0.606) | 0.467 (0.418-0.513) |

  -> features with |AUC - 0.5| >= 0.05 and an interval excluding 0.5 before the start: fake 6 of 22 ['money_in', 'money_out', 'max_in', 'money_in_cum', 'peer_ratio_in', 'income_fit_in'], real mules 2 of 22 ['money_in_cum', 'n_rows_cum'].
the same AUCs inside each BAF income band (normal banking scales with BAF income only, src/sim/normal.py):
| group     | feature       |   auc |   auc within income band |
|:----------|:--------------|------:|-------------------------:|
| fake      | money_in      | 0.583 |                    0.508 |
| fake      | money_out     | 0.568 |                    0.478 |
| fake      | max_in        | 0.583 |                    0.507 |
| fake      | money_in_cum  | 0.570 |                    0.497 |
| fake      | peer_ratio_in | 0.572 |                    0.508 |
| fake      | income_fit_in | 0.578 |                    0.509 |
| real mule | money_in_cum  | 0.440 |                    0.465 |
| real mule | n_rows_cum    | 0.449 |                    0.379 |

share in the top BAF income band (0.9): fake 31%, real mules 16%, normal 20%
  -> inside an income band, 7 of 8 gaps fall below 0.05: before laundering starts,
     activity differs through the application's income, which the application already shows. Weeks before an
     account's start can only be won on application data.
     Not explained by income (or too few launderers per band to check): ['n_rows_cum']. With 44 looks, about 2 pass by chance at 95%.

activity that stops (weeks 0-77): accounts whose last active week is before week 77, and zero-activity weeks
|   is_launderer |   accounts |   stopped_before_week_77 |   zero_activity_weeks |   account_weeks |
|---------------:|-----------:|-------------------------:|----------------------:|----------------:|
|              0 |     164364 |                        1 |                    82 |        12820392 |
|              1 |        455 |                      116 |                  6003 |           35490 |

  -> 116 of 455 launderers stop early, against 1 normal account(s). Only the bank's rules close accounts, only after a
     confirmed (true) alert, so weeks after a closure are a label giveaway a live model never sees (the harness
     counts closed accounts as caught). A zero-row week is not a clean closure test: normal accounts have 82 too.
     labels() returns open_by_day (decision 10 Oct 2026: 0 once the bank has closed the account; a bank knows its
     closures). The screen below and Phase 3/4 drop account-weeks with open_by_day = 0.

==============================================================================
4. WHEN LAUNDERING STARTS ON THE WEEKLY CLOCK (training launderers)
==============================================================================
| profile   |   count |   min |   10% |   50% |   90% |   max |
|:----------|--------:|------:|------:|------:|------:|------:|
| fake      |     320 |     8 |     9 |    13 |    16 |    17 |
| unwitting |      69 |     1 |     4 |    42 |    69 |    74 |
| witting   |      66 |     1 |    13 |    47 |    70 |    75 |

launderers whose start lies inside the main horizon (week <= 26): 361 of 455; by type: {'fake': 320, 'unwitting': 25, 'witting': 16}
  -> weeks before an account's start week can only be won on application data (fake accounts) or not at all
     (real-customer mules). Report 'days earlier' separately for the two.

==============================================================================
5. CANDIDATE FEATURE SCREEN AT WEEKS 4, 8, 12, 26 (months 0-4)
==============================================================================
Accounts the bank has not closed (open_by_day = 1); AUCs with fewer than 20 positives shown as NaN.
AUC against mule_by_day (main label) by week since opening; 0.5 = no signal:
| feature             |      4 |      8 |     12 |     26 |   max_sep |
|:--------------------|-------:|-------:|-------:|-------:|----------:|
| n_rows_cum          | 0.4945 | 0.5057 | 0.6036 | 0.7088 |    0.2088 |
| money_in_cum        | 0.5787 | 0.5909 | 0.6453 | 0.6689 |    0.1689 |
| money_out           | 0.5674 | 0.5721 | 0.6422 | 0.5704 |    0.1422 |
| self_vs_past_payers | 0.5124 | 0.5047 | 0.5639 | 0.6421 |    0.1421 |
| self_vs_past_in     | 0.5159 | 0.4980 | 0.5698 | 0.6393 |    0.1393 |
| med_delay_min       | 0.5054 | 0.4787 | 0.3742 | 0.4649 |    0.1258 |
| out_1h_share        | 0.5068 | 0.5091 | 0.6210 | 0.5229 |    0.1210 |
| n_rows              | 0.5018 | 0.5031 | 0.6161 | 0.5141 |    0.1161 |
| out_24h_share       | 0.5172 | 0.5047 | 0.6104 | 0.5303 |    0.1104 |
| n_payers            | 0.5048 | 0.5062 | 0.5980 | 0.5224 |    0.0980 |
| money_in            | 0.5031 | 0.5002 | 0.5970 | 0.5095 |    0.0970 |
| income_fit_in       | 0.5026 | 0.5002 | 0.5969 | 0.5097 |    0.0969 |
| peer_ratio_in       | 0.4787 | 0.4995 | 0.5937 | 0.5077 |    0.0937 |
| max_in              | 0.4998 | 0.4979 | 0.5828 | 0.5075 |    0.0828 |
| new_payer_share     | 0.5080 | 0.5082 | 0.5751 | 0.5255 |    0.0751 |
| passthrough_wk      | 0.5081 | 0.5094 | 0.5732 | 0.5269 |    0.0732 |
| n_payees            | 0.5074 | 0.5044 | 0.5619 | 0.5062 |    0.0619 |
| night_share         | 0.4908 | 0.5146 | 0.5295 | 0.5012 |    0.0295 |
| internal_share      | 0.5023 | 0.4860 | 0.5232 | 0.4867 |    0.0232 |
| cash_share          | 0.4952 | 0.4835 | 0.4872 | 0.4974 |    0.0165 |
| abroad_share        | 0.4978 | 0.4978 | 0.5069 | 0.5016 |    0.0069 |
| hr_share            | 0.5009 | 0.4994 | 0.5024 | 0.4994 |    0.0024 |

AUC against started_by_day (accounts whose laundering has started vs normal):
launderers started by week: {4: 12, 8: 31, 12: 157, 26: 277} (real-customer mules: {4: 12, 8: 19, 12: 18, 26: 32})
| feature             |   4 |      8 |     12 |     26 |
|:--------------------|----:|-------:|-------:|-------:|
| n_rows_cum          | nan | 0.8642 | 0.7761 | 0.7088 |
| money_in_cum        | nan | 0.6488 | 0.7245 | 0.6689 |
| money_out           | nan | 0.7329 | 0.7527 | 0.5703 |
| self_vs_past_payers | nan | 0.6664 | 0.6400 | 0.6421 |
| self_vs_past_in     | nan | 0.6459 | 0.6808 | 0.6393 |
| med_delay_min       | nan | 0.2110 | 0.2236 | 0.4649 |
| out_1h_share        | nan | 0.7833 | 0.7553 | 0.5229 |
| n_rows              | nan | 0.8045 | 0.7617 | 0.5141 |
| out_24h_share       | nan | 0.7546 | 0.7353 | 0.5303 |
| n_payers            | nan | 0.7580 | 0.7102 | 0.5224 |
| money_in            | nan | 0.7088 | 0.6962 | 0.5095 |
| income_fit_in       | nan | 0.7084 | 0.6963 | 0.5097 |
| peer_ratio_in       | nan | 0.7094 | 0.6925 | 0.5077 |
| max_in              | nan | 0.6812 | 0.6668 | 0.5075 |
| new_payer_share     | nan | 0.7096 | 0.6564 | 0.5255 |
| passthrough_wk      | nan | 0.7012 | 0.6651 | 0.5269 |
| n_payees            | nan | 0.6906 | 0.6613 | 0.5062 |
| night_share         | nan | 0.5638 | 0.5582 | 0.5011 |
| internal_share      | nan | 0.5050 | 0.5595 | 0.4867 |
| cash_share          | nan | 0.5022 | 0.4581 | 0.4974 |
| abroad_share        | nan | 0.4964 | 0.5152 | 0.5016 |
| hr_share            | nan | 0.4994 | 0.5057 | 0.4994 |

  -> mule_by_day counts fake accounts from week 0 even while their activity is still normal, so activity
     features look weak against it in early weeks by construction. started_by_day shows what activity
     can see once a burst exists; with few starts before week 8, those early AUCs are noisy.
candidate pairs with |Spearman| > 0.8 at week 12 (keep one of each for logistic regression):
| a                   | b                   |   spearman |
|:--------------------|:--------------------|-----------:|
| money_in            | income_fit_in       |     0.9999 |
| money_in            | max_in              |     0.9994 |
| max_in              | income_fit_in       |     0.9993 |
| peer_ratio_in       | income_fit_in       |     0.9984 |
| money_in            | peer_ratio_in       |     0.9983 |
| max_in              | peer_ratio_in       |     0.9978 |
| money_in            | self_vs_past_in     |     0.9188 |
| self_vs_past_in     | income_fit_in       |     0.9187 |
| self_vs_past_in     | peer_ratio_in       |     0.9180 |
| max_in              | self_vs_past_in     |     0.9177 |
| n_payers            | self_vs_past_payers |     0.9056 |
| money_in            | n_payers            |     0.8791 |
| n_payers            | income_fit_in       |     0.8791 |
| n_payers            | peer_ratio_in       |     0.8787 |
| self_vs_past_in     | self_vs_past_payers |     0.8758 |
| max_in              | n_payers            |     0.8729 |
| money_in            | passthrough_wk      |    -0.8588 |
| passthrough_wk      | income_fit_in       |    -0.8570 |
| max_in              | passthrough_wk      |    -0.8555 |
| n_payers            | self_vs_past_in     |     0.8544 |
| passthrough_wk      | peer_ratio_in       |    -0.8495 |
| n_rows              | n_payees            |     0.8374 |
| money_in            | self_vs_past_payers |     0.8323 |
| self_vs_past_payers | income_fit_in       |     0.8322 |
| self_vs_past_payers | peer_ratio_in       |     0.8318 |
| max_in              | self_vs_past_payers |     0.8287 |


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

payment network, months 0-4: 1,257,205 links between 164,814 accounts (450 launderers); mixed links 5,663; launderer-launderer links 163
links per account (the 2xy test assumes these are about equal):
| group     |   link_ends |   accounts |   mean_links |
|:----------|------------:|-----------:|-------------:|
| normal    |     2508421 |     164364 |         15.3 |
| launderer |        5989 |        450 |         13.3 |

the homophily test: r clearly below 2xy = launderers link to each other more than chance
|                                                         |   launderer share |   expected mixed share (2xy) |   observed mixed share (r) |   r / 2xy |       z |   p (one-sided, r < 2xy) |   launderer-launderer links expected |   launderer-launderer links found |
|:--------------------------------------------------------|------------------:|-----------------------------:|---------------------------:|----------:|--------:|-------------------------:|-------------------------------------:|----------------------------------:|
| homophily test (x = share of accounts)                  |          0.00273  |                     0.005446 |                   0.004504 |    0.8271 | -14.34  |                5.972e-47 |                                9.372 |                               163 |
| allowing for links per account (x = share of link ends) |          0.002382 |                     0.004752 |                   0.004504 |    0.9478 |  -4.043 |                2.643e-05 |                                7.133 |                               163 |

label-shuffle test (1,000 shuffles): mixed links 5,663 observed vs 6,843 on average (range 6,601-7,097), p = 0.0010; launderer-launderer links 163 vs 9.6 (range 0-23), p = 0.0010. p = 1/1001 = no shuffle reached the observed value.
launderer-launderer links: 1 of 163 begin before both ends have started laundering, 4 before at least one end has.
|   src_l |        edges |    accounts |   launderer_share_of_payees |
|--------:|-------------:|------------:|----------------------------:|
|       0 | 1254238.0000 | 164270.0000 |                      0.0023 |
|       1 |    2994.0000 |    433.0000 |                      0.0544 |

lift: base launderer rate in months 0-4: 0.2761%. A launderer's internal payees are launderers 5.44% of the time (20x the base rate); a normal account's 0.226%.
  -> homophily test: r = 0.450% vs 2xy = 0.545% (r / 2xy 0.83, z -14.3); allowing for links per account r / expected 0.95, z -4.0.
     r / 2xy looks modest only because launderers are 0.3% of accounts: nearly all their links are mixed links
     either way. The same fact, easier to read: 163 launderer-launderer links vs 9 expected by chance (17x; 23x allowing for links per account), and the 20x lift above.
     The shuffle test confirms it without assuming independent links (p = 0.0010). So the chains and the big
     network leave a trace in the public transactions, and graph features (Phase 6) have something to find.
     But the links are made by the laundering itself (1 of 163 exist before both ends start): graph
     features can help find the rest of a network once one member is active or closed, not give a head start
     before the first burst. Only links with both ends in months 0-4 are counted, so no test-month account enters.

==============================================================================
7. BENFORD'S LAW ON ALL AMOUNTS (realism check for comment 1; not a feature)
==============================================================================
|   d |             n |   observed |   benford |
|----:|--------------:|-----------:|----------:|
|   1 | 23179887.0000 |     0.3176 |    0.3010 |
|   2 | 13639835.0000 |     0.1869 |    0.1761 |
|   3 |  9445403.0000 |     0.1294 |    0.1249 |
|   4 |  6629732.0000 |     0.0908 |    0.0969 |
|   5 |  5265947.0000 |     0.0722 |    0.0792 |
|   6 |  4408183.0000 |     0.0604 |    0.0669 |
|   7 |  3819446.0000 |     0.0523 |    0.0580 |
|   8 |  3438397.0000 |     0.0471 |    0.0512 |
|   9 |  3151946.0000 |     0.0432 |    0.0458 |

rows 72,978,776; chi-square 320,829 (any large sample rejects); Nigrini MAD 0.0071 (first digit: < 0.006 close, 0.006-0.012 acceptable, 0.012-0.015 marginal, > 0.015 nonconformity)
  -> amounts are lognormal around published medians, so rough conformity is expected; it says the amount
     mix is not absurd, nothing more. Each launderer has 3-15 laundering payments, far too few for Benford.

==============================================================================
8. PROPOSED FEATURE LIST FOR PHASE 3 (the team fixed it on 15 Oct 2026)
==============================================================================
| feature             |   best_sep_mule |   best_sep_started |   looks_separating |   nonnull | proposal                                                                          |
|:--------------------|----------------:|-------------------:|-------------------:|----------:|:----------------------------------------------------------------------------------|
| n_rows_cum          |          0.2088 |             0.3642 |                  3 |    1.0000 | keep                                                                              |
| n_rows              |          0.1161 |             0.3045 |                  2 |    1.0000 | keep                                                                              |
| med_delay_min       |          0.1258 |             0.2890 |                  2 |    0.9999 | keep                                                                              |
| out_1h_share        |          0.1210 |             0.2833 |                  2 |    0.5246 | keep                                                                              |
| n_payers            |          0.0980 |             0.2580 |                  2 |    1.0000 | keep                                                                              |
| out_24h_share       |          0.1104 |             0.2546 |                  2 |    0.5246 | keep                                                                              |
| money_out           |          0.1422 |             0.2527 |                  4 |    1.0000 | keep                                                                              |
| money_in_cum        |          0.1689 |             0.2245 |                  4 |    1.0000 | keep                                                                              |
| new_payer_share     |          0.0751 |             0.2096 |                  2 |    0.5137 | keep                                                                              |
| peer_ratio_in       |          0.0937 |             0.2094 |                  2 |    0.9712 | keep                                                                              |
| money_in            |          0.0970 |             0.2088 |                  2 |    1.0000 | keep                                                                              |
| income_fit_in       |          0.0969 |             0.2084 |                  2 |    1.0000 | keep                                                                              |
| passthrough_wk      |          0.0732 |             0.2012 |                  2 |    0.5246 | keep                                                                              |
| n_payees            |          0.0619 |             0.1906 |                  2 |    1.0000 | keep                                                                              |
| max_in              |          0.0828 |             0.1812 |                  2 |    1.0000 | keep                                                                              |
| self_vs_past_in     |          0.1393 |             0.1808 |                  3 |    0.3740 | keep                                                                              |
| self_vs_past_payers |          0.1421 |             0.1664 |                  3 |    0.3062 | keep                                                                              |
| night_share         |          0.0295 |             0.0638 |                  1 |    1.0000 | keep; the simulator gives everyone the same hour weights (team dropped it 15 Oct) |
| internal_share      |          0.0232 |             0.0595 |                  1 |    1.0000 | keep                                                                              |
| cash_share          |          0.0165 |             0.0419 |                  0 |    1.0000 | drop (no screened week passes both tests)                                         |
| abroad_share        |          0.0069 |             0.0152 |                  0 |    1.0000 | drop (no screened week passes both tests)                                         |
| hr_share            |          0.0024 |             0.0057 |                  0 |    1.0000 | drop (no screened week passes both tests)                                         |

looks_separating: in how many of up to 8 looks (4 weeks x 2 labels) |AUC - 0.5| >= 0.05 and the 95% interval
excludes 0.5. Both tests are needed: rare-event shares (mostly 0) get narrow intervals around tiny effects.
Speed features separate started launderers: best |AUC - 0.5| vs started_by_day 0.28 (out_1h_share) and 0.25 (out_24h_share).
They are NaN in weeks with no money in (set in only 52% of screened account-weeks), and the AUC ranks NaN lowest. Correction 18 Oct 2026: the first version of
this notebook ranked NaN highest by mistake, which made the speed shares look swamped by everyday outflows and led to
a proposal to redefine them; the store keeps this definition (decision 15 Oct 2026).
abroad_share, hr_share and cash_share are rare events at week level; the store keeps them cumulative (Phase 3).
Application columns: keep all 29 after Phase 2 cleaning; LightGBM ignores useless ones and L1 logistic
regression drops them. Candidate pairs above |0.8| correlation: keep one for the logistic model.

done in 35s