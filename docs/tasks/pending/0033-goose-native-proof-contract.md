# Task 0033: Decide the native runtime evidence contract

Owner: unclaimed
Claimed: not claimed
State: pending (directory is authoritative)
Phase: C1
Depends on: [0024](../pending/0024-goose-implementation-scope.md)
Authorization / external gate: Not authorized for implementation by this tracking package. Task 0024 must record the applicable scope approval; later native/approval work also needs its specific accepted contract and integration consent. Completed prerequisites alone do not grant permission.

## Goal

Produce an approved, implementable native ownership/lifecycle/acceptance design or record the concrete external blocker; do not invent a hooks-only Ready proof.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); its Proposed status is not approval.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0003: full parity](../../milestones/0003-goose-full-agent-parity.md).

## Acceptance criteria

- [ ] Pin the target implementation/version and create a separately numbered proposed detailed ADR/spec after scanning IDs; record actual decision authority before accepting it.
- [ ] Specify current-session epoch, runtime nonce, process/start/boot/tty/store evidence, ordered state/freshness and actual editor-settled semantics after vetoable continuations/cleanup.
- [ ] Specify native-input persistence provenance, full normalized digest and bounded durable sequence/retention; history edits/replays/imports cannot mint acceptance.
- [ ] Specify session ownership/exclusivity coverage for resume (including other native owners), child isolation and fail-closed behavior for partial/stale/uninstrumented coverage.
- [ ] Record approved upstream versus maintained opt-in integration ownership, packaging, private metadata permissions and exact consent needed for fixture/native integration; no automatic installation, live reload or network listener.
- [ ] Separate metadata observation from decision authority; either link an accepted feasible contract and concrete native provider or keep dependent native work blocked with an owner/action. A decision to defer does not deliver parity.

## Files likely involved

- `docs/decisions/0002-goose-integration-direction.md`
- `docs/plans/0002-goose-agent-parity.md`
- `docs/decisions/ (allocate a new detailed contract ADR when authorized)`

## Findings and decisions

Not started. Keep architectural decisions, discoveries and exact source references here; link a numbered ADR for consequential choices. No prior research test pass is implementation evidence.

## Validation plan

Run from the repository root after creating the required fixture cases. These are validation entry points, **not executed evidence**. Existing suites alone do not prove the new acceptance cases; record the exact new test names and nonzero counts. See [testing guidance](../../testing.md) and [plan verification](../../plans/0002-goose-agent-parity.md#8-verification-plan).

```sh
git status --short
git diff --check
```

The exact producer/native harness command cannot be fixed until the integration contract is selected. Record it, its pinned version, isolated configuration and nonzero results here **before** claiming the corresponding native acceptance criteria; the existing suites above are not a substitute.

## Validation evidence

Not run for this task. Record command, environment/fixture revision, exit status, counts/results and limitations as work happens. Fixture input/launch/restart/close tests must never target real work agents or user windows. Do not use private production receipts/transcripts for fixtures.

## Next action / blocker / handoff

- Last completed checkpoint: none; task unclaimed.
- Working tree / commit: no implementation changes for this task; incoming agent must inspect `git status --short` and the actual diff before proceeding.
- Current blocker: scope authorization and unmet prerequisites; do not treat task number order as permission.
- Exact next action: After authorized design scope, resolve the native-versus-managed architecture and the real producer of current-session/settled/input events with the user; do not assume existing hooks satisfy it.
- Resume validation: read prerequisite evidence and accepted decisions, inspect the actual diff, then run only affected checks needed for new changes or unverified/stale evidence; do not blindly rerun completed work.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
