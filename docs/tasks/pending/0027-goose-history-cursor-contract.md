# Task 0027: Separate history ordering, revisions and read cursors

Owner: unclaimed
Claimed: not claimed
State: pending (directory is authoritative)
Phase: A3
Depends on: [0026](../pending/0026-goose-capability-guards.md)
Authorization / external gate: Not authorized for implementation by this tracking package. Task 0024 must record the applicable scope approval; later native/approval work also needs its specific accepted contract and integration consent. Completed prerequisites alone do not grant permission.

## Goal

Remove byte-offset/file-metadata assumptions from the new provider display/read path without changing legacy receipt semantics.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); its Proposed status is not approval.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0002: limited observation](../../milestones/0002-goose-native-observation.md).

## Acceptance criteria

- [ ] Specify opaque message/activity IDs, native session/store identity, explicit order keys, paging/version/reset and reply cursors separately from acceptance proof.
- [ ] Remove numeric parsing of opaque IDs on the new path; large database integers cannot lose precision through JavaScript numbers.
- [ ] Legacy JSONL pagination, reply acknowledgements and existing provider read state remain compatible.
- [ ] Define bounded reset/edit handling: no tool-only or old-row-reinsertion unread replies, no heartbeat completion transitions and no stale acknowledgement clearing a newer event.
- [ ] Add compatibility/reset fixtures in Python/Rust/browser and document the additive API fields. No fake transcript offsets or Goose acceptance anchors.

## Files likely involved

- `src/agent_remote.py`
- `src/attention.rs`
- `src/agents.rs`
- `web/src/queue.ts`
- `web/src/agent-activity.ts`
- `docs/api.md`
- `tests/test_agent_history.py`
- `web/tests/agents.spec.ts`

## Findings and decisions

Not started. Keep architectural decisions, discoveries and exact source references here; link a numbered ADR for consequential choices. No prior research test pass is implementation evidence.

## Validation plan

Run from the repository root after creating the required fixture cases. These are validation entry points, **not executed evidence**. Existing suites alone do not prove the new acceptance cases; record the exact new test names and nonzero counts. See [testing guidance](../../testing.md) and [plan verification](../../plans/0002-goose-agent-parity.md#8-verification-plan).

```sh
cargo fmt --check
python3 -m unittest discover -s tests -p 'test_agent_history.py'
cargo test
cargo build --release
npm --prefix web run build -- --outDir dist-next
CC_BINARY=../target/release/command-center CC_WEB_DIR=dist-next npm --prefix web test -- tests/agents.spec.ts
cargo clippy --all-targets -- -D warnings
```

Browser prerequisites: dependencies installed as described in testing guidance, supported Chromium (`CHROME_BIN` if needed), tmux and fixture-only SSH tooling where the spec requires it. Use fresh build artifacts. Missing SSH/browser/device coverage is not a pass.

## Validation evidence

Not run for this task. Record command, environment/fixture revision, exit status, counts/results and limitations as work happens. Fixture input/launch/restart/close tests must never target real work agents or user windows. Do not use private production receipts/transcripts for fixtures.

## Next action / blocker / handoff

- Last completed checkpoint: none; task unclaimed.
- Working tree / commit: no implementation changes for this task; incoming agent must inspect `git status --short` and the actual diff before proceeding.
- Current blocker: scope authorization and unmet prerequisites; do not treat task number order as permission.
- Exact next action: Trace every file-offset/Number(id)/mtime read-cursor assumption and write the additive cursor/reset contract and a legacy compatibility fixture.
- Resume validation: read prerequisite evidence and accepted decisions, inspect the actual diff, then run only affected checks needed for new changes or unverified/stale evidence; do not blindly rerun completed work.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
