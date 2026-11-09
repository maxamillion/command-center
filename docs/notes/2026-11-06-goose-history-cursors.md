# Goose history cursor handoff — 2026-11-06

Task 0027 is complete and task 0028 is current under the user's recorded CC-owned scope in ADR-0002. The plan tracker now shows 22 remaining records: one current, 19 pending and two externally blocked.

## Completed: task 0027

- Added `cc.history.v1` opaque paging tokens bound to provider, store identity, conversation, revision and branch. Kept legacy numeric paging/receipt fields compatible.
- Added explicit lexical message/activity order keys, source/session identity and separate exact reply cursors. Browser sorting does not parse opaque display IDs and resets stale merged pages on revision changes.
- Tightened attention reconciliation for source/session changes, transcript rewrites that move replies backward or delete the latest assistant reply, exact acknowledgements and stale event rejection. Tool-only appends keep the existing reply cursor.
- Documented the additive API contract in `docs/api.md` and recorded evidence in task 0027.

## Validation

- `python3 -m unittest discover -s tests -p 'test_agent_history.py'`: 35 passed.
- `python3 -m unittest discover -s tests -p 'test_agent*.py'`: 67 passed; adjacent fixture suites emitted SQLite ResourceWarnings.
- `cargo test`: 47 library, 2 binary and 2 tmux integration tests passed.
- `cargo clippy --all-targets -- -D warnings`, `cargo fmt --check`, `git diff --check` and `cargo build --release`: passed.
- Web build passed after the TypeScript changes. Release-backed browser spec `opaque history IDs sort by order key and a reset replaces stale pages`: 1 passed.
- The wider agents browser suite previously had fixture SSH 502s and unrelated card assertions; no live SSH or phone-device tests were run for the cursor task.

## Current: task 0028

Inspect the current `/proc` foreground resolver, process identity and environment handling, then compare them with the exact interactive and utility/headless Goose invocation forms documented in Plan 0002's pinned references. Add synthetic process-tree fixtures before implementation. Process discovery must not claim a native conversation or live Ready state. Do not install Goose, operate live agents, or cross the blocked native-runtime proof gate.

The shared worktree remains uncommitted and includes earlier Plan 0002 tasks. Reinspect `git status --short` and the current process-detection diff before editing.
