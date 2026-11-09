# 2026-11-08: Goose history projection

Task 0030 is complete. The Goose schema-17 reader now exposes bounded, source-bound project history and user-visible tool activity through the existing Agent API. Message projection enforces message visibility and block audience, excludes hidden/control/system/internal content, redacts media/resources to placeholders, and pairs tool calls/results by scoped ID plus occurrence. Opaque history cursors revalidate loaded pages; edits and delete/reinsert changes reset the latest page. The reply cursor advances only for visible assistant chat with a native message ID. Goose remains unlinked to the running process; live lifecycle and action capabilities stay unavailable.

Verification used temporary synthetic stores and an isolated browser fixture:

- 10 Goose history projection tests, 12 Goose store tests, 17 process-discovery tests, and 96 total `test_agent*.py` tests passed.
- `cargo fmt --check`, `git diff --check`, `cargo test` (47 library, 2 binary, 2 tmux integration), and `cargo clippy --all-targets -- -D warnings` passed.
- Frontend build, release build, and the focused opaque-history-ID Playwright test passed. The browser test required approved sandbox escalation to access its temporary tmux socket.
- No live Goose process or private history was used. Vite emitted existing bundle warnings; the Python suite emitted existing SQLite resource warnings in `test_agent_history.py`.

Next: Task 0031, observation-only UI and state preservation. Keep project history explicitly unverified and do not enable Goose send, resume, restart, approval or launch. Close-agent handling remains the next task, 0032; native current-session/lifecycle evidence and approval integration remain blocked behind their external gates.
