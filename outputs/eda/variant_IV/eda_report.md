ROOT     : /private/tmp/claude-501/-Users-cheepheng-aml-detection-system/1db6e3ad-fff6-45ed-9d4a-0657fb872fe2/scratchpad/wt-variants
DATA_DIR : /Users/cheepheng/aml-detection-system/data/variant_IV
OUT_DIR  : /Users/cheepheng/aml-detection-system/outputs/eda/variant_IV
pandas 3.0.6 | python 3.12.15

==============================================================================
2. FILE INVENTORY
==============================================================================
accounts                244,000 rows x 32 cols
accounts_truth          244,000 rows x  8 cols
transactions_truth   106,027,108 rows x  3 cols
aml_alerts                6,084 rows x  6 cols
aml_outcomes            244,000 rows x  3 cols
transactions         (streamed)      transactions.parquet  3,825 MB

account_id unique in accounts        : True
accounts_truth covers every account  : True
row counts match (accounts == truth) : True
aml_outcomes non-null alert days      : 5,967

==============================================================================
3. SCHEMA, DTYPES, MISSINGNESS, SENTINELS
==============================================================================
26 numeric, 5 categorical feature columns
categoricals: ['payment_type', 'employment_status', 'housing_status', 'source', 'device_os']

true NaNs: none

negative-coded missingness (BAF sentinels, NOT real NaN):
                              share_negative
prev_address_months_count           0.762705
intended_balcon_amount              0.750758
bank_months_count                   0.246107
credit_risk_score                   0.011980
current_address_months_count        0.003570
session_length_in_minutes           0.002340
device_distinct_emails_8w           0.000262
velocity_6h                         0.000049

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
baf_fraud_bool (onboarding)  : 2,717  (1.114%)

profile mix:
                     n     share
profile                         
normal          241088  0.988066
app_fraud_only    2180  0.008934
fake               537  0.002201
witting             98  0.000402
unwitting           97  0.000398

profile x is_launderer:
is_launderer         0    1
profile                    
app_fraud_only    2180    0
fake                 0  537
normal          241088    0
unwitting            0   97
witting              0   98

baf_fraud_bool x is_launderer  (this is the authored onboarding<->laundering link
that replaces the rho/p linkage parameter from the SAML-D+BAF join):
is_launderer         0    1
baf_fraud_bool             
0               241088  195
1                 2180  537

  P(launderer | baf_fraud=1) = 19.764%
  P(launderer | baf_fraud=0) = 0.081%
  lift                       = 244.6x
  phi coefficient            = 0.3777

  Report this number explicitly. It is the simulator's answer to 'how are the two
  datasets related', and unlike the join it is known exactly rather than assumed.

==============================================================================
5. ONBOARDING (BAF) FEATURES VS is_launderer
==============================================================================
univariate AUC vs is_launderer (0.5 = no signal):
                         feature    auc   mean_pos   mean_neg
               credit_risk_score 0.6259   174.1899   139.0025
           proposed_credit_limit 0.6053   792.7459   551.5453
              keep_alive_session 0.4056     0.3675     0.5564
                          income 0.5824     0.6520     0.5782
           name_email_similarity 0.4226     0.4114     0.4877
    current_address_months_count 0.5759   116.6858    99.2256
date_of_birth_distinct_emails_4w 0.4302     6.7295     7.7852
                 has_other_cards 0.4326     0.1134     0.2482
                phone_home_valid 0.4331     0.3593     0.4931
       prev_address_months_count 0.4468     9.4699    14.6199
                    customer_age 0.5506    43.4016    41.2881
            bank_branch_count_8w 0.4594   190.5956   200.6422
          intended_balcon_amount 0.4658     5.0685     8.6135
                   email_is_free 0.5324     0.5847     0.5199
       device_distinct_emails_8w 0.5260     1.0738     1.0212
                    velocity_24h 0.4773 4,534.4503 4,659.4929
       session_length_in_minutes 0.5214     8.6312     7.8097
                    zip_count_4w 0.5214 1,589.1216 1,515.3569
              days_since_request 0.4822     0.8980     0.8957
              phone_mobile_valid 0.4829     0.8224     0.8565

categorical features: P(launderer) by level

-- payment_type
               size   mean
payment_type              
AC            60057 0.0037
AD            25525 0.0035
AB            97523 0.0031
AA            60834 0.0019

-- employment_status
                     size   mean
employment_status               
CC                  21657 0.0044
CA                 167369 0.0032
CE                   4586 0.0026
CB                  32797 0.0020
CD                   6474 0.0019
CF                  11008 0.0006

-- housing_status
                 size   mean
housing_status              
BA              52720 0.0070
BD               6419 0.0033
BC              81972 0.0020
BE              29050 0.0020
BB              73369 0.0017
BF                397 0.0000

-- source
            size   mean
source                 
INTERNET  242107 0.0030
TELEAPP     1893 0.0016

-- device_os
            size   mean
device_os              
windows    74253 0.0053
macintosh  12232 0.0048
x11         2099 0.0033
other      73304 0.0019
linux      82112 0.0016

