# Task 0052: Comprehensive Goose branch review

Owner: Codex
Claimed: 2026-11-09
State: done

Review `main...goose_support` at `6983b63` for code quality, correctness and accuracy against Plan 0002. Review only; no feature fixes or live agent actions.

Acceptance: inspect all runtime changes, compare staged scope and evidence, run relevant available checks, record actionable findings and coverage limitations, and update index/handoff.

Validation: completed for this review; coverage limitations below.

## Findings

- P2 bug 0020: native five-page history cursor overflows 1024 bytes on page four with ordinary timestamps/session IDs. A 510-message reproduction returned cursor lengths 576/726/877 before Failure(500).
- P2 bug 0021: a new assistant reply plus 101 tool-only rows arriving between polls leaves the baseline cursor unchanged indefinitely. The next poll reports unchanged=true, suppressing unread attention.
- P2 bug 0022: ordinary appends trigger the same reset as destructive history edits, dropping loaded older pages during normal polling.
- Maintainability: the helper grows by approximately 1,277 lines with storage, parsing, projection and cursor concerns together. Extract cohesive Goose units while preserving the single remote-helper packaging boundary. Shared Rust/Python capability declarations need an exhaustive cross-language contract test; independent action guards should remain.
- Ledger accuracy: both Goose milestone headers still say task 0024 is pending and link to its removed pending path. Their incomplete milestone status is correct, but authorization/progress text needs updating.

## Plan assessment

Plan 0002 foundation A1–A3 and observation B1–B4-observation are present, with explicit provider dispatch, separately guarded capabilities, schema-17 read-only store checks, project-only association labels and unsupported-action denial. B4-close is implemented but task 0032 correctly remains current without required real-tmux browser evidence. C–G/full parity remain pending or blocked as recorded; missing launch, input, resume/restart and approval support is intentional scope, not a branch regression. Bugs 0020–0022 expose gaps in completed paging/UI acceptance, despite passing existing fixtures. Observation qualification 0048 and full qualification 0049 must remain incomplete; local/SSH/ProxyJump, representative performance and physical phone evidence is absent from this review.

## Validation evidence

- `python3 -m unittest discover -s tests -p 'test_agent*.py'`: 102 passed; four existing unclosed SQLite ResourceWarnings.
- `python3 -m unittest discover -s tests -p 'test_claude_continuation.py'`: 12 passed.
- `cargo test --lib`: 45 passed, 2 failed opening socket listeners with sandbox Operation not permitted (`features::tests::disabling_waits_for_active_handlers_and_blocks_subsequent_requests`, `tests::https_origin_guard_preserves_host_and_csrf_checks`). This is not a clean full Rust pass.
- `cargo fmt --check`: exit 0. `cargo clippy --all-targets -- -D warnings`: exit 0.
- `npm --prefix web run build -- --outDir /tmp/cc-review52-web`: exit 0, TypeScript/Vite; dynamic-import/large-chunk warnings.
- Three direct synthetic Python reproductions used `GooseHistory` temporary SQLite fixtures and no live provider data. Exact setups/results are in bugs 0020–0022.
- Initial `node tests/pi_bridge.mjs` failed because PI_CODING_AGENT_DIR was absent; corrected isolated-environment result recorded below.
- Browser integration, SSH/ProxyJump, live native Goose and physical phone checks were not executed. No feature code was changed or live agent action taken.

## Handoff

Request changes for bugs 0020–0022. Add focused regressions and fix the paging/reply contracts, then rerun affected unit/browser tests in a socket-capable environment. Preserve the staged native proof/approval gates. Source reviewed at HEAD 6983b63 against main; review records are uncommitted.

- Corrected bridge check: `PI_CODING_AGENT_DIR=<temporary directory> node tests/pi_bridge.mjs` passed lifecycle, heartbeat, nested dialogs, branch and session replacement checks.

Follow-up: [Task 0053](0053-goose-history-review-fixes.md) implements bugs 0020–0022 and contract/documentation improvements; its validation limitations remain explicit.
