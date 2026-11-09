# Task 0025: Make agent provider dispatch explicit

Owner: Codex
Claimed: 2026-11-06
State: done (directory is authoritative)
Phase: A1
Depends on: [0024](../done/0024-goose-implementation-scope.md)
Authorization / external gate: Authorized under the user's 2026-11-06 scope decision recorded in [ADR-0002](../../decisions/0002-goose-integration-direction.md). Later native/approval work still needs its specific accepted contract and integration consent.

## Goal

Remove accidental else-Claude behavior before adding Goose to any exposed provider list.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); accepted for the recorded CC-owned implementation scope, with external gates retained.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0002: limited observation](../../milestones/0002-goose-native-observation.md).

## Acceptance criteria

- [x] Audit provider branches across discovery, homes/history, activity, launch/restart and input; unknown providers fail closed with no helper mutation.
- [x] Existing Claude/Codex/pi direct-process identities, paths, history and argv behavior remain byte/behavior compatible.
- [x] Add a small explicit provider boundary and fixture cases; do not introduce a generic plugin framework or enable Goose actions yet.
- [x] The Python helper was not split, so local/SSH embedding has no new packaging/import dependency.

## Files likely involved

- `src/agent_remote.py`
- `src/queue.rs`
- `src/transport.rs`
- `tests/test_agent_detection.py`

## Findings and decisions

Added an explicit supported-provider map and exact command-name lookup for existing Codex, Claude and pi aliases. Provider-specific history, activity, process-session, provider-home, launch and restart entry points now reject unsupported values before taking Claude fallthroughs. Launch requests validate the provider before filesystem or tmux work. Stored launch metadata is validated before use.

The Rust queue's tmux command hint now uses exact command names rather than substring matches. Existing discovery identity construction and provider launch argv branches are unchanged. No Goose provider was exposed and no Goose action was enabled; task 0026 owns the separate capability guards.

Added fixtures for exact provider aliases, unrelated names, unknown provider no-IO rejection and history fallthrough rejection. Existing direct-process identity coverage remains in `test_direct_identity_hash_is_unchanged_and_wrappers_include_child_identity`.

## Validation plan

Run from the repository root after creating the required fixture cases. These are validation entry points, **not executed evidence**. Existing suites alone do not prove the new acceptance cases; record the exact new test names and nonzero counts. See [testing guidance](../../testing.md) and [plan verification](../../plans/0002-goose-agent-parity.md#8-verification-plan).

```sh
cargo fmt --check
python3 -m unittest discover -s tests -p 'test_agent_*.py'
python3 -m unittest discover -s tests -p 'test_claude_continuation.py'
cargo clippy --all-targets -- -D warnings
```

## Validation evidence

From the repository root:

- `cargo fmt --check` — passed.
- `cargo test queue::tests::pane_command_provider_hints_are_exact` — passed, 1 test; 42 other library tests filtered out.
- `python3 -m unittest discover -s tests -p 'test_agent_*.py'` — passed, 61 tests. Existing SQLite fixture tests emitted `ResourceWarning` messages for unclosed test connections; no failures.
- `python3 -m unittest discover -s tests -p 'test_claude_continuation.py'` — passed, 12 tests.
- `cargo clippy --all-targets -- -D warnings` — passed.
- `git diff --check` — passed.

No live Goose runtime, SSH host, native Goose session, or provider launch was exercised. No Goose runtime capability is enabled by this task.

## Next action / blocker / handoff

- Last completed checkpoint: implemented and verified explicit provider dispatch; task 0025 acceptance criteria are complete.
- Working tree / commit: uncommitted; shared changes also contain completed scope task 0024 and current task 0026. Inspect `git status --short` and actual diff before handoff.
- Current blocker: none for task 0026; Goose action capabilities must remain unavailable until the new guards are implemented.
- Exact next action: implement the additive capabilities and backend/Python direct-action rejection fixtures in task 0026.
- Resume validation: read prerequisite evidence and accepted decisions, inspect the actual diff, then run only affected checks needed for new changes or unverified/stale evidence; do not blindly rerun completed work.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
