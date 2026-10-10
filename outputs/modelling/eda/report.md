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
|                              |   share_negative |       min | note                                                |
|:-----------------------------|-----------------:|----------:|:----------------------------------------------------|
| intended_balcon_amount       |           0.7299 |  -12.1995 | missing code -> NaN + flag                          |
| prev_address_months_count    |           0.6944 |   -1.0000 | missing code -> NaN + flag                          |
| bank_months_count            |           0.2550 |   -1.0000 | missing code -> NaN + flag                          |
| credit_risk_score            |           0.0181 | -165.0000 | real values: the score runs negative; keep as is    |
| current_address_months_count |           0.0040 |   -1.0000 | missing code -> NaN + flag                          |
| session_length_in_minutes    |           0.0018 |   -1.0000 | missing code -> NaN + flag                          |
| device_distinct_emails_8w    |           0.0004 |   -1.0000 | missing code -> NaN + flag                          |
| velocity_6h                  |           0.0000 |   25.5402 | 9 rows of generator noise at full size -> clip at 0 |

categorical levels:
|                   |   levels | values                                |
|:------------------|---------:|:--------------------------------------|
| payment_type      |        5 | AA, AB, AC, AD, AE                    |
| employment_status |        7 | CA, CB, CC, CD, CE, CF, CG            |
| housing_status    |        7 | BA, BB, BC, BD, BE, BF, BG            |
| source            |        2 | INTERNET, TELEAPP                     |
| device_os         |        5 | linux, macintosh, other, windows, x11 |

skew of numeric columns (|skew| > 2 -> log1p for logistic regression and the autoencoder):
|                              |    skew |    distinct |
|:-----------------------------|--------:|------------:|
| days_since_request           |  8.8619 | 164523.0000 |
| foreign_request              |  5.9194 |      2.0000 |
| prev_address_months_count    |  3.9720 |    355.0000 |
| session_length_in_minutes    |  3.2291 | 164429.0000 |
| bank_branch_count_8w         |  2.6812 |   2202.0000 |
| intended_balcon_amount       |  2.4315 | 164681.0000 |
| phone_mobile_valid           | -2.3427 |      2.0000 |
| device_distinct_emails_8w    |  2.3270 |      4.0000 |
| current_address_months_count |  1.4118 |    412.0000 |
| has_other_cards              |  1.3791 |      2.0000 |
| zip_count_4w                 |  1.3442 |   5930.0000 |
| proposed_credit_limit        |  1.1978 |     12.0000 |

application columns with |Spearman| > 0.5 (candidates to drop one of, for logistic regression):
| a                         | b                            |   spearman |
|:--------------------------|:-----------------------------|-----------:|
| prev_address_months_count | current_address_months_count |    -0.6600 |
| credit_risk_score         | proposed_credit_limit        |     0.6427 |
| bank_branch_count_8w      | bank_months_count            |     0.5105 |


