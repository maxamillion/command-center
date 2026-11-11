# Task 0053: Implement comprehensive Goose review fixes

Owner: Codex
Claimed: 2026-11-10
State: done

Scope: fix bugs 0020–0022 with bounded snapshot paging and latest-reply discovery, add Rust/Python capability parity coverage, repair stale milestone references, and organize history contracts into a cohesive unit. Preserve independent action guards and external/native gates. No live agent actions.

Acceptance: reproduce defects in regression tests before fixes; verify five-page paging, source binding, append retention, rewrite resets, reply discovery under tool tails and bounded incomplete reads; run Python/Rust/frontend checks; record unavailable browser coverage and handoff.

Validation: synthetic regression and available static/unit checks completed; browser integration blocked as described below.

## Implementation and decisions

- Replaced growing page-spec lists with a compact source/session-bound snapshot proof (hash, top/bottom timestamp+ID, source-row count). `GooseHistorySnapshot` owns decoding, range revalidation, paging and refresh. Keeping this cohesive class inside the existing helper preserves its single-script remote deployment; a broad provider-module packaging migration is not needed for these fixes.
- Added `history_view` for refresh and `view_cursor`/`replace` response metadata. Goose refresh/paging returns a complete bounded replacement, retaining loaded rows across appends and removing stale activity on actual edits. Views retain at most 500 source rows, respect the existing content budgets, and evict oldest rows on append overflow. Local SQL materialization now also enforces a 2 MiB raw-field byte bound.
- Frontend sends the opaque view proof on polls, applies full replacements and preserves the visible message anchor on ordinary refresh/older-page loads. Legacy providers retain existing merge behavior.
- Latest reply discovery scans assistant rows separately from display pages, bounded to 2,000 rows, bytes and existing query/total time budgets. A late persisted reply can advance even when the latest display-page fingerprint is unchanged. Incomplete scans disclose limits and are excluded from Rust attention metadata; they cannot create baselines or clear unread state. A discovered reply outside the displayed view has no acknowledgement cursor.
- Added exhaustive Python/Rust capability availability/action-denial parity coverage for all four providers and eleven capabilities. Independent production guards remain.
- Corrected observation milestone state, full-parity progress wording and stale authorization references. Native proof, launch/input/approval gates and task 0032's missing integration evidence remain unchanged.

## Regression and validation evidence

- Before implementation, the three new defect regressions failed: page-four cursor overflow, unchanged reply cursor behind a tool tail, and append-only reset. The corresponding regressions now pass.
- `python3 -m unittest discover -s tests -p 'test_agent*.py'`: 112 passed. Ten added Python cases cover the three defects plus source/marker validation, deletion/reinsertion, retention limits, incomplete scans, unseen-reply acknowledgement, byte limits and late persistence. Existing SQLite fixture ResourceWarnings remain.
- `python3 -m unittest discover -s tests -p 'test_claude_continuation.py'`: 12 passed.
- `cargo test`: attempted; 46 library tests passed and two listener tests failed with sandbox Operation not permitted before later test additions. Final `cargo test --lib -- --skip features::tests::disabling_waits_for_active_handlers_and_blocks_subsequent_requests --skip tests::https_origin_guard_preserves_host_and_csrf_checks`: 47 passed, two explicitly filtered. Includes new cross-language parity and incomplete-observation attention tests. `cargo test --bin command-center`: two passed. This is not a full Rust-suite pass; tmux integration remains unavailable.
- `cargo clippy --all-targets -- -D warnings` and `cargo fmt --check`: passed.
- `npm --prefix web run build -- --outDir /tmp/cc53-web`: passed TypeScript/Vite; existing import/chunk-size warnings.
- `npm --prefix web test -- --list tests/agents.spec.ts`: 30 tests discovered, including the new snapshot-scroll regression. Discovery is not execution.
- `CC_BINARY=../target/debug/command-center CC_WEB_DIR=/tmp/cc53-web CHROME_BIN=/usr/bin/google-chrome npm --prefix web test -- tests/agents.spec.ts --grep 'Goose snapshot refresh'`: failed during fixture setup, before browser assertions, because the sandbox denies the isolated tmux socket. A standalone Playwright/Chromium smoke attempt also failed at startup (crashpad socket setsockopt Operation not permitted). No live panes or provider stores were used.
- Synthetic 510-row schema-17 fixture: loading all five pages returned 500 messages with cursor lengths 322/322/322/322/321 bytes in 125.24 ms total on this container. This is a small local fixture measurement, not SSH/large-store qualification.

## Handoff

Fixes and regression coverage for bugs 0020–0022 are implemented. Browser scroll behavior, real tmux/SSH/ProxyJump and physical-device acceptance must be exercised in an environment that permits fixture sockets. Task 0032 and qualification tasks retain their outstanding evidence requirements. No deployment, live agent actions, commit or push performed. Earlier review records and these fixes remain in the shared uncommitted tree.

- Final `cargo build --release`: passed. Final agent suite: 112 passed; final three Rust capability tests passed. `git diff --check`: passed.
