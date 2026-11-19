# AML detection system (BT4012 Fraud Analytics, Group 09)

Words the report and the slides use for the project's ideas: one word per idea, so a non-specialist reader never
wonders whether two words mean two things.

## Language

**Mule account**:
A bank account used to receive criminal money and pass it on. It is one of three kinds: fake account, witting mule or
unwitting mule.
_Avoid_: launderer, money-laundering account, fraud account

**Fake account**:
A mule account opened with a stolen or invented identity, used for laundering from the day it opens.
_Avoid_: synthetic account, fraud row

**Witting mule**:
A real customer who knowingly sells or lends their account for laundering.
_Avoid_: complicit mule

**Unwitting mule**:
A real customer tricked into moving criminal money through their own account.
_Avoid_: innocent mule, victim mule

**The bank's rules**:
The six weekly transaction-monitoring rules (R1–R6) that our model is compared against.
_Avoid_: benchmark, baseline, rule-based system, existing rules

**Flag**:
Putting an account on the week's review list, whether the model or the bank's rules does it. A flag is permanent.
_Avoid_: alert (for the model), detection, hit

**Caught**:
A mule account that has been flagged while it is a mule account.
_Avoid_: detected, found earlier

**Weekly alert budget**:
The number of accounts the bank's rules flag in a given week of the accounts' lives; the model may flag exactly as
many that week.
_Avoid_: review cost, alert count, workload

**Days from start**:
The number of days from a mule account's first laundering payment to its first flag, the only measure of speed.
_Avoid_: earlier (as a word for "caught when the rules never are")
