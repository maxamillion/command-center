# Task 0031: Present honest Goose observation, cards and read state

Owner: Codex
Claimed: 2026-11-08
State: done (directory is authoritative)
Phase: B4-observation
Depends on: [0030](../done/0030-goose-history-activity-projection.md), [0028](../done/0028-goose-process-discovery.md)
Authorization / external gate: Authorized as CC-owned observation UI work under the user's 2026-11-06 scope decision in [ADR-0002](../../decisions/0002-goose-integration-direction.md). Native current-session/lifecycle proof, messaging, launch/restart, Close (Task 0032), approvals and live-agent operations remain separately gated.

## Goal

Expose the useful observation-only slice while preserving card metadata, selection, read state and compact isolation.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); its Proposed status is not approval.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0002: limited observation](../../milestones/0002-goose-native-observation.md).

## Acceptance criteria

- [x] Add Goose labels/filter/title handling and an explicitly unverified project-history picker; do not auto-link a fresh launch to sole/newest history.
- [x] Render Unknown/unavailable capability reasons and inferred input attention honestly; no Goose send/resume/restart/approval controls or grants become authorized.
- [x] Card name/notes/color/pin persistence and conflicts remain endpoint/process-scoped; replacement processes do not inherit metadata. Closed pane tuples disappear authoritatively while connectivity uncertainty retains only the existing grace interval.
- [x] Baseline old history, acknowledge exact observed replies, preserve newer replies against stale acknowledgements and keep open conversations visible when attention filters change; resets/tool-only changes cannot fabricate unread or finished events.
- [x] Polling preserves drafts, disclosures, focus, list/filter state and scroll, with bounded caches and no terminal-content-to-history shortcuts.
- [x] Desktop and compact fixtures validate actual conversation proportions/navigation and zero compact viewer/input/resize traffic with simultaneous desktop processes/dimensions unchanged. Close remains gated to task 0032.

## Files likely involved

- `web/src/queue.ts`
- `web/src/agent-activity.ts`
- `web/src/agent-card-editor.ts`
- `src/queue.rs`
- `src/agents.rs`
- `src/agent_cards.rs`
- `src/attention.rs`
- `web/tests/agents.spec.ts`
- `web/tests/navigation.spec.ts`

## Findings and decisions

Task 0030 now supplies read-only Goose history pages, visible activity, project candidate metadata and exact reply observations. The frontend is provider-generic but assumes that a provider may have process-linked history and may expose Close via capability. Goose must remain labeled as unverified project history, must never be auto-associated to a running process, and must show capability reasons without surfacing action controls. Preserve shared endpoint/process card scoping and exact observed reply cursors. Compact navigation must continue to avoid attaching a terminal viewer or sending input/resize traffic.

During fixture validation, the embedded `agent_remote.py` source exceeded the operating system's per-argument limit because the transport passed it as one `python3 -c` argument. [Bug 0016](../../bugs/fixed/0016-provider-helper-argument-limit.md) records the fix: stream a length-prefixed source over stdin and leave the request JSON after it. Local card/detail flows now execute the larger helper. The test SSH server still fails to execute `/bin/bash` in this environment, so remote-host coverage remains unavailable.

## Validation plan

Run from the repository root after creating the required fixture cases. These are validation entry points, **not executed evidence**. Existing suites alone do not prove the new acceptance cases; record the exact new test names and nonzero counts. See [testing guidance](../../testing.md) and [plan verification](../../plans/0002-goose-agent-parity.md#8-verification-plan).

```sh
cargo fmt --check
cargo test
cargo build --release
npm --prefix web run build -- --outDir dist-next
CC_BINARY=../target/release/command-center CC_WEB_DIR=dist-next npm --prefix web test -- tests/agents.spec.ts tests/navigation.spec.ts
cargo clippy --all-targets -- -D warnings
```

Browser prerequisites: dependencies installed as described in testing guidance, supported Chromium (`CHROME_BIN` if needed), tmux and fixture-only SSH tooling where the spec requires it. Use fresh build artifacts. Missing SSH/browser/device coverage is not a pass.

## Validation evidence

Environment: 2026-11-09 repository checkout, synthetic tmux/agent fixtures, Python 3, Rust toolchain, Node/Vite and Chromium. No live Goose process, provider history, message, input, launch, restart or approval was used.

- `cargo fmt --check` — exit 0.
- `cargo test` — sandbox run initially had two listener tests fail with `Operation not permitted`; rerun with approved process/network permissions passed: 47 library, 2 binary and 2 tmux integration tests.
- `cargo clippy --all-targets -- -D warnings` — exit 0.
- `cargo build --release` — exit 0.
- `npm --prefix web run build -- --outDir dist-next` — exit 0; Vite emitted existing dynamic-import and large-chunk warnings.
- `git diff --check` — exit 0.
- Focused Playwright checks passed the Goose capability/read-only gate, unverified history picker, exact reply acknowledgement, compact navigation/filter retention, desktop process/dimension preservation, card conflict/process replacement, and attention-label behavior. `inline activity for all providers stays collapsed, updates in place, and fits mobile` passed after adding stable `order_key` values to its synthetic API fixture.
- `/usr/bin/bash -lc 'CC_BINARY=../target/release/command-center CC_WEB_DIR=dist-next CHROME_BIN=/usr/bin/google-chrome npm --prefix web test -- tests/agents.spec.ts tests/navigation.spec.ts'` — 33 passed, 5 failed out of 38. All five failures were SSH-fixture paths: remote conversation/approval/card helpers returned `Broken pipe` or `/bin/bash: Permission denied`, and remote Close preview returned 502. Local transport, all Goose-specific cases and all ten navigation tests passed. The fixture SSH server could not execute its shell in this environment, so SSH behavior remains unverified here.
- The helper-size regression was reproduced as `Argument list too long`: `agent_remote.py` was 158,877 bytes and exceeded the OS per-argument limit when passed via `python3 -c`. The helper now streams length-prefixed source plus the unchanged JSON request over stdin; local agent/card fixtures pass. See [Bug 0016](../../bugs/fixed/0016-provider-helper-argument-limit.md).

No private production receipts/transcripts or live work agents were used. The installed Goose CLI was not exercised. Project history remains explicitly unverified, and lifecycle, messaging, launch, resume, restart and approval capabilities remain unavailable. Close is handled by Task 0032.

## Next action / blocker / handoff

- Last completed checkpoint: Goose observation UI, card/read-state preservation and compact isolation meet Task 0031 acceptance; the embedded-helper argv limit was fixed. Remote SSH fixture commands could not execute `/bin/bash` in this environment.
- Working tree / commit: shared tree is uncommitted and contains earlier Goose tasks plus unrelated workspace changes. Preserve all unrelated work.
- Current blocker: SSH fixture execution is unavailable in this environment. It does not block the CC-owned observation slice; real SSH-host coverage remains a reported limitation.
- Exact next action: continue with [Task 0032](../current/0032-goose-close-agent.md) and verify existing reviewed Close preview/confirmation against an isolated Goose pane, endpoint identity and shared-window topology. Do not close a live Goose pane.
- Resume validation: read prerequisite evidence and accepted decisions, inspect the actual diff, then run only affected checks needed for new changes or unverified/stale evidence; do not blindly rerun completed work.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
