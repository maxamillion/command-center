# Task 0024: Resolve Goose implementation scope and authorization

Owner: unclaimed
Claimed: not claimed
State: pending (directory is authoritative)
Phase: Gate
Depends on: None; this is the next scope/authorization decision.
Authorization / external gate: Documentation/decision capture only; the actual implementation direction and approved scope must come from the user. This record does not authorize code, installs or live actions.

## Goal

Record the user-approved execution scope before any feature work; do not infer approval from the request to prepare this tracking package.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); its Proposed status is not approval.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0003: full parity](../../milestones/0003-goose-full-agent-parity.md).

## Acceptance criteria

- [ ] The user decision, date and scope are recorded in ADR-0002: observation-first native work, explicitly separate managed-ACP replanning, or continued deferral. Only actually approved entries are marked accepted.
- [ ] Record separately which CC-only phases, native proof design/spike, launch/message work and any upstream or opt-in integration work are authorized; installation, live actions and deployment remain separately controlled.
- [ ] If native observation is selected, confirm the proposed dependency graph and milestone boundaries; if ACP is selected, replan dependent tasks before implementation instead of treating native work as approved.
- [ ] Define the native/approval decision owners and next approval requests; unresolved decisions retain Proposed status and their blocked tasks.
- [ ] Update the plan execution status, decision register and root next-action link without marking any implementation criterion complete.

## Files likely involved

- `docs/decisions/0002-goose-integration-direction.md`
- `docs/plans/0002-goose-agent-parity.md`
- `PLAN.md`

## Findings and decisions

Not started. Keep architectural decisions, discoveries and exact source references here; link a numbered ADR for consequential choices. No prior research test pass is implementation evidence.

## Validation plan

Run from the repository root after creating the required fixture cases. These are validation entry points, **not executed evidence**. Existing suites alone do not prove the new acceptance cases; record the exact new test names and nonzero counts. See [testing guidance](../../testing.md) and [plan verification](../../plans/0002-goose-agent-parity.md#8-verification-plan).

```sh
git status --short
git diff --check
```

## Validation evidence

Not run for this task. Record command, environment/fixture revision, exit status, counts/results and limitations as work happens. Fixture input/launch/restart/close tests must never target real work agents or user windows. Do not use private production receipts/transcripts for fixtures.

## Next action / blocker / handoff

- Last completed checkpoint: none; task unclaimed.
- Working tree / commit: no implementation changes for this task; incoming agent must inspect `git status --short` and the actual diff before proceeding.
- Current blocker: awaiting user implementation-scope decision; no code prerequisites for recording it.
- Exact next action: Ask the user to approve the limited native observation scope and identify which later design/implementation phases may proceed; record their literal scope, not a guessed answer.
- Resume validation: read prerequisite evidence and accepted decisions, inspect the actual diff, then run only affected checks needed for new changes or unverified/stale evidence; do not blindly rerun completed work.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
