# Task 0036: Build provider-specific Goose launch arguments

Owner: unclaimed
Claimed: not claimed
State: pending (directory is authoritative)
Phase: D1
Depends on: [0025](../done/0025-goose-provider-dispatch.md)
Authorization / external gate: Not authorized for implementation by this tracking package. Task 0024 must record the applicable scope approval; later native/approval work also needs its specific accepted contract and integration consent. Completed prerequisites alone do not grant permission.

## Goal

Add a tested literal argv builder for new interactive, reviewed prompt/model and exact resume shapes without launching agents.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); its Proposed status is not approval.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0003: full parity](../../milestones/0003-goose-full-agent-parity.md).

## Acceptance criteria

- [ ] Replace shared positional-prompt/UUID assumptions with provider-specific validated native ID and argv rules; keep CC action UUIDs separate.
- [ ] New without text, new with literal text, and exact resume command arrays match the supported pinned CLI; system instructions, latest/name/fork/edit/no-session shortcuts are not substituted.
- [ ] Validate optional literal model and root/default inheritance; blank does not add overrides. Disclose native provider/model/cwd prompts and unsupported configuration rather than answering or guessing.
- [ ] Fixtures cover hyphen-leading values, Unicode/newline/quotes, worst-case escaping at 24,000 UTF-8 bytes, byte limits and private argv handoff cleanup.
- [ ] Builder tests do not expose resume/restart or execute the installed Goose; legacy provider arrays and launch validation remain unchanged.

## Files likely involved

- `src/agent_remote.py`
- `src/launch.rs`
- `tests/test_agent_history.py`
- `web/tests/launch.spec.ts`
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
- Exact next action: Add argv-capture fixtures against pinned native help/source rules, including text beginning with a hyphen, before changing command construction.
- Resume validation: read prerequisite evidence and accepted decisions, inspect the actual diff, then run only affected checks needed for new changes or unverified/stale evidence; do not blindly rerun completed work.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
