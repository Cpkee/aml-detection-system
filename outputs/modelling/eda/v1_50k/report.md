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
univariate AUC vs the label (0.5 = none), for all launderers, fake accounts and real-customer mules,
with Mann-Whitney / Welch t (numeric) or chi-square + Cramer's V (categorical). Categorical AUC uses the
level's launderer rate as the score. A small p with 400 positives is support, not proof of usefulness.
| feature                          | kind        |   auc_all |   auc_fake_vs_normal |   auc_real_vs_normal |   mann_whitney_p |   chi2_p |   cramers_v |
|:---------------------------------|:------------|----------:|---------------------:|---------------------:|-----------------:|---------:|------------:|
| housing_status                   | categorical |    0.6840 |               0.7453 |               0.4633 |         nan      |   0.0000 |      0.0476 |
| device_os                        | categorical |    0.6723 |               0.7342 |               0.4496 |         nan      |   0.0000 |      0.0356 |
| keep_alive_session               | numeric     |    0.3706 |               0.3434 |               0.4684 |           0.0000 | nan      |    nan      |
| credit_risk_score                | numeric     |    0.6234 |               0.6735 |               0.4429 |           0.0000 | nan      |    nan      |
| current_address_months_count     | numeric     |    0.6190 |               0.6420 |               0.5364 |           0.0001 | nan      |    nan      |
| name_email_similarity            | numeric     |    0.3962 |               0.3744 |               0.4745 |           0.0006 | nan      |    nan      |
| proposed_credit_limit            | numeric     |    0.6035 |               0.6341 |               0.4937 |           0.0001 | nan      |    nan      |
| date_of_birth_distinct_emails_4w | numeric     |    0.3970 |               0.3634 |               0.5183 |           0.0006 | nan      |    nan      |
| income                           | numeric     |    0.5897 |               0.6344 |               0.4289 |           0.0026 | nan      |    nan      |
| prev_address_months_count        | numeric     |    0.4108 |               0.4012 |               0.4457 |           0.0003 | nan      |    nan      |
| payment_type                     | categorical |    0.5718 |               0.5762 |               0.5563 |         nan      |   0.1583 |      0.0140 |
| customer_age                     | numeric     |    0.5656 |               0.6351 |               0.3156 |           0.0245 | nan      |    nan      |
| has_other_cards                  | numeric     |    0.4440 |               0.4452 |               0.4397 |           0.0097 | nan      |    nan      |
| employment_status                | categorical |    0.5542 |               0.5903 |               0.4242 |         nan      |   0.3080 |      0.0145 |
| phone_home_valid                 | numeric     |    0.4470 |               0.4377 |               0.4807 |           0.0373 | nan      |    nan      |
| bank_branch_count_8w             | numeric     |    0.4490 |               0.4398 |               0.4821 |           0.0896 | nan      |    nan      |

