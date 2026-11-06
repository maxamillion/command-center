# Task 0048: Qualify the limited Goose observation milestone

Owner: unclaimed
Claimed: not claimed
State: pending (directory is authoritative)
Phase: G-observation
Depends on: [0032](../pending/0032-goose-close-agent.md)
Authorization / external gate: Not authorized for implementation by this tracking package. Task 0024 must record the applicable scope approval; later native/approval work also needs its specific accepted contract and integration consent. Completed prerequisites alone do not grant permission.

## Goal

Verify and document the useful observation-only deliverable separately from complete agent parity.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); its Proposed status is not approval.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0002: limited observation](../../milestones/0002-goose-native-observation.md).

## Acceptance criteria

- [ ] All observation milestone task criteria/evidence are reviewed against implemented behavior; no future native/approval claims are presented as supported.
- [ ] Run existing-provider and Goose synthetic fixtures, frontend checks and isolated local/SSH/ProxyJump observation tests with bounded shared-store/per-host failure behavior; missing coverage remains a limitation, not a pass.
- [ ] Record supported binary/schema/OS cases, no-write evidence, query/scan/cache budgets and actual measured slow/noisy/disconnected-host results.
- [ ] Verify cards/history/close/read/conflict/draft behavior across restart/multiple clients and compact zero-terminal traffic with desktop processes/dimensions unchanged.
- [ ] Document actually shipped capabilities, clear unavailable reasons and setup/limits without inventing commands or installing integrations; record manual device coverage honestly.
- [ ] Milestone 0002 may complete only with its evidence; full-parity milestone 0003 remains unmet and no production deployment is implied.

## Files likely involved

- `docs/milestones/0002-goose-native-observation.md`
- `docs/plans/0002-goose-agent-parity.md`
- `docs/api.md`
- `docs/reference/features.md`
- `docs/testing.md`
- `AGENTS.md (only established enduring rules)`
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
CC_BINARY=../target/release/command-center CC_WEB_DIR=dist-next npm --prefix web test -- tests/agents.spec.ts tests/navigation.spec.ts tests/tmux.spec.ts tests/ssh.spec.ts
cargo clippy --all-targets -- -D warnings
```

Browser prerequisites: dependencies installed as described in testing guidance, supported Chromium (`CHROME_BIN` if needed), tmux and fixture-only SSH tooling where the spec requires it. Use fresh build artifacts. Missing SSH/browser/device coverage is not a pass.

## Validation evidence

Not run for this task. Record command, environment/fixture revision, exit status, counts/results and limitations as work happens. Fixture input/launch/restart/close tests must never target real work agents or user windows. Do not use private production receipts/transcripts for fixtures.

## Next action / blocker / handoff

- Last completed checkpoint: none; task unclaimed.
- Working tree / commit: no implementation changes for this task; incoming agent must inspect `git status --short` and the actual diff before proceeding.
- Current blocker: scope authorization and unmet prerequisites; do not treat task number order as permission.
- Exact next action: Review milestone 0002 evidence task-by-task, then run observation qualification against isolated fixtures; do not wait for native full-parity gates to qualify a deliberately limited slice.
- Resume validation: read prerequisite evidence and accepted decisions, inspect the actual diff, then run only affected checks needed for new changes or unverified/stale evidence; do not blindly rerun completed work.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
