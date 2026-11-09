# Goose process discovery handoff — 2026-11-06

Task 0028 is complete and task 0029 is current under the CC-owned scope accepted in [ADR-0002](../decisions/0002-goose-integration-direction.md). Plan 0002 now shows 21 remaining execution records: one current, 18 pending and two externally blocked.

## Completed: task 0028

- Goose process observation recognizes exact `goose`/`goose-cli` executable names and explicit interactive `session`/`s` or `run -s/--interactive` forms. Utilities, ACP/serve, headless runs, malformed/unknown arguments and bare invocation fail closed.
- Foreground discovery checks process ancestry/start identity, foreground process group, controlling TTY and stdin device for direct and wrapped processes. An outer Goose process prevents delegated provider CLIs from being selected as the pane agent.
- Resolved only approved path environment values. Goose identity includes mode and canonical data-root/session-store identity; direct-provider identity hashes remain compatible.
- Added Linux, macOS and Windows path fixtures, process-tree fixtures, redirected-stdin rejection and store-replacement identity coverage. Goose still has process observation only; no current session, history, Ready state or action capability was enabled.

## Validation

- `python3 -m unittest discover -s tests -p 'test_agent_detection.py'` — 17 passed.
- `python3 -m unittest discover -s tests -p 'test_agent*.py'` — 74 passed; adjacent history fixtures emitted SQLite ResourceWarnings for unclosed fixture connections.
- `cargo test` — 47 library, 2 binary and 2 tmux integration tests passed.
- `cargo fmt --check`, `cargo clippy --all-targets -- -D warnings` and `git diff --check` — passed.
- Tests used synthetic process files and temporary files. No live Goose process, remote machine or user tmux window was targeted.

## Current: task 0029

Implement the schema-17 read-only session-store adapter against synthetic WAL fixtures. The pinned v1.55/v1.57 schema evidence is recorded in [Plan 0002 U1](../plans/0002-goose-agent-parity.md#10-source-evidence-index). Keep reads bounded, parameterized and query-only; do not initialize, repair, checkpoint or modify the provider database. Native session ownership and lifecycle proof remain outside this task.

The shared worktree is uncommitted and contains earlier Plan 0002 implementation plus other workspace changes. Preserve it and inspect the current diff before editing.
