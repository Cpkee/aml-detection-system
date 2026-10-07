ROOT     : /Users/cheepheng/aml-detection-system
DATA_DIR : /Users/cheepheng/aml-detection-system/data/v1_full
OUT_DIR  : /Users/cheepheng/aml-detection-system/outputs/eda/v1_full
pandas 3.0.6 | python 3.12.15

==============================================================================
2. FILE INVENTORY
==============================================================================
accounts                244,000 rows x 32 cols
accounts_truth          244,000 rows x  8 cols
transactions_truth   106,052,285 rows x  3 cols
aml_alerts                5,930 rows x  6 cols
aml_outcomes            244,000 rows x  3 cols
transactions         (streamed)      transactions.parquet  3,825 MB

account_id unique in accounts        : True
accounts_truth covers every account  : True
row counts match (accounts == truth) : True
aml_outcomes non-null alert days      : 5,806

==============================================================================
3. SCHEMA, DTYPES, MISSINGNESS, SENTINELS
==============================================================================
26 numeric, 5 categorical feature columns
categoricals: ['payment_type', 'employment_status', 'housing_status', 'source', 'device_os']

true NaNs: none

negative-coded missingness (BAF sentinels, NOT real NaN):
                              share_negative
intended_balcon_amount              0.741586
prev_address_months_count           0.712242
bank_months_count                   0.253893
credit_risk_score                   0.014324
current_address_months_count        0.004197
session_length_in_minutes           0.001922
device_distinct_emails_8w           0.000328
velocity_6h                         0.000037

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
baf_fraud_bool (onboarding)  : 2,757  (1.130%)

profile mix:
                     n     share
profile                         
normal          241048  0.987902
app_fraud_only    2220  0.009098
fake               537  0.002201
witting             98  0.000402
unwitting           97  0.000398

profile x is_launderer:
is_launderer         0    1
profile                    
app_fraud_only    2220    0
fake                 0  537
normal          241048    0
unwitting            0   97
witting              0   98

baf_fraud_bool x is_launderer  (this is the authored onboarding<->laundering link
that replaces the rho/p linkage parameter from the SAML-D+BAF join):
is_launderer         0    1
baf_fraud_bool             
0               241048  195
1                 2220  537

  P(launderer | baf_fraud=1) = 19.478%
  P(launderer | baf_fraud=0) = 0.081%
  lift                       = 241.0x
  phi coefficient            = 0.3749

  Report this number explicitly. It is the simulator's answer to 'how are the two
  datasets related', and unlike the join it is known exactly rather than assumed.

==============================================================================
5. ONBOARDING (BAF) FEATURES VS is_launderer
==============================================================================
univariate AUC vs is_launderer (0.5 = no signal):
                         feature    auc   mean_pos   mean_neg
              keep_alive_session 0.3868     0.3497     0.5760
    current_address_months_count 0.6088   113.6475    86.5847
               credit_risk_score 0.6036   158.9399   131.0288
date_of_birth_distinct_emails_4w 0.4106     8.0355     9.5222
           proposed_credit_limit 0.5814   708.2104   516.4386
       prev_address_months_count 0.4232     8.3538    16.7738
                phone_home_valid 0.4290     0.2760     0.4180
           name_email_similarity 0.4309     0.4249     0.4941
                          income 0.5684     0.6287     0.5621
            bank_branch_count_8w 0.4357   154.0956   185.2453
                    customer_age 0.5511    36.3525    33.6690
                 has_other_cards 0.4512     0.1270     0.2246
          intended_balcon_amount 0.4698     5.1245     8.7055
       device_distinct_emails_8w 0.5286     1.0765     1.0186
              days_since_request 0.4736     1.2061     1.0127
                     velocity_4w 0.4736 4,800.3055 4,856.8578
                        open_day 0.5245   118.9672   113.1941
       session_length_in_minutes 0.5243     9.0378     7.5522
                      open_month 0.5230     3.4699     3.2901
                   email_is_free 0.5219     0.5738     0.5300

categorical features: P(launderer) by level

-- payment_type
               size   mean
payment_type              
AC            61572 0.0043
AD            29126 0.0030
AB            89923 0.0028
AA            63314 0.0021

-- employment_status
                     size   mean
employment_status               
CC                   9074 0.0056
CA                 178283 0.0033
CE                   5484 0.0020
CB                  33752 0.0019
CD                   6487 0.0017
CF                  10811 0.0012

-- housing_status
                 size   mean
housing_status              
BA              41193 0.0079
BD               6316 0.0028
BE              41431 0.0027
BC              91245 0.0019
BB              63334 0.0016
BF                408 0.0000

-- source
            size   mean
source                 
INTERNET  242331 0.0030
TELEAPP     1669 0.0030

-- device_os
            size   mean
device_os              
windows    64264 0.0056
macintosh  13154 0.0043
other      83851 0.0023
x11         1780 0.0017
linux      80951 0.0015

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
0           32217        0.0033
1           31076        0.0025
2           33523        0.0027
3           36724        0.0024
4           31279        0.0030
5           29120        0.0033
6           26529        0.0039
7           23532        0.0033

launder_start_day: n=732  min=25  med=244  max=744
lag from open_day to launder_start_day: med=98 days, p10=67, p90=374
  -> this lag sets the earliest week a mule is detectable. If your weekly panel
     starts before it, those weeks are structurally unlabelable, not just hard.

