# Task 0035: Validate an authorized native runtime evidence producer

Owner: unclaimed
Claimed: not claimed
State: blocked (directory is authoritative)
Phase: C3
Depends on: [0034](../pending/0034-goose-runtime-proof-fixtures.md)
Authorization / external gate: Explicitly blocked on an authorized actual native runtime evidence producer, its pinned implementation and permission to validate it; none is selected. User and native integration maintainer must supply/approve this before implementation.

## Goal

Integrate and validate a real consented native producer; do not promote fixture signals or terminal telemetry into authority.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); its Proposed status is not approval.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0003: full parity](../../milestones/0003-goose-full-agent-parity.md).

## Acceptance criteria

- [ ] Link the accepted contract/producer revision, license/maintenance owner and explicit authorization for its implementation/testing; no external checkout changes or installs without that scope.
- [ ] Validate real current-session switches, actual input-ready settlement after stop-hook veto/continuation, child isolation, errors/cancellation/max-turns and stale/frozen/reordered evidence against that producer.
- [ ] Prove actual native-input persistence provenance and durable acceptance sequence without storing message/tool/reply content in observation metadata.
- [ ] Prove ownership/exclusive-resume checks across native owners or fail closed where coverage is incomplete; startup args/shared DB/bridge liveness alone never establish current authority.
- [ ] Read bounded private metadata over existing local/SSH/ProxyJump transport; preserve no-daemon/no-network-exposure and noninvasive uninstrumented-agent fallback.
- [ ] Record exact reproducible isolated native harness commands and versioned results; no work-agent launch/send, global provider reconfiguration or live reload. Consumer capabilities are exposed only for demonstrated cases; missing producer coverage remains blocked.

## Files likely involved

- `src/agent_remote.py`
- `src/transport.rs`
- `src/queue.rs`
- `an explicitly approved native producer location (not selected yet)`
- `isolated native integration fixtures (define after approval)`

## Findings and decisions

Not started. Keep architectural decisions, discoveries and exact source references here; link a numbered ADR for consequential choices. No prior research test pass is implementation evidence.

## Validation plan

Run from the repository root after creating the required fixture cases. These are validation entry points, **not executed evidence**. Existing suites alone do not prove the new acceptance cases; record the exact new test names and nonzero counts. See [testing guidance](../../testing.md) and [plan verification](../../plans/0002-goose-agent-parity.md#8-verification-plan).

```sh
cargo fmt --check
python3 -m unittest discover -s tests -p 'test_agent_activity.py'
python3 -m unittest discover -s tests -p 'test_agent_outbox.py'
cargo test
cargo clippy --all-targets -- -D warnings
```

The exact producer/native harness command cannot be fixed until the integration contract is selected. Record it, its pinned version, isolated configuration and nonzero results here **before** claiming the corresponding native acceptance criteria; the existing suites above are not a substitute.

## Validation evidence

Not run for this task. Record command, environment/fixture revision, exit status, counts/results and limitations as work happens. Fixture input/launch/restart/close tests must never target real work agents or user windows. Do not use private production receipts/transcripts for fixtures.

## Next action / blocker / handoff

- Last completed checkpoint: none; task unclaimed.
- Working tree / commit: no implementation changes for this task; incoming agent must inspect `git status --short` and the actual diff before proceeding.
- Current blocker: external dependency above, plus unmet prerequisites and authorization.
- Exact next action: User/integration maintainer must select and authorize a producer satisfying task 0033, supply its pinned implementation and permit isolated native tests; only then move this task out of blocked.
- Resume validation: read prerequisite evidence and accepted decisions, inspect the actual diff, then run only affected checks needed for new changes or unverified/stale evidence; do not blindly rerun completed work.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
