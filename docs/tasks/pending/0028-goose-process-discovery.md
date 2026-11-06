# Task 0028: Discover interactive Goose and resolve its storage roots

Owner: unclaimed
Claimed: not claimed
State: pending (directory is authoritative)
Phase: B1
Depends on: [0026](../pending/0026-goose-capability-guards.md)
Authorization / external gate: Not authorized for implementation by this tracking package. Task 0024 must record the applicable scope approval; later native/approval work also needs its specific accepted contract and integration consent. Completed prerequisites alone do not grant permission.

## Goal

Recognize the actual interactive foreground Goose process and its nonsecret path configuration without claiming a conversation or live Ready state.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); its Proposed status is not approval.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0002: limited observation](../../milestones/0002-goose-native-observation.md).

## Acceptance criteria

- [ ] Exact supported interactive invocation classification covers direct/wrapped processes and rejects similarly named programs, utility/serve/ACP/headless invocations, redirected stdin and other foreground groups.
- [ ] An outer supported Goose CLI wins over delegated provider/tool descendants; ambiguous candidates and PID/start/tty changes fail closed.
- [ ] Read only approved nonsecret environment keys for path resolution on the correct host/account; preserve existing direct-provider identity hashes.
- [ ] Absolute provider-root and relevant platform path rules are supported by fixtures; endpoint/store replacement invalidates observation.
- [ ] Shared DB descriptors, cwd, startup arguments and inherited child session variables are never promoted to current-session proof. Unknown remains the honest live state.

## Files likely involved

- `src/agent_remote.py`
- `src/queue.rs`
- `tests/test_agent_detection.py`
- `tests/test_agent_history.py`
- `web/tests/agents.spec.ts`

## Findings and decisions

Not started. Keep architectural decisions, discoveries and exact source references here; link a numbered ADR for consequential choices. No prior research test pass is implementation evidence.

## Validation plan

Run from the repository root after creating the required fixture cases. These are validation entry points, **not executed evidence**. Existing suites alone do not prove the new acceptance cases; record the exact new test names and nonzero counts. See [testing guidance](../../testing.md) and [plan verification](../../plans/0002-goose-agent-parity.md#8-verification-plan).

```sh
cargo fmt --check
python3 -m unittest discover -s tests -p 'test_agent_detection.py'
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
- Exact next action: Add kernel/process fixture cases for interactive Goose versus utility/headless/child processes, then implement classification and the minimal path-environment allowlist.
- Resume validation: read prerequisite evidence and accepted decisions, inspect the actual diff, then run only affected checks needed for new changes or unverified/stale evidence; do not blindly rerun completed work.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
