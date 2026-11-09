# Task 0024: Resolve Goose implementation scope and authorization

Owner: Codex
Claimed: 2026-11-06
State: done (directory is authoritative)
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

- [x] The user decision, date and scope are recorded in ADR-0002: native observation-first work; managed ACP was not selected.
- [x] CC-only implementation, native proof design/synthetic work, launch/message code work and background qualification are authorized in dependency order; upstream changes, integration installation and live actions remain separately controlled.
- [x] The native observation dependency graph and separate observation/full-parity milestones are retained in Plan 0002.
- [x] Native producer and approval-channel owners/next actions remain recorded as unresolved external gates; their tasks remain blocked.
- [x] Updated the plan execution status, ADR register and root index without marking implementation criteria complete.

## Files likely involved

- `docs/decisions/0002-goose-integration-direction.md`
- `docs/plans/0002-goose-agent-parity.md`
- `PLAN.md`

## Findings and decisions

The user explicitly authorized implementation by requesting: “please follow and implement Plan 0002 in order to implement support for goose into this project.” Recorded this as native Goose support in Command Center, with the plan's limited observation milestone first and task dependency order thereafter. CC-owned implementation, synthetic fixtures and qualification are in scope once prerequisites are met. Managed ACP was not selected.

This does not authorize upstream/third-party repository changes, installation or activation of an external integration, or live Goose launches/messages/restarts/closes/approvals. Task 0035 still needs a named, pinned and consented native evidence producer; task 0046 still needs an accepted implemented terminal-coordinated approval channel. Runtime action capabilities remain disabled until task-level evidence and the plan's gates are met. See [ADR-0002](../../decisions/0002-goose-integration-direction.md).

## Validation plan

Run from the repository root after creating the required fixture cases. These are validation entry points, **not executed evidence**. Existing suites alone do not prove the new acceptance cases; record the exact new test names and nonzero counts. See [testing guidance](../../testing.md) and [plan verification](../../plans/0002-goose-agent-parity.md#8-verification-plan).

```sh
git status --short
git diff --check
```

## Validation evidence

`git status --short` and `git diff --check` run from the repository root after the scope/decision/index updates: clean of pre-existing changes before edits; diff check recorded with the implementation checkpoint. No runtime tests apply to this documentation/authorization task. No live operation or external installation was performed.

## Next action / blocker / handoff

- Last completed checkpoint: recorded the user's implementation request and scoped authorization in ADR-0002; updated Plan 0002 and PLAN.md; moved task 0024 to done.
- Working tree / commit: documentation changes are uncommitted alongside the active task 0025 implementation; inspect the actual diff before handoff.
- Current blocker: none for task 0025. Tasks 0035 and 0046 remain externally blocked as documented.
- Exact next action: claim and implement task 0025, explicit provider dispatch, then proceed in dependency order.
- Resume validation: read prerequisite evidence and accepted decisions, inspect the actual diff, then run only affected checks needed for new changes or unverified/stale evidence; do not blindly rerun completed work.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
