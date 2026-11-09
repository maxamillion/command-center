# 2026-11-06 Goose capability guards

Task 0026 is complete; task 0027 is claimed and current. The user's scope decision in ADR-0002 authorizes this CC-owned work in dependency order. Native runtime evidence and approval-channel tasks 0035/0046 remain blocked.

## Completed

- Added a fixed, additive capability map with explicit reasons in Rust and the Python helper. Codex/Claude/Pi behavior is preserved; Goose currently has no enabled capability and Pi native approvals remain terminal-only.
- Added independent action-time guards for Python history, phase, message, approval, launch, resume/restart and Close paths; Rust guards for send/approval grants, launch/resume, restart and Close; and UI gating for unsupported actions.
- Added direct helper tests proving rejected Goose operations reach no terminal, launch or close IO, Rust capability tests, and a Playwright fixture for disabled controls/reasons.
- Full browser verification revealed the Python `status` action omitted `provider`; Rust's new Close capability check then rejected existing providers. Added the provider to that response. Focused regression tests cover supported-provider Close and Goose's disabled Close.

## Verification

- `cargo fmt --check` and `git diff --check`: pass.
- `cargo test`: 49 passed; initial sandbox socket bind failed, then the approved outside-sandbox run passed.
- `cargo clippy --all-targets -- -D warnings`: pass.
- `cargo build --release`: pass after the status-provider fix.
- `python3 -m unittest discover -s tests -p 'test_agent_*.py'`: 63 passed; existing SQLite ResourceWarnings remain.
- `npm --prefix web run build -- --outDir dist-next`: pass, with existing chunk warnings.
- Focused release-backed agent specs, using `/usr/bin/google-chrome`: 4 passed (Goose capability UI and three local Close behavior specs).
- Full `agents.spec.ts`: 18 passed, 8 failed before the status-provider fix. Three local Close failures were fixed and the four directly affected/local Close specs passed afterward. SSH helper scenarios returned HTTP 502 in three specs; two other local card specs also failed during that full shared fixture run and were not independently rerun. The complete suite/SSH coverage therefore remains unqualified.

No live Goose process, external integration, user window or production conversation was accessed.

## Current work

Task 0027 is current. Next, trace byte offsets, numeric message IDs, file-metadata versions and reply acknowledgements across `agent_remote.py`, `attention.rs`, `agents.rs`, `queue.ts`, `agent-activity.ts` and `docs/api.md`. Design additive opaque display/order/page/reset cursors that remain separate from future input-acceptance proof. Preserve legacy JSONL paging and read state.

The tree is uncommitted and includes tasks 0024–0027. Reinspect `git status --short` and the current diff before continuing. Do not infer that this work enables Goose input, Ready, approvals, launch, resume, restart or Close.
