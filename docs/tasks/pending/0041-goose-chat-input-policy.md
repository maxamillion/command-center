# Task 0041: Validate native Goose editor and ordinary input policy

Owner: unclaimed
Claimed: not claimed
State: pending (directory is authoritative)
Phase: E1
Depends on: [0035](../blocked/0035-goose-native-runtime-integration.md), [0031](../pending/0031-goose-observation-ui.md)
Authorization / external gate: Not authorized for implementation by this tracking package. Task 0024 must record the applicable scope approval; later native/approval work also needs its specific accepted contract and integration consent. Completed prerequisites alone do not grant permission.

## Goal

Establish when literal ordinary chat submission is safe, without enabling dispatch yet or using Ctrl+C to force an input state.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); its Proposed status is not approval.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0003: full parity](../../milestones/0003-goose-full-agent-parity.md).

## Acceptance criteria

- [ ] Define and enforce supported native editor/prompt states from fresh process/session/epoch evidence; working/dialog/copy-mode/unknown states reject ordinary input.
- [ ] Fixture-tested bracketed paste/Enter handles multiline, Unicode and maximum text without accidental shell, slash command, exit/quit or menu responses; document an explicit command-like-text reject/disclosure policy.
- [ ] Never clear/cancel the native process implicitly to send; preserve drafts and native user input, and reject conflicting editor state rather than overwriting it.
- [ ] Revalidate process/start/endpoint/session/epoch/screen and editor state immediately before any transport input; an earlier Ready snapshot is insufficient.
- [ ] Record exact isolated native parser/editor test commands and provenance; fake-agent success alone is not native editor validation. No live work-agent input is authorized.

## Files likely involved

- `src/agent_remote.py`
- `src/agents.rs`
- `tests/test_agent_outbox.py`
- `web/tests/outbox.spec.ts`
- `docs/api.md`

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

The exact producer/native harness command cannot be fixed until the integration contract is selected. Record it, its pinned version, isolated configuration and nonzero results here **before** claiming the corresponding native acceptance criteria; the existing suites above are not a substitute.

## Validation evidence

Not run for this task. Record command, environment/fixture revision, exit status, counts/results and limitations as work happens. Fixture input/launch/restart/close tests must never target real work agents or user windows. Do not use private production receipts/transcripts for fixtures.

## Next action / blocker / handoff

- Last completed checkpoint: none; task unclaimed.
- Working tree / commit: no implementation changes for this task; incoming agent must inspect `git status --short` and the actual diff before proceeding.
- Current blocker: scope authorization and unmet prerequisites; do not treat task number order as permission.
- Exact next action: Using the consented isolated native harness, add command-like-text and dialog/editor-race negative cases before implementing any submit capability.
- Resume validation: read prerequisite evidence and accepted decisions, inspect the actual diff, then run only affected checks needed for new changes or unverified/stale evidence; do not blindly rerun completed work.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
