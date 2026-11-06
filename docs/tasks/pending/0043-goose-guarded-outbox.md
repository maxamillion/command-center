# Task 0043: Enable guarded Goose messages and FIFO delivery

Owner: unclaimed
Claimed: not claimed
State: pending (directory is authoritative)
Phase: E3
Depends on: [0035](../blocked/0035-goose-native-runtime-integration.md), [0041](../pending/0041-goose-chat-input-policy.md), [0042](../pending/0042-goose-acceptance-receipts.md), [0037](../pending/0037-goose-new-launch-recovery.md)
Authorization / external gate: Not authorized for implementation by this tracking package. Task 0024 must record the applicable scope approval; later native/approval work also needs its specific accepted contract and integration consent. Completed prerequisites alone do not grant permission.

## Goal

Permit human-authorized one-use message submission and Ready-gated deferred delivery only after actual native evidence/input/receipt gates pass.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); its Proposed status is not approval.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0003: full parity](../../milestones/0003-goose-full-agent-parity.md).

## Acceptance criteria

- [ ] Both Rust evidence-source allowlist and Python require-ready/action-time guard enforce fresh native current-session/editor evidence; unknown/blocked/replaced/stale evidence authorizes no automatic send.
- [ ] Persist idempotent human intent and complete acceptance baseline before IO; exact client UUID reuse with different target/text is rejected, FIFO head claims serialize with endpoint edits and across clients.
- [ ] Recheck process/screen/session epoch/native editor after waits and immediately before paste; no stale dialog/Ready snapshot is enough.
- [ ] Keep Submit now explicit and freshly reviewed; unavailable dialogs/approvals cannot be bypassed, uncertain delivery is never retried, and Submitting recovers to Uncertain.
- [ ] Fixture tests demonstrate no duplicate input/false Seen across loss/restart, identical messages, multiple clients, cancellation/archiving/retention gaps and disappeared agents; existing providers remain unchanged.
- [ ] HTTP actions from compact clients leave panes/dimensions/processes and viewer traffic unchanged except the explicitly authorized input to the verified fixture agent.

## Files likely involved

- `src/outbox.rs`
- `src/agents.rs`
- `src/agent_remote.py`
- `src/queue.rs`
- `tests/test_agent_outbox.py`
- `web/tests/outbox.spec.ts`
- `web/tests/agents.spec.ts`

## Findings and decisions

Not started. Keep architectural decisions, discoveries and exact source references here; link a numbered ADR for consequential choices. No prior research test pass is implementation evidence.

## Validation plan

Run from the repository root after creating the required fixture cases. These are validation entry points, **not executed evidence**. Existing suites alone do not prove the new acceptance cases; record the exact new test names and nonzero counts. See [testing guidance](../../testing.md) and [plan verification](../../plans/0002-goose-agent-parity.md#8-verification-plan).

```sh
cargo fmt --check
python3 -m unittest discover -s tests -p 'test_agent_outbox.py'
cargo test
cargo build --release
npm --prefix web run build -- --outDir dist-next
CC_BINARY=../target/release/command-center CC_WEB_DIR=dist-next npm --prefix web test -- tests/outbox.spec.ts tests/agents.spec.ts
cargo clippy --all-targets -- -D warnings
```

Browser prerequisites: dependencies installed as described in testing guidance, supported Chromium (`CHROME_BIN` if needed), tmux and fixture-only SSH tooling where the spec requires it. Use fresh build artifacts. Missing SSH/browser/device coverage is not a pass.

## Validation evidence

Not run for this task. Record command, environment/fixture revision, exit status, counts/results and limitations as work happens. Fixture input/launch/restart/close tests must never target real work agents or user windows. Do not use private production receipts/transcripts for fixtures.

## Next action / blocker / handoff

- Last completed checkpoint: none; task unclaimed.
- Working tree / commit: no implementation changes for this task; incoming agent must inspect `git status --short` and the actual diff before proceeding.
- Current blocker: scope authorization and unmet prerequisites; do not treat task number order as permission.
- Exact next action: Confirm prerequisite native evidence and input-policy reports, then add a fail-closed Ready-to-dialog race fixture before enabling any dispatcher source.
- Resume validation: read prerequisite evidence and accepted decisions, inspect the actual diff, then run only affected checks needed for new changes or unverified/stale evidence; do not blindly rerun completed work.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
