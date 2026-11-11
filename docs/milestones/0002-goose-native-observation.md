# Milestone 0002: Useful, honest native Goose observation

Status: In progress — observation implementation authorized by [Task 0024](../tasks/done/0024-goose-implementation-scope.md); Close-agent acceptance and qualification remain incomplete.
Plan: [0002](../plans/0002-goose-agent-parity.md).

## Outcome

Agents can show kernel-proven interactive Goose processes, bounded native project history/activity and process-scoped card preferences without pretending that project history or terminal telemetry proves a live native conversation or Ready state. Existing providers and compact terminal isolation remain correct. This is deliberately **not full agent parity**.

## Acceptance

- [ ] Provider/cursor/capability foundations fail closed, preserve legacy identities/history/read semantics and do not enable unproven actions.
- [ ] Supported native process/path cases and read-only schema compatibility are proven with synthetic fixtures and bounded IO/query measurements; provider storage/config is not modified.
- [ ] Chat/activity visibility, audience filtering, native order, edits/compaction/reset and literal/sanitized rendering are fixture-proven; tool/control records never become human input or unread replies.
- [ ] Cards/filters/preferences/read acknowledgements and authoritative removal retain endpoint/process scope; Unknown/project-history/unavailable reasons are honest and do not manufacture completion notifications.
- [ ] Close agent has the existing exact process/topology preview/confirmation, no retry and fixture-only destructive evidence; other actions remain unavailable unless separately authorized and proven.
- [ ] Compact navigation/actions make no terminal viewer/input/resize traffic; simultaneous desktop processes/dimensions and drafts survive. Actual device/SSH gaps are labeled, not reported as passes.
- [ ] [Qualification task 0048](../tasks/pending/0048-goose-observation-qualification.md) records actual local/SSH/ProxyJump/version/schema/performance coverage and updates maintained docs only to demonstrated behavior.

## Work

Tasks [0025–0032](../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff) implement the observation slice; task 0048 qualifies it. Their task files are authoritative for state, acceptance and evidence. Dependencies and current paths are in the plan tracker.

## Completion and remaining limits

Not completed; implementation evidence is recorded in tasks 0025–0031, with Close-agent acceptance in current task 0032 and qualification pending in task 0048. [Research task 0022](../tasks/done/0022-goose-agent-parity-research.md) and tracking preparation do not satisfy this milestone.

Verified native session ownership/Ready, messages/Outbox acceptance, exact resume/restart, launch/Board work and approval choices belong to separately gated tasks and [Milestone 0003](0003-goose-full-agent-parity.md). Completing observation does not imply those features, authorize installation/deployment, or change live Board tickets.
