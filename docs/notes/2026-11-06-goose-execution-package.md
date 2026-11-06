# 2026-11-06: Resumable Goose implementation package

## Scope and checkpoint

The user asked to follow repository conventions when preparing the plan for stop/resume handoff. This is documentation preparation, not feature implementation, a native/ACP decision, installation or deployment authorization.

- [Plan 0002](../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff) is the execution entry point and linked state/dependency summary.
- [Task 0023](../tasks/done/0023-goose-execution-tracking.md) completed this package; research evidence remains in [done Task 0022](../tasks/done/0022-goose-agent-parity-research.md).
- Execution tasks **0024–0049** have individual acceptance checklists, prerequisite links, likely files, validation commands, empty actual-evidence sections and last-checkpoint/working-tree/blocker/next-action fields. All are unclaimed: **24 pending, 2 blocked** (0035 real native producer, 0046 actual approval channel).
- [ADR-0002](../decisions/0002-goose-integration-direction.md) is **Proposed**, with scope/consent gates and no architecture approval recorded. Detailed native/approval contracts receive their own ADRs when authorized.
- [Milestone 0002](../milestones/0002-goose-native-observation.md) qualifies limited observation independently; [Milestone 0003](../milestones/0003-goose-full-agent-parity.md) cannot complete with a required capability unavailable/deferred. Both remain Proposed/not started.

## Immediate next action

Open [Task 0024: implementation scope](../tasks/pending/0024-goose-implementation-scope.md), obtain or record the user's actual scope/direction and update ADR-0002. Do not start 0025 or release native/approval gates merely because tasks exist. If a later explicit user implementation request supplies sufficient scope, record that authorization rather than asking for the same approval again.

For subsequent work, the task directory is authoritative. Claim one eligible task, update its owner/date and all inbound links/table/root; record acceptance evidence in that task, not duplicated plan checklists. Before stopping, record completed/remaining work, exact diff/commit state, actual checks/failures and one precise next action; add/link a new dated note. Concurrent writers must not share files. Re-scan IDs before allocating new records; do not rely on stale “next number” hints.

## Working tree / transfer

No runtime/source changes, agent actions, provider configuration or deployments. The user explicitly authorized committing the research and execution package on 2026-11-06; these records are included in the documentation commit introducing this handoff on branch `goose_support`. Locate it with `git log --oneline -- docs/notes/2026-11-06-goose-execution-package.md` and inspect `git status --short` before continuing. No push was requested. A handoff to another checkout requires transferring that commit; a branch name alone does not make an unpushed commit available remotely. No temporary research checkout/cache is required: the plan contains pinned upstream source and official documentation links.

Unrelated current task 0009 and existing records were not changed. The research's 70 passing tests are historical evidence only, not implementation passes for any new task.

## Validation

Preparation validation passed and is recorded in task 0023: 33 package/index records, 351 relative links/anchors, unique per-type IDs, 26 unclaimed execution tasks/139 unchecked criteria, 46 acyclic prerequisite edges and tracker/state agreement, A–G/background coverage, Proposed decision/milestone gates, documentation whitespace and source-diff checks. Independent review found no actionable issues. Task 0023 is done; final links were rechecked after its move, with no stale current-task references. No native runtime, Rust/frontend, SSH interoperability or device validation was performed for this documentation package.
