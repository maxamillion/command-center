# Task 0051: Fix Goose review findings

Owner: Codex
Claimed: 2026-11-09
State: done

Fix bugs 0017–0019 from task 0050, preserving bounded read-only observation and real history-reset handling. Add regressions for distinct identical replies, tool-only tails and long tool arguments. No live provider operations.

## Acceptance

- [x] Regression cases fail before fixes and pass afterward.
- [x] Agent regression suite and relevant checks pass.
- [x] Update bug records and handoff with actual evidence.

## Implementation and evidence

`src/agent_remote.py` now separates tool argument text/truncation from request errors in named fields, preserving actual result status/output. Reply resets use native row/message identity instead of text equality. A direct bounded lookup revalidates the known reply when tool-only rows push it beyond the latest page; actual deletion still resets even when the latest-page fingerprint is unchanged.

Added five regression tests in `tests/test_agent_goose_history.py`. The initial three regressions failed against the original implementation. Final `python3 -m unittest discover -s tests -p 'test_agent*.py'`: 102 passed, with four pre-existing SQLite ResourceWarnings. Covers identical distinct replies, tool-only tail retention/polling/deletion, subsequent new reply, long pending/successful/failed tools and native request errors. Existing deletion/reinsertion reset tests also pass.

`cargo fmt --check`, `cargo clippy --all-targets -- -D warnings`, Python compilation and `git diff --check` passed. `cargo test --lib`: 45 passed, two listener tests failed with sandbox `Operation not permitted` (features disabling and HTTPS origin guard). Focused attention tests (5) and agent capability tests (2) passed. No frontend source changed. Browser, SSH, native Goose and phone testing were not performed; existing task 0032 integration gaps remain. No live agents, deployment, input or closure actions.

## Handoff

Bugs 0017–0019 fixed with synthetic regression coverage. Review/fix work is complete; task 0032 remains current awaiting its separate real-tmux browser evidence. Changes remain uncommitted.