==============================================================================
6. TIME STRUCTURE (concern #2: changing cohort composition)
==============================================================================
account opening:
          open_month       open_day
count  244000.000000  244000.000000
mean        3.660443     124.306488
std         2.115392      64.064432
min         0.000000       0.000000
25%         2.000000      73.000000
50%         4.000000     123.000000
75%         5.000000     178.000000
max         7.000000     239.000000

accounts opened per open_month:
                n  launder_rate
open_month                     
0           19471        0.0031
1           25567        0.0028
2           34919        0.0020
3           38172        0.0033
4           30863        0.0041
5           35923        0.0029
6           33435        0.0036
7           25650        0.0019

launder_start_day: n=732  min=40  med=237  max=730
lag from open_day to launder_start_day: med=98 days, p10=67, p90=377
  -> this lag sets the earliest week a mule is detectable. If your weekly panel
     starts before it, those weeks are structurally unlabelable, not just hard.

==============================================================================
7. PASS OVER TRANSACTIONS (DuckDB)
==============================================================================
read 108,647,341 transaction rows -> 74,924,365 account-days
txn_id prefixes: {'T': 108647341}

acct_day: 74,924,365 rows (1,570 MB on disk)

transaction volume by payment_type x direction:
   payment_type direction        n                 amt  share
            ACH       out 65912353  7,959,478,295.9999 0.6067
     Debit card       out 19292315  5,724,697,551.5100 0.1776
            ACH        in 13539478 19,858,939,106.4704 0.1246
Cash Withdrawal       out  8782282  1,398,167,703.7400 0.0808
   Cash Deposit        in   526066    111,482,692.6200 0.0048
         Cheque       out   440098     60,595,726.2200 0.0041
   Cross-border       out   154749     96,058,427.6900 0.0014

==============================================================================
8. ACCOUNT-LEVEL TRANSACTION BEHAVIOUR
==============================================================================
accounts with zero transactions: 0 (0.00%)

behaviour features, launderers vs the rest:
                    non_launderer_median  launderer_median  ratio
n_txn                            442.000           440.500  0.997
share_out                          0.885             0.867  0.979
share_internal                     0.048             0.061  1.269
share_night                        0.063             0.067  1.074
share_cash                         0.083             0.080  0.974
amt_total                    139,860.220       148,418.020  1.061
amt_mean                         313.651           379.742  1.211
max_amt_in_a_day               4,714.405         6,537.860  1.387
max_txn_in_a_day                   4.000             5.000  1.250
passthrough                        0.772             0.766  0.992
in_degree                         30.000            33.000  1.100
out_degree                       137.000           139.000  1.015
active_days                      306.000           302.000  0.987
txn_per_active_day                 1.437             1.485  1.033

univariate AUC, behaviour features:
           feature    auc
  max_txn_in_a_day 0.7730
    share_internal 0.7189
  max_amt_in_a_day 0.6752
         share_out 0.3284
txn_per_active_day 0.6607
          amt_mean 0.6016
       share_night 0.5993
         in_degree 0.5898
       active_days 0.4282
             n_txn 0.4635
        share_cash 0.4655
       passthrough 0.4933
         amt_total 0.5037
        out_degree 0.4999

  Compare these against §5. If behaviour dominates onboarding by a wide margin,
  the BAF half of the dataset is contributing little and you should say so.

==============================================================================
9. LAUNDERING AT THE TRANSACTION LEVEL
==============================================================================
transactions_truth rows        : 106,027,108
is_laundering rate             : 0.01126%

laundering_type mix:
                               n   share
laundering_type                         
Normal_DirectDebit      32086908 0.30263
Normal_Transfer         30301559 0.28579
Normal_Card             19292315 0.18196
Normal_CashWithdrawal    8781965 0.08283
Normal_Salary            6380345 0.06018
Normal_TransferIn        4388544 0.04139
Normal_StandingOrder     3516519 0.03317
Normal_CashDeposit        525037 0.00495
Normal_Cheque             440098 0.00415
Normal_Abroad             154657 0.00146
Normal_Bonus              103971 0.00098
Normal_GroupCollection     42542 0.00040
Structuring                 4969 0.00005
Deposit-Send                1256 0.00001
Layered_Fan_In               844 0.00001
Layered_Fan_Out              727 0.00001
Normal_LargeCash             709 0.00001
Behavioural_Change_1         510 0.00000
Fan_In                       503 0.00000
Cycle                        500 0.00000
Behavioural_Change_2         452 0.00000
Cash_Withdrawal              390 0.00000
Stacked Bipartite            321 0.00000
Bipartite                    318 0.00000
Smurfing                     305 0.00000

typologies actually generated: 15
laundering_type
Structuring             4969
Deposit-Send            1256
Layered_Fan_In           844
Layered_Fan_Out          727
Behavioural_Change_1     510
Fan_In                   503
Cycle                    500
Behavioural_Change_2     452
Cash_Withdrawal          390
Stacked Bipartite        321
Bipartite                318
Smurfing                 305
Fan_Out                  292
Gather-Scatter           288
Scatter-Gather           264
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
CH_0130      4
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

internal (account-to-account) edges seen in transactions: 5,240,466

==============================================================================
11. WEEKLY PANEL + COHORT COMPOSITION
==============================================================================
weekly panel (head/tail):
      n_accounts   n_txn  n_launderers  n_active_launderers  launder_share
week                                                                      
0           4586   16918            14                    0        0.00305
1           9070   42511            30                    0        0.00331
2          13634   69539            43                    0        0.00315
3          18212   94959            56                    0        0.00307
4          23705  121030            71                    0        0.00300
5          29717  155297            78                    1        0.00262
6          35750  190793            96                    1        0.00269
7          41605  223110           121                    1        0.00291
105        50143  263943           107                  107        0.00213
106        42381  220247            86                   86        0.00203
107        34536  173892            65                   65        0.00188
108        26762  135943            40                   40        0.00149
109        20443  101395            33                   33        0.00161
110        14540   67595            26                   26        0.00179
111         8585   33378            14                   14        0.00163
112         2626    5261             7                    7        0.00267

COHORT CHECK — the composition your prof flagged:
  accounts active in week  0: 4,586
  accounts active in week  112: 2,626
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

wrote /Users/cheepheng/aml-detection-system/data/variant_IV/eda_cache/account_model_table.csv  (244,000 x 61)
  Onboarding + behaviour features + label, truth columns excluded. This is the table
  the baseline model should read.