11 of 29 columns significant at p < 0.01 against all launderers; columns with |AUC-0.5| >= 0.05 for real-customer mules: ['device_os', 'credit_risk_score', 'income', 'prev_address_months_count', 'payment_type', 'customer_age', 'has_other_cards', 'employment_status', 'velocity_6h']
  -> if that last list is empty or short, real-customer mules are indistinguishable at opening (the
     'ceiling on earliness' trap): the application can only buy a head start on fake accounts.

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

  -> every open account has at least a weekly card row, so a week with no rows means the account is closed,
     and in this data only the bank's rules close accounts, only after a confirmed (true) alert. Weeks after a
     closure are therefore a label giveaway that a live model never sees (the harness removes closed accounts
     from the pool as caught). Phase 3/4 must drop account-weeks after closure from TRAINING; the screen below
     already leaves them out (rows with n_rows = 0). Decision needed: let labels() return 'open at week w' for
     months 0-5, since a bank knows which accounts it closed.

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
Account-weeks with activity only (closed accounts left out); AUCs with fewer than 20 positives shown as NaN.
AUC against mule_by_day (main label) by week since opening; 0.5 = no signal:
| feature             |      4 |      8 |     12 |     26 |   max_sep |
|:--------------------|-------:|-------:|-------:|-------:|----------:|
| n_rows_cum          | 0.5091 | 0.5378 | 0.6798 | 0.7626 |    0.2626 |
| money_in_cum        | 0.6258 | 0.6176 | 0.6971 | 0.6972 |    0.1972 |
| med_delay_min       | 0.5297 | 0.4972 | 0.3315 | 0.4804 |    0.1685 |
| self_vs_past_in     | 0.5119 | 0.4795 | 0.4531 | 0.3395 |    0.1605 |
| self_vs_past_payers | 0.5136 | 0.4918 | 0.4424 | 0.3533 |    0.1467 |
| money_out           | 0.5762 | 0.6307 | 0.6009 | 0.5639 |    0.1307 |
| n_payers            | 0.5078 | 0.5023 | 0.6092 | 0.5322 |    0.1092 |
| income_fit_in       | 0.5226 | 0.4941 | 0.5936 | 0.5690 |    0.0936 |
| money_in            | 0.5222 | 0.4923 | 0.5925 | 0.5690 |    0.0925 |
| peer_ratio_in       | 0.4885 | 0.4790 | 0.5798 | 0.5624 |    0.0798 |
| max_in              | 0.5224 | 0.4907 | 0.5743 | 0.5652 |    0.0743 |
| n_rows              | 0.5344 | 0.5586 | 0.5382 | 0.4970 |    0.0586 |
| cash_share          | 0.5169 | 0.5151 | 0.4572 | 0.4468 |    0.0532 |
| passthrough_wk      | 0.4845 | 0.5304 | 0.4547 | 0.4548 |    0.0453 |
| night_share         | 0.5014 | 0.5069 | 0.5424 | 0.4780 |    0.0424 |
| new_payer_share     | 0.4801 | 0.5416 | 0.4784 | 0.4595 |    0.0416 |
| out_24h_share       | 0.4940 | 0.5409 | 0.4593 | 0.4762 |    0.0409 |
| n_payees            | 0.5157 | 0.5198 | 0.4664 | 0.5104 |    0.0336 |
| out_1h_share        | 0.4932 | 0.5305 | 0.4785 | 0.4829 |    0.0305 |
| abroad_share        | 0.4960 | 0.5174 | 0.5100 | 0.5048 |    0.0174 |
| internal_share      | 0.5056 | 0.5170 | 0.5118 | 0.5035 |    0.0170 |
| hr_share            | 0.4994 | 0.5065 | 0.5063 | 0.4992 |    0.0065 |

