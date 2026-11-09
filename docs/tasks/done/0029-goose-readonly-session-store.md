# Task 0029: Read the Goose session store safely

Owner: Codex
Claimed: 2026-11-06
State: done (directory is authoritative)
Phase: B2
Depends on: [0027](../done/0027-goose-history-cursor-contract.md), [0028](../done/0028-goose-process-discovery.md)
Authorization / external gate: Authorized as CC-owned, read-only schema-17 observation work under the user's 2026-11-06 scope decision in [ADR-0002](../../decisions/0002-goose-integration-direction.md). This does not authorize provider-store writes, native-session ownership claims, integration installation, or live Goose operations.

## Goal

Provide bounded read-only session discovery and row access for the explicitly supported native schema.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); accepted for CC-owned work in dependency order.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0002: limited observation](../../milestones/0002-goose-native-observation.md).

## Acceptance criteria

- [x] Create synthetic schema-17 fixtures grounded in both pinned release definitions; schema 18 is optional only with separately evidenced compatibility, never inferred from main.
- [x] Open existing validated storage read-only/query-only with known parameterized queries, safe WAL handling, no extension loading, short busy/query deadlines and row/cell/output bounds.
- [x] Never initialize or migrate provider storage, change permissions/journal mode, checkpoint, add indexes or copy a live main DB without its WAL; unavailable/corrupt/unknown schema is not empty success.
- [x] Whitelist metadata fields, filter ordinary project candidates appropriately, and scope memory-only bounded caches to endpoint + store + session; no credentials/system/recipe content returned.
- [x] Test WAL-only writes, concurrent readers/writers, busy/timeouts, missing/corrupt/unsafe/replaced files and verify no provider writes.
- [x] Measure query plans and worst-case large/hostile fixtures; record actual rows/bytes/time budgets and demonstrate termination rather than relying on SQL LIMIT alone.

## Files likely involved

- `src/agent_remote.py`
- `src/transport.rs`
- `tests/test_agent_goose_store.py`
- `tests/test_agent_history.py`
- `docs/api.md`

## Findings and decisions

Schema-17 structure and version boundaries were reviewed in the source audit recorded by [Plan 0002 U1](../../plans/0002-goose-agent-parity.md#10-source-evidence-index): the pinned v1.55 and v1.57 release definitions agree on the core `sessions`/`messages` fields used here; main's schema 18 adds session tags and is rejected. Goose uses a shared WAL database, and message order is `created_timestamp`, then integer row ID. The adapter uses the resolved host-local data directory from task 0028, requires existing same-account directories/files without symlinks or group/world write permission, and uses `mode=ro`, `query_only`, `trusted_schema=OFF`, disabled extension loading, SQLite limits and progress/busy deadlines. It never initializes, migrates, repairs, checkpoints, changes journal mode or copies the provider DB. For a live WAL store it requires the existing regular WAL and SHM sidecars; when sidecars are absent it reports unavailable instead of allowing SQLite to create them. A path audit during this task corrected the Windows default root to `%APPDATA%\\Block\\goose\\data`; see [Bug 0015](../../bugs/fixed/0015-goose-windows-store-data-directory.md).

Project discovery returns at most 20 whitelisted user-session metadata rows for the observed project and excludes hidden/non-user and scheduled sessions. Message access is parameterized and bounded to the same eligible project session, returns integer row IDs and timestamps as decimal strings, and exposes only the `userVisible` metadata bit. Message blocks remain inside the helper until task 0030 filters them into a public projection. No Goose store cache was added; process observation still grants no current-session link or history API capability.

## Validation plan

Run from the repository root after creating the required fixture cases. These are validation entry points, **not executed evidence**. Existing suites alone do not prove the new acceptance cases; record the exact new test names and nonzero counts. See [testing guidance](../../testing.md) and [plan verification](../../plans/0002-goose-agent-parity.md#8-verification-plan).

```sh
cargo fmt --check
python3 -m unittest discover -s tests -p 'test_agent_goose_store.py'
python3 -m unittest discover -s tests -p 'test_agent_history.py'
cargo test
cargo clippy --all-targets -- -D warnings
```

## Validation evidence

All storage fixtures are synthetic and temporary; no live Goose account/database, remote host or user tmux window was used. Read-only tests confirmed the main database and WAL bytes remained unchanged, no sidecars were created for ordinary rollback-journal stores, and `query_only` rejected writes. A clean WAL-mode DB without pre-existing WAL/SHM sidecars is refused before open so this helper does not create coordination files.

- `python3 -m unittest discover -s tests -p 'test_agent_goose_store.py'` — passed, 12 tests. Covers schema 17, schema 18 rejection, views, whitelisted candidates, parameterized history rows, timestamp/ID order and paging, malformed/oversized cells, read-only writes, WAL-only commits, concurrent reader/writer snapshots, busy timeout, missing/corrupt/symlink/writable/replaced paths and bounded scan cancellation.
- `python3 -m unittest discover -s tests -p 'test_agent_detection.py'` — passed, 17 tests, including the corrected Windows data root.
- `python3 -m unittest discover -s tests -p 'test_agent*.py'` — passed, 86 tests. Existing history fixtures emitted SQLite `ResourceWarning`s for unclosed connections; no failures.
- Synthetic query plans: session discovery reports `SCAN sessions`; message history reports `SEARCH messages USING INDEX idx_messages_session_message (session_id=?)` plus `USE TEMP B-TREE FOR ORDER BY` for Goose's timestamp/ID order.
- A 30,000-row sparse-project scan with the progress limit temporarily reduced to 10 callbacks was interrupted in 1.93 ms, demonstrating cancellation without relying on SQL `LIMIT`. Production bounds are 1,200 callbacks × 1,000 VM operations per statement, 250 ms per query and one second per store request; SQLite lock waiting is 100 ms.
- Bounds: 20 session candidates, 100 rows per page, 128 KiB maximum SQLite cell, 64 KiB content JSON per returned row, 512 KiB combined source content per page, 256 MiB WAL and 64 MiB SHM. No metadata/content cache is retained.
- `cargo test` — passed: 47 library, 2 binary and 2 tmux integration tests.
- `cargo clippy --all-targets -- -D warnings`, `cargo fmt --check` and `git diff --check` — passed.

The row reader is not wired into the Agent API yet. Goose `project_history` remains unavailable until task 0030 adds a safe projection and reset-contract integration; this task does not expose raw blocks, infer current session/Ready, or enable actions. No actual Goose database interoperability, macOS/Windows runtime or remote SSH store was exercised.

## Next action / blocker / handoff

- Last completed checkpoint: tasks 0027–0029 cover opaque history ordering/read cursors, interactive process identity and a bounded read-only schema-17 session-store adapter.
- Working tree / commit: uncommitted shared tree includes Plan tasks 0024–0029, Bug 0015 and earlier workspace work. Preserve them and inspect the actual diff before editing.
- Current blocker: none for task 0030's authorized CC-owned projection. Native current-session/Ready proof remains gated by task 0035.
- Exact next action: claim task 0030 and implement Goose's visible text/activity projection over the internal row reader, with repeated/null call IDs, visibility/audience rules, mutable history resets and no raw metadata exposure.
- Resume validation: read prerequisite evidence and accepted decisions, inspect the actual diff, then run only affected checks needed for new changes or unverified/stale evidence; do not blindly rerun completed work.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
