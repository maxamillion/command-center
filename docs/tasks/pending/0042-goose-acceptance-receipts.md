# Task 0042: Add versioned native-input acceptance receipts

Owner: unclaimed
Claimed: not claimed
State: pending (directory is authoritative)
Phase: E2
Depends on: [0034](../pending/0034-goose-runtime-proof-fixtures.md), [0027](../done/0027-goose-history-cursor-contract.md)
Authorization / external gate: Not authorized for implementation by this tracking package. Task 0024 must record the applicable scope approval; later native/approval work also needs its specific accepted contract and integration consent. Completed prerequisites alone do not grant permission.

## Goal

Extend durable receipt serialization/matching additively; never reinterpret mutable history positions as accepted input.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); its Proposed status is not approval.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0003: full parity](../../milestones/0003-goose-full-agent-parity.md).

## Acceptance criteria

- [ ] Add a tagged optional acceptance proof scoped to endpoint/process/start/boot/runtime/session epoch/store generation and native input sequence/digest, with a baseline persisted before IO.
- [ ] Only later provider-origin persisted native human-input events match once; tool rows, ready changes, summaries/replays, edited/imported/reinserted text and retention gaps cannot confirm Seen.
- [ ] Legacy baseline/pending-pi/seen fields and provider matching remain readable with unchanged IDs/digests/status/revisions; missing new fields do not trigger retrofitted anchors.
- [ ] Preserve archived ambiguity, exact bulk snapshot semantics, private persistence and Submitting-to-Uncertain crash recovery. If physical migration is needed, take a private backup and prove restart/migration without auto-restoring receipt backups.
- [ ] Add serialization/matching/restart fixtures for old and new receipts; synthetic proof is not native proof and cannot enable delivery until tasks 0035/0041/0043 are satisfied.

## Files likely involved

- `src/outbox.rs`
- `src/agent_remote.py`
- `src/board.rs (only if physical storage migration is required)`
- `tests/test_agent_outbox.py`
- `web/tests/outbox.spec.ts`

## Findings and decisions

Not started. Keep architectural decisions, discoveries and exact source references here; link a numbered ADR for consequential choices. No prior research test pass is implementation evidence.

## Validation plan

Run from the repository root after creating the required fixture cases. These are validation entry points, **not executed evidence**. Existing suites alone do not prove the new acceptance cases; record the exact new test names and nonzero counts. See [testing guidance](../../testing.md) and [plan verification](../../plans/0002-goose-agent-parity.md#8-verification-plan).

```sh
cargo fmt --check
python3 -m unittest discover -s tests -p 'test_agent_outbox.py'
cargo test
cargo clippy --all-targets -- -D warnings
```

## Validation evidence

Not run for this task. Record command, environment/fixture revision, exit status, counts/results and limitations as work happens. Fixture input/launch/restart/close tests must never target real work agents or user windows. Do not use private production receipts/transcripts for fixtures.

## Next action / blocker / handoff

- Last completed checkpoint: none; task unclaimed.
- Working tree / commit: no implementation changes for this task; incoming agent must inspect `git status --short` and the actual diff before proceeding.
- Current blocker: scope authorization and unmet prerequisites; do not treat task number order as permission.
- Exact next action: Write old-JSON receipt round-trip and false-confirmation-from-reinserted-history tests before extending the receipt record.
- Resume validation: read prerequisite evidence and accepted decisions, inspect the actual diff, then run only affected checks needed for new changes or unverified/stale evidence; do not blindly rerun completed work.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
