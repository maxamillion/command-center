# Task 0049: Qualify complete Goose agent parity

Owner: unclaimed
Claimed: not claimed
State: pending (directory is authoritative)
Phase: G-full
Depends on: [0048](../pending/0048-goose-observation-qualification.md), [0035](../blocked/0035-goose-native-runtime-integration.md), [0038](../pending/0038-goose-board-launch.md), [0039](../pending/0039-goose-exact-resume.md), [0040](../pending/0040-goose-exact-restart.md), [0043](../pending/0043-goose-guarded-outbox.md), [0044](../pending/0044-goose-chat-attention-feedback.md), [0046](../blocked/0046-goose-guarded-approvals.md), [0047](../pending/0047-goose-background-task-evidence.md)
Authorization / external gate: Not authorized for implementation by this tracking package. Task 0024 must record the applicable scope approval; later native/approval work also needs its specific accepted contract and integration consent. Completed prerequisites alone do not grant permission.

## Goal

Close the full capability matrix only after actual native lifecycle, messaging, acceptance and approval dependencies are satisfied.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); its Proposed status is not approval.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0003: full parity](../../milestones/0003-goose-full-agent-parity.md).

## Acceptance criteria

- [ ] Audit every plan parity row and milestone 0003 criterion against source plus actual evidence, including any linked background follow-up; a deferred/unavailable required capability prevents full completion.
- [ ] Run legacy and Goose fixture matrices for supported versions/schemas, local/SSH/ProxyJump, wrappers, stale/replaced identities, multi-client arbitration, restart/recovery and uncertain delivery with no replay.
- [ ] Verify actual native current-session/settled/input acceptance and approval coordination against the pinned consented producer; synthetic/fake-agent tests do not replace this coverage.
- [ ] Measure bounded scan/query/IO and selected-chat polling under large/noisy/slow/disconnected fixtures; preserve desktop terminal correctness and compact no-viewer/resize invariants for every action.
- [ ] Record phone/device checks and unavailable environment coverage explicitly; only supported combinations are claimed and complete mandatory evidence is required for full milestone sign-off.
- [ ] Update maintained API/features/testing/rules to shipped behavior, record independent safety review and the final handoff; milestone status, task state and plan summary agree. No deployment or live-user action is authorized by qualification.

## Files likely involved

- `docs/milestones/0003-goose-full-agent-parity.md`
- `docs/plans/0002-goose-agent-parity.md`
- `docs/api.md`
- `docs/reference/features.md`
- `docs/testing.md`
- `AGENTS.md`
- `tests/`
- `web/tests/`

## Findings and decisions

Not started. Keep architectural decisions, discoveries and exact source references here; link a numbered ADR for consequential choices. No prior research test pass is implementation evidence.

## Validation plan

Run from the repository root after creating the required fixture cases. These are validation entry points, **not executed evidence**. Existing suites alone do not prove the new acceptance cases; record the exact new test names and nonzero counts. See [testing guidance](../../testing.md) and [plan verification](../../plans/0002-goose-agent-parity.md#8-verification-plan).

```sh
cargo fmt --check
python3 -m unittest discover -s tests -p 'test_agent_*.py'
python3 -m unittest discover -s tests -p 'test_claude_continuation.py'
node tests/pi_bridge.mjs
cargo test
cargo build --release
npm --prefix web run build -- --outDir dist-next
CC_BINARY=../target/release/command-center CC_WEB_DIR=dist-next npm --prefix web test -- tests/agents.spec.ts tests/launch.spec.ts tests/restart.spec.ts tests/outbox.spec.ts tests/background.spec.ts tests/navigation.spec.ts tests/ssh.spec.ts
cargo clippy --all-targets -- -D warnings
```

Browser prerequisites: dependencies installed as described in testing guidance, supported Chromium (`CHROME_BIN` if needed), tmux and fixture-only SSH tooling where the spec requires it. Use fresh build artifacts. Missing SSH/browser/device coverage is not a pass.

## Validation evidence

Not run for this task. Record command, environment/fixture revision, exit status, counts/results and limitations as work happens. Fixture input/launch/restart/close tests must never target real work agents or user windows. Do not use private production receipts/transcripts for fixtures.

## Next action / blocker / handoff

- Last completed checkpoint: none; task unclaimed.
- Working tree / commit: no implementation changes for this task; incoming agent must inspect `git status --short` and the actual diff before proceeding.
- Current blocker: scope authorization and unmet prerequisites; do not treat task number order as permission.
- Exact next action: Check all prerequisite receipts/decisions and background capability follow-ups; remain blocked on any missing actual native evidence or required parity capability before attempting final qualification.
- Resume validation: read prerequisite evidence and accepted decisions, inspect the actual diff, then run only affected checks needed for new changes or unverified/stale evidence; do not blindly rerun completed work.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
