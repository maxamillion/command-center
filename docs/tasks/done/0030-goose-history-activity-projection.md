# Task 0030: Project Goose chat history and inline activity

Owner: Codex
Claimed: 2026-11-06
State: done (directory is authoritative)
Phase: B3
Depends on: [0029](../done/0029-goose-readonly-session-store.md)
Authorization / external gate: Authorized as CC-owned history projection work under the user's 2026-11-06 scope decision in [ADR-0002](../../decisions/0002-goose-integration-direction.md). Keep current-session linkage, lifecycle, input and approval capabilities disabled; no live Goose operation is in scope.

## Goal

Normalize visible native history into CC chat and activity without confusing tool/control records with human input or assistant replies.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); accepted for CC-owned work in dependency order.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0002: limited observation](../../milestones/0002-goose-native-observation.md).

## Acceptance criteria

- [x] Apply message user visibility and content audience rules; preserve native timestamp/tie ordering and visible text; exclude hidden context/replays/control/system/internal records.
- [x] User-role tool results never become human chat/input acceptance; tool calls/results pair by scoped ID plus occurrence, including repeated/null source IDs and legacy/error wrappers.
- [x] Export only provider-visible supported activity text; signatures/redacted opaque fields stay excluded, media gets bounded placeholders, and no logged resource/spill paths are fetched.
- [x] Implement bounded paging/version/reset using task 0027 contracts; loaded-page edits and delete/reinsert invalidate stale pages without inventing unread replies. Truncation, malformed rows, incomplete activity scans and unsupported content are reported as limited; no native compaction event is inferred.
- [x] Stable source identities preserve disclosures/order across polling; tool-result updates do not advance reply cursors and no result means Awaiting result.
- [x] Add fixtures for malformed/huge content, sanitization, hidden context, mixed activity/text and store mutation; disclose omissions and persisted-not-streaming limits.

## Files likely involved

- `src/agent_remote.py`
- `src/attention.rs`
- `tests/test_agent_history.py`
- `tests/test_agent_activity.py`
- `web/src/queue.ts`
- `web/src/agent-activity.ts`
- `web/tests/agents.spec.ts`

## Findings and decisions

Task 0029 provides bounded schema-17 rows with exact timestamp/row-ID order. This task adds the read-only Agent API projection. Message-level `userVisible` and block audience both matter; role `user` alone does not prove human input because tool responses also use it. Tool calls/results pair by scoped ID and occurrence. User-visible messages have opaque stable source IDs and native timestamp/tie order; no SQLite row ID is exported as a client position. Media and resources are represented by placeholders, and unsupported/control/system/context content and arbitrary metadata are omitted. A bounded loaded-history window and opaque source-bound cursor detect edits to already loaded pages; reset preserves only the latest page. The reply cursor advances only on visible assistant chat with a native message ID, so tool-result updates cannot create unread replies or input-acceptance evidence. Incomplete scans leave calls Awaiting result and disclose limited history.

## Validation plan

See the actual results below. The browser case used its isolated synthetic tmux fixture and made no live Goose calls. See [testing guidance](../../testing.md) and [plan verification](../../plans/0002-goose-agent-parity.md#8-verification-plan).

```sh
cargo fmt --check
python3 -m unittest discover -s tests -p 'test_agent_history.py'
python3 -m unittest discover -s tests -p 'test_agent_activity.py'
cargo test
cargo clippy --all-targets -- -D warnings
npm --prefix web run build -- --outDir dist-next
```

## Validation evidence

Environment: repository checkout, Python 3, Rust toolchain, Node/Vite and Chromium; all Goose history/store tests used temporary synthetic schema-17 SQLite stores. No live Goose process, production history, message, input, launch, restart, or approval was used.

- `python3 -m py_compile src/agent_remote.py` — exit 0.
- `python3 -m unittest discover -s tests -p 'test_agent_goose_history.py'` — exit 0, 10 tests passed. Covers visibility/audience, hidden context/control records, media/resource redaction, repeated/null IDs, cross-page pairing, incomplete scans, edit/delete-reinsert resets, read-cursor behavior, malformed/large rows, and API dispatch/capability limits.
- `python3 -m unittest discover -s tests -p 'test_agent_goose_store.py'` — exit 0, 12 tests passed.
- `python3 -m unittest discover -s tests -p 'test_agent_detection.py'` — exit 0, 17 tests passed.
- `python3 -m unittest discover -s tests -p 'test_agent*.py'` — exit 0, 96 tests passed. Existing unclosed-SQLite `ResourceWarning`s in `test_agent_history.py` remain outside this task.
- `cargo fmt --check` and `git diff --check` — exit 0.
- `cargo test` — exit 0: 47 library, 2 binary and 2 tmux integration tests passed.
- `cargo clippy --all-targets -- -D warnings` — exit 0.
- `npm --prefix web run build -- --outDir dist-next` — exit 0; TypeScript and Vite build passed. Vite emitted existing chunk-size and dynamic-import warnings.
- `cargo build --release` — exit 0.
- `/usr/bin/bash -lc 'CC_BINARY=../target/release/command-center CC_WEB_DIR=dist-next CHROME_BIN=/usr/bin/google-chrome npm --prefix web test -- tests/agents.spec.ts --grep "opaque history IDs"'` — first sandbox attempt could not access its temporary tmux socket; rerun with approved escalation passed, 1 Playwright test. It verifies opaque IDs, ordering, page merge, safe text rendering and stale-page reset/disclosure behavior.

Limit: the installed Goose CLI was not exercised. Persisted history is not a live token stream, and this projection does not establish current-session linkage, live Working/Ready state, message acceptance, launch, resume, restart, close, or approval capabilities.

## Next action / blocker / handoff

- Completed checkpoint: schema-17 store rows now project into bounded, paged Goose chat/activity with explicit unlinked project-history semantics and safe reset behavior.
- Working tree / commit: implementation and ledger updates remain uncommitted in the shared worktree. `git status --short` includes unrelated work; retain it and review the complete diff before staging.
- Current blocker: none for Task 0030. Native current-session/Ready evidence and approval remain separately gated by Tasks 0035/0046.
- Exact next action: Task 0031 is complete; continue with [Task 0032](../current/0032-goose-close-agent.md) for reviewed Close-agent support on isolated Goose fixtures.
- Handoff: [2026-11-08 Goose history projection](../../notes/2026-11-08-goose-history-projection.md).
