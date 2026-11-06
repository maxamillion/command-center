# ADR-0002: Goose integration direction and authorization gates

Status: Proposed — no implementation direction accepted.
Date: 2026-11-06.
Decision authority: user; native integration maintainer/owner also required for external implementation or installation scope.

## Context

[Plan 0002](../plans/0002-goose-agent-parity.md) identifies independently useful CC-only native observation work and additional native evidence/decision dependencies for guarded full parity. The user requested a resumable implementation-tracking package following the repository conventions. That request authorizes documentation preparation, not feature implementation or selection of native versus managed-ACP architecture.

[Task 0024](../tasks/pending/0024-goose-implementation-scope.md) records the next actual scope decision. Detailed native lifecycle/acceptance and approval contracts need their own subsequently allocated ADRs; their exact interfaces and producers are not chosen by this record.

## Decision

**No option is accepted yet.** The recommendation under review is observation-first native support, with guarded operations remaining unavailable until their independent evidence and authorization gates pass. This is not a change to current application behavior or operating rules.

| Gate | Proposed scope / choice to resolve | Current disposition | Owner / action |
|---|---|---|---|
| Observation architecture | Native tmux process observation + read-only history, or explicitly separate managed-ACP replanning, or defer | Awaiting user choice | Task 0024 obtains and records the actual direction. |
| CC-only implementation | Authorize provider/cursor/capability foundations and limited observation tasks 0025–0032, then observation qualification 0048 | Not authorized | User identifies accepted scope; dependency completion alone is not permission. |
| Native proof design/spike | Authorize detailed native ownership/settled/input-provenance design and synthetic contract work 0033–0034 | Not authorized; contract not accepted | User authorizes scope; implementer allocates a detailed Proposed ADR/spec and seeks acceptance. |
| Actual native producer | Upstream capability versus explicitly maintained opt-in integration; named owner, pinned revision and test/installation scope | No producer selected; task 0035 blocked | User + integration owner select/authorize the producer and isolated validation. |
| Launch / Board | Authorize literal argv, fresh detached process launch/Board work 0036–0038, independently of exact session linkage | Not authorized | User may approve this limited scope separately; no newest-session association. |
| Exact lifecycle / messages | Authorize exact resume/restart/input/receipt/Outbox/feedback work 0039–0044 once native gates are evidenced | Not authorized; actual native proof missing | User-approved scope plus prerequisite contract, evidence and action-time guards. |
| Approval contract / channel | Design 0045 and actual guarded decision implementation 0046, coordinated with native terminal UI | No accepted contract or channel; 0046 blocked | User + integration owner approve a detailed contract and implemented channel. |
| Background-task parity | Assess provider evidence and approve implementation or record explicit remaining gap in 0047 | Unresolved | User-scoped investigation; a deferred/unavailable outcome is not full parity. |
| Deployment / live operations | Install/reload integrations on live agents, mutate external projects, launch/send/restart/close real work agents or deploy | Not authorized | Separate explicit operational authorization; ledger tasks/Board state never grant it. |

When an actual choice is made, record its date, authority, exact scope and reference in the decision log below and the affected task. If only the observation direction is accepted, this ADR can be Accepted **only for that documented direction and scope**; unresolved native/approval contracts remain Proposed in their own ADRs and their task gates stay closed. Do not mark all rows accepted because one scope is approved. If the user instead directs implementation with an explicit scope, record that direction here rather than repeatedly requesting the same approval.

### Decision log

No architecture/implementation approvals recorded. Documentation-only preparation on 2026-11-06 is tracked in [Task 0023](../tasks/done/0023-goose-execution-tracking.md).

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
