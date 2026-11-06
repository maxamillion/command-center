# Task 0030: Project Goose chat history and inline activity

Owner: unclaimed
Claimed: not claimed
State: pending (directory is authoritative)
Phase: B3
Depends on: [0029](../pending/0029-goose-readonly-session-store.md)
Authorization / external gate: Not authorized for implementation by this tracking package. Task 0024 must record the applicable scope approval; later native/approval work also needs its specific accepted contract and integration consent. Completed prerequisites alone do not grant permission.

## Goal

Normalize visible native history into CC chat and activity without confusing tool/control records with human input or assistant replies.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); its Proposed status is not approval.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0002: limited observation](../../milestones/0002-goose-native-observation.md).

## Acceptance criteria

- [ ] Apply message user visibility and content audience rules; preserve native timestamp/tie ordering and visible text; exclude hidden context/replays/control/system/internal records.
- [ ] User-role tool results never become human chat/input acceptance; tool calls/results pair by scoped ID plus occurrence, including repeated/null source IDs and legacy/error wrappers.
- [ ] Export only provider-visible supported activity text; signatures/redacted opaque fields stay excluded, media gets bounded placeholders, and no logged resource/spill paths are fetched.
- [ ] Implement bounded paging/version/reset using task 0027 contracts; edits, truncation, compaction and delete/reinsert invalidate stale pages without inventing unread replies.
- [ ] Stable source identities preserve disclosures/order across polling; tool-result updates do not advance reply cursors and no result means Awaiting result.
- [ ] Add fixtures for malformed/huge content, sanitization, hidden replays, mixed activity/text and store mutation; disclose omissions and persisted-not-streaming limits.

## Files likely involved

- `src/agent_remote.py`
- `src/attention.rs`
- `tests/test_agent_history.py`
- `tests/test_agent_activity.py`
- `web/src/queue.ts`
- `web/src/agent-activity.ts`
- `web/tests/agents.spec.ts`

## Findings and decisions

Not started. Keep architectural decisions, discoveries and exact source references here; link a numbered ADR for consequential choices. No prior research test pass is implementation evidence.

## Validation plan

Run from the repository root after creating the required fixture cases. These are validation entry points, **not executed evidence**. Existing suites alone do not prove the new acceptance cases; record the exact new test names and nonzero counts. See [testing guidance](../../testing.md) and [plan verification](../../plans/0002-goose-agent-parity.md#8-verification-plan).

```sh
cargo fmt --check
python3 -m unittest discover -s tests -p 'test_agent_history.py'
python3 -m unittest discover -s tests -p 'test_agent_activity.py'
cargo test
cargo clippy --all-targets -- -D warnings
npm --prefix web run build -- --outDir dist-next
```

## Validation evidence

Not run for this task. Record command, environment/fixture revision, exit status, counts/results and limitations as work happens. Fixture input/launch/restart/close tests must never target real work agents or user windows. Do not use private production receipts/transcripts for fixtures.

## Next action / blocker / handoff

- Last completed checkpoint: none; task unclaimed.
- Working tree / commit: no implementation changes for this task; incoming agent must inspect `git status --short` and the actual diff before proceeding.
- Current blocker: scope authorization and unmet prerequisites; do not treat task number order as permission.
- Exact next action: Implement the two-level visible-content projection against synthetic records, starting with tool-only user rows and hidden-summary negative fixtures.
- Resume validation: read prerequisite evidence and accepted decisions, inspect the actual diff, then run only affected checks needed for new changes or unverified/stale evidence; do not blindly rerun completed work.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
