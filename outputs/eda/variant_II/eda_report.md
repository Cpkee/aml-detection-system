ROOT     : /private/tmp/claude-501/-Users-cheepheng-aml-detection-system/1db6e3ad-fff6-45ed-9d4a-0657fb872fe2/scratchpad/wt-r6
DATA_DIR : /Users/cheepheng/aml-detection-system/data/variant_II
OUT_DIR  : /Users/cheepheng/aml-detection-system/outputs/eda/variant_II
pandas 3.0.6 | python 3.12.15

==============================================================================
2. FILE INVENTORY
==============================================================================
accounts                244,000 rows x 32 cols
accounts_truth          244,000 rows x  8 cols
transactions_truth   106,068,446 rows x  3 cols
aml_alerts                3,624 rows x  6 cols
aml_outcomes            244,000 rows x  3 cols
transactions         (streamed)      transactions.parquet  3,826 MB

account_id unique in accounts        : True
accounts_truth covers every account  : True
row counts match (accounts == truth) : True
aml_outcomes non-null alert days      : 3,286

==============================================================================
3. SCHEMA, DTYPES, MISSINGNESS, SENTINELS
==============================================================================
26 numeric, 5 categorical feature columns
categoricals: ['payment_type', 'employment_status', 'housing_status', 'source', 'device_os']

true NaNs: none

negative-coded missingness (BAF sentinels, NOT real NaN):
                              share_negative
prev_address_months_count           0.759184
intended_balcon_amount              0.749926
bank_months_count                   0.242922
credit_risk_score                   0.012713
current_address_months_count        0.003598
session_length_in_minutes           0.002217
device_distinct_emails_8w           0.000307
velocity_6h                         0.000029

  -> treat these as missing indicators before modelling; a raw -1 is not 'one month'.

categorical cardinality:
payment_type         5
employment_status    7
housing_status       7
source               2
device_os            5

==============================================================================
4. LABEL LANDSCAPE
==============================================================================
accounts                     : 244,000
is_launderer  (model target) : 732  (0.300%)
baf_fraud_bool (onboarding)  : 2,631  (1.078%)

profile mix:
                     n     share
profile                         
normal          241174  0.988418
app_fraud_only    2094  0.008582
fake               537  0.002201
witting             98  0.000402
unwitting           97  0.000398

profile x is_launderer:
is_launderer         0    1
profile                    
app_fraud_only    2094    0
fake                 0  537
normal          241174    0
unwitting            0   97
witting              0   98

baf_fraud_bool x is_launderer  (this is the authored onboarding<->laundering link
that replaces the rho/p linkage parameter from the SAML-D+BAF join):
is_launderer         0    1
baf_fraud_bool             
0               241174  195
1                 2094  537

  P(launderer | baf_fraud=1) = 20.410%
  P(launderer | baf_fraud=0) = 0.081%
  lift                       = 252.6x
  phi coefficient            = 0.3839

  Report this number explicitly. It is the simulator's answer to 'how are the two
  datasets related', and unlike the join it is known exactly rather than assumed.

==============================================================================
5. ONBOARDING (BAF) FEATURES VS is_launderer
==============================================================================
univariate AUC vs is_launderer (0.5 = no signal):
                         feature    auc   mean_pos   mean_neg
               credit_risk_score 0.6202   171.2760   137.4588
           proposed_credit_limit 0.6126   817.0492   558.3886
              keep_alive_session 0.4065     0.3743     0.5612
                          income 0.5931     0.6564     0.5731
            bank_branch_count_8w 0.4108   135.2760   202.5854
date_of_birth_distinct_emails_4w 0.4153     6.6352     7.9563
                phone_home_valid 0.4194     0.3292     0.4904
    current_address_months_count 0.5781   117.1284    99.3598
       prev_address_months_count 0.4373     7.1270    14.8130
           name_email_similarity 0.4440     0.4336     0.4883
                 has_other_cards 0.4448     0.1339     0.2442
                    customer_age 0.5499    43.2104    41.2908
                   email_is_free 0.5450     0.6120     0.5220
       device_distinct_emails_8w 0.5371     1.0984     1.0234
          intended_balcon_amount 0.4632     5.8014     8.6294
              days_since_request 0.4697     0.9582     0.9064
       session_length_in_minutes 0.5288     9.0738     7.8902
                     velocity_4w 0.4738 4,793.2378 4,859.3535
               bank_months_count 0.4754    10.8497    11.1791
                        open_day 0.5225   118.4372   113.1957

categorical features: P(launderer) by level

-- payment_type
               size   mean
payment_type              
AC            59235 0.0042
AD            27015 0.0032
AB            96338 0.0028
AA            61352 0.0020

-- employment_status
                     size   mean
employment_status               
CC                  21741 0.0042
CA                 165401 0.0033
CB                  34639 0.0019
CE                   4436 0.0018
CF                  11065 0.0010
CD                   6610 0.0008