==============================================================================
2. APPLICATION COLUMNS VS is_launderer (months 0-4), BY HIDDEN TYPE
==============================================================================
univariate AUC vs the label (0.5 = none), for all launderers, fake accounts and real-customer mules,
with Mann-Whitney / Welch t (numeric) or chi-square + Cramer's V (categorical). Categorical AUC uses the
level's launderer rate as the score. A small p with 400 positives is support, not proof of usefulness.
| feature                          | kind        |   auc_all |   auc_fake_vs_normal |   auc_real_vs_normal |   mann_whitney_p |   chi2_p |   cramers_v |
|:---------------------------------|:------------|----------:|---------------------:|---------------------:|-----------------:|---------:|------------:|
| housing_status                   | categorical |    0.6422 |               0.6727 |               0.5701 |         nan      |   0.0000 |      0.0332 |
| device_os                        | categorical |    0.6385 |               0.6884 |               0.5205 |         nan      |   0.0000 |      0.0284 |
| keep_alive_session               | numeric     |    0.3984 |               0.3728 |               0.4589 |           0.0000 | nan      |    nan      |
| current_address_months_count     | numeric     |    0.6000 |               0.6453 |               0.4926 |           0.0000 | nan      |    nan      |
| date_of_birth_distinct_emails_4w | numeric     |    0.4074 |               0.3663 |               0.5048 |           0.0000 | nan      |    nan      |
| credit_risk_score                | numeric     |    0.5798 |               0.6241 |               0.4750 |           0.0000 | nan      |    nan      |
| proposed_credit_limit            | numeric     |    0.5700 |               0.6057 |               0.4853 |           0.0000 | nan      |    nan      |
| prev_address_months_count        | numeric     |    0.4349 |               0.4005 |               0.5165 |           0.0000 | nan      |    nan      |
| employment_status                | categorical |    0.5642 |               0.5942 |               0.4930 |         nan      |   0.0000 |      0.0151 |
| payment_type                     | categorical |    0.5642 |               0.6106 |               0.4541 |         nan      |   0.0000 |      0.0131 |
| phone_home_valid                 | numeric     |    0.4422 |               0.4435 |               0.4393 |           0.0000 | nan      |    nan      |
| income                           | numeric     |    0.5546 |               0.6008 |               0.4453 |           0.0000 | nan      |    nan      |
| bank_branch_count_8w             | numeric     |    0.4482 |               0.4129 |               0.5318 |           0.0001 | nan      |    nan      |
| has_other_cards                  | numeric     |    0.4489 |               0.4418 |               0.4659 |           0.0000 | nan      |    nan      |
| name_email_similarity            | numeric     |    0.4523 |               0.4325 |               0.4993 |           0.0004 | nan      |    nan      |
| device_distinct_emails_8w        | numeric     |    0.5364 |               0.5521 |               0.4993 |           0.0000 | nan      |    nan      |

17 of 29 columns significant at p < 0.01 against all launderers; columns with |AUC-0.5| >= 0.05 for real-customer mules: ['housing_status', 'phone_home_valid', 'income', 'customer_age', 'bank_months_count']
  -> if that last list is empty or short, real-customer mules are indistinguishable at opening (the
     'ceiling on earliness' trap): the application can only buy a head start on fake accounts.

==============================================================================
3. A WEEK OF ACTIVITY, BY WEEK SINCE OPENING (weeks 0-26) + LABEL MATURITY
==============================================================================
account-week panel for months (0, 1, 2, 3, 4), weeks 0-26: 4,450,113 rows in 20s
medians per account-week, launderers (1) vs normal (0), weeks 0, 1, 4, 8, 12, 26:
|         |         n |   rows_med |   in_med |   out_med |   payers_avg |   payees_med |   cash_avg |   internal_avg |   abroad_avg |   new_payer_avg |   out_24h_avg |
|:--------|----------:|-----------:|---------:|----------:|-------------:|-------------:|-----------:|---------------:|-------------:|----------------:|--------------:|
| (0, 0)  | 164364.00 |       6.00 |    30.44 |    662.59 |         0.63 |         3.00 |       0.08 |           0.01 |         0.00 |            1.00 |          0.56 |
| (0, 1)  |    455.00 |       5.00 |     0.00 |    717.53 |         0.60 |         3.00 |       0.07 |           0.01 |         0.00 |            1.00 |          0.71 |
| (1, 0)  | 164364.00 |       6.00 |    32.39 |    662.61 |         0.63 |         3.00 |       0.08 |           0.01 |         0.00 |            0.78 |          0.58 |
| (1, 1)  |    455.00 |       6.00 |    40.89 |    701.93 |         0.63 |         3.00 |       0.09 |           0.01 |         0.00 |            0.80 |          0.56 |
| (4, 0)  | 164364.00 |       5.00 |    40.59 |    622.47 |         0.65 |         3.00 |       0.09 |           0.01 |         0.00 |            0.53 |          0.55 |
| (4, 1)  |    455.00 |       5.00 |    59.40 |    718.57 |         0.73 |         3.00 |       0.08 |           0.02 |         0.00 |            0.58 |          0.79 |
| (8, 0)  | 164364.00 |       5.00 |    49.20 |    623.22 |         0.66 |         3.00 |       0.09 |           0.02 |         0.00 |            0.44 |          0.57 |
| (8, 1)  |    455.00 |       5.00 |    42.09 |    697.18 |         0.69 |         3.00 |       0.08 |           0.01 |         0.00 |            0.47 |          0.54 |
| (12, 0) | 164364.00 |       5.00 |    55.62 |    605.25 |         0.68 |         3.00 |       0.09 |           0.02 |         0.00 |            0.46 |          0.55 |
| (12, 1) |    455.00 |       5.00 |   298.24 |    753.00 |         1.06 |         3.00 |       0.09 |           0.04 |         0.01 |            0.54 |          0.50 |
| (26, 0) | 164364.00 |       6.00 |    74.10 |    660.91 |         0.73 |         3.00 |       0.08 |           0.03 |         0.00 |            0.49 |          0.62 |
| (26, 1) |    455.00 |       5.00 |     0.00 |    588.25 |         0.66 |         3.00 |       0.07 |           0.02 |         0.00 |            0.55 |          0.60 |

  -> before any laundering starts, launderers' weeks should look like everyone else's: the simulator gives
     every profile the same normal life. Differences in early weeks come from the application side only.

activity that stops (weeks 0-77): accounts whose last active week is before week 77, and zero-activity weeks
|   is_launderer |   accounts |   stopped_before_week_77 |   zero_activity_weeks |   account_weeks |
|---------------:|-----------:|-------------------------:|----------------------:|----------------:|
|              0 |     164364 |                        1 |                    82 |        12820392 |
|              1 |        455 |                      116 |                  6003 |           35490 |

  -> every open account has at least a weekly card row, so a week with no rows means the account is closed,
     and in this data only the bank's rules close accounts, only after a confirmed (true) alert. Weeks after a
     closure are therefore a label giveaway that a live model never sees (the harness removes closed accounts
     from the pool as caught). Phase 3/4 must drop account-weeks after closure from TRAINING; the screen below
     already leaves them out (rows with n_rows = 0). Decision needed: let labels() return 'open at week w' for
     months 0-5, since a bank knows which accounts it closed.

label maturity on training accounts (2s): launderers labelled under each label, by week
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
Account-weeks with activity only (closed accounts left out); AUCs with fewer than 20 positives shown as NaN.
AUC against mule_by_day (main label) by week since opening; 0.5 = no signal:
| feature             |      4 |      8 |     12 |     26 |   max_sep |
|:--------------------|-------:|-------:|-------:|-------:|----------:|
| n_rows_cum          | 0.4945 | 0.5057 | 0.6079 | 0.7087 |    0.2087 |
| money_in_cum        | 0.5787 | 0.5909 | 0.6505 | 0.6689 |    0.1689 |
| self_vs_past_in     | 0.4976 | 0.4981 | 0.4680 | 0.3558 |    0.1442 |
| money_out           | 0.5674 | 0.5721 | 0.6431 | 0.5704 |    0.1431 |
| self_vs_past_payers | 0.4968 | 0.5007 | 0.4684 | 0.3594 |    0.1406 |
| med_delay_min       | 0.5053 | 0.4787 | 0.3722 | 0.4649 |    0.1278 |
| n_rows              | 0.5018 | 0.5031 | 0.6127 | 0.5141 |    0.1127 |
| peer_ratio_in       | 0.5313 | 0.5031 | 0.5978 | 0.5163 |    0.0978 |
| n_payers            | 0.5048 | 0.5062 | 0.5978 | 0.5224 |    0.0978 |
| income_fit_in       | 0.5026 | 0.5002 | 0.5953 | 0.5097 |    0.0953 |
| money_in            | 0.5031 | 0.5002 | 0.5953 | 0.5095 |    0.0953 |
| max_in              | 0.4998 | 0.4979 | 0.5812 | 0.5075 |    0.0812 |
| n_payees            | 0.5074 | 0.5044 | 0.5583 | 0.5062 |    0.0583 |
| passthrough_wk      | 0.5086 | 0.5109 | 0.4535 | 0.5017 |    0.0465 |
| new_payer_share     | 0.5036 | 0.5047 | 0.4581 | 0.4979 |    0.0419 |
| night_share         | 0.4908 | 0.5145 | 0.5320 | 0.5012 |    0.0320 |
| internal_share      | 0.5023 | 0.4860 | 0.5239 | 0.4867 |    0.0239 |
| out_24h_share       | 0.5178 | 0.5062 | 0.4902 | 0.5051 |    0.0178 |
| cash_share          | 0.4952 | 0.4835 | 0.4870 | 0.4974 |    0.0165 |
| out_1h_share        | 0.5074 | 0.5106 | 0.4994 | 0.4977 |    0.0106 |
| abroad_share        | 0.4978 | 0.4978 | 0.5096 | 0.5016 |    0.0096 |
| hr_share            | 0.5009 | 0.4994 | 0.5038 | 0.4994 |    0.0038 |

