ROOT     : C:\Users\chail\OneDrive\Desktop\BT4012\aml-detection-system
DATA_DIR : C:\Users\chail\OneDrive\Desktop\BT4012\aml-detection-system\data\v0
OUT_DIR  : C:\Users\chail\OneDrive\Desktop\BT4012\aml-detection-system\outputs\eda
pandas 3.0.6 | python 3.12.0

==============================================================================
2. FILE INVENTORY
==============================================================================
accounts                 50,000 rows x 32 cols
accounts_truth           50,000 rows x  8 cols
transactions_truth   21,751,750 rows x  3 cols
aml_alerts                    0 rows x  6 cols
aml_outcomes             50,000 rows x  3 cols
transactions         (streamed)      transactions.parquet  394 MB

account_id unique in accounts        : True
accounts_truth covers every account  : True
row counts match (accounts == truth) : True
aml_alerts is EMPTY -> the 6-rules module has not been written yet;
  any 'alert-based' baseline or review-capacity comparison is blocked on it.
aml_outcomes non-null alert days      : 0

==============================================================================
3. SCHEMA, DTYPES, MISSINGNESS, SENTINELS
==============================================================================
26 numeric, 5 categorical feature columns
categoricals: ['payment_type', 'employment_status', 'housing_status', 'source', 'device_os']

true NaNs: none

negative-coded missingness (BAF sentinels, NOT real NaN):
                              share_negative
intended_balcon_amount               0.74198
prev_address_months_count            0.71208
bank_months_count                    0.25396
credit_risk_score                    0.01372
current_address_months_count         0.00434
session_length_in_minutes            0.00182
device_distinct_emails_8w            0.00024
velocity_6h                          0.00010

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
accounts                     : 50,000
is_launderer  (model target) : 150  (0.300%)
baf_fraud_bool (onboarding)  : 562  (1.124%)

profile mix:
                    n    share
profile                       
normal          49398  0.98796
app_fraud_only    452  0.00904
fake              110  0.00220
unwitting          20  0.00040
witting            20  0.00040

profile x is_launderer:
is_launderer        0    1
profile                   
app_fraud_only    452    0
fake                0  110
normal          49398    0
unwitting           0   20
witting             0   20

baf_fraud_bool x is_launderer  (this is the authored onboarding<->laundering link
that replaces the rho/p linkage parameter from the SAML-D+BAF join):
is_launderer        0    1
baf_fraud_bool            
0               49398   40
1                 452  110

  P(launderer | baf_fraud=1) = 19.573%
  P(launderer | baf_fraud=0) = 0.081%
  lift                       = 241.9x
  phi coefficient            = 0.3757

  Report this number explicitly. It is the simulator's answer to 'how are the two
  datasets related', and unlike the join it is known exactly rather than assumed.

==============================================================================
5. ONBOARDING (BAF) FEATURES VS is_launderer
==============================================================================
univariate AUC vs is_launderer (0.5 = no signal):
                         feature    auc   mean_pos   mean_neg
               credit_risk_score 0.6128   162.7400   131.3843
              keep_alive_session 0.3920     0.3600     0.5760
           name_email_similarity 0.4006     0.3948     0.4940
    current_address_months_count 0.5927   101.5867    86.2235
                          income 0.5925     0.6460     0.5629
date_of_birth_distinct_emails_4w 0.4116     7.9467     9.5321
           proposed_credit_limit 0.5865   731.8667   520.9701
       prev_address_months_count 0.4163     8.3267    16.6663
                phone_home_valid 0.4374     0.2933     0.4185
                 has_other_cards 0.4495     0.1267     0.2276
                    customer_age 0.5475    35.6667    33.6604
                      open_month 0.5459     3.6333     3.2856
          intended_balcon_amount 0.4559     4.0197     8.6755
                        open_day 0.5428   122.8733   113.0768
            bank_branch_count_8w 0.4623   199.1067   183.3663
                   email_is_free 0.5345     0.6000     0.5310
               bank_months_count 0.4770    10.3867    10.8692
       device_distinct_emails_8w 0.5177     1.0533     1.0179
              days_since_request 0.4826     1.3389     1.0268
                     velocity_4w 0.4859 4,817.8097 4,856.6510

categorical features: P(launderer) by level

-- payment_type
               size   mean
