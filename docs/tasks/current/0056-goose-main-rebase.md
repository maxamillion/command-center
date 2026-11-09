# Task 0056: Rebase Goose support onto main

Owner: Codex
Claimed: 2026-11-11
State: current

## Current rebase (2026-11-13)

Latest checkpoint: second replay a4e6d88 onto d63da77 stopped in PLAN.md, src/agent_remote.py, src/agents.rs and web/src/queue.ts. All four working-tree conflicts are resolved, preserving both branches. The index still needs local staging. Two topic commits remain (bb37036 and 89c06dd).

The merge retains VIRTUAL_ENV and the selected tmux socket in process observations, Python-venv and approval-policy launch metadata, native Claude questions and guarded answer controls, and input-attention labels/notifications. Goose capability checks/history fields coexist with those behaviors. Shared questions::enrich now uses Target::is_latest to exclude opaque older-history pages as well as legacy numeric pages from answer grants. Extended synthetic process-observation assertions to prove VIRTUAL_ENV/socket retention while unrelated environment values remain excluded, and extended the Rust question-grant test to cover both paging forms.

Validation at this checkpoint: the combined Python run executed 180 tests, 179 passed and the real named-session/tmux socket integration test errored with sandbox Operation not permitted. Socket-dependent test_agent_attachments and test_question_api were not selected. Frontend TypeScript/Vite build to /tmp/cc-rebase-nov13-web passed; formatting, Python syntax and whitespace/conflict-marker checks passed. Clippy offline was attempted and is blocked by uncached image; Rust compile/tests, browser, SSH and physical-device coverage remain unavailable, not passes.

Next: stage all tracked resolutions and this task/handoff (git add -u), then GIT_EDITOR=true git rebase --continue locally. Preserve the same integrations as the two remaining Goose-fix commits replay. Do not report rebase completion until Git confirms it.

### Earlier checkpoint (first replay)

Owner: Codex, resumed 2026-11-13 at the user's request.
The previous rebase completed at 89c06dd. The user has now started a new rebase onto main d63da77 (project Python venv launch/restart support). Git is replaying 59b014e, a4e6d88, bb37036 and 89c06dd.

The first replay, 59b014e, stopped only on one additive PLAN.md conflict: upstream blank lines versus this task's active-work entry. Resolved the working-tree conflict, keeping the task entry and all upstream records. No source conflicts are present at this stop. `git diff --check` passes. Three topic commits remain to replay; this does not establish runtime compatibility with the newer main.

Next action: stage PLAN.md and this updated task, then continue the rebase. If Git metadata remains read-only in the agent environment, continuation must run locally. Preserve new main's launch/restart Python-venv settings, question/approval handling, Whiteboard live events and all earlier conflict resolutions in subsequent source merges. Ledger numbering collisions remain unresolved; no records were renumbered.

## Previous rebase scope/checkpoint (historical)

Continue the user-started rebase of goose_support (original tip 67bc4d4) onto main f1e12bb, preserving upstream changes and Goose behavior. Four topic commits are being replayed.

## Checkpoint

The user continued past the first replay (116192f). The second replay, ccc76e4 (initial Goose implementation), stopped in PLAN.md, src/agent_remote.py and web/src/queue.ts. All conflict markers in those files are resolved in the working tree; the index still records unmerged paths until the user can stage them locally.

Resolution retains upstream pi command receipts, busy-agent input state/guards and native-dialog checks, Codex launch approval-policy metadata and visibility-filter version/reset migration, queue file links and recall invalidation. It combines these with Goose capability denial, independent provider dispatch, opaque display IDs and history paging. Added tests/test_agent_rebase_contract.py to exercise receipt positions versus opaque display IDs, Codex migration on opaque paging, and early Goose denial before upstream busy-input IO. PLAN.md preserves upstream and Goose work entries and replaces the obsolete Goose execution-package handoff text with its newer description.

Two commits (6983b63 and 67bc4d4) remain to replay. Do not report this intermediate source as the completed history-fix branch; those fixes arrive in the remaining commits.

Upstream and topic histories independently allocated overlapping task, plan, bug and decision numbers. Both records remain present; numbering reconciliation needs a recorded migration decision respecting immutable record identities. Resolving textual conflicts does not establish ledger-number uniqueness.

## Validation and next action

- `python3 -m py_compile src/agent_remote.py`, `cargo fmt --check`, and `git diff --check`: passed; no conflict markers remain in the three resolved files.
- Agent unit discovery excluding test_agent_attachments.py: 104 passed, including three new merge-boundary tests. The unfiltered command ran 101 tests successfully but had a setUpClass error for AgentAttachments because sandbox sockets are prohibited; the exclusion is explicit, not an integration pass.
- Additional selected suites (busy-agent input, pi command receipts, Codex history/environment/association/status, attachment remote helper, launch policy, Claude continuation): 51 passed.
- Initial frontend build reported missing roughjs after main added the dependency. `npm --prefix web ci --offline --ignore-scripts --no-audit --no-fund` restored the locked dependencies from cache (82 packages). `npm --prefix web run build -- --outDir /tmp/cc-rebase-web` then passed TypeScript/Vite, with existing import/chunk-size warnings.
- Clippy attempted: blocked by unavailable crates.io DNS and uncached resvg. Offline retry confirms missing resvg, so no Rust compile/test/Clippy success is claimed.

Git metadata remains read-only here. Next: stage PLAN.md, src/agent_remote.py, web/src/queue.ts, tests/test_agent_rebase_contract.py, this task and the dated rebase handoff, then run GIT_EDITOR=true git rebase --continue locally. Resolve and validate any subsequent conflicts; preserve both upstream features and the remaining Goose fixes. Ledger-number collisions described above remain unresolved.
