# Task 0044: Complete Goose chat feedback, attention and notifications

Owner: unclaimed
Claimed: not claimed
State: pending (directory is authoritative)
Phase: E4
Depends on: [0043](../pending/0043-goose-guarded-outbox.md), [0031](../done/0031-goose-observation-ui.md)
Authorization / external gate: Not authorized for implementation by this tracking package. Task 0024 must record the applicable scope approval; later native/approval work also needs its specific accepted contract and integration consent. Completed prerequisites alone do not grant permission.

## Goal

Connect proven lifecycle/receipt events to chat and attention UI without regressing observation-safe read semantics.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); its Proposed status is not approval.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0003: full parity](../../milestones/0003-goose-full-agent-parity.md).

## Acceptance criteria

- [ ] Working/Ready uses verified provider source/timestamps; local waiting-after-send remains a distinct hint and unavailable/disconnected states invalidate cached Ready.
- [ ] Stable lifecycle transition IDs avoid heartbeat completion spam; exact reply/event revisions and stale acknowledgement protection survive restart and mutable history resets.
- [ ] Pending bubbles reflect durable receipt status and keep blocked/uncertain/replaced warnings; confirmed Seen receipts disappear independently of loaded history pages, while global Outbox remains available for disappeared agents.
- [ ] Clear duplicate composer text only after exact durable receipt presence; preserve newer drafts, process/session isolation, scroll, focus and disclosures during polling.
- [ ] Browser notifications remain explicit opt-in, privacy-preserving and cross-tab deduplicated, with current endpoint/process validation on click and no input authorization.
- [ ] Compact/landscape/keyboard fixtures verify visible conversation feedback and zero terminal attachment/resize traffic with a simultaneous desktop client.

## Files likely involved

- `src/attention.rs`
- `src/agents.rs`
- `web/src/queue.ts`
- `web/src/agent-outbox.ts`
- `web/src/notifications.ts`
- `web/tests/agents.spec.ts`
- `web/tests/outbox.spec.ts`
- `web/tests/navigation.spec.ts`

## Findings and decisions

Not started. Keep architectural decisions, discoveries and exact source references here; link a numbered ADR for consequential choices. No prior research test pass is implementation evidence.

## Validation plan

Run from the repository root after creating the required fixture cases. These are validation entry points, **not executed evidence**. Existing suites alone do not prove the new acceptance cases; record the exact new test names and nonzero counts. See [testing guidance](../../testing.md) and [plan verification](../../plans/0002-goose-agent-parity.md#8-verification-plan).

```sh
cargo fmt --check
cargo test
cargo build --release
npm --prefix web run build -- --outDir dist-next
CC_BINARY=../target/release/command-center CC_WEB_DIR=dist-next npm --prefix web test -- tests/agents.spec.ts tests/outbox.spec.ts tests/navigation.spec.ts
cargo clippy --all-targets -- -D warnings
```

Browser prerequisites: dependencies installed as described in testing guidance, supported Chromium (`CHROME_BIN` if needed), tmux and fixture-only SSH tooling where the spec requires it. Use fresh build artifacts. Missing SSH/browser/device coverage is not a pass.

## Validation evidence

Not run for this task. Record command, environment/fixture revision, exit status, counts/results and limitations as work happens. Fixture input/launch/restart/close tests must never target real work agents or user windows. Do not use private production receipts/transcripts for fixtures.

## Next action / blocker / handoff

- Last completed checkpoint: none; task unclaimed.
- Working tree / commit: no implementation changes for this task; incoming agent must inspect `git status --short` and the actual diff before proceeding.
- Current blocker: scope authorization and unmet prerequisites; do not treat task number order as permission.
- Exact next action: Add native-epoch transition/receipt fixture events and prove one completion notification plus no tool-only unread before wiring feedback.
- Resume validation: read prerequisite evidence and accepted decisions, inspect the actual diff, then run only affected checks needed for new changes or unverified/stale evidence; do not blindly rerun completed work.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
