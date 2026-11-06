# Task 0029: Read the Goose session store safely

Owner: unclaimed
Claimed: not claimed
State: pending (directory is authoritative)
Phase: B2
Depends on: [0027](../pending/0027-goose-history-cursor-contract.md), [0028](../pending/0028-goose-process-discovery.md)
Authorization / external gate: Not authorized for implementation by this tracking package. Task 0024 must record the applicable scope approval; later native/approval work also needs its specific accepted contract and integration consent. Completed prerequisites alone do not grant permission.

## Goal

Provide bounded read-only session discovery and row access for the explicitly supported native schema.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); its Proposed status is not approval.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0002: limited observation](../../milestones/0002-goose-native-observation.md).

## Acceptance criteria

- [ ] Create synthetic schema-17 fixtures grounded in both pinned release definitions; schema 18 is optional only with separately evidenced compatibility, never inferred from main.
- [ ] Open existing validated storage read-only/query-only with known parameterized queries, safe WAL handling, no extension loading, short busy/query deadlines and row/cell/output bounds.
- [ ] Never initialize or migrate provider storage, change permissions/journal mode, checkpoint, add indexes or copy a live main DB without its WAL; unavailable/corrupt/unknown schema is not empty success.
- [ ] Whitelist metadata fields, filter ordinary project candidates appropriately, and scope memory-only bounded caches to endpoint + store + session; no credentials/system/recipe content returned.
- [ ] Test WAL-only writes, concurrent readers/writers, busy/timeouts, missing/corrupt/unsafe/replaced files and verify no provider writes.
- [ ] Measure query plans and worst-case large/hostile fixtures; record actual rows/bytes/time budgets and demonstrate termination rather than relying on SQL LIMIT alone.

## Files likely involved

- `src/agent_remote.py`
- `src/transport.rs`
- `tests/test_agent_history.py`
- `docs/api.md`

## Findings and decisions

Not started. Keep architectural decisions, discoveries and exact source references here; link a numbered ADR for consequential choices. No prior research test pass is implementation evidence.

## Validation plan

Run from the repository root after creating the required fixture cases. These are validation entry points, **not executed evidence**. Existing suites alone do not prove the new acceptance cases; record the exact new test names and nonzero counts. See [testing guidance](../../testing.md) and [plan verification](../../plans/0002-goose-agent-parity.md#8-verification-plan).

```sh
cargo fmt --check
python3 -m unittest discover -s tests -p 'test_agent_history.py'
cargo test
cargo clippy --all-targets -- -D warnings
```

## Validation evidence

Not run for this task. Record command, environment/fixture revision, exit status, counts/results and limitations as work happens. Fixture input/launch/restart/close tests must never target real work agents or user windows. Do not use private production receipts/transcripts for fixtures.

## Next action / blocker / handoff

- Last completed checkpoint: none; task unclaimed.
- Working tree / commit: no implementation changes for this task; incoming agent must inspect `git status --short` and the actual diff before proceeding.
- Current blocker: scope authorization and unmet prerequisites; do not treat task number order as permission.
- Exact next action: Add a minimal synthetic WAL schema-17 fixture plus no-write/unknown-schema tests, then implement the bounded store reader.
- Resume validation: read prerequisite evidence and accepted decisions, inspect the actual diff, then run only affected checks needed for new changes or unverified/stale evidence; do not blindly rerun completed work.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