-- housing_status
                 size   mean
housing_status              
BA              52275 0.0072
BF                438 0.0046
BE              29804 0.0023
BD               6466 0.0022
BC              82871 0.0019
BB              72082 0.0016

-- source
            size   mean
source                 
TELEAPP     1897 0.0032
INTERNET  242103 0.0030

-- device_os
            size   mean
device_os              
windows    73883 0.0053
macintosh  12130 0.0045
x11         1990 0.0025
other      73229 0.0019
linux      82768 0.0017

==============================================================================
6. TIME STRUCTURE (concern #2: changing cohort composition)
==============================================================================
account opening:
          open_month       open_day
count  244000.000000  244000.000000
mean        3.290607     113.211406
std         2.208600      66.832348
min         0.000000       0.000000
25%         1.000000      57.000000
50%         3.000000     110.000000
75%         5.000000     168.000000
max         7.000000     239.000000

accounts opened per open_month:
                n  launder_rate
open_month                     
0           32217        0.0032
1           31076        0.0023
2           33523        0.0027
3           36724        0.0028
4           31279        0.0031
5           29120        0.0033
6           26529        0.0034
7           23532        0.0034

launder_start_day: n=732  min=31  med=240  max=750
lag from open_day to launder_start_day: med=98 days, p10=67, p90=374
  -> this lag sets the earliest week a mule is detectable. If your weekly panel
     starts before it, those weeks are structurally unlabelable, not just hard.

==============================================================================
7. PASS OVER TRANSACTIONS (DuckDB)
==============================================================================
read 108,673,613 transaction rows -> 74,942,385 account-days
txn_id prefixes: {'T': 108673613}

acct_day: 74,942,385 rows (1,570 MB on disk)

transaction volume by payment_type x direction:
   payment_type direction        n                 amt  share
            ACH       out 65954183  7,903,136,693.1898 0.6069
     Debit card       out 19289833  5,688,541,449.4500 0.1775
            ACH        in 13521658 19,701,573,146.0996 0.1244
Cash Withdrawal       out  8783483  1,398,044,118.7300 0.0808
   Cash Deposit        in   527512    111,955,320.0400 0.0049
         Cheque       out   439724     60,600,010.9000 0.0040
   Cross-border       out   157220     97,144,144.2100 0.0014

==============================================================================
8. ACCOUNT-LEVEL TRANSACTION BEHAVIOUR
==============================================================================
accounts with zero transactions: 0 (0.00%)

behaviour features, launderers vs the rest:
                    non_launderer_median  launderer_median  ratio
n_txn                            442.000           436.000  0.986
share_out                          0.886             0.866  0.978
share_internal                     0.048             0.057  1.203
share_night                        0.063             0.067  1.060
share_cash                         0.083             0.081  0.977
amt_total                    138,559.140       134,561.360  0.971
amt_mean                         310.604           386.037  1.243
max_amt_in_a_day               4,667.530         6,534.400  1.400
max_txn_in_a_day                   4.000             5.000  1.250
passthrough                        0.775             0.767  0.991
in_degree                         30.000            31.000  1.033
out_degree                       137.000           135.000  0.985
active_days                      306.000           298.000  0.974
txn_per_active_day                 1.437             1.500  1.044

univariate AUC, behaviour features:
           feature    auc
  max_txn_in_a_day 0.7796
txn_per_active_day 0.6899
    share_internal 0.6858
  max_amt_in_a_day 0.6740
         share_out 0.3367
          amt_mean 0.6152
       active_days 0.4023
       share_night 0.5877
             n_txn 0.4410
        out_degree 0.4461
        share_cash 0.4661
         in_degree 0.5327
       passthrough 0.4826
         amt_total 0.4826

  Compare these against §5. If behaviour dominates onboarding by a wide margin,
  the BAF half of the dataset is contributing little and you should say so.

==============================================================================
9. LAUNDERING AT THE TRANSACTION LEVEL
==============================================================================
transactions_truth rows        : 106,068,446
is_laundering rate             : 0.01099%

laundering_type mix:
                               n   share
laundering_type                         
Normal_DirectDebit      32127347 0.30289
Normal_Transfer         30303356 0.28570
Normal_Card             19289833 0.18186
Normal_CashWithdrawal    8783334 0.08281
Normal_Salary            6378872 0.06014
Normal_TransferIn        4387060 0.04136
Normal_StandingOrder     3516266 0.03315
Normal_CashDeposit        526523 0.00496
Normal_Cheque             439724 0.00415
Normal_Abroad             157103 0.00148
Normal_Bonus              104205 0.00098
Normal_GroupCollection     42442 0.00040
Structuring                 4933 0.00005
Deposit-Send                1220 0.00001
Layered_Fan_Out              822 0.00001
Normal_LargeCash             726 0.00001
Layered_Fan_In               639 0.00001
Fan_In                       593 0.00001
Stacked Bipartite            528 0.00000
Behavioural_Change_1         495 0.00000
Gather-Scatter               472 0.00000
Cycle                        440 0.00000
Behavioural_Change_2         411 0.00000
Scatter-Gather               313 0.00000
Bipartite                    226 0.00000

typologies actually generated: 15
laundering_type
Structuring             4933
Deposit-Send            1220
Layered_Fan_Out          822
Layered_Fan_In           639
Fan_In                   593
Stacked Bipartite        528
Behavioural_Change_1     495
Gather-Scatter           472
Cycle                    440
Behavioural_Change_2     411
Scatter-Gather           313
Bipartite                226
Fan_Out                  192
Cash_Withdrawal          186
Smurfing                 185
  -> SAML-D ships 28 typology names. Any with zero rows exist in the vocabulary
     but not in your data; do not claim coverage you do not have.

==============================================================================
10. NETWORK STRUCTURE
==============================================================================
accounts attached to a network : 732 (0.300%)
distinct networks              : 177

network size distribution:
       n_networks
count            
2              54
3              47
4              75
183             1

largest networks:
network_id
NET_BIG    183
CH_0169      4
CH_0116      4
CH_0166      4
CH_0039      4
CH_0111      4
CH_0168      4
CH_0133      4
CH_0093      4
CH_0012      4

laundering rate inside networks vs outside:
          size  sum   mean
in_net                    
False   243268    0 0.0000
True       732  732 1.0000

  -> network_id is truth-only. If you build graph features, derive them from the
     internal A->A edges in transactions, never from this column.

internal (account-to-account) edges seen in transactions: 5,210,334

==============================================================================
11. WEEKLY PANEL + COHORT COMPOSITION
==============================================================================
weekly panel (head/tail):
      n_accounts   n_txn  n_launderers  n_active_launderers  launder_share
week                                                                      
0           7559   28132            19                    0        0.00251
1          15033   70923            41                    0        0.00273
2          22633  114215            67                    0        0.00296
3          30142  157459            92                    0        0.00305
4          37409  195555           115                    1        0.00307
5          44742  237549           131                    2        0.00293
6          51914  280515           151                    2        0.00291
7          59142  320684           167                    2        0.00282
105        42944  226213           109                  107        0.00254
106        36770  191934            92                   91        0.00250
107        30517  155192            76                   76        0.00249
108        24402  124714            61                   61        0.00250
109        18707   92771            49                   49        0.00262
110        13310   62035            38                   38        0.00285
111         7870   30188            23                   23        0.00292
112         2393    4716             6                    6        0.00251

COHORT CHECK — the composition your prof flagged:
  accounts active in week  0: 7,559
  accounts active in week  112: 2,393
  If this count drifts across weeks, a week-over-week comparison is confounded by
  who is present, not just by behaviour. Fix: restrict to the fixed cohort of
  accounts active in EVERY week you compare, and report the cohort size.

  accounts active in every one of the 113 weeks: 0 (0.00% of all accounts)

==============================================================================
12. LEAKAGE AUDIT + MODELLING READINESS
==============================================================================
NEVER-FEATURE list (ground truth written by the simulator):
  - profile
  - baf_fraud_bool
  - network_id
  - is_launderer
  - launder_start_day
  - laundered_in
  - laundered_out

  laundered_in / laundered_out are the amounts the simulator laundered through the
  account. They are a perfect giveaway. profile and network_id likewise.

ID-based leakage:
  txn_id: anonymous since 7 Oct 2026 ('T' + 16 hex); older runs used 'N###_' / 'L_' prefixes
  that leaked the label. Still never build features from txn_id; it only joins pair rows.
  counterparty_id: 'EXT_*' external, 'CARD_MERCHANTS'/'CASH_*' synthetic sinks,
  'A#######' internal accounts. Only the internal ones carry real graph signal.

class balance for modelling:
  positives 732 / 244,000 = 0.300%  (1 in 333)
  With this prevalence, accuracy is meaningless. Use PR-AUC plus precision@k where
  k is the analyst review capacity, which is the framing in your proposal.
    reviewing top   50 accounts = 0.020% of the book; perfect ranking would catch 6.8% of launderers
    reviewing top  100 accounts = 0.041% of the book; perfect ranking would catch 13.7% of launderers
    reviewing top  250 accounts = 0.102% of the book; perfect ranking would catch 34.2% of launderers
    reviewing top  500 accounts = 0.205% of the book; perfect ranking would catch 68.3% of launderers

recommended split, given §6:
  Split by TIME (train on early days, test on later), not at random. A random split
  lets the same account's later behaviour inform its earlier prediction.
  Hold the test-set prevalence at the natural rate; resample the TRAIN set only.

wrote /Users/cheepheng/aml-detection-system/data/variant_II/eda_cache/account_model_table.csv  (244,000 x 61)
  Onboarding + behaviour features + label, truth columns excluded. This is the table
  the baseline model should read.