AUC against started_by_day (accounts whose laundering has started vs normal):
launderers started by week: {4: 12, 8: 31, 12: 167, 26: 277} (real-customer mules: {4: 12, 8: 19, 12: 18, 26: 32})
| feature             |   4 |      8 |     12 |     26 |
|:--------------------|----:|-------:|-------:|-------:|
| n_rows_cum          | nan | 0.8642 | 0.7745 | 0.7088 |
| money_in_cum        | nan | 0.6488 | 0.7302 | 0.6689 |
| self_vs_past_in     | nan | 0.3994 | 0.4189 | 0.3558 |
| money_out           | nan | 0.7329 | 0.7480 | 0.5703 |
| self_vs_past_payers | nan | 0.4152 | 0.4363 | 0.3594 |
| med_delay_min       | nan | 0.2110 | 0.2287 | 0.4649 |
| n_rows              | nan | 0.8045 | 0.7462 | 0.5141 |
| peer_ratio_in       | nan | 0.7071 | 0.6836 | 0.5163 |
| n_payers            | nan | 0.7580 | 0.7031 | 0.5224 |
| income_fit_in       | nan | 0.7084 | 0.6871 | 0.5097 |
| money_in            | nan | 0.7088 | 0.6869 | 0.5095 |
| max_in              | nan | 0.6812 | 0.6585 | 0.5075 |
| n_payees            | nan | 0.6906 | 0.6483 | 0.5062 |
| passthrough_wk      | nan | 0.3950 | 0.4089 | 0.5017 |
| new_payer_share     | nan | 0.3925 | 0.4109 | 0.4979 |
| night_share         | nan | 0.5638 | 0.5615 | 0.5011 |
| internal_share      | nan | 0.5050 | 0.5587 | 0.4867 |
| out_24h_share       | nan | 0.4484 | 0.4761 | 0.5051 |
| cash_share          | nan | 0.5022 | 0.4595 | 0.4974 |
| out_1h_share        | nan | 0.4771 | 0.4928 | 0.4977 |
| abroad_share        | nan | 0.4963 | 0.5200 | 0.5016 |
| hr_share            | nan | 0.4994 | 0.5083 | 0.4994 |

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
| max_in              | peer_ratio_in       |     0.9977 |
| money_in            | self_vs_past_in     |     0.9188 |
| self_vs_past_in     | income_fit_in       |     0.9187 |
| self_vs_past_in     | peer_ratio_in       |     0.9180 |
| max_in              | self_vs_past_in     |     0.9178 |
| n_payers            | self_vs_past_payers |     0.9056 |
| money_in            | n_payers            |     0.8791 |
| n_payers            | income_fit_in       |     0.8791 |
| n_payers            | peer_ratio_in       |     0.8787 |
| self_vs_past_in     | self_vs_past_payers |     0.8758 |
| max_in              | n_payers            |     0.8728 |
| money_in            | passthrough_wk      |    -0.8587 |
| passthrough_wk      | income_fit_in       |    -0.8569 |
| max_in              | passthrough_wk      |    -0.8554 |
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