==============================================================================
7. PASS OVER TRANSACTIONS (DuckDB)
==============================================================================
read 108,654,971 transaction rows -> 74,940,338 account-days
txn_id prefixes: {'T': 108654971}

acct_day: 74,940,338 rows (1,568 MB on disk)

transaction volume by payment_type x direction:
   payment_type direction        n                 amt  share
            ACH       out 65934624  7,784,217,072.0897 0.6068
     Debit card       out 19292246  5,617,552,487.3000 0.1776
            ACH        in 13521510 19,401,597,705.4599 0.1244
Cash Withdrawal       out  8785781  1,398,240,208.1500 0.0809
   Cash Deposit        in   526686    112,452,165.3700 0.0048
         Cheque       out   440419     60,742,058.1800 0.0041
   Cross-border       out   153705     95,440,677.5900 0.0014

==============================================================================
8. ACCOUNT-LEVEL TRANSACTION BEHAVIOUR
==============================================================================
accounts with zero transactions: 0 (0.00%)

behaviour features, launderers vs the rest:
                    non_launderer_median  launderer_median  ratio
n_txn                            442.000           449.000  1.016
share_out                          0.885             0.867  0.980
share_internal                     0.048             0.057  1.204
share_night                        0.063             0.066  1.052
share_cash                         0.083             0.080  0.971
amt_total                    135,756.575       142,128.065  1.047
amt_mean                         304.536           350.829  1.152
max_amt_in_a_day               4,557.000         6,315.910  1.386
max_txn_in_a_day                   4.000             5.000  1.250
passthrough                        0.778             0.776  0.997
in_degree                         30.000            33.000  1.100
out_degree                       136.000           138.000  1.015
active_days                      306.000           304.000  0.993
txn_per_active_day                 1.436             1.497  1.042

univariate AUC, behaviour features:
           feature    auc
  max_txn_in_a_day 0.7769
    share_internal 0.6905
txn_per_active_day 0.6766
  max_amt_in_a_day 0.6759
         share_out 0.3515
          amt_mean 0.5886
         in_degree 0.5817
       share_night 0.5775
       active_days 0.4528
        share_cash 0.4632
         amt_total 0.5100
       passthrough 0.4900
        out_degree 0.5085
             n_txn 0.4987

  Compare these against §5. If behaviour dominates onboarding by a wide margin,
  the BAF half of the dataset is contributing little and you should say so.

==============================================================================
9. LAUNDERING AT THE TRANSACTION LEVEL
==============================================================================
transactions_truth rows        : 106,052,285
is_laundering rate             : 0.01118%

laundering_type mix:
                               n   share
laundering_type                         
Normal_DirectDebit      32120188 0.30287
Normal_Transfer         30285499 0.28557
Normal_Card             19292246 0.18191
Normal_CashWithdrawal    8785520 0.08284
Normal_Salary            6380508 0.06016
Normal_TransferIn        4389270 0.04139
Normal_StandingOrder     3521595 0.03321
Normal_CashDeposit        525628 0.00496
Normal_Cheque             440419 0.00415
Normal_Abroad             153600 0.00145
Normal_Bonus              104241 0.00098
Normal_GroupCollection     40934 0.00039
Structuring                 4886 0.00005
Deposit-Send                1434 0.00001
Normal_LargeCash             781 0.00001
Layered_Fan_Out              734 0.00001
Layered_Fan_In               665 0.00001
Behavioural_Change_1         560 0.00001
Cycle                        548 0.00001
Behavioural_Change_2         512 0.00000
Gather-Scatter               495 0.00000
Fan_In                       382 0.00000
Fan_Out                      345 0.00000
Cash_Withdrawal              325 0.00000
Scatter-Gather               319 0.00000

typologies actually generated: 15
laundering_type
Structuring             4886
Deposit-Send            1434
Layered_Fan_Out          734
Layered_Fan_In           665
Behavioural_Change_1     560
Cycle                    548
Behavioural_Change_2     512
Gather-Scatter           495
Fan_In                   382
Fan_Out                  345
Cash_Withdrawal          325
Scatter-Gather           319
Bipartite                255
Stacked Bipartite        243
Smurfing                 153
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

internal (account-to-account) edges seen in transactions: 5,205,372

==============================================================================
11. WEEKLY PANEL + COHORT COMPOSITION
==============================================================================
weekly panel (head/tail):
      n_accounts   n_txn  n_launderers  n_active_launderers  launder_share
week                                                                      
0           7559   27843            29                    0        0.00384
1          15033   70495            52                    0        0.00346
2          22633  114721            76                    0        0.00336
3          30139  157578           100                    1        0.00332
4          37408  195531           117                    2        0.00313
5          44743  237869           137                    2        0.00306
6          51917  279678           147                    2        0.00283
7          59140  319971           170                    2        0.00287
105        42945  226345           121                  120        0.00282
106        36779  192355           108                  108        0.00294
107        30522  155639            86                   86        0.00282
108        24407  124040            62                   62        0.00254
109        18715   93015            52                   52        0.00278
110        13317   61806            37                   37        0.00278
111         7872   30560            26                   26        0.00330
112         2395    4763            13                   13        0.00543

COHORT CHECK — the composition your prof flagged:
  accounts active in week  0: 7,559
  accounts active in week  112: 2,395
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

wrote /Users/cheepheng/aml-detection-system/data/v1_full/eda_cache/account_model_table.csv  (244,000 x 61)
  Onboarding + behaviour features + label, truth columns excluded. This is the table
  the baseline model should read.