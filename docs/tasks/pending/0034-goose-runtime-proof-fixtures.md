# Task 0034: Build synthetic native-runtime evidence contract tests

Owner: unclaimed
Claimed: not claimed
State: pending (directory is authoritative)
Phase: C2
Depends on: [0033](../pending/0033-goose-native-proof-contract.md), [0026](../done/0026-goose-capability-guards.md)
Authorization / external gate: Not authorized for implementation by this tracking package. Task 0024 must record the applicable scope approval; later native/approval work also needs its specific accepted contract and integration consent. Completed prerequisites alone do not grant permission.

## Goal

Prove the accepted evidence consumer contract with synthetic metadata and processes before trusting an actual native integration.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); its Proposed status is not approval.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0003: full parity](../../milestones/0003-goose-full-agent-parity.md).

## Acceptance criteria

- [ ] Create bounded synthetic producer/consumer fixtures matching the accepted versioned contract; no production provider hooks/config are installed.
- [ ] Reject PID/start/boot/endpoint/store/epoch mismatches, insecure record ownership/permissions, future/stale/malformed/missed/out-of-order evidence and ambiguous owners.
- [ ] Exercise session switch, Stop veto/continuation, child events, crash/freeze, editor/dialog transitions, retention gaps and source identity changes; no invalid case yields Ready/input/restart authority.
- [ ] Durable input-event fixtures distinguish accepted native human input from history replacement/tool/replay records and demonstrate bounded one-use matching.
- [ ] Record exact nonzero test counts and new fixture commands; synthetic success is explicitly not native interoperability approval and cannot itself release task 0035 action gates.

## Files likely involved

- `src/agent_remote.py`
- `tests/test_agent_activity.py`
- `tests/test_agent_outbox.py`
- `tests/test_agent_detection.py`
- `new synthetic native-evidence fixtures (name when implemented)`

## Findings and decisions

Not started. Keep architectural decisions, discoveries and exact source references here; link a numbered ADR for consequential choices. No prior research test pass is implementation evidence.

## Validation plan

Run from the repository root after creating the required fixture cases. These are validation entry points, **not executed evidence**. Existing suites alone do not prove the new acceptance cases; record the exact new test names and nonzero counts. See [testing guidance](../../testing.md) and [plan verification](../../plans/0002-goose-agent-parity.md#8-verification-plan).

```sh
python3 -m unittest discover -s tests -p 'test_agent_activity.py'
python3 -m unittest discover -s tests -p 'test_agent_outbox.py'
python3 -m unittest discover -s tests -p 'test_agent_detection.py'
```

## Validation evidence

Not run for this task. Record command, environment/fixture revision, exit status, counts/results and limitations as work happens. Fixture input/launch/restart/close tests must never target real work agents or user windows. Do not use private production receipts/transcripts for fixtures.

## Next action / blocker / handoff

- Last completed checkpoint: none; task unclaimed.
- Working tree / commit: no implementation changes for this task; incoming agent must inspect `git status --short` and the actual diff before proceeding.
- Current blocker: scope authorization and unmet prerequisites; do not treat task number order as permission.
- Exact next action: Implement negative consumer fixtures from the accepted contract before wiring any authoritative evidence source.
- Resume validation: read prerequisite evidence and accepted decisions, inspect the actual diff, then run only affected checks needed for new changes or unverified/stale evidence; do not blindly rerun completed work.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