|   src_l |        edges |    accounts |   launderer_share_of_payees |
|--------:|-------------:|------------:|----------------------------:|
|       0 | 1254238.0000 | 164270.0000 |                      0.0023 |
|       1 |    2994.0000 |    433.0000 |                      0.0544 |

base launderer rate in months 0-4: 0.2761%. A launderer's internal payees are launderers 5.44% of the time (20x the base rate); a normal account's 0.226%.
  -> this is the L8 homophily test. A ratio well above 1 says the chains and the big network leave a trace in
     the public transactions, so graph features (Phase 6) have something to find. Only edges with both ends
     in months 0-4 are counted, so no test-month account enters the test.

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
8. PROPOSED FEATURE LIST FOR PHASE 3 (the team fixes it at the gate)
==============================================================================
| feature             |   best_sep_mule |   best_sep_started |   nonnull | proposal                                       |
|:--------------------|----------------:|-------------------:|----------:|:-----------------------------------------------|
| n_rows_cum          |          0.2087 |             0.3642 |    1.0000 | keep                                           |
| n_rows              |          0.1127 |             0.3045 |    1.0000 | keep                                           |
| med_delay_min       |          0.1278 |             0.2890 |    0.9999 | keep                                           |
| n_payers            |          0.0978 |             0.2580 |    1.0000 | keep                                           |
| money_out           |          0.1431 |             0.2480 |    1.0000 | keep                                           |
| money_in_cum        |          0.1689 |             0.2302 |    1.0000 | keep                                           |
| money_in            |          0.0953 |             0.2088 |    1.0000 | keep                                           |
| income_fit_in       |          0.0953 |             0.2084 |    1.0000 | keep                                           |
| peer_ratio_in       |          0.0978 |             0.2071 |    0.9712 | keep                                           |
| n_payees            |          0.0583 |             0.1906 |    1.0000 | keep                                           |
| max_in              |          0.0812 |             0.1812 |    1.0000 | keep                                           |
| self_vs_past_in     |          0.1442 |             0.1442 |    0.3740 | keep                                           |
| self_vs_past_payers |          0.1406 |             0.1406 |    0.3062 | keep                                           |
| new_payer_share     |          0.0419 |             0.1075 |    0.5137 | keep                                           |
| passthrough_wk      |          0.0465 |             0.1050 |    0.5246 | keep                                           |
| night_share         |          0.0320 |             0.0638 |    1.0000 | keep; expected: same hour weights for everyone |
| internal_share      |          0.0239 |             0.0587 |    1.0000 | keep                                           |
| out_24h_share       |          0.0178 |             0.0516 |    0.5246 | keep                                           |
| cash_share          |          0.0165 |             0.0405 |    1.0000 | drop (no signal at any screened week)          |
| out_1h_share        |          0.0106 |             0.0229 |    0.5246 | drop (no signal at any screened week)          |
| abroad_share        |          0.0096 |             0.0200 |    1.0000 | drop (no signal at any screened week)          |
| hr_share            |          0.0038 |             0.0083 |    1.0000 | drop (no signal at any screened week)          |

Speed features as screened here (out_1h_share, out_24h_share) are swamped by everyday outflows: the ASOF join
pairs every card, direct-debit or cash row with the latest payment in, so normal accounts also 'forward' about
half of their money in within a day. Phase 3 should define them as transfers OUT (ACH, Cross-border) within
1h / 24h after each transfer IN, capped at that payment's amount; med_delay_min already carries the signal.
abroad_share, hr_share and cash_share are rare events at week level (launderers send ~1.6% of transfers abroad);
keep them cumulative rather than weekly if kept at all.
Application columns: keep all 29 after Phase 2 cleaning; LightGBM ignores useless ones and L1 logistic
regression drops them. Candidate pairs above |0.8| correlation: keep one for the logistic model.

done in 34s