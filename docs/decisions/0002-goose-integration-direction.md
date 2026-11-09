# ADR-0002: Goose integration direction and authorization gates

Status: Accepted for the native Goose implementation scope recorded below; conditional design gates remain Proposed.
Date: 2026-11-06.
Decision authority: user; native integration maintainer/owner also required for external implementation or installation scope.

## Context

[Plan 0002](../plans/0002-goose-agent-parity.md) identifies independently useful CC-only native observation work and additional native evidence/decision dependencies for guarded full parity. On 2026-11-06, the user explicitly requested: “please follow and implement Plan 0002 in order to implement support for goose into this project.” This authorizes Command Center implementation work under the native Goose plan, in dependency order, with observation first. It does not authorize upstream/third-party repository changes, installation or activation of an external integration, or actions against live Goose agents. The plan's external native producer and approval-channel gates remain binding.

[Task 0024](../tasks/done/0024-goose-implementation-scope.md) records the accepted scope decision. Detailed native lifecycle/acceptance and approval contracts need their own subsequently allocated ADRs; their exact interfaces and producers are not chosen by this record.

## Decision

**Accepted direction:** implement native Goose support in Command Center, beginning with the limited observation milestone and following the execution task dependency graph. Treat this scope as authorization for CC-owned code, synthetic fixtures, and qualification work in tasks 0025–0034 and 0036–0049 when prerequisites are satisfied. Runtime capabilities remain disabled until their task acceptance criteria and evidence pass.

This authorization does not supply the named, pinned, consented native producer required by task 0035 or the implemented terminal-coordinated decision channel required by task 0046. Those tasks remain blocked. It does not authorize upstream Goose changes, third-party installs/hooks, or live launch/send/restart/close/approval actions. Such operations require their stated separate gates and explicit operational authorization.

| Gate | Proposed scope / choice to resolve | Current disposition | Owner / action |
|---|---|---|---|
| Observation architecture | Native tmux process observation + read-only history, or explicitly separate managed-ACP replanning, or defer | **Accepted: native, observation-first** | User's 2026-11-06 implementation request; follow Plan 0002 dependencies. |
| CC-only implementation | Provider/cursor/capability foundations and observation tasks 0025–0032, then qualification 0048 | **Authorized in dependency order** | Code and synthetic fixtures only; runtime capabilities require evidence. |
| Native proof design/spike | Native ownership/settled/input-provenance design and synthetic contract work 0033–0034 | **Authorized in dependency order; contract acceptance remains separate** | Detailed contract must be recorded and accepted before actual producer integration. |
| Actual native producer | Upstream capability versus explicitly maintained opt-in integration; named owner, pinned revision and test/installation scope | No producer selected; task 0035 blocked | User + integration owner must select/authorize producer and isolated validation. |
| Launch / Board | Literal argv, fresh detached process launch/Board work 0036–0038, independently of exact session linkage | **CC-owned code authorized in dependency order** | No live launches; no newest-session association; operational action still needs separate authorization. |
| Exact lifecycle / messages | Exact resume/restart/input/receipt/Outbox/feedback work 0039–0044 after native gates | **CC-owned code authorized only after prerequisites** | Actual native proof and action-time guards remain required; no live messages/actions. |
| Approval contract / channel | Design 0045 and guarded decision implementation 0046 coordinated with native terminal UI | Design work authorized after prerequisites; 0046 blocked | User + integration owner must approve an implemented channel. |
| Background-task parity | Assess provider evidence and implement or record remaining gap in 0047 | **Authorized in dependency order** | A deferred/unavailable outcome remains an unmet full-parity criterion. |
| Deployment / live operations | Install/reload integrations on live agents, mutate external projects, launch/send/restart/close real work agents or deploy | Not authorized | Separate explicit operational authorization; ledger tasks/Board state never grant it. |

When an actual choice is made, record its date, authority, exact scope and reference in the decision log below and the affected task. If only the observation direction is accepted, this ADR can be Accepted **only for that documented direction and scope**; unresolved native/approval contracts remain Proposed in their own ADRs and their task gates stay closed. Do not mark all rows accepted because one scope is approved. If the user instead directs implementation with an explicit scope, record that direction here rather than repeatedly requesting the same approval.

### Decision log

- **2026-11-06 — user:** “please follow and implement Plan 0002 in order to implement support for goose into this project.” Accepted native Goose direction and authorized CC-owned implementation work in the execution tracker, in prerequisite order, with limited observation first. External producer/approval dependencies and operational actions remain separately gated. Captured by [Task 0024](../tasks/done/0024-goose-implementation-scope.md).
- Documentation-only preparation on 2026-11-06 is tracked in [Task 0023](../tasks/done/0023-goose-execution-tracking.md).

## Alternatives and consequences

- **Observation-first native (recommended, not accepted):** useful cards/history with honest Unknown/project-history labels. It does not deliver verified Ready, native input acceptance or approval buttons by itself. Keep these limits visible.
- **Native full-parity integration:** retains the existing tmux workflow but needs proven current-session/settled/input provenance and decision arbitration. Existing telemetry must not be promoted to authority merely to avoid an external dependency. Detailed contracts and operational consent remain necessary.
- **Explicit CC-managed ACP architecture:** can be planned separately, but is not transparent attachment to an existing native CLI. Replan dependent native tasks; do not mark them completed as though equivalent native coverage exists.
- **Defer:** retain the proposed plan and tasks. A completed decision to defer does not satisfy implementation dependencies or milestone acceptance; annotate the withheld scope and reopening trigger.

No alternative may weaken existing endpoint/process/screen guards, uncertain-delivery no-retry behavior, private data boundaries or compact terminal isolation. This ADR does not invent a current Goose schema or installable bridge.

## Evidence and related records

- [Research task 0022](../tasks/done/0022-goose-agent-parity-research.md) and [plan source/official-documentation evidence](../plans/0002-goose-agent-parity.md#10-source-evidence-index).
- [ADR-0001](0001-filesystem-work-ledger.md) and [work ledger](../work-ledger.md): documentation, task completion and live actions are distinct.
- [Milestone 0002: limited native observation](../milestones/0002-goose-native-observation.md).
- [Milestone 0003: full native agent parity](../milestones/0003-goose-full-agent-parity.md).

## Supersedes / superseded by

None. If the architecture changes, record the superseding decision and update affected tasks/dependencies without renumbering or silently discarding their evidence.
