---
name: feature-round
description: One round of the EDA -> feature loop for the AML project. Runs the eda-explorer agent (up to 5 insights from months 0-4), lets the user pick which to try, runs the feature-engineer agent on them (at most 3 trials, winners confirmed once on seed 43), and reports. Use for "/feature-round", "run a feature round", "explore and try new features". Report-appendix work; never changes the frozen feature list.
---

# /feature-round

One round of the loop agreed on 27 Oct 2026: **EDA agent -> the user picks -> feature engineer -> report.** It is
report-appendix work: results never change the frozen feature list for tuning or the test months. Optional
arguments: a focus for the EDA (e.g. "counterparties", "real-customer mules"), the number of insights (default 5)
and trials (default 3).

## 0. Preflight
- Not on `main`: if `git branch --show-current` is `main`, stop and ask for a branch (suggest `feature-round-<round>`).
- `data/v1_full/features/weekly.parquet` and `data/v1/features/weekly.parquet` exist; if not, stop and say which
  command builds them (CLAUDE.md, Commands).
- Count the looks: rows of `outputs/modelling/feature_lab/ledger.csv`, in total and with `data = v1_full`. Tell the
  user the number before starting.

## 1. EDA
Run the `eda-explorer` agent in the foreground (`run_in_background: false`) and without worktree isolation, so its
files land in this checkout. Pass the focus and the number of insights, if given. When it returns, read the new rows
of `outputs/modelling/eda_agent/insights.csv` yourself (do not rely on the summary alone) and run
`PYTHONPATH=src venv/bin/python -m pytest -q tests/test_eda_agent.py tests/test_hidden_files.py`.

## 2. The user picks (the gate)
Show the new insights as a table: id, finding, who, before_start, AUC per group, artefact, buildable. Only rows with
`buildable = store` and `artefact` not `yes` can go to the feature engineer; say so for the others (`raw` ones are
team proposals). Ask which to try: with up to 4 eligible insights, use AskUserQuestion (multiSelect); with more,
list them and ask for the ids. Never pick for the user. Then set `status` in `insights.csv` to `approved` for the
chosen ones and `rejected` for the eligible ones not chosen (status column only). If none are chosen, skip to 4.

## 3. Feature engineer
Run the `feature-engineer` agent in the foreground, without worktree isolation, with the approved ids and the trial
limit (default 3). It runs v1, then v1_full for groups that pass, then seed 43 once for promotion candidates, and
updates the insights' `status`. When it returns, run
`PYTHONPATH=src venv/bin/python -m pytest -q tests/test_feature_candidates.py tests/test_feature_lab.py tests/test_eda_agent.py tests/test_hidden_files.py`
and check the ledger gained the rows it reports.

## 4. Report
In plain language (the team includes non-specialists):
- one table, one row per insight: id, finding, decision (rejected / tried / dropped / candidate / confirmed /
  not confirmed), the main numbers (`d_weekly_recall`, `d_start_recall`, `d_first_caught_2wk` per fold);
- looks so far, before and after the round (total and v1_full);
- the caveat: the lab judges each week's top 1%, about 60x more flags than the rules raise; only the Phase 5 harness
  at the rules' budget shows whether a feature helps;
- every file changed or created. Nothing is committed: offer a commit and PR (CHANGELOG entry first), do not make one
  unasked. A confirmed group is a recommendation for the team, never added to `ADOPTED` or the store by this skill.
