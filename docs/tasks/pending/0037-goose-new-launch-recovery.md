# Task 0037: Launch new Goose processes with durable recovery

Owner: unclaimed
Claimed: not claimed
State: pending (directory is authoritative)
Phase: D2
Depends on: [0036](../pending/0036-goose-launch-arguments.md), [0031](../done/0031-goose-observation-ui.md)
Authorization / external gate: Not authorized for implementation by this tracking package. Task 0024 must record the applicable scope approval; later native/approval work also needs its specific accepted contract and integration consent. Completed prerequisites alone do not grant permission.

## Goal

Enable explicit fresh interactive Goose launches with honest process-only recovery until native session linkage is proved.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); its Proposed status is not approval.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0003: full parity](../../milestones/0003-goose-full-agent-parity.md).

## Acceptance criteria

- [ ] Preparation binds endpoint/directory/executable/model/destination and literal names; action validates optional prompt before consuming its one-use grant.
- [ ] Dedicated detached session or explicitly chosen detached window preserves existing selection/dimensions/processes; remain-on-exit keeps startup errors.
- [ ] Persist CC launch identity/endpoint and per-window recovery metadata before mutation; lost responses/backend/browser restart recover read-only, never relaunch or replay the prompt.
- [ ] Report process-started separately from current-session-linked; suppress unrelated sole/newest project history on fresh launches. Resume remains gated until task 0039.
- [ ] Fixtures verify stale executable/directory/endpoint/destination rejection, prompt-once argv, literal names/model, private handoff cleanup, multiple launches per session and endpoint-change recovery rejection.
- [ ] Phone launch uses guarded HTTP only and preserves simultaneous desktop terminal dimensions/processes; no authentication/trust prompt is answered automatically.

## Files likely involved

- `src/launch.rs`
- `src/agent_remote.py`
- `web/src/agent-launch.ts`
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
cargo build --release
npm --prefix web run build -- --outDir dist-next
CC_BINARY=../target/release/command-center CC_WEB_DIR=dist-next npm --prefix web test -- tests/launch.spec.ts
cargo clippy --all-targets -- -D warnings
```

Browser prerequisites: dependencies installed as described in testing guidance, supported Chromium (`CHROME_BIN` if needed), tmux and fixture-only SSH tooling where the spec requires it. Use fresh build artifacts. Missing SSH/browser/device coverage is not a pass.

## Validation evidence

Not run for this task. Record command, environment/fixture revision, exit status, counts/results and limitations as work happens. Fixture input/launch/restart/close tests must never target real work agents or user windows. Do not use private production receipts/transcripts for fixtures.

## Next action / blocker / handoff

- Last completed checkpoint: none; task unclaimed.
- Working tree / commit: no implementation changes for this task; incoming agent must inspect `git status --short` and the actual diff before proceeding.
- Current blocker: scope authorization and unmet prerequisites; do not treat task number order as permission.
- Exact next action: Extend the detached launch/recovery fake-agent fixtures; keep installed native Goose out of PATH for any test that can create a session.
- Resume validation: read prerequisite evidence and accepted decisions, inspect the actual diff, then run only affected checks needed for new changes or unverified/stale evidence; do not blindly rerun completed work.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
