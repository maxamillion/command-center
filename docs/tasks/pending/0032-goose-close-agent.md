# Task 0032: Enable reviewed Close agent for Goose

Owner: unclaimed
Claimed: not claimed
State: pending (directory is authoritative)
Phase: B4-close
Depends on: [0031](../pending/0031-goose-observation-ui.md)
Authorization / external gate: Not authorized for implementation by this tracking package. Task 0024 must record the applicable scope approval; later native/approval work also needs its specific accepted contract and integration consent. Completed prerequisites alone do not grant permission.

## Goal

Reuse existing exact process/topology window-close safeguards for Goose without adding native-session dependence.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); its Proposed status is not approval.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0002: limited observation](../../milestones/0002-goose-native-observation.md).

## Acceptance criteria

- [ ] Preview binds the original foreground Goose instance, endpoint/server/session/window/pane topology and all linked copies.
- [ ] Confirmation shows machine/window, pane count, shared links and last-session consequences, focuses Cancel, and is available through desktop/phone card actions.
- [ ] Action-time process/topology changes reject closure; uncertain close is never retried; authoritative inventory refresh removes closed cards.
- [ ] Preserve unrelated pane processes, metadata, tickets and outbox receipts; closure never marks work done or resends input.
- [ ] Destructive tests use isolated fixture windows only; compact close uses HTTP without any viewer attachment/input/resize.

## Files likely involved

- `src/tmux_management.rs`
- `src/agent_remote.py`
- `web/src/agent-close.ts`
- `web/src/queue.ts`
- `web/tests/agents.spec.ts`
- `web/tests/tmux.spec.ts`

## Findings and decisions

Not started. Keep architectural decisions, discoveries and exact source references here; link a numbered ADR for consequential choices. No prior research test pass is implementation evidence.

## Validation plan

Run from the repository root after creating the required fixture cases. These are validation entry points, **not executed evidence**. Existing suites alone do not prove the new acceptance cases; record the exact new test names and nonzero counts. See [testing guidance](../../testing.md) and [plan verification](../../plans/0002-goose-agent-parity.md#8-verification-plan).

```sh
cargo fmt --check
cargo test
cargo build --release
npm --prefix web run build -- --outDir dist-next
CC_BINARY=../target/release/command-center CC_WEB_DIR=dist-next npm --prefix web test -- tests/agents.spec.ts tests/tmux.spec.ts
cargo clippy --all-targets -- -D warnings
```

Browser prerequisites: dependencies installed as described in testing guidance, supported Chromium (`CHROME_BIN` if needed), tmux and fixture-only SSH tooling where the spec requires it. Use fresh build artifacts. Missing SSH/browser/device coverage is not a pass.

## Validation evidence

Not run for this task. Record command, environment/fixture revision, exit status, counts/results and limitations as work happens. Fixture input/launch/restart/close tests must never target real work agents or user windows. Do not use private production receipts/transcripts for fixtures.

## Next action / blocker / handoff

- Last completed checkpoint: none; task unclaimed.
- Working tree / commit: no implementation changes for this task; incoming agent must inspect `git status --short` and the actual diff before proceeding.
- Current blocker: scope authorization and unmet prerequisites; do not treat task number order as permission.
- Exact next action: Extend the isolated close-preview fixture with a Goose process and assert stale-instance rejection before enabling the action.
- Resume validation: read prerequisite evidence and accepted decisions, inspect the actual diff, then run only affected checks needed for new changes or unverified/stale evidence; do not blindly rerun completed work.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
