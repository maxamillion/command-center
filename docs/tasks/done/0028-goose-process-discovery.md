# Task 0028: Discover interactive Goose and resolve its storage roots

Owner: Codex
Claimed: 2026-11-06
State: done (directory is authoritative)
Phase: B1
Depends on: [0026](../done/0026-goose-capability-guards.md)
Authorization / external gate: Authorized under the user's 2026-11-06 CC-owned implementation scope recorded in [ADR-0002](../../decisions/0002-goose-integration-direction.md). This task covers local detection fixtures and path-only discovery; it does not authorize a Goose integration install, live agent operation, or current-session claim.

## Goal

Recognize the actual interactive foreground Goose process and its nonsecret path configuration without claiming a conversation or live Ready state.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); implementation is authorized within its CC-owned scope.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0002: limited observation](../../milestones/0002-goose-native-observation.md).

## Acceptance criteria

- [x] Exact supported interactive invocation classification covers direct/wrapped processes and rejects similarly named programs, utility/serve/ACP/headless invocations, redirected stdin and other foreground groups.
- [x] An outer supported Goose CLI wins over delegated provider/tool descendants; ambiguous candidates and PID/start/tty changes fail closed.
- [x] Read only approved nonsecret environment keys for path resolution on the correct host/account; preserve existing direct-provider identity hashes.
- [x] Absolute provider-root and relevant platform path rules are supported by fixtures; endpoint/store replacement invalidates observation.
- [x] Shared DB descriptors, cwd, startup arguments and inherited child session variables are never promoted to current-session proof. Unknown remains the honest live state.

## Files likely involved

- `src/agent_remote.py`
- `src/queue.rs`
- `tests/test_agent_detection.py`
- `tests/test_agent_history.py`
- `web/tests/agents.spec.ts`

## Findings and decisions

Claimed after task 0027 completed. Traced the `/proc` foreground resolver, environment allowlist and direct-provider identity behavior. The pinned [v1.57 CLI](https://github.com/aaif-goose/goose/blob/30bba95105e59bc3e7df624cf6b4d433690cfe12/crates/goose-cli/src/cli.rs) exposes `session` and `run`; `RunBehavior::interactive` is the explicit `-s`/`--interactive` gate. The [v1.57 path resolver](https://raw.githubusercontent.com/aaif-goose/goose/30bba95105e59bc3e7df624cf6b4d433690cfe12/crates/goose/src/config/paths.rs) accepts only absolute `GOOSE_PATH_ROOT` and places the data directory below `data/`. The official [CLI session guide](https://goose-docs.ai/docs/guides/goose-cli-commands/) and [running tasks guide](https://goose-docs.ai/docs/guides/running-tasks/) distinguish interactive session/run forms from list/configure/ACP and headless run modes. Classification accepts only explicit `session`/`s` and `run` with the interactive flag; bare/unknown invocation forms fail closed. Direct and wrapped processes must retain the pane's foreground group, controlling TTY and stdin device, and an outer Goose process prevents delegated provider children from being mistaken for the pane agent. Goose data identity includes the canonical resolved root and existing session-store device/inode, so root/store replacement changes the observation identity. Platform data roots include `%APPDATA%\\Block\\goose\\data` on Windows, along with the pinned path resolver's macOS and XDG locations. No process, cwd, startup argument, database handle or environment value is treated as current-session or Ready proof.

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

No live Goose process or user tmux window was targeted; process-tree and path behavior used synthetic `/proc` fixtures and temporary files only.

- `python3 -m unittest discover -s tests -p 'test_agent_detection.py'` — passed, 17 tests, including the new direct-Goose redirected-stdin case and invocation/path/root replacement fixtures.
- `python3 -m unittest discover -s tests -p 'test_agent*.py'` — passed, 74 tests. Adjacent history fixtures emitted SQLite `ResourceWarning`s for unclosed fixture connections; no failures.
- `cargo test` — passed: 47 library, 2 binary and 2 tmux integration tests.
- `cargo fmt --check`, `cargo clippy --all-targets -- -D warnings` and `git diff --check` — passed.

The B2 path audit corrected the Windows default from `%APPDATA%\\Block\\goose` to `%APPDATA%\\Block\\goose\\data`; [Bug 0015](../../bugs/fixed/0015-goose-windows-store-data-directory.md) records the finding. The Goose detection suite was rerun with this platform fixture and passed, 17 tests.

The task's store-replacement fixture checks that replacing `sessions.db` changes the root/store identity incorporated into a fresh process observation. Connection revisions continue to guard endpoint changes in the Rust machine/transport request path. Goose remains process/project observation only: no session linkage, history read, Ready state, launch, message, close or approval capability was enabled here. No live SSH Goose or Windows/macOS host integration was exercised; platform path cases are pure path fixtures.

## Next action / blocker / handoff

- Last completed checkpoint: exact interactive process classification, nonsecret Goose path roots and fail-closed identity invalidation completed after task 0027.
- Working tree / commit: uncommitted; shared implementation includes tasks 0024–0028 and earlier unrelated workspace changes. Preserve them and inspect the actual diff before editing.
- Current blocker: none for task 0029's authorized CC-owned read-only schema-17 work. Native session ownership/Ready proof remains gated by task 0035.
- Exact next action: claim task 0029, confirm the pinned schema-17 definitions, then add a synthetic WAL-backed fixture and verify opening/querying leaves the provider store unchanged.
- Resume validation: read task 0027 evidence and task 0028 prerequisites; rerun only checks made stale by the next changes.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