payment_type              
AC            12588 0.0039
AB            18483 0.0034
AD             5925 0.0030
AA            12989 0.0016

-- employment_status
                    size   mean
employment_status              
CC                  1892 0.0053
CA                 36475 0.0031
CB                  6999 0.0030
CE                  1078 0.0019
CD                  1334 0.0015
CF                  2198 0.0005

-- housing_status
                 size   mean
housing_status              
BF                 93 0.0108
BA               8449 0.0083
BD               1338 0.0022
BE               8307 0.0019
BB              13028 0.0019
BC              18767 0.0019

-- source
           size   mean
source                
TELEAPP     350 0.0057
INTERNET  49650 0.0030

-- device_os
            size   mean
device_os              
windows    13104 0.0060
x11          368 0.0054
macintosh   2712 0.0041
other      17019 0.0019
linux      16797 0.0015

==============================================================================
6. TIME STRUCTURE (concern #2: changing cohort composition)
==============================================================================
account opening:
         open_month      open_day
count  50000.000000  50000.000000
mean       3.286600    113.106140
std        2.212139     66.915207
min        0.000000      0.000000
25%        1.000000     57.000000
50%        3.000000    110.000000
75%        5.000000    168.000000
max        7.000000    239.000000

accounts opened per open_month:
               n  launder_rate
open_month                    
0           6633        0.0021
1           6437        0.0025
2           6803        0.0028
3           7519        0.0028
4           6409        0.0034
5           6016        0.0043
6           5267        0.0027
7           4916        0.0037

launder_start_day: n=150  min=62  med=230  max=751
lag from open_day to launder_start_day: med=92 days, p10=68, p90=412
  -> this lag sets the earliest week a mule is detectable. If your weekly panel
     starts before it, those weeks are structurally unlabelable, not just hard.

==============================================================================
7. STREAMING PASS OVER TRANSACTIONS
==============================================================================
cache hit -> loading acct_day / global stats / counterparty pairs from eda_cache/

acct_day: 15,361,412 rows (983 MB)

transaction volume by payment_type x direction:
   payment_type direction        n                amt  share
            ACH       out 13525862 1,593,437,075.9200 0.6069
     Debit card       out  3954896 1,150,454,361.9600 0.1775
            ACH        in  2771056 3,973,848,741.3100 0.1243
Cash Withdrawal       out  1800250   286,576,530.0000 0.0808
   Cash Deposit        in   111716    45,541,130.7300 0.0050
         Cheque       out    90325    12,480,227.4300 0.0041
   Cross-border       out    32236    20,052,741.2700 0.0014

==============================================================================
8. ACCOUNT-LEVEL TRANSACTION BEHAVIOUR
==============================================================================
accounts with zero transactions: 0 (0.00%)

behaviour features, launderers vs the rest:
                    non_launderer_median  launderer_median  ratio
n_txn                            442.000           459.000  1.038
share_out                          0.885             0.877  0.990
share_internal                     0.048             0.056  1.164
share_night                        0.063             0.065  1.035
share_cash                         0.083             0.080  0.966
amt_total                    136,361.595       169,083.600  1.240
amt_mean                         305.871           356.986  1.167
max_amt_in_a_day               4,597.415         7,174.080  1.560
max_txn_in_a_day                   4.000             5.000  1.250
passthrough                        0.775             0.753  0.971
in_degree                         30.000            34.000  1.133
out_degree                       137.000           144.000  1.051
active_days                      306.000           312.000  1.020
txn_per_active_day                 1.438             1.473  1.024

univariate AUC, behaviour features:
           feature    auc
  max_txn_in_a_day 0.7479
         in_degree 0.7176
  max_amt_in_a_day 0.6993
        out_degree 0.6771
    share_internal 0.6559
txn_per_active_day 0.6207
         amt_total 0.6126
             n_txn 0.6039
         share_out 0.4043
       share_night 0.5792
          amt_mean 0.5789
       active_days 0.5708
       passthrough 0.4578
        share_cash 0.4734

  Compare these against §5. If behaviour dominates onboarding by a wide margin,
  the BAF half of the dataset is contributing little and you should say so.

==============================================================================
9. LAUNDERING AT THE TRANSACTION LEVEL
==============================================================================
transactions_truth rows        : 21,751,750
is_laundering rate             : 0.00839%

laundering_type mix:
                              n   share
laundering_type                        
Normal_DirectDebit      6591673 0.30304
Normal_Transfer         6211645 0.28557
Normal_Card             3954896 0.18182
Normal_CashWithdrawal   1800250 0.08276
Normal_Salary           1306049 0.06004
Normal_TransferIn        899857 0.04137
Normal_StandingOrder     721554 0.03317
Normal_CashDeposit       111536 0.00513
Normal_Cheque             90325 0.00415
Normal_Abroad             31917 0.00147
Normal_Bonus              21465 0.00099
Normal_GroupCollection     8579 0.00039
Fan_In                     1824 0.00008
Normal_LargeCash            180 0.00001

typologies actually generated: 1
laundering_type
Fan_In    1824
  -> SAML-D ships 28 typology names. Any with zero rows exist in the vocabulary
     but not in your data; do not claim coverage you do not have.

==============================================================================
10. NETWORK STRUCTURE
==============================================================================
accounts attached to a network : 149 (0.298%)
distinct networks              : 36

network size distribution:
       n_networks
count            
2               9
3              11
4              15
38              1

largest networks:
network_id
NET_BIG    38
CH_0024     4
CH_0028     4
CH_0016     4
CH_0021     4
CH_0013     4
CH_0001     4
CH_0033     4
CH_0003     4
CH_0008     4

laundering rate inside networks vs outside:
         size  sum   mean
in_net                   
False   49851    1 0.0000
True      149  149 1.0000

  -> network_id is truth-only. If you build graph features, derive them from the
     internal A->A edges in transactions, never from this column.

internal (account-to-account) edges seen in transactions: 1,069,182

==============================================================================
11. WEEKLY PANEL + COHORT COMPOSITION
==============================================================================
weekly panel (head/tail):
      n_accounts  n_txn  n_launderers  n_active_launderers  launder_share
week                                                                     
0           1497   5620             5                    0        0.00334
1           3075  14337             7                    0        0.00228
2           4646  23694            12                    0        0.00258
3           6200  32301            13                    0        0.00210
4           7668  40248            19                    0        0.00248
5           9155  48727            24                    0        0.00262
6          10661  57956            30                    0        0.00281
7          12193  66028            30                    0        0.00246
105         8749  45894            27                   26        0.00309
106         7504  39231            25                   24        0.00333
107         6319  32055            19                   19        0.00301
108         5075  25998            18                   18        0.00355
109         3925  19372            15                   15        0.00382
110         2789  12787            14                   14        0.00502
111         1609   6228             8                    8        0.00497
112          497    971             1                    1        0.00201

COHORT CHECK — the composition your prof flagged:
  accounts active in week  0: 1,497
  accounts active in week  112: 497
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
  txn_id prefix encodes provenance: 'N###_' = normal generator batch, 'L' = laundering.
  Any feature derived from txn_id (or a join key built from it) leaks the label.
  counterparty_id: 'EXT_*' external, 'CARD_MERCHANTS'/'CASH_*' synthetic sinks,
  'A#######' internal accounts. Only the internal ones carry real graph signal.

class balance for modelling:
  positives 150 / 50,000 = 0.300%  (1 in 333)
  With this prevalence, accuracy is meaningless. Use PR-AUC plus precision@k where
  k is the analyst review capacity, which is the framing in your proposal.
    reviewing top   50 accounts = 0.100% of the book; perfect ranking would catch 33.3% of launderers
    reviewing top  100 accounts = 0.200% of the book; perfect ranking would catch 66.7% of launderers
    reviewing top  250 accounts = 0.500% of the book; perfect ranking would catch 100.0% of launderers
    reviewing top  500 accounts = 1.000% of the book; perfect ranking would catch 100.0% of launderers

recommended split, given §6:
  Split by TIME (train on early days, test on later), not at random. A random split
  lets the same account's later behaviour inform its earlier prediction.
  Hold the test-set prevalence at the natural rate; resample the TRAIN set only.

wrote C:\Users\chail\OneDrive\Desktop\BT4012\aml-detection-system\data\v0\eda_cache\account_model_table.csv  (50,000 x 61)
  Onboarding + behaviour features + label, truth columns excluded. This is the table
  the baseline model should read.