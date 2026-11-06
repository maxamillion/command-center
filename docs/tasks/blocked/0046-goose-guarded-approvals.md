# Task 0046: Implement durable guarded Goose approval choices

Owner: unclaimed
Claimed: not claimed
State: blocked (directory is authoritative)
Phase: F2-F3
Depends on: [0045](../pending/0045-goose-approval-contract.md), [0035](../blocked/0035-goose-native-runtime-integration.md), [0026](../pending/0026-goose-capability-guards.md)
Authorization / external gate: Explicitly blocked on an accepted, implemented native decision channel coordinated with the terminal UI; none is selected. User and native integration maintainer must supply/approve this before implementation.

## Goal

Implement only the accepted request-correlated native approval mechanism, retaining CC durable claim/uncertainty safeguards.

## Context and related records

- [Plan 0002](../../plans/0002-goose-agent-parity.md), especially the feature matrix, safety contracts, phase gates and pinned source/doc references.
- [ADR-0002: direction and authorization](../../decisions/0002-goose-integration-direction.md); its Proposed status is not approval.
- [Resume/update protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). Use the current task paths in the tracker when dependencies move.
- [Milestone 0003: full parity](../../milestones/0003-goose-full-agent-parity.md).

## Acceptance criteria

- [ ] Link actual accepted contract, implemented channel revision and explicit integration/testing permission; current cursor+Enter terminal menus remain unsupported without it.
- [ ] Render original request and exact CLI option labels/scopes; bind expiring one-use grants to endpoint/target/process/session/request generation/screen as appropriate.
- [ ] Commit durable prompt claims before decision IO, arbitrate across clients and native terminal, reject stale/duplicate/changed requests and never automatically approve or retry uncertain delivery.
- [ ] Tests cover repeated identical requests, notice variant, persistent-scope choice, another terminal client, clipped/ambiguous request, channel failure, stale owner, restart and persistence failure; unsupported elicitation stays terminal-only.
- [ ] Actions neither send ordinary chat nor resize/attach compact terminals; explicit completion never acknowledges unrelated replies, resolves future approvals or marks work done.

## Files likely involved

- `src/agents.rs`
- `src/agent_remote.py`
- `src/attention.rs`
- `src/queue.rs`
- `web/src/queue.ts`
- `tests/test_agent_outbox.py`
- `web/tests/agents.spec.ts`
- `authorized native decision integration (not selected yet)`

## Findings and decisions

Not started. Keep architectural decisions, discoveries and exact source references here; link a numbered ADR for consequential choices. No prior research test pass is implementation evidence.

## Validation plan

Run from the repository root after creating the required fixture cases. These are validation entry points, **not executed evidence**. Existing suites alone do not prove the new acceptance cases; record the exact new test names and nonzero counts. See [testing guidance](../../testing.md) and [plan verification](../../plans/0002-goose-agent-parity.md#8-verification-plan).

```sh
cargo fmt --check
python3 -m unittest discover -s tests -p 'test_agent_outbox.py'
cargo test
cargo build --release
npm --prefix web run build -- --outDir dist-next
CC_BINARY=../target/release/command-center CC_WEB_DIR=dist-next npm --prefix web test -- tests/agents.spec.ts
cargo clippy --all-targets -- -D warnings
```

Browser prerequisites: dependencies installed as described in testing guidance, supported Chromium (`CHROME_BIN` if needed), tmux and fixture-only SSH tooling where the spec requires it. Use fresh build artifacts. Missing SSH/browser/device coverage is not a pass.

The exact producer/native harness command cannot be fixed until the integration contract is selected. Record it, its pinned version, isolated configuration and nonzero results here **before** claiming the corresponding native acceptance criteria; the existing suites above are not a substitute.

## Validation evidence

Not run for this task. Record command, environment/fixture revision, exit status, counts/results and limitations as work happens. Fixture input/launch/restart/close tests must never target real work agents or user windows. Do not use private production receipts/transcripts for fixtures.

## Next action / blocker / handoff

- Last completed checkpoint: none; task unclaimed.
- Working tree / commit: no implementation changes for this task; incoming agent must inspect `git status --short` and the actual diff before proceeding.
- Current blocker: external dependency above, plus unmet prerequisites and authorization.
- Exact next action: User/native integration owner must authorize and supply the terminal-coordinated decision channel; after contract/native proof tests pass, add repeated-generation and persistence-failure fixtures before enabling choices.
- Resume validation: read prerequisite evidence and accepted decisions, inspect the actual diff, then run only affected checks needed for new changes or unverified/stale evidence; do not blindly rerun completed work.
- On pause: replace these fields with completed/remaining acceptance items, affected files/commit or uncommitted state, actual checks/failures, unresolved decisions, and one exact next action. Update state/links/tracker and add a dated handoff note.
