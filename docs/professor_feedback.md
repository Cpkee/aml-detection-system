# Professor's feedback on the proposal

Verbatim, as received (pasted into the project on 8 Oct 2026).

> 1. Since the dataset is synthetic, how it can effectively reflect real-life situations and bring practical
>    significance would be a potential problem. You can try artificially adjusting your currently balanced test
>    set to a realistically imbalanced ratio (e.g., 1% phishing) to evaluate if false positives spike.
>
> 2. From Week 1 to Week 8, it is likely to have a different population of surviving accounts. Performance
>    changes may reflect data availability, cohort composition, or label maturity. If you want to estimate the
>    values of onboarding information, it is important to consider the other changing variables.
>
> For the final report, please provide sufficient detail and justification for each section. For example,
> explain your choice of dataset, its key characteristics such as size and variables, the preprocessing and
> feature engineering steps, and why the selected models are suitable for the task.

## How we answer it (plan agreed 8 Oct 2026)

| Comment | Our answer |
|---|---|
| 1. Realism of synthetic data | Every simulator number has a published source or is labelled an assumption and tested (`configs/sim.yaml`, 42 sensitivity runs); the bank's rules are set to practitioner-like false-alarm levels. |
| 1. "Balanced test set" → realistic imbalance | Our test set is **not** balanced: it uses the natural 0.3% launderer rate (BioCatch), rarer than the 1% example, and is never resampled. Prevalence datasets at 0.1% (732k accounts) and 1% (244k) exist; the rules' false alarms rise from 81.3% (1%) to 93.4% (0.3%) to 97.8% (0.1%) (after the R6 fix). Milestone: the same comparison for the model (false-alarm share and precision at 0.1 / 0.3 / 1%). |
| 2. Cohort composition | One fixed cohort: the 50,061 test accounts (opened months 6–7), clock = weeks since each account opened. Accounts closed by the bank stay in the cohort (as caught), never silently dropped; report accounts still open per week. |
| 2. Data availability | The value of onboarding information = activity-only vs application + activity **at the same week**, on the same cohort and the same transactions, so more data alone cannot explain the gap. |
| 2. Label maturity | Main label "mule account by this week" (fake accounts from opening, real customers from their start). Also score against a fixed final label (mule at any point in the window) and report per week how many launderers have started. |
| Report detail | Checklist in CLAUDE.md: dataset choice, size and variables, preprocessing, feature engineering, model suitability, each with justification. |
