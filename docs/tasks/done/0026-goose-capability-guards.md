# Task 0026: Add independent agent capabilities and action guards

Owner: Codex
Claimed: 2026-11-06
State: current (directory is authoritative)
Phase: A2
Depends on: [0025](../done/0025-goose-provider-dispatch.md)
Authorization / external gate: Authorized under the user's 2026-11-06 scope decision recorded in [ADR-0002](../../decisions/0002-goose-integration-direction.md). Later native/approval work still needs its specific accepted contract and integration consent.

## Goal

Separate observation/history capability from session, Ready, input, acceptance, launch, resume, restart and approval authority.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); accepted for the recorded CC-owned implementation scope, with external gates retained.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0002: limited observation](../../milestones/0002-goose-native-observation.md).

## Acceptance criteria

- [x] Define additive backend capabilities and unavailable reasons; existing providers preserve established behavior.
- [x] Rust handlers and Python action-time paths independently reject unavailable Goose operations, including direct HTTP/helper calls that bypass the UI.
- [x] Selected project history, terminal prompts and provider labels cannot grant current-session or send authority.
- [x] No Goose Ready source, message token, approval choice, resume or restart is enabled merely by adding the provider.
- [x] Add negative helper fixtures proving rejected Goose operations reach no terminal, launch or close IO; keep Goose Close and launch exposure separately gated.

## Files likely involved

- `src/agents.rs`
- `src/queue.rs`
- `src/outbox.rs`
- `src/launch.rs`
- `src/agent_restart.rs`
- `src/agent_remote.py`
- `web/src/queue.ts`
- `web/tests/agents.spec.ts`

## Findings and decisions

Added a small fixed capability vocabulary in Rust and Python. Existing Codex/Claude/Pi behavior remains enabled as before (Pi native approvals stay terminal-only); Goose currently has no enabled capability, each with an explicit user-facing reason. Queue/detail responses carry the same additive map. Rust send/approval grants retain provider identity and recheck capability at consumption; launch, resume, restart and Close guards are checked at action time. Python helper paths independently guard history, phase, send, approval, launch, resume/restart and Close. Goose history currently returns no candidates, phase is Unknown, and terminal text cannot mint capabilities.

Full agents browser verification exposed that the status helper did not return its provider field, which made the new Rust Close guard reject supported providers. Added the provider to the status response; focused capability and Close specs pass after rebuilding the embedded helper. This does not enable Goose Close: its capability remains unavailable.

## Validation plan

Run from the repository root after creating the required fixture cases. These are validation entry points, **not executed evidence**. Existing suites alone do not prove the new acceptance cases; record the exact new test names and nonzero counts. See [testing guidance](../../testing.md) and [plan verification](../../plans/0002-goose-agent-parity.md#8-verification-plan).

```sh
cargo fmt --check
python3 -m unittest discover -s tests -p 'test_agent_*.py'
cargo test
cargo build --release
npm --prefix web run build -- --outDir dist-next
CC_BINARY=../target/release/command-center CC_WEB_DIR=dist-next npm --prefix web test -- tests/agents.spec.ts
cargo clippy --all-targets -- -D warnings
```

Browser prerequisites: dependencies installed as described in testing guidance, supported Chromium (`CHROME_BIN` if needed), tmux and fixture-only SSH tooling where the spec requires it. Use fresh build artifacts. Missing SSH/browser/device coverage is not a pass.

## Validation evidence

From the repository root; all terminal/action specs used temporary tmux sessions, fake Codex/Python fixtures, and local browser routes. No live Goose process or user window was targeted.

- `cargo fmt --check` and `git diff --check`: exit 0.
- `python3 -m unittest discover -s tests -p 'test_agent_*.py'`: exit 0, 63 tests passed. Includes `ProviderBoundary.test_goose_capabilities_are_independent_and_disabled`, `ProviderBoundary.test_direct_goose_actions_are_rejected_before_mutating_io`, and unknown-provider pre-IO tests. Existing SQLite ResourceWarnings remain.
- `cargo test`: exit 0, 49 tests passed (45 library, 2 binary, 2 tmux integration). One initial sandbox run could not bind local sockets; the approved outside-sandbox rerun passed.
- `cargo clippy --all-targets -- -D warnings`: exit 0.
- `cargo build --release`: exit 0 after the status-provider helper fix.
- `npm --prefix web run build -- --outDir dist-next`: exit 0 (TypeScript and Vite); existing marked/DOMPurify chunk and large-chunk warnings.
- `CC_BINARY=../target/release/command-center CC_WEB_DIR=dist-next CHROME_BIN=/usr/bin/google-chrome npm --prefix web test -- tests/agents.spec.ts --grep 'provider capability reasons|Close agent on a phone|Close agent rejects replacement|desktop Close agent menu'`: exit 0, 4 specs passed. The capability spec confirms Goose message/approval/restart/Close UI controls are disabled with reasons. Three existing destructive Close specs confirm existing providers still work with the action-time provider guard.
- A full 26-spec `agents.spec.ts` run with the installed browser completed 18 passed, 8 failed before the status-provider fix. The focused rerun above confirms all three local Close failures were fixed. Remaining full-suite failures involved SSH fixture operations returning HTTP 502 (3 cases) and two local agent-card specs that failed after those fixture failures in the shared suite; they were not rerun independently. Treat SSH and full-suite coverage as incomplete.

## Next action / blocker / handoff

- Last completed checkpoint: additive capability maps, Python/Rust action guards and UI gates are implemented; direct Python negative tests and the focused browser capability/Close tests pass.
- Working tree / commit: uncommitted; task 0024/0025 records and implementation remain in the shared tree. See the dated handoff.
- Current blocker: no blocker for the next contract task. Native runtime proof and approval channel remain externally blocked in 0035/0046.
- Exact next action at completion: begin task 0027 after this task's capability evidence was recorded. Task 0027 is now done; task 0028 is current.
- Resume validation: read prerequisite evidence and accepted decisions, inspect the actual diff, then run only affected checks needed for new changes or unverified/stale evidence; do not blindly rerun completed work.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
