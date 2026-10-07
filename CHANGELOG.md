# Changelog

Changes to the simulator and the data it generates, newest first. Settings changes are also noted in the
`source` of each value in `configs/sim.yaml`; decisions are recorded in the "Simulated Dataset: Logic,
Assumptions and Use" doc.

## 7 Oct 2026 — anonymous transaction ids (fixes a label leak)

**Problem.** `txn_id` in the public `transactions` file started with `L_` for every laundering transfer and
`N###_` for normal ones, so anyone reading the column could see which rows were laundering. Laundering rows
also sat together at the start of the file, so a row's position gave the label away too. Flagged in the EDA
report (§12); fix approved 7 Oct 2026.

**Change.**
- `finalize` now gives every transfer a new id: `T` + 16 hex characters of md5(provisional id + seed).
  Both rows of an internal transfer still share one id. Same config + seed still gives identical data.
- `transactions` is written sorted by `day`, `time` (ties by `txn_id`, `account_id`).
- The provisional `N###_` / `L_` ids remain only in the hidden working files under `_internal/`.
- New check 10 (`anonymous ids`) fails if any id is not `T` + 16 hex, if laundering ids are not spread
  evenly (mean position must be within 0.45–0.55), or if rows are out of time order.

**Effect on results: none.** Rebuilding `data/v1` (50,000 accounts, seed 42) left `accounts`,
`accounts_truth`, `aml_alerts` and `aml_outcomes` byte-identical; every transaction row and label is
unchanged (22,276,022 rows, 21,741,821 distinct ids, no collisions). Only `txn_id` values and row order
changed. All 10 checks and 5 tests pass.

**Action for the team.** Re-generate or re-run `finalize` on any local copy of `data/v1` made before this
change; old copies still carry the leak. Never build features from `txn_id`; use it only to join the two
rows of a transfer.
