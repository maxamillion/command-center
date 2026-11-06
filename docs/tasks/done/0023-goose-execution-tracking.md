# Task 0023: Prepare resumable Goose implementation tracking

Owner: goose documentation coordinator
Claimed: 2026-11-06
State: done (directory is authoritative)

## Goal

Convert [Plan 0002](../../plans/0002-goose-agent-parity.md) into a repository-conformant execution package that an agent can claim, update, pause and hand off without relying on chat history.

## Context and related records

- User authorized documentation preparation, not feature implementation or a choice of native/ACP integration.
- Read [work ledger](../../work-ledger.md), [ADR-0001](../../decisions/0001-filesystem-work-ledger.md), [research task 0022](../done/0022-goose-agent-parity-research.md) and the existing task template.
- Preserve the existing research evidence and unrelated current task 0009. No live Board edits, source/runtime changes, agent actions or deployment.

## Acceptance criteria

- [x] Plan has a linked implementation progress/dependency table, clear authorization/decision gates and explicit resume/update instructions.
- [x] Work has immutable numbered task files, owner/state/dependencies, observable acceptance checklists, relevant files, validation commands and a precise checkpoint/next action.
- [x] Unresolved architecture decisions are Proposed, with approval and external dependencies explicit; no decision is silently accepted.
- [x] Milestone outcomes distinguish limited observation from complete parity; no future work is marked complete or validated.
- [x] PLAN.md and a dated handoff identify the exact next task; relative links, numbering, dependency coverage/state consistency and documentation whitespace are checked.
- [x] Independent documentation review and final source-diff check recorded; only documentation changed.

## Findings and decisions

Prepared the linked execution tracker and 26 immutable tasks (0024–0049): 24 pending, 2 concretely blocked on native evidence/approval integrations. Each owns acceptance checks, dependencies, authorization, likely files, validation entry points, empty actual-evidence sections and a precise resumable checkpoint. No execution task is claimed or complete.

Added Proposed ADR-0002 and two Proposed milestones: limited observation (0002) versus full parity (0003). Detailed native/approval contracts remain decisions for later scope, not invented current interfaces. Split observation UI/Close, fresh launch/Board and exact resume/restart into separate tasks; test query bounds/read/reset safety before final qualification.

Plan 0002 now defines authoritative task state, dependency graph, scope gates, claim/pause/resume/completion protocol, shared-file ownership limits and handoff transfer requirements. Root index links the next scope task, external blockers and latest handoff. Existing research evidence and unrelated task 0009 remain unchanged.

## Validation evidence

- Ran `python3 /tmp/cc-goose-ledger-check.py` (temporary documentation audit, not a runtime/required handoff artifact): PASS for 33 package/index records, 348 relative links/anchors, unique per-type IDs/names, 26 execution tasks with 139 unchecked criteria, 46 acyclic prerequisite edges, tracker/task-state agreement and A–G/background coverage. All task checks are initially empty; actual-evidence sections say Not run. Decision/milestone states remain Proposed. The checker also verifies referenced existing test suites/spec paths and frontend build entry points.
- Ran `git diff --check` and explicit whitespace checks on new/untracked package docs: passed. Existing Markdown two-space hard breaks are permitted; no stray tabs/trailing whitespace.
- Ran `git diff --exit-code -- src web tests integrations scripts Cargo.toml Cargo.lock README.md AGENTS.md docs/tasks/current/0009-pi-first-message-receipts.md`: no changes. Audit confirms every changed/untracked repository path is PLAN.md or docs/.
- Independent read-only architecture/dependency review and final self-review found no actionable issues. They confirmed explicit authorization and native proof/approval blockers, separate observation/full-parity gates and usable per-task stop/resume fields.
- Final post-move audit rerun: PASS for the same 33 records, now 351 relative links/anchors (completion/handoff links added), all 26 task states and 46 prerequisite edges unchanged; no stale current/0023 references. No implementation/Rust/browser/native/SSH/device tests were run; existing research test results are not new execution evidence. No commit, push, live Board action, provider configuration, agent input/launch/restart/close or deployment.

- Commit preparation on user request: reran the package audit (33 records/351 links, task states and prerequisites unchanged) and verified documentation-only staging. The staged Git whitespace check caught eight intentional Markdown hard-break lines that the earlier custom audit permitted; removed those trailing spaces and reran staged whitespace checks. No implementation tests were needed for this documentation-only commit.

## Next action / blocker / handoff

Completed checkpoint: documentation execution package only. No remaining preparation blocker or code changes. The user subsequently authorized committing these records on 2026-11-06; this task and the earlier research records are included in the documentation commit introducing the execution handoff on branch `goose_support`. Locate it through the handoff file history and inspect `git status --short` before continuing. No push was requested; outside-checkout handoff requires transferring the commit.

Exact next action: [Task 0024](../pending/0024-goose-implementation-scope.md) records the actual user scope/architecture decision before feature implementation. Read [execution handoff](../../notes/2026-11-06-goose-execution-package.md) and [Plan 0002 tracking protocol](../../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff). No feature implementation, integration install or architectural choice is authorized by this completed documentation record.
