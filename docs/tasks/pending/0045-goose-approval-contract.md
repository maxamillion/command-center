# Task 0045: Specify native Goose approval arbitration

Owner: unclaimed
Claimed: not claimed
State: pending (directory is authoritative)
Phase: F1-design
Depends on: [0033](../pending/0033-goose-native-proof-contract.md)
Authorization / external gate: Not authorized for implementation by this tracking package. Task 0024 must record the applicable scope approval; later native/approval work also needs its specific accepted contract and integration consent. Completed prerequisites alone do not grant permission.

## Goal

Obtain an accepted approval decision contract or record the exact unavailable capability; do not automate native cursor navigation.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); its Proposed status is not approval.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0003: full parity](../../milestones/0003-goose-full-agent-parity.md).

## Acceptance criteria

- [ ] Link a separately allocated detailed proposed ADR/spec and actual decision authority; preserve ADR-0002 gate status until the chosen contract is accepted.
- [ ] Specify exact original request/arguments/scopes, offered option IDs/labels, unique generation/expiry, fresh process/session binding and one-use cross-client arbitration.
- [ ] Specify coordination with the native terminal menu so an external decision invalidates/releases that exact pending UI; repeated identical prompts remain distinguishable.
- [ ] Disclose persistent Always Allow scope and notice-dependent choices; arbitrary elicitation remains unsupported. No guessed single key, navigation-plus-Enter or implicit cancellation workaround.
- [ ] Record upstream/opt-in implementation owner, version, authorization and test plan; acceptance of this design is not delivered approval support and cannot unblock task 0046 without a real channel.

## Files likely involved

- `docs/decisions/0002-goose-integration-direction.md`
- `docs/plans/0002-goose-agent-parity.md`
- `docs/decisions/ (allocate approval ADR/spec after authorization)`

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
- Exact next action: Ask the native integration owner for a request-correlated channel that coordinates with the terminal UI; leave terminal-only handling explicit if no feasible authorized channel exists.
- Resume validation: read prerequisite evidence and accepted decisions, inspect the actual diff, then run only affected checks needed for new changes or unverified/stale evidence; do not blindly rerun completed work.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
