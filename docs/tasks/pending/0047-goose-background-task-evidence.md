# Task 0047: Resolve Goose background-task evidence parity

Owner: unclaimed
Claimed: not claimed
State: pending (directory is authoritative)
Phase: Union-background
Depends on: [0033](../pending/0033-goose-native-proof-contract.md)
Authorization / external gate: Not authorized for implementation by this tracking package. Task 0024 must record the applicable scope approval; later native/approval work also needs its specific accepted contract and integration consent. Completed prerequisites alone do not grant permission.

## Goal

Assess the Claude-only background-task equivalent independently of foreground readiness; deliver proven observation or preserve the explicit parity gap.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); its Proposed status is not approval.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0003: full parity](../../milestones/0003-goose-full-agent-parity.md).

## Acceptance criteria

- [ ] Inspect pinned provider-native launch/outcome provenance, parent/child/session/time evidence and limits without reading output paths or polling new SSH services.
- [ ] If authoritative evidence exists and scope is approved, normalize bounded task IDs/descriptions/outcomes with safe literal presentation and stale/partial/unavailable states; a child tool result never sets parent Ready.
- [ ] If unavailable or deferred, record the exact residual capability gap, decision authority and reopening trigger; leave full parity unsatisfied and create a linked blocked follow-up implementation task if needed.
- [ ] Add synthetic false-positive cases for human XML/text, foreign/sidechain sessions, child completion, duplicate/replayed events and missing outcomes; no background event confirms user input or unread assistant replies.
- [ ] Record a supported-capability disposition with actual evidence, not a claim that Codex already has Claude background-task support. A completed investigation is not delivered parity.

## Files likely involved

- `src/agent_remote.py`
- `web/src/agent-background.ts`
- `tests/test_agent_background.py`
- `web/tests/background.spec.ts`
- `docs/plans/0002-goose-agent-parity.md`
- `docs/reference/features.md (only for shipped behavior)`

## Findings and decisions

Not started. Keep architectural decisions, discoveries and exact source references here; link a numbered ADR for consequential choices. No prior research test pass is implementation evidence.

## Validation plan

Run from the repository root after creating the required fixture cases. These are validation entry points, **not executed evidence**. Existing suites alone do not prove the new acceptance cases; record the exact new test names and nonzero counts. See [testing guidance](../../testing.md) and [plan verification](../../plans/0002-goose-agent-parity.md#8-verification-plan).

```sh
cargo fmt --check
python3 -m unittest discover -s tests -p 'test_agent_background.py'
cargo test
cargo build --release
npm --prefix web run build -- --outDir dist-next
CC_BINARY=../target/release/command-center CC_WEB_DIR=dist-next npm --prefix web test -- tests/background.spec.ts
cargo clippy --all-targets -- -D warnings
```

Browser prerequisites: dependencies installed as described in testing guidance, supported Chromium (`CHROME_BIN` if needed), tmux and fixture-only SSH tooling where the spec requires it. Use fresh build artifacts. Missing SSH/browser/device coverage is not a pass.

## Validation evidence

Not run for this task. Record command, environment/fixture revision, exit status, counts/results and limitations as work happens. Fixture input/launch/restart/close tests must never target real work agents or user windows. Do not use private production receipts/transcripts for fixtures.

## Next action / blocker / handoff

- Last completed checkpoint: none; task unclaimed.
- Working tree / commit: no implementation changes for this task; incoming agent must inspect `git status --short` and the actual diff before proceeding.
- Current blocker: scope authorization and unmet prerequisites; do not treat task number order as permission.
- Exact next action: Inspect the approved native source for parent-linked task provenance; document supported evidence or an explicit capability gap before touching task status.
- Resume validation: read prerequisite evidence and accepted decisions, inspect the actual diff, then run only affected checks needed for new changes or unverified/stale evidence; do not blindly rerun completed work.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
