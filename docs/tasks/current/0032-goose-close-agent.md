# Task 0032: Enable reviewed Close agent for Goose

Owner: Codex
Claimed: 2026-11-09
State: current (directory is authoritative)
Phase: B4-close
Depends on: [0031](../done/0031-goose-observation-ui.md)
Authorization / external gate: Authorized as CC-owned Close-agent code and isolated-fixture work under the user's 2026-11-06 scope decision in [ADR-0002](../../decisions/0002-goose-integration-direction.md). Do not close live Goose panes; the SSH fixture limitation from Task 0031 remains reported.

## Goal

Reuse existing exact process/topology window-close safeguards for Goose without adding native-session dependence.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); its recorded CC-owned scope is accepted; external producer and approval-channel gates remain conditional.
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

Existing window-close code already binds preview and confirmation to endpoint revision, source session/window/pane, foreground process identity and observed topology; it already refreshes inventory after closure and does not retry uncertain outcomes. Goose had `close_agent` unavailable in both Rust and Python capability maps, so the existing action was unreachable for that provider. The capability maps now expose it, with reasons that describe the exact review requirement. Rust and Python still reject other Goose actions. Added isolated coverage for a synthetic Goose process, stale topology/process rejection, linked-session consequences, compact confirmation, and preservation of unrelated panes/card metadata. The synthetic executable uses a FIFO-backed `session` argument so it remains foreground and observable while the fixture runs.

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

Partial; browser integration evidence is still required before acceptance.

- `cargo fmt --check` — passed in the resumed session.
- `python3 -m unittest discover -s tests -p 'test_agent*.py'` — passed, 97 tests. Four existing `ResourceWarning`s report unclosed SQLite fixture connections in `tests/test_agent_history.py`.
- `npm --prefix web run build -- --outDir dist-task32` — passed; TypeScript check and Vite build succeeded. Vite reported the existing dynamic-import/chunk-size warnings. The temporary output directory was removed afterward.
- `npm --prefix web test -- --list tests/agents.spec.ts` — passed; Playwright discovered 29 cases, including the new Goose Close case and the desktop Close case now using the Goose fixture. Listing validates test discovery only; it does not execute the browser tests.
- `git diff --check` and `cargo fmt --check` — passed.
- Earlier in this implementation checkpoint, `cargo test` passed (47 library, 2 binary, 2 tmux integration tests), `cargo clippy --all-targets -- -D warnings` passed, and `cargo build --release` passed in an environment that permitted local tmux sockets.
- `TMPDIR=/home/admiller/src/dev/command-center/.tmp CC_BINARY=../target/release/command-center CC_WEB_DIR=dist-next npm --prefix web test -- tests/agents.spec.ts --grep 'Goose Close binds the exact process'` — failed before fixture setup (0 ms) because the sandbox denied connection to the temporary tmux socket with `Operation not permitted`, even when the socket directory was inside the writable repository. The current environment has approval policy `never`, so the required real-tmux browser fixture cannot be run here. This is a verification blocker, not a pass. Do not use live Goose panes for the missing evidence.

Fixture input/launch/restart/close tests must never target real work agents or user windows. Do not use private production receipts/transcripts for fixtures.

## Next action / blocker / handoff

- Last completed checkpoint: Goose Close is enabled behind the existing exact process/topology guards and isolated fixtures are implemented. Scope authorization covers CC-owned implementation and synthetic fixtures; live close operations remain unauthorized.
- Working tree / commit: shared tree is uncommitted and contains prior Goose tasks plus unrelated workspace changes. Preserve them and inspect the actual diff.
- Current blocker: the required browser integration test cannot create/access its temporary local tmux socket in the current sandbox. SSH integration also remains unverified because the fixture server cannot execute its shell in this environment.
- Exact next action: rerun the focused Goose Close Playwright case in an environment that permits temporary local tmux sockets, then record its real-tmux result and update acceptance checkboxes. Keep all actions on the synthetic fixture.
- Resume validation: read prerequisite evidence and accepted decisions, inspect the actual diff, then run only affected checks needed for new changes or unverified/stale evidence; do not blindly rerun completed work.
- Acceptance status: implementation and unit/build checks are in place; browser criteria remain unverified because the fixture could not start. Keep this task current until that evidence is obtained.
