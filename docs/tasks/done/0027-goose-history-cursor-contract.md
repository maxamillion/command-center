# Task 0027: Separate history ordering, revisions and read cursors

Owner: Codex
Claimed: 2026-11-06
State: current (directory is authoritative)
Phase: A3
Depends on: [0026](../done/0026-goose-capability-guards.md)
Authorization / external gate: Authorized under the user's 2026-11-06 CC-owned implementation scope recorded in [ADR-0002](../../decisions/0002-goose-integration-direction.md). This task is limited to additive cursor/version/reset compatibility work; native runtime and approval contracts remain separately gated.

## Goal

Remove byte-offset/file-metadata assumptions from the new provider display/read path without changing legacy receipt semantics.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); implementation is authorized within its CC-owned scope.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0002: limited observation](../../milestones/0002-goose-native-observation.md).

## Acceptance criteria

- [x] Specify opaque message/activity IDs, native session/store identity, explicit order keys, paging/version/reset and reply cursors separately from acceptance proof.
- [x] Remove numeric parsing of opaque IDs on the new path; large database integers cannot lose precision through JavaScript numbers.
- [x] Legacy JSONL pagination, reply acknowledgements and existing provider read state remain compatible.
- [x] Define bounded reset/edit handling: no tool-only or old-row-reinsertion unread replies, no heartbeat completion transitions and no stale acknowledgement clearing a newer event.
- [x] Add compatibility/reset fixtures in Python/Rust/browser and document the additive API fields. No fake transcript offsets or Goose acceptance anchors.

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

Audited the helper/Rust/TypeScript history and acknowledgement path. Added an additive `cc.history.v1` page cursor bound to provider, store, conversation, revision and branch; exposed store/session/revision identity and stable lexical order keys; kept legacy `before` and byte-position receipt fields intact. The browser merges by order key and replaces stale pages on reset without parsing display IDs. Reply reconciliation tracks source/session/order independently, baselines old-row reinsertion and deletion resets, and acknowledges only the exact observed reply cursor. Tool-only changes do not manufacture unread replies. No Goose history reader or acceptance proof was introduced here.

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

All history fixtures use synthetic temporary files and browser routes. No live agents or user data were targeted.

- `python3 -m unittest discover -s tests -p 'test_agent_history.py'` — passed, 35 tests. Includes source-bound opaque cursor/revision reset, rewrite moving the latest reply backward or deleting it, tool-only append stability, legacy pagination, and provider history filtering.
- `python3 -m unittest discover -s tests -p 'test_agent*.py'` — passed, 67 tests. Python emitted ResourceWarnings for unclosed SQLite connections in adjacent fixture suites; no failures.
- `cargo test` — passed: 47 library, 2 binary, and 2 tmux integration tests. Includes opaque order/reset, exact-cursor acknowledgement and stale-ack protection.
- `cargo clippy --all-targets -- -D warnings` — passed.
- `cargo fmt --check` and `git diff --check` — passed.
- `cargo build --release` — passed; helper is embedded in the release binary.
- `npm --prefix web run build -- --outDir dist-next` — passed earlier in this task after the TypeScript history paging changes; only Python/Rust files changed afterward.
- `CC_BINARY=../target/release/command-center CC_WEB_DIR=dist-next CHROME_BIN=/usr/bin/google-chrome npm --prefix web test -- tests/agents.spec.ts --grep 'opaque history IDs'` — passed, 1 browser test against the rebuilt release backend. It verifies IDs larger than JavaScript's safe integer range, order-key ordering, opaque cursor reuse, and stale-page replacement on reset.

The broader `tests/agents.spec.ts` run from the preceding capability task had fixture-SSH 502 failures and unrelated card assertions; this task's focused browser fixture passes. Live SSH and phone-device coverage were not part of this cursor contract.

## Next action / blocker / handoff

- Last completed checkpoint: task 0027 opaque history cursor, ordering, reset and reply-read contract completed; all acceptance items are satisfied.
- Working tree / commit: uncommitted; shared implementation includes tasks 0024–0027. Preserve unrelated workspace edits.
- Current blocker: none for task 0027. Actual Goose native proof remains gated by 0035 and is outside this cursor contract.
- Exact next action: claim task 0028 and add fixtures for interactive Goose versus utility/headless/child processes before implementing classification and the minimal process environment allowlist.
- Resume validation: read task 0027 evidence and task 0028 prerequisites; inspect current `git status --short` and shared process-detection diff before editing.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
