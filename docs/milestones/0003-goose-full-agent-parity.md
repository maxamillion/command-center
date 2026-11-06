# Milestone 0003: Guarded native Goose agent feature parity

Status: Proposed — not started; native evidence and approval dependencies unresolved.
Plan: [0002](../plans/0002-goose-agent-parity.md).
Decision gate: [ADR-0002](../decisions/0002-goose-integration-direction.md).

## Outcome

Native Goose agents have the supported union of CC's Claude/Codex agent capabilities without weakening current-session proof, guarded input/decisions, durability, history privacy or terminal correctness. This includes independently assessed Claude-only background-task feedback. A selected managed-ACP architecture requires an explicit replacement plan/milestone, not silent completion of native parity.

## Acceptance

- [ ] [Milestone 0002](0002-goose-native-observation.md) is qualified; legacy providers continue to pass relevant regression coverage.
- [ ] Accepted native contract and consented pinned producer provide actual current-session ownership/epoch, fresh settled/input-ready state, child isolation and native-input persistence provenance. Synthetic-only or terminal/history-derived evidence is insufficient.
- [ ] Literal new launch/model/prompt and fresh Board launch behavior, per-window durable recovery and once-only card initialization are proven without newest-history association or uncertain launch retry.
- [ ] Exact native session resume excludes ambiguous/concurrent ownership; same-pane restart binds the reviewed original process/session and verifies the replacement before once-only preference transfer. Old drafts/outbox do not transfer or replay.
- [ ] Ordinary chat/editor policy, durable FIFO intent, dual-layer fresh Ready guards and versioned one-use acceptance receipts are proven across session switch, mutable history, concurrent clients, endpoint/process replacement and lost-response/restart cases; no false Seen or uncertain replay.
- [ ] Read/attention/notification/pending-bubble behavior uses exact observed replies/events/receipts, not heartbeat/tool/user-only changes; drafts and focus/scroll survive polling/navigation.
- [ ] Accepted native approval channel arbitrates the exact request generation with the terminal UI and durable CC claim, displays exact choices/scopes and rejects stale/ambiguous requests. Unsupported dialogs remain terminal-only; no cursor+Enter automation or automatic approvals.
- [ ] Background-task equivalent is implemented with authoritative bounded provenance or remains explicitly an unmet parity criterion. A completed investigation or decision to defer does not satisfy this box; any follow-up task is linked and fulfilled before full completion.
- [ ] [Qualification task 0049](../tasks/pending/0049-goose-full-parity-qualification.md) provides actual supported-version/schema/native/local/SSH/ProxyJump/multi-client/restart/mobile/performance evidence and independent review; unavailable mandatory evidence keeps full completion open.

## Work and external dependencies

The [execution tracker](../plans/0002-goose-agent-parity.md#execution-tracking-and-handoff) links design/proof tasks 0033–0035, lifecycle tasks 0036–0040, input/receipt/feedback tasks 0041–0044, approval tasks 0045–0046, background evidence task 0047 and qualification tasks 0048–0049.

Task [0035](../tasks/blocked/0035-goose-native-runtime-integration.md) needs a selected/authorized actual native producer. Task [0046](../tasks/blocked/0046-goose-guarded-approvals.md) needs an accepted/implemented terminal-coordinated decision channel. Neither exists as a chosen integration in this package. Recording a detailed decision, running synthetic tests or finishing observation cannot release those gates.

## Completion

Not completed; no feature implementation or native interoperability evidence yet. Only accept this milestone when every criterion has linked evidence, all required capability gaps are closed and maintained docs describe the actual supported combinations. Reduced-scope delivery must be labeled as such rather than redefining full parity by checking unavailable capabilities off. This record grants no live actions or deployment authorization.