AUC against started_by_day (accounts whose laundering has started vs normal):
launderers started by week: {4: 0, 8: 4, 12: 46, 26: 60} (real-customer mules: {4: 0, 8: 0, 12: 1, 26: 4})
| feature             |   4 |   8 |     12 |     26 |
|:--------------------|----:|----:|-------:|-------:|
| n_rows_cum          | nan | nan | 0.8234 | 0.7625 |
| money_in_cum        | nan | nan | 0.7441 | 0.6972 |
| med_delay_min       | nan | nan | 0.2200 | 0.4804 |
| self_vs_past_in     | nan | nan | 0.4098 | 0.3395 |
| self_vs_past_payers | nan | nan | 0.3912 | 0.3533 |
| money_out           | nan | nan | 0.6621 | 0.5639 |
| n_payers            | nan | nan | 0.6945 | 0.5322 |
| income_fit_in       | nan | nan | 0.6737 | 0.5690 |
| money_in            | nan | nan | 0.6721 | 0.5690 |
| peer_ratio_in       | nan | nan | 0.6591 | 0.5625 |
| max_in              | nan | nan | 0.6433 | 0.5652 |
| n_rows              | nan | nan | 0.6178 | 0.4970 |
| cash_share          | nan | nan | 0.4703 | 0.4468 |
| passthrough_wk      | nan | nan | 0.4056 | 0.4548 |
| night_share         | nan | nan | 0.5670 | 0.4780 |
| new_payer_share     | nan | nan | 0.4359 | 0.4595 |
| out_24h_share       | nan | nan | 0.4215 | 0.4762 |
| n_payees            | nan | nan | 0.5045 | 0.5104 |
| out_1h_share        | nan | nan | 0.4463 | 0.4829 |
| abroad_share        | nan | nan | 0.5178 | 0.5048 |
| internal_share      | nan | nan | 0.5159 | 0.5035 |
| hr_share            | nan | nan | 0.5102 | 0.4992 |

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
| money_in            | self_vs_past_in     |     0.9177 |
| self_vs_past_in     | income_fit_in       |     0.9170 |
| max_in              | self_vs_past_in     |     0.9168 |
| self_vs_past_in     | peer_ratio_in       |     0.9151 |
| n_payers            | self_vs_past_payers |     0.9072 |
| money_in            | n_payers            |     0.8784 |
| n_payers            | income_fit_in       |     0.8783 |
| n_payers            | peer_ratio_in       |     0.8771 |
| self_vs_past_in     | self_vs_past_payers |     0.8753 |
| max_in              | n_payers            |     0.8722 |
| money_in            | passthrough_wk      |    -0.8604 |
| max_in              | passthrough_wk      |    -0.8573 |
| n_payers            | self_vs_past_in     |     0.8531 |
| passthrough_wk      | income_fit_in       |    -0.8502 |
| n_rows              | n_payees            |     0.8386 |
| passthrough_wk      | peer_ratio_in       |    -0.8385 |
| money_in            | self_vs_past_payers |     0.8301 |
| self_vs_past_payers | income_fit_in       |     0.8297 |
| self_vs_past_payers | peer_ratio_in       |     0.8294 |
| max_in              | self_vs_past_payers |     0.8268 |


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
8. PROPOSED FEATURE LIST FOR PHASE 3 (the team fixes it at the gate)
==============================================================================
| feature             |   best_sep_mule |   best_sep_started |   nonnull | proposal                                       |
|:--------------------|----------------:|-------------------:|----------:|:-----------------------------------------------|
| n_rows_cum          |          0.2626 |             0.3234 |    1.0000 | keep                                           |
| med_delay_min       |          0.1685 |             0.2800 |    0.9999 | keep                                           |
| money_in_cum        |          0.1972 |             0.2441 |    1.0000 | keep                                           |
| n_payers            |          0.1092 |             0.1945 |    1.0000 | keep                                           |
| income_fit_in       |          0.0936 |             0.1737 |    1.0000 | keep                                           |
| money_in            |          0.0925 |             0.1721 |    1.0000 | keep                                           |
| money_out           |          0.1307 |             0.1621 |    1.0000 | keep                                           |
| self_vs_past_in     |          0.1605 |             0.1605 |    0.3810 | keep                                           |
| peer_ratio_in       |          0.0798 |             0.1591 |    0.9436 | keep                                           |
| self_vs_past_payers |          0.1467 |             0.1467 |    0.3115 | keep                                           |
| max_in              |          0.0743 |             0.1433 |    1.0000 | keep                                           |
| n_rows              |          0.0586 |             0.1178 |    1.0000 | keep                                           |
| passthrough_wk      |          0.0453 |             0.0944 |    0.5251 | keep                                           |
| out_24h_share       |          0.0409 |             0.0785 |    0.5251 | keep                                           |
| night_share         |          0.0424 |             0.0670 |    1.0000 | keep; expected: same hour weights for everyone |
| new_payer_share     |          0.0416 |             0.0641 |    0.5145 | keep                                           |
| out_1h_share        |          0.0305 |             0.0537 |    0.5251 | keep                                           |
| cash_share          |          0.0532 |             0.0532 |    1.0000 | keep                                           |
| abroad_share        |          0.0174 |             0.0178 |    1.0000 | drop (no signal at any screened week)          |
| internal_share      |          0.0170 |             0.0159 |    1.0000 | drop (no signal at any screened week)          |
| n_payees            |          0.0336 |             0.0104 |    1.0000 | drop (no signal at any screened week)          |
| hr_share            |          0.0065 |             0.0102 |    1.0000 | drop (no signal at any screened week)          |

Speed features as screened here (out_1h_share, out_24h_share) are swamped by everyday outflows: the ASOF join
pairs every card, direct-debit or cash row with the latest payment in, so normal accounts also 'forward' about
half of their money in within a day. Phase 3 should define them as transfers OUT (ACH, Cross-border) within
1h / 24h after each transfer IN, capped at that payment's amount; med_delay_min already carries the signal.
abroad_share, hr_share and cash_share are rare events at week level (launderers send ~1.6% of transfers abroad);
keep them cumulative rather than weekly if kept at all.
Application columns: keep all 29 after Phase 2 cleaning; LightGBM ignores useless ones and L1 logistic
regression drops them. Candidate pairs above |0.8| correlation: keep one for the logistic model.

done in 7s