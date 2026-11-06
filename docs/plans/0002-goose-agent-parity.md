# Plan 0002: AAIF Goose support in Agents

Status: Proposed; research and execution-tracking package prepared, feature implementation not started or authorized.
Research date: 2026-11-06.
Research: [Task 0022](../tasks/done/0022-goose-agent-parity-research.md). Tracking preparation: [Task 0023](../tasks/done/0023-goose-execution-tracking.md).
Next gate: [Task 0024: scope/authorization](../tasks/pending/0024-goose-implementation-scope.md). Decision: [ADR-0002](../decisions/0002-goose-integration-direction.md) (Proposed).

## Execution tracking and handoff

### Start here / current checkpoint

- **No feature implementation has started.** Research 0022 is done; documentation preparation 0023 is separate from the execution records below.
- **Next action:** use task 0024 to obtain/record the actual scope decision. The user's request to follow ledger conventions authorizes this tracking package, not a native/ACP choice, installs or live actions. If a later explicit implementation request already supplies scope, record that direction rather than asking for the same approval again.
- All **26 execution records are unclaimed: 24 pending, 2 externally blocked**. Pending means planned, **not ready/authorized**; a task is eligible only when its applicable authorization/accepted decisions and prerequisite acceptance evidence are satisfied. Blocked records 0035/0046 identify concrete external dependencies and owners/actions.
- Outcomes are deliberately separate: [Milestone 0002: limited native observation](../milestones/0002-goose-native-observation.md) and [Milestone 0003: complete native parity](../milestones/0003-goose-full-agent-parity.md), both Proposed/not started.
- Latest checkpoint/handoff: [execution package handoff](../notes/2026-11-06-goose-execution-package.md). It records actual working-tree state and the immediate next action. This must be updated or replaced by the next dated note when work pauses.

### Source of truth and task tracker

**Task directory is authoritative for state; each task file owns its checklist, implementation findings, validation evidence and exact next action.** This table is a navigation/status summary, not a second acceptance checklist. On every claim/move/pause/completion, update the row, dependency links, root index and current checkpoint so a successor does not follow a stale state. Preserve task filenames/numbers across moves.

| Task | Plan step(s) | State | Owner | Prerequisite task IDs |
|---|---|---|---|---|
| [0024: Resolve Goose implementation scope and authorization](../tasks/pending/0024-goose-implementation-scope.md) | Gate | Pending | Unclaimed | — |
| [0025: Make agent provider dispatch explicit](../tasks/pending/0025-goose-provider-dispatch.md) | A1 | Pending | Unclaimed | 0024 |
| [0026: Add independent agent capabilities and action guards](../tasks/pending/0026-goose-capability-guards.md) | A2 | Pending | Unclaimed | 0025 |
| [0027: Separate history ordering, revisions and read cursors](../tasks/pending/0027-goose-history-cursor-contract.md) | A3 | Pending | Unclaimed | 0026 |
| [0028: Discover interactive Goose and resolve its storage roots](../tasks/pending/0028-goose-process-discovery.md) | B1 | Pending | Unclaimed | 0026 |
| [0029: Read the Goose session store safely](../tasks/pending/0029-goose-readonly-session-store.md) | B2 | Pending | Unclaimed | 0027, 0028 |
| [0030: Project Goose chat history and inline activity](../tasks/pending/0030-goose-history-activity-projection.md) | B3 | Pending | Unclaimed | 0029 |
| [0031: Present honest Goose observation, cards and read state](../tasks/pending/0031-goose-observation-ui.md) | B4-observation | Pending | Unclaimed | 0030, 0028 |
| [0032: Enable reviewed Close agent for Goose](../tasks/pending/0032-goose-close-agent.md) | B4-close | Pending | Unclaimed | 0031 |
| [0033: Decide the native runtime evidence contract](../tasks/pending/0033-goose-native-proof-contract.md) | C1 | Pending | Unclaimed | 0024 |
| [0034: Build synthetic native-runtime evidence contract tests](../tasks/pending/0034-goose-runtime-proof-fixtures.md) | C2 | Pending | Unclaimed | 0033, 0026 |
| [0035: Validate an authorized native runtime evidence producer](../tasks/blocked/0035-goose-native-runtime-integration.md) | C3 | Blocked | Unclaimed | 0034 |
| [0036: Build provider-specific Goose launch arguments](../tasks/pending/0036-goose-launch-arguments.md) | D1 | Pending | Unclaimed | 0025 |
| [0037: Launch new Goose processes with durable recovery](../tasks/pending/0037-goose-new-launch-recovery.md) | D2 | Pending | Unclaimed | 0036, 0031 |
| [0038: Add fresh Goose launches from Board tickets](../tasks/pending/0038-goose-board-launch.md) | D4-fresh-Board | Pending | Unclaimed | 0037 |
| [0039: Resume only an exact unowned Goose conversation](../tasks/pending/0039-goose-exact-resume.md) | D3 | Pending | Unclaimed | 0035, 0037 |
| [0040: Restart a reviewed Goose pane into its current session](../tasks/pending/0040-goose-exact-restart.md) | D4-restart | Pending | Unclaimed | 0039 |
| [0041: Validate native Goose editor and ordinary input policy](../tasks/pending/0041-goose-chat-input-policy.md) | E1 | Pending | Unclaimed | 0035, 0031 |
| [0042: Add versioned native-input acceptance receipts](../tasks/pending/0042-goose-acceptance-receipts.md) | E2 | Pending | Unclaimed | 0034, 0027 |
| [0043: Enable guarded Goose messages and FIFO delivery](../tasks/pending/0043-goose-guarded-outbox.md) | E3 | Pending | Unclaimed | 0035, 0041, 0042, 0037 |
| [0044: Complete Goose chat feedback, attention and notifications](../tasks/pending/0044-goose-chat-attention-feedback.md) | E4 | Pending | Unclaimed | 0043, 0031 |
| [0045: Specify native Goose approval arbitration](../tasks/pending/0045-goose-approval-contract.md) | F1-design | Pending | Unclaimed | 0033 |
| [0046: Implement durable guarded Goose approval choices](../tasks/blocked/0046-goose-guarded-approvals.md) | F2-F3 | Blocked | Unclaimed | 0045, 0035, 0026 |
| [0047: Resolve Goose background-task evidence parity](../tasks/pending/0047-goose-background-task-evidence.md) | Union-background | Pending | Unclaimed | 0033 |
| [0048: Qualify the limited Goose observation milestone](../tasks/pending/0048-goose-observation-qualification.md) | G-observation | Pending | Unclaimed | 0032 |
| [0049: Qualify complete Goose agent parity](../tasks/pending/0049-goose-full-parity-qualification.md) | G-full | Pending | Unclaimed | 0048, 0035, 0038, 0039, 0040, 0043, 0044, 0046, 0047 |

Numbers identify tasks, not execution order. The graph permits independent work only after scope approval and file ownership coordination. Many records touch the same helper/Rust/UI files; **do not run simultaneous writers to the same files**. Split/sequence ownership explicitly before delegation. Before allocating any follow-up, rescan all state directories for the next unique ID; do not infer the next number from an old handoff.

### Dependency and decision gates

- **Observation path:** 0024 → 0025 → 0026; cursor contract 0027 and discovery 0028 → reader 0029 → projection 0030 → observation UI 0031 → Close 0032 → observation qualification 0048. State/read/reset and bounded query behavior are tested in these tasks, not deferred to final parity.
- **Native proof path:** accepted design 0033 → synthetic contract 0034 → actual native integration 0035. Scope approval in 0024/ADR-0002 is separate. Synthetic success cannot release actual native gates. 0035 remains blocked until a named producer, accepted contract and authorization exist.
- **Fresh process launches:** argv 0036 + observation/capability prerequisites → new launch/recovery 0037 → fresh Board 0038. These can be explicitly approved as limited process launches without native session linkage. They must not guess the newest conversation.
- **Exact lifecycle:** actual native proof 0035 + launch foundations → exact/ownership-safe resume 0039 → same-pane restart 0040. An inability to exclude concurrent ownership is a rejection, not permission to resume.
- **Messaging:** actual proof 0035 → native editor policy 0041; synthetic contract 0034 + cursor foundation 0027 → additive receipts 0042; all native/input/receipt prerequisites → guarded delivery 0043 → feedback 0044. A display cursor is never an acceptance proof.
- **Approval:** detailed decision design 0045 + actual native proof → guarded implementation 0046, blocked until the real terminal-coordinated channel is supplied/authorized. Approval-design completion does not mean approval support exists.
- **Background/full qualification:** evidence/disposition 0047 remains an explicit union-parity requirement. A decision to defer or label unavailable must retain an unmet criterion/linked follow-up. 0049 cannot complete full parity while any required capability or mandatory evidence remains missing.

[ADR-0002](../decisions/0002-goose-integration-direction.md) owns the direction/authorization register. Detailed runtime and approval contracts must receive newly allocated ADRs during 0033/0045, with explicit Proposed/Accepted status and actual decision authority; neither contract is invented or accepted by this package. If ACP is selected, explicitly replan native tasks/milestones rather than silently counting them as equivalent work. If a scope is deferred, record its blocked dependencies/reopening trigger; completed decision tasks do not satisfy withheld implementation authorization.

### Claim, pause, resume and complete

1. **Orient:** read `AGENTS.md`, `PLAN.md`, this checkpoint, the latest handoff, the target task and its prerequisite evidence/accepted ADRs. Inspect `git status --short`, branch/commit and actual diff; do not reset another agent's changes. Use pinned source links below to reconstruct research if temporary checkouts/caches are absent. Temporary paths are not handoff dependencies.
2. **Claim:** only after eligibility is established, move the task from pending/blocked to current using its existing filename. Record owner and claim date. Respect another owner's claim; on a real handoff record ownership transfer and the preserved checkpoint, not a silent takeover. Update all inbound links, tracker and root active-work index. Do not claim downstream work just because its task number is next.
3. **Work in checkpoints:** check an acceptance box only with linked actual evidence. Record affected files/commit or uncommitted state, decisions/bugs, new fixture names, exact commands/environment/exit status/counts and remaining limits in the task. Existing test entry points are not proof the new cases were added or ran. Keep changes small and runnable.
4. **Pause:** leave the task current with an explicit resumable ownership handoff if merely stopping between sessions; move to blocked only for a concrete unmet dependency with an owner/action. Update its last completed checkpoint, remaining work/failure, working-tree/commit state, actual checks and **one precise next action**. Add a distinct dated note under `docs/notes/`, link it from the root and this checkpoint, and update the summary table. If a durable handoff requires committing/pushing, do so only when authorized; otherwise disclose uncommitted/untracked files so the user can transfer them.
5. **Resume:** confirm state/owner/authorization and compare the actual tree to the recorded checkpoint. Continue from its exact next action; do not blindly redo or re-verify completed checkpoints. Run checks needed for new changes, missing evidence or stale artifacts. Missing private runtime evidence is not recoverable by reading unrelated logs.
6. **Complete:** verify every criterion with fresh relevant evidence and report unavailable checks honestly. Move the task to done only when its own scope is met; preserve filename, repair inbound links and update table/root/handoff. A completed investigation, approved design, process launch or observation milestone is not full feature completion. Qualifiers 0048/0049 update milestone status only against their complete acceptance evidence.

Each execution task starts with empty findings and **Not run** validation evidence. The prior research's 70-test baseline belongs to task 0022 and must not be copied as a new task pass. No task metadata or completion changes live Board tickets, installs hooks or authorizes messages/approvals/launches/deployment.

## 1. Conclusion and scope

Goose support is feasible, but **full native-CLI parity is not a provider-name addition**. Command Center (CC) needs a new native history adapter, provider-specific launch/input handling, and storage-independent history/receipt contracts. More importantly, the inspected stock Goose releases do not expose the externally verifiable current-session, settled-state and approval interfaces needed to reproduce CC's guarded behavior without weakening it.

A CC-only first slice can discover native interactive Goose processes, show cards and independently selected project history/activity, retain card preferences, and reuse explicit process-verified Close agent. It must honestly show Unknown when live state is unverified. It is not full parity: deferred delivery, native-input acceptance confirmation, approval buttons and exact-current-session restart need additional evidence/capabilities.

**Recommended direction:** preserve native tmux agents, implement bounded read-only observation first, and agree a native Goose runtime-observation/decision contract before enabling the guarded actions. An explicitly authorized bridge can help, but existing hooks alone do not provide all missing semantics. A CC-owned ACP runtime is an alternative architecture, not a transparent attachment to an existing CLI.

This plan covers the union of existing Claude/Codex features, including shared Agents/Board/Outbox behavior. Claude-only background-task observation is listed separately; Codex does not already have it. It does not authorize implementation, upstream changes, bridge installation, permissions changes, network exposure, live sends, or launching/restarting work agents.

## 2. Research baseline and limits

| Component | Inspected baseline | Qualification |
|---|---|---|
| Command Center | `188b7ce2e20bb14a56a514a80e78c20850017787` | Working tree was clean before the research ledger was created. |
| Goose latest GitHub release | [v1.57.0](https://github.com/aaif-goose/goose/releases/tag/v1.57.0), commit `30bba95105e59bc3e7df624cf6b4d433690cfe12` | Release API reported publication on 2026-10-28; native storage schema 17. |
| Locally installed Goose | Version output `1.55.0`; help inspected without starting a session | Compared against [v1.55.0 source](https://github.com/aaif-goose/goose/tree/2bcb8583a18a0623eb78c9ed845d597ed99fae48). Version string does not prove binary provenance. Schema 17 in tag source. |
| Goose upstream main | `4facf56cbab049142809d9afa4648ebe6823ba80`, workspace version 1.58.0 | Schema 18; not treated as a released compatibility baseline. |
| Official documentation | Mapped pages fetched from the official documentation site | Current/unversioned; source tags determine historical behavior. |

Independent investigations covered CC integration contracts, Goose history/launch behavior, lifecycle/approval security, release differences, and an architectural challenge for overlooked interfaces. Source was cloned/extracted outside CC. No private transcripts, credentials, user configuration or live Board contents were needed. The reference `checkouts/` projects are absent in this working copy.

All negative findings below mean **not found in the inspected native CLI, storage, hook and runtime paths at these revisions**, not a universal claim about future versions or third-party extensions. Source inspection is not runtime interoperability certification.

### Release differences that matter

- v1.55.0 and v1.57.0 both use shared SQLite, non-UUID session IDs, mutable histories, same-process session switching and the incompatible native approval menu described below.
- v1.55.0 has no inspected OSC 7501 program-status reporter. v1.57.0 and inspected main have it; upgrading to v1.57.0 does **not** supply verified Ready or current-session ownership.
- Both releases have schema 17. Main's schema 18 adds session tags; do not assume every 1.55/1.57 installation has main's schema or internal APIs.
- v1.57.0/main have an internal caller-supplied session-ID creation method. The public CLI still requires resume when a session ID is supplied; it is not a public new-session identity feature.

Evidence: [U1–U9](#10-source-evidence-index), [official storage/CLI/environment docs](#11-verification-completed-and-official-documentation).

## 3. Feature-parity matrix

“CC-only” means implementable without modifying Goose, not already implemented or behaviorally validated.

| Capability | Existing CC contract | Goose gap and required work | Delivery boundary |
|---|---|---|---|
| Process discovery | Kernel-proven foreground CLI, tty/stdin, ancestry, start identity; bounded wrapper resolution | Recognize exact Goose CLI and interactive invocation, not arbitrary substrings, config commands, ACP/serve or headless jobs. Outer Goose must win over delegated Claude/Codex children. | CC-only. |
| Cards, filters, pin/color/name/notes | Stable endpoint/tmux/process scope; revision-checked private metadata | Add provider labels/options without changing existing instance hashes. Reuse metadata and disconnected/removed-target handling. | CC-only. |
| Current conversation association | Registry, owned writer lock, open per-session log or equivalent process proof; project-history labels otherwise | Shared DB handles do not identify a session. Startup resume arguments become stale after same-process session switching. Need current-session evidence. | Native integration dependency. |
| Conversation picker/history | Bounded native history, stable identity, paging/version/reset; safe text | Implement read-only SQLite projection and provider-native IDs. Keep project history explicitly unverified unless linked independently. | CC-only browsing. |
| Inline tool/activity feed | Stable call/result identity; collapsed literal output; not assistant replies | Decode Goose content/audience/visibility, pair call occurrences, hide internal and opaque fields, handle mutable rows. Persisted activity is not token streaming. | CC-only persisted observation. |
| Working/Ready/blocked | Process-linked source and timestamps, freshness, parent-turn isolation | No inspected fresh external native-CLI registry. OSC/status hooks/persisted completion are insufficient dispatch authority. | Native integration dependency. |
| Explicit ordinary messages | One-use process/screen/endpoint grants, no uncertain replay, literal guarded input | Validate native editor/paste/dialog behavior and command-like input policy. Enforce capabilities on APIs, not just disabled buttons. | Gate on proven safe native input state. |
| Deferred FIFO Outbox | Durable human intent before IO; verified Ready; fresh action-time guard | Add Goose Ready source only after proof exists, in both Rust and Python. No Ready inference from DB/terminal silence. | Native integration dependency. |
| Submitted vs Seen | Exact one-use native user-input evidence after a pre-send baseline in the same proven session | Current byte-offset receipt baseline does not apply to mutable SQLite. Need a versioned acceptance proof, not synthetic row offsets. | Cross-layer work plus native provenance. |
| Tool approvals | Original request and exact option/scope; prompt generation, one-use durable claim; one verified key, no Enter | Goose uses cursor navigation and Enter; identical requests lack a displayed unique request ID. Need request-correlated external decision arbitration or a separately approved safety contract. | Terminal-only initially. |
| New launch / model / initial prompt | Reviewed executable/directory/model, detached target, durable one-use recovery, literal prompt once | Different CLI argument shapes; no public new-session ID flag. Generic launch recovery can prove the process, not guess its new DB conversation. | CC-only process launch possible; association gated. |
| Resume | Explicit selected session, same endpoint/store, reject already running | Non-UUID IDs; names/latest are unsafe selectors. Cannot reliably exclude active native owners without current-session evidence. | Do not enable unproven concurrent resume. |
| Restart | Replace only reviewed pane; exact current native session; durable receipt; verify replacement before preference transfer | Native exact resume exists, but current-session and exclusive-ownership proof are missing. Preserve saved provider/model behavior and normal prompts. | Gate on native session proof. |
| Close agent | Full kill-window consequence preview; exact process/topology; no retry | Mostly reusable after discovery/action revalidation; does not require native session linkage. | CC-only, destructive fixture tests only. |
| Board launches | Reviewed literal ticket prompt/model/names, atomic receipt/ticket claim, original process association | Extend provider selection and launch command builder; retain process-vs-conversation distinction and lost-response recovery. | Same launch/association gates. |
| Attention/read state/notifications | Exact reply/event revisions, baseline old history, no tool-only unread; opt-in privacy-preserving notifications | Separate mutable history revision from newly observed assistant reply; do not turn heartbeats or replayed rows into completion/unread events. | Browsing reusable; completion needs proven lifecycle. |
| Phone / desktop | Compact clients never attach/resize terminals; drafts and navigation survive | Same UI and HTTP-only guarded actions. Unavailable approval/restart must not secretly fall back to a mobile viewer. | CC-only invariant. |
| Background tasks | Claude-only structured task launch/outcome evidence, independent of parent Ready | Research Goose delegate/background provenance separately. A tool result can describe a child result without proving parent phase or a complete live task inventory. | Explicitly unavailable until demonstrated. |

## 4. Native Goose findings

### 4.1 Shared storage changes the history boundary

Goose stores sessions in `sessions/sessions.db` under its resolved data directory. The documented common Unix location is not a portable substitute for the actual platform/environment rules. An absolute `GOOSE_PATH_ROOT` changes the roots; resolve the running process's selected nonsecret path environment on the correct machine/account, including relevant platform/XDG paths. Preserve the provider root on CC launches/restarts without copying credentials. [U1, U2; D1, D3]

Sessions and messages share one WAL database. The inspected message columns include integer row `id`, nullable/nonunique `message_id`, `session_id`, `role`, `content_json`, `created_timestamp`, and `metadata_json`. Native load order is **created timestamp, then row ID**, not simply row ID. Session IDs normally resemble `YYYYMMDD_<count>`, not UUIDs. Main/internal custom-ID support has its own bounded grammar. Keep native IDs distinct from CC action UUIDs and opaque history IDs. [U1]

The history adapter must:

1. Open an existing validated database read-only, with query-only mode, parameterized known queries, supported-schema/column checks, short busy/query deadlines, a progress handler and bounded row/text/output budgets. Keep SQLite extension loading disabled; consider disabling trusted-schema behavior where supported. Do not invoke Goose's SessionManager or a session CLI as a read helper: native storage initialization can create, import, chmod and migrate.
2. Read live WAL correctly. Do not set immutable mode on a live DB, copy only its main file, or checkpoint it. Ordinary read-only SQLite may require existing readable WAL/SHM coordination; if safe access is unavailable, report unavailable rather than fixing permissions or changing journal mode. Recheck store/connection identity after IO and reject replacements.
3. Query only a whitelist of fields. Never return arbitrary recipe/configuration/extension/system-prompt columns, raw environments or credentials. Scope caches to machine endpoint + canonical store + native session, not session ID alone. Keep message content bounded in memory rather than copying the store into CC.
4. Treat missing/unknown/corrupt schema and malformed JSON as unavailable or explicitly omitted, not empty success. Exclude non-user/hidden/background session types from ordinary project candidates unless an explicitly proven target requires separately supported handling.
5. Bound worst-case work on the shared store. SQL LIMIT alone does not bound a sort/table scan or huge JSON cell. Measure query plans and exercise large/malformed stores; do not add indexes or schema changes to the provider DB to solve performance.

Goose history is mutable. Clear/edit can delete and reinsert all rows; truncation deletes suffixes; visibility/tool metadata can change in place. Some mutations do not advance session `updated_at`. Neither DB mtime, row count, last row ID, nullable message ID nor session time is a sufficient conversation revision. [U1, U3]

Use opaque, versioned display cursors and explicit ordering keys. For the bounded loaded window, fingerprint the normalized source rows/visibility and invalidate stale pages on any detected replacement/deletion/edit. A bounded fingerprint cannot prove an unobserved whole-history generation: if continuity cannot be established, reset/reload or report a limit rather than claiming append-only continuity. Keep revision/reset semantics separate from reply-read cursors and from outbox acceptance.

### 4.2 Visible chat is not every user/assistant row

There are only user and assistant roles in the inspected store. Tool responses are also stored as user-role messages. Apply both message-level `userVisible` and content-level audience filtering; do not mistake `agentVisible` for human visibility. Compaction preserves old user-visible history while adding hidden model-context records/replays. [U3; D4]

Normalize typed blocks rather than flattening JSON:

- Human chat: supported visible text, preserving source order. Exclude tool-only batches, control/confirmation blocks, system notifications, turn-context/compaction summaries, hidden replays and unsupported internals. A user role alone cannot establish native human-input provenance.
- Activity: visible `toolRequest`/`toolResponse`, scoped by call ID **and occurrence**. Duplicate message/call IDs are possible; include row/block occurrence identities. Handle status/value/error wrappers, legacy result arrays and tool-level `isError`. No result means Awaiting result, not execution success.
- Provider-exported visible thinking text can use the existing collapsed activity presentation. Never expose signatures, redacted/opaque data or arbitrary provider metadata; never attempt decryption. This is provider-visible exported content, not access to hidden reasoning.
- Images/documents/resources get bounded placeholders unless separately supported; no remote image loading or automatic file/resource dereferences. Do not read tool-output spill paths to reconstruct results.

Stable message/activity IDs, source ordering and resets must survive polling without losing disclosures, keyboard focus, scroll or drafts. Tool-result/metadata updates must not advance assistant reply cursors. [U3; D5]

### 4.3 Current-session proof is missing for stock native observation

The kernel can prove which foreground Goose CLI owns a pane, but a shared database open descriptor/SQLite lock cannot prove its current session. Native session runtime and active-run registries inspected here are process-local maps, not external ownership records. [U4]

Explicit resume argv identifies the startup target, but Goose's in-session new-conversation action changes `self.session_id` without changing PID/start identity or argv. Therefore startup arguments alone must not authorize continued association, restart, Ready delivery or receipt matching. A sole/newest project session, banner, window title or cwd is not a repair. [U5]

`AGENT_SESSION_ID` is documented for extension/shell children, not a reliable native parent CLI registry. Shell integration can introduce an inherited ID belonging to a separate terminal session. A verified owned extension child might improve evidence, but stale leases/background children/session switching require testing; its liveness is not Ready. [U2, U4; D3]

For newly CC-launched Goose, retain the CC launch UUID/endpoint/window receipt and prove the resulting process. Do not automatically associate the newest saved session. A launch can be observed as process-started while conversation linkage is explicitly unavailable.

### 4.4 Lifecycle telemetry is not authorization

v1.57.0/main emit terminal OSC 7501 states including idle, working, done, error and blocked permission/question. Their payload lacks session ID, process-start/boot identity, sequence and timestamp. Tool/terminal output is untrusted; cold observation, missed output and tmux passthrough are unresolved. v1.55.0 lacks this reporter. Treat it, if surfaced at all, as a labeled hint, not verified provider Ready. [U6]

The older status-command hook reports waiting/thinking asynchronously. Waiting is emitted near the input read, but callbacks lack an authoritative session binding, sequence and heartbeat and can finish out of order. It is not a ready-made verified bridge. [U6]

Lifecycle plugins expose session/start/end, prompt/tool events and Stop. Stop is vetoable: another hook can make inference continue, and non-normal exits need not traverse it. It is not an after-settled signal. Payloads do not carry PID/start/boot/heartbeat evidence and can contain sensitive message/tool content. Session changes and child events complicate correlation. Do not install a plugin silently or map a Stop callback to Ready. [U7; D6]

### 4.5 Native input and approvals need separate handling

The ordinary CLI input layer uses rustyline and bracketed paste, trims text and interprets special inputs such as exit/quit and slash commands. Ctrl+C can cancel work, clear a line or eventually exit at idle; it is not a safe implicit “clear before send.” Multiline/Unicode/large paste behavior must be fixture-tested in actual tmux before enabling HTTP message submission. Bind a native chat-input capability to a fresh prompt/session epoch; command-like text needs an explicit reject/disclosure policy, not a promise that every string is literal chat. [U5]

The normal approval menu offers Allow, Always Allow, Deny and Cancel. A provider/security-notice variant omits Always Allow. The locked cliclack selection widget navigates with arrows or h/j/k/l and submits with Enter; it does not expose CC's existing numbered/lettered one-key approval contract. The initially selected option is Allow. The displayed request omits the internal request ID, so repeated identical requests can have identical screens. Always Allow updates broader tool permission metadata, not just this argument invocation. [U8; D7]

**Do not send guessed numbers, y/n, arrows-plus-Enter or an optimistic Enter.** Initial Goose approval/elicitation handling should remain terminal-only, with an honest attention label and ordinary messages/Outbox dispatch blocked. Full approval parity needs a fresh request-generation/choice interface shared with the native terminal, or an explicitly approved redesign with equivalent safety evidence. Arbitrary elicitation dialogs must not become approval capabilities.

### 4.6 Launch/resume/restart argument contracts differ

This is an implementation contract to verify in fixture argv tests, not operator setup instructions. Public CLI fields were checked in both release sources and local help. [U9; D2]

| CC intent | Goose argument shape to implement |
|---|---|
| New interactive, no initial prompt | Session subcommand; no user-prompt positional argument. |
| New interactive with reviewed initial prompt | Run subcommand, interactive flag and literal text option. The current shared positional-after-`--` builder is wrong for Goose. |
| Exact resume / restart | Session subcommand, resume flag and exact session-ID option in the same validated store. Never latest/name selection, fork, edit or import. |
| Optional model | Native model option; omit when blank. Preserve native provider configuration unless a separately reviewed provider override is introduced. |

A system-instruction option is not an initial user prompt. Stdin instruction input reads to EOF and must not consume the interactive PTY. Literal option values starting with hyphens need an unambiguous argument representation and parser fixture coverage. Keep CC's 24,000-byte prompt limit, private large-argv handoff, pre-IO receipt and uncertain-launch no-retry rules.

The public session-ID option requires resume; the launch UUID cannot simply become a chosen new Goose session ID. Resume may prompt about cwd differences and may have native provider/model fallback or provider-managed-context restrictions. Start from the reviewed directory, disclose normal setup/trust prompts, never answer them automatically, and test that blank overrides preserve intended native defaults. Do not promise exact effective model preservation without verification. Session IDs of a nested provider are not outer Goose IDs. [U9]

Goose's no-session option is not a safe workaround: inspected code creates a persisted hidden session. Do not advertise it as no-persistence or use it to avoid association work. [U9]

## 5. Required CC architecture changes

### 5.1 Explicit provider dispatch and capabilities

`src/agent_remote.py` has many codex/pi/else-Claude branches. Adding Goose to discovery alone would let it fall into Claude home/history/launch paths. Introduce explicit dispatch for the small supported provider set, with unsupported providers failing closed. Keep this a local adapter/capability boundary, not a plugin framework.

Expose separate backend capabilities with reasons: process observation, project history, current-session linkage, verified phase, ordinary message submission, acceptance confirmation, native approval, launch, resume and restart. Enforce them in HTTP handlers **and** helper action-time revalidation. A provider label, selected history or browser button state never grants authority.

### 5.2 Storage-independent display and attention protocol

Separate display IDs, sort keys, paging cursors, history revisions, reply cursors and acceptance positions. Current Python/Rust/TS interfaces conflate these with file byte offsets and file metadata. Goose must not fake a transcript path or byte size for a DB session.

Retain the existing provider API compatibility where practical, adding explicit versioned cursor/order fields for Goose. Do not pass unbounded SQLite integer IDs through JavaScript numbers or parse opaque message IDs with `Number(...)`. Unknown fields/providers must fail closed, not reinterpret as a legacy offset.

`attention.rs` currently compares `(mtime_ns, position)`. Add provider-appropriate observed reply revision semantics so WAL/tool changes, session edits, old-row reinsertion or heartbeat refresh cannot manufacture unread assistant replies/completion. Baseline old history once, acknowledge the exact observed event/cursor, and preserve newer events across stale acknowledgements. If a reset cannot distinguish a fresh reply from a replay, show the reset honestly and do not invent attention.

### 5.3 Versioned durable acceptance proof

Current Outbox records use conversation/device/inode/file-size baselines and post-baseline byte positions. A naive Goose row-ID baseline is unsafe: replacing history can insert the **same old text** after the recorded high-water row ID. Tool-result user rows and native edit/import add further ambiguity.

Proposed additive contract, **not an existing Goose API**:

- Preserve legacy JSON receipt fields/semantics for existing providers. Add an optional tagged acceptance-proof version for Goose; keep CC action UUIDs/digests/status/revision and archived ambiguity unchanged.
- Bind the proof to endpoint, verified process/start/boot, runtime nonce, current session plus session epoch, and canonical store identity/generation. Record the baseline before delivery.
- Require a later provider-origin native-input acceptance event, with monotonic sequence, native message identity and versioned full normalized input digest. Emit at the actual human-input persistence boundary, not arbitrary user-role row insertion. Replays/compaction/import/edits must not mint acceptance events. Match each event once.
- A read-only DB display cursor alone is not such proof. Until provenance exists, do not claim Seen in conversation; retain Submitted/Uncertain appropriately. Never retrofit an anchor onto legacy unconfirmed receipts or retry an uncertain submission.
- Keep Submitting-to-Uncertain crash recovery and exact bulk cancellation/archive snapshots. Old providers must remain readable without a forced semantic migration. If physical CC schema migration is required, back up the private database and verify permissions/migration/restart first; never auto-restore receipt backups.

### 5.4 Files and contracts to change

| Area | Files / key symbols |
|---|---|
| Native adapter | `src/agent_remote.py`: `process_kind`, `foreground_agent`, `discover_agents`, `observe`, `provider_home`, `conversations`, `metadata`, `provider_activity`, `history`, `history_activities`, `transcript_version`, `reply_observation`, `native_input_hash`, `_outbox_observation` result construction, `execute`. A focused Goose module is possible only if embedded helper packaging is updated too. |
| Transport/packaging | `src/transport.rs`: retain one bounded local/SSH/ProxyJump helper request, no remote daemon. If splitting Python, include all helper source explicitly; remote imports must not depend on a nonexistent installation. |
| Queue and grants | `src/queue.rs`: provider allowlists/fallbacks, `Activity::from_value`, prompt precedence/labels; `src/agents.rs`: detail/message/approval capability checks and one-use grants. Do not generalize the existing pi-specific terminal-prompt exception blindly. |
| Outbox / attention | `src/outbox.rs`: `Record`, legacy `Log`, `matching_receipt`, `confirm_observed`, `process`, manual submission and history receipt observation; `src/attention.rs`: reply ordering/reset and exact read acknowledgements. Ready source allowlist and helper `require_ready` must agree. |
| Launch and restart | Adapter `launch_executable`, `launch_candidates`, `launch_options`, `active_launch_sessions`, `launch_agent`, `launch_status`, `restart_plan`, `restart_agent`, `restart_status`; `src/launch.rs`, `src/agent_restart.rs`. Native IDs need provider-specific validation instead of unconditional UUID checks. |
| Shared lifecycle | `src/board.rs`, `src/agent_cards.rs`, `src/tmux_management.rs`: reuse durable ticket claims, once-only metadata initialization/transfer, exact original-process checks and close previews. Audit provider/conversation assumptions. |
| Web | `web/src/queue.ts`: provider title/phase labels, opaque cursor/order handling, detail capabilities, safe history reset; `agent-launch.ts`, `board.ts`: Goose selector and launch capabilities; `agent-outbox.ts`, `agent-restart.ts`, `agent-close.ts`, `agent-activity.ts`, `notifications.ts`: reasons, safe evidence labels and regression coverage. |
| Documentation | `docs/api.md`, `docs/reference/features.md`, `docs/testing.md`, and `AGENTS.md` only when behavior/contracts are actually established. This research plan is not a claim of shipped support. |

## 6. Missing native integration contract and alternatives

### Recommended native contract

Agree an upstream capability or an explicitly authorized CC integration with these properties. Field descriptions are proposed requirements, not valid current Goose configuration/schema.

1. **Live ownership snapshot:** private owner-validated record/socket, verified parent PID/start/boot and tty/pane, runtime nonce, canonical store, current native session and session epoch. Switch epoch synchronously on same-process session changes. Bind the CC endpoint externally; do not trust a record alone without fresh kernel/target revalidation.
2. **Authoritative lifecycle:** ordered events plus a fresh snapshot/heartbeat. Ready means the actual ordinary input editor is accepting chat after all stop-hook continuations and cleanup. Distinguish loading/working/approval/question/error/exit; child completion never sets parent Ready. Missing/reordered/future/stale evidence becomes Unknown. Heartbeats must not mint completion transitions.
3. **Acceptance provenance:** bounded metadata-only native-input acceptance events as described above, durably associated with the actual persisted input. No prompt/reply/tool-content transcript copy. Retention gaps fail closed. A bridge process being alive is not parent settled evidence.
4. **Optional decision channel:** live original request/arguments, exact offered option IDs/labels/scopes, a unique request generation and expiry, and atomic one-use arbitration shared with the native UI. Resolving externally must also release/invalidate its waiting menu, so another terminal client cannot answer a different request afterward. Persist CC's durable claim before decision IO; no automatic approval or uncertain replay.
5. **Operational boundaries:** explicit installation/enable consent, private bounded records, no additional exposed network listener, credential copying, policy changes or live-process reload/restart. Existing uninstrumented agents remain honestly limited.

Likely upstream implementation locations are native CLI session/input transitions, runtime/confirmation coordination and the message persistence boundary. Merely extending OSC with a session ID, or using current Stop/status hooks, does not satisfy this contract. A hooks-only experiment may establish some association/Working hints, but must not be presented as full parity.

### ACP alternative: useful, but a different product decision

Goose's documented ACP interface provides sessions, streaming updates and structured permission callbacks for an application-owned runtime. It does not attach to a separately running CLI's in-memory active run/confirmation state. Starting a second runtime against the same saved session is not passive observation. In particular, session load can activate providers/extensions and resume pending work. A read-oriented session-info method exists, but saved metadata still does not prove another CLI's live state. [U4, U10; D8]

If upstream native integration is undesirable, a separately approved CC-managed ACP design could provide new managed Goose agents. It would require ownership/lifetime persistence, reconnect semantics, structured permissions, prompt acceptance/idempotency, crash recovery, remote transport and a decision about native terminal handoff. Do not assume protocol request IDs make lost submissions safely retryable. This route would not deliver transparent parity for arbitrary existing native tmux agents and is outside the recommended first slice.

## 7. Proposed implementation phases and gates

The phase vocabulary below maps to the allocated [execution tasks](#execution-tracking-and-handoff); these are planned records, not claimed work or live Board tickets. Task files contain the checklists/evidence. Their creation does not authorize implementation. Keep changes small; allocate additional uniquely numbered tasks only for new work or a necessary split, preserving these references.

| Phase | Atomic steps | Exit gate / dependency |
|---|---|---|
| A. Provider/storage contract foundation (0025–0027) | A1 explicit fail-closed provider dispatch; A2 additive capabilities; A3 opaque history IDs/cursors/order and legacy compatibility fixtures. | Existing providers unchanged; no unsupported action reaches IO. |
| B. Useful native observation (0028–0032) | B1 exact interactive Goose classification and path environment; B2 read-only schema-17 history/picker; B3 visibility/activity/reset projection; B4 cards/labels/close and desktop/phone fixtures. Consider schema 18 only with its own compatibility fixture. | Uninstrumented Goose works as honest process/project observation; Unknown and unavailable capabilities remain visible. No writes to provider store or agent input. |
| C. Native proof spike (0033–0035) | C1 agree observation/settlement/acceptance contract; C2 synthetic reference producer/consumer; C3 explicit opt-in integration or upstream implementation, including session switches/child isolation. | Fresh current-session and actual Ready proof, measured bounds and no false authority. Blocks deferred delivery, exact restart/resume and full association. |
| D. Launch and exact lifecycle (0036–0040) | D1 provider argv builder/model/default/prompt tests; D2 detached new launch + per-window recovery; D3 exact resume/running checks; D4 Board prompts/names and same-pane restart/preferences verification. | New process launch can be delivered earlier as explicitly limited; exact session operations wait for C. No changed endpoint/session/process inheritance or uncertain relaunch. |
| E. Messaging and receipt parity (0041–0044) | E1 native editor/dialog/paste policy; E2 additive acceptance proof and legacy receipt persistence; E3 fresh dual-layer Ready gating/FIFO dispatch; E4 read/attention/notifications and pending bubbles. | Fixture-proven no duplicate input, false Seen, tool-only unread or action replay across restarts/session changes. C required for complete parity. |
| F. Approval parity (0045–0046) | F1 request-generation/choice capability; F2 durable cross-client claim and terminal UI arbitration; F3 provider notice/Always Allow scope/unsupported dialogs. | No cursor-navigation shortcut. Structured decision contract or separately accepted equivalent safety design required. Terminal-only until then. |
| G. Release qualification (0048–0049) | G1 supported-version matrix/docs; G2 local+SSH/ProxyJump fixtures, restart/multi-client/mobile; G3 measured query/scan budgets and device check. Assess Claude-only background-task equivalent separately. | Do not call full union parity while a listed capability remains unsupported; publish tested version/schema coverage and honest limits. |

Task 0047 separately resolves the Claude-only background-task evidence requirement; a documented unavailable/deferred result does not close full parity. Observation qualifier 0048 can finish independently of C/F; full qualifier 0049 cannot.

The critical path is **C (current session/settlement/provenance), not the Goose selector**. B is independently useful. D's guarded process launch is separable from native session linkage. No duration estimate is defensible before the C/F integration choice and native compatibility spike.

## 8. Verification plan

### Required synthetic coverage

- Discovery: direct and wrapped CLI; same-cwd multiple Goose agents; unrelated executable with similar name; foreground server/config/headless exclusion; redirected stdin/background groups; delegated Claude/Codex children; PID reuse/replacement; unchanged legacy direct instance hashes.
- Store: schema 17 fixtures from both release definitions; optional separately tested schema 18; wrong schema/columns, missing/corrupt DB, hostile long JSON, duplicate/null IDs, audience filtering and malformed metadata. WAL-only changes, concurrent readers/writers, busy timeout, symlink/replacement, root override/account boundaries, no initialization/migration/provider writes.
- Projection: native timestamp/tie ordering, visible text vs user-role tool results, repeated call IDs, legacy result wrappers, hidden summaries/replays, system/banner/internal exclusion, redacted/signature exclusion, overflow/XSS/file URLs. Edits/deletion/reinsertion reset loaded pages without fabricating replies or losing unrelated drafts.
- Native proof: startup/no-log, same-process new session, cleared history, stale child lease, delayed status-hook callback, Stop veto then more work, max-turn/error/cancel/exit, child completion, stale/future heartbeat/boot/process/endpoint. Negative cases must produce no send/restart authority.
- Messages/Outbox: multiline/Unicode/bracketed paste, leading hyphens, slash/exit-like input policy, copy-mode/dialog/busy editor, exact fresh process/screen/epoch, duplicate client UUID, identical text twice, history edit/import above baseline, one-use acceptance, queued-to-submitting persistence, lost response/restart, archive ambiguity and legacy unconfirmed receipts. Never use real work agents.
- Approvals: identical consecutive requests, option/cursor changes by another client, stale generation, clipped request, provider notice variant, persistent scope disclosure, external-vs-terminal arbitration, unsupported elicitation, claim-persistence failure and uncertain decisions. No automatic approval.
- Lifecycle/UI: explicit resume cannot race known active ownership; detached launch preserves other panes; exact lost-response status; Board ticket revision/prompt binding; restart replaces only fixture pane and transfers metadata once; Close shows linked-window consequences. Phone navigation/actions generate zero terminal viewer/input/resize traffic, with simultaneous desktop dimensions/processes unchanged.
- Performance: representative synthetic large shared store and noisy/slow/disconnected SSH host. Report scan/query rows/bytes/time, selected-chat poll load, switch/refresh latency and connection reuse. Establish measured budgets rather than treating LIMIT as proof of bounded work. Actual phone keyboard/landscape/touch remains a device check.

### Commands for future implementation validation

These are existing CC validation entry points, not assertions that Goose compatibility tests already exist. Add focused Goose fixture cases before running the affected suites. From repository root:

```sh
cargo fmt --check
cargo test
cargo clippy --all-targets -- -D warnings
cargo build --release
python3 -m unittest discover -s tests -p 'test_agent_*.py'
python3 -m unittest discover -s tests -p 'test_claude_continuation.py'
node tests/pi_bridge.mjs
npm --prefix web run build -- --outDir dist-next
CC_BINARY=../target/release/command-center CC_WEB_DIR=dist-next npm --prefix web test -- tests/agents.spec.ts tests/launch.spec.ts tests/restart.spec.ts tests/outbox.spec.ts tests/background.spec.ts
```

Browser/SSH prerequisites and fixture-only destructive testing remain governed by [testing.md](../testing.md). Also extend navigation/mobile coverage when changing shared routes/layout. No live tool approvals, work-agent launches or user-window closures are acceptable compatibility tests.

## 9. Actual research validation

- Fetched official map and relevant pages; pinned GitHub main, v1.57.0 and v1.55.0 source. Queried latest release metadata. Inspected local binary version and session/run help only; no session was started.
- Read relevant CC Python/Rust/TypeScript implementation, test definitions and feature contracts. Independently checked critical storage, approval, lifecycle and launch findings; release audit compared extracted critical files to tagged Git blobs.
- Existing Python regression baseline executed: detection 5, history 31, activity 5, outbox 6, restart 4, Claude continuation 12, background 7 — **70 tests passed**. History emitted ResourceWarnings about unclosed SQLite connections; no failure was reported. These existing tests do not establish Goose support.
- Temporary synthetic probe extracted the schema-17 session/message DDL and demonstrated WAL-aware read-only queries, write rejection, old-text reinsertion receiving a higher row ID, and content mutation retaining row/message IDs. The first probe failed because a rejected write left its reader transaction open; after explicit rollback the probe passed. This verifies SQLite mechanics, not a Goose runtime adapter or acceptance proof. No probe files or synthetic content were installed in CC/provider data.
- Research documentation receives `git diff --check` and relative-link/source-reference validation before handoff. No Rust/frontend runtime code changed; Rust/browser/native-provider integration tests were not run for this documentation-only task. No live SSH Goose interoperability, bridge, native menu/paste, ACP recovery, iPhone or upstream build tests were performed.

## 10. Source evidence index

CC paths in section 5 are repository-grounded touchpoints. Goose links below are immutable source; release references take precedence over main for compatibility. Ranges locate the relevant implementation, not a published stable external schema.

| Ref | Pinned source and relevant symbols |
|---|---|
| U1 | [v1.57 session manager](https://github.com/aaif-goose/goose/blob/30bba95105e59bc3e7df624cf6b4d433690cfe12/crates/goose/src/session/session_manager.rs): schema 17 (32–34), pool/bootstrap (1075–1160), table definitions (1164–1218), ID allocation (1781–1851), load order (2118), replacement (2201 onward), mutations (2870–2967). [v1.55 manager](https://github.com/aaif-goose/goose/blob/2bcb8583a18a0623eb78c9ed845d597ed99fae48/crates/goose/src/session/session_manager.rs) confirms schema 17 and equivalent core definitions. [Main manager](https://github.com/aaif-goose/goose/blob/4facf56cbab049142809d9afa4648ebe6823ba80/crates/goose/src/session/session_manager.rs): schema 18, session-tags migration, repeated-call metadata tests. |
| U2 | [v1.57 paths](https://github.com/aaif-goose/goose/blob/30bba95105e59bc3e7df624cf6b4d433690cfe12/crates/goose/src/config/paths.rs), `Paths::get_dir/path_root` (8–53); [main extension manager](https://github.com/aaif-goose/goose/blob/4facf56cbab049142809d9afa4648ebe6823ba80/crates/goose/src/agents/extension_manager/mod.rs) environment injection (949–965); [main terminal integration](https://github.com/aaif-goose/goose/blob/4facf56cbab049142809d9afa4648ebe6823ba80/crates/goose-cli/src/commands/term.rs), separate terminal session/load behavior. |
| U3 | [v1.57 message types](https://github.com/aaif-goose/goose/blob/30bba95105e59bc3e7df624cf6b4d433690cfe12/crates/goose-provider-types/src/conversation/message.rs): typed blocks (317–332), audience projection (383–467), metadata (829 onward), user-visible projection and serialization fixtures; [result serialization](https://github.com/aaif-goose/goose/blob/30bba95105e59bc3e7df624cf6b4d433690cfe12/crates/goose-provider-types/src/conversation/tool_result_serde.rs); [main compaction](https://github.com/aaif-goose/goose/blob/4facf56cbab049142809d9afa4648ebe6823ba80/crates/goose/src/context_mgmt/mod.rs), preservation/replay (183–237); [main tool recording](https://github.com/aaif-goose/goose/blob/4facf56cbab049142809d9afa4648ebe6823ba80/crates/goose/src/agents/state_machine/ops_toolcalling.rs), `ToolBatch::record` (153–165). |
| U4 | [Main session runtime](https://github.com/aaif-goose/goose/blob/4facf56cbab049142809d9afa4648ebe6823ba80/crates/goose/src/agents/session_runtime.rs), in-memory maps (21–44); [active-run registry](https://github.com/aaif-goose/goose/blob/4facf56cbab049142809d9afa4648ebe6823ba80/crates/goose/src/agents/active_run.rs); [service construction](https://github.com/aaif-goose/goose/blob/4facf56cbab049142809d9afa4648ebe6823ba80/crates/goose/src/agents/services.rs). Negative registry finding also checked across both release trees. |
| U5 | [v1.57 native session](https://github.com/aaif-goose/goose/blob/30bba95105e59bc3e7df624cf6b4d433690cfe12/crates/goose-cli/src/session/mod.rs), `handle_new` (1109–1199), same-PID session reassignment (1146); [native input](https://github.com/aaif-goose/goose/blob/30bba95105e59bc3e7df624cf6b4d433690cfe12/crates/goose-cli/src/session/input.rs), editor/trim/command dispatch; [main paste](https://github.com/aaif-goose/goose/blob/4facf56cbab049142809d9afa4648ebe6823ba80/crates/goose-cli/src/session/paste.rs). |
| U6 | [v1.57 program status](https://github.com/aaif-goose/goose/blob/30bba95105e59bc3e7df624cf6b4d433690cfe12/crates/goose-cli/src/session/program_status.rs) (1–99); [main output](https://github.com/aaif-goose/goose/blob/4facf56cbab049142809d9afa4648ebe6823ba80/crates/goose-cli/src/session/output.rs), `run_status_hook` (261–285). Reporter absence checked in v1.55 tree. |
| U7 | [v1.57 hooks](https://github.com/aaif-goose/goose/blob/30bba95105e59bc3e7df624cf6b4d433690cfe12/crates/goose/src/hooks/mod.rs), event/context/command execution; [v1.57 Stop operation](https://github.com/aaif-goose/goose/blob/30bba95105e59bc3e7df624cf6b4d433690cfe12/crates/goose/src/agents/state_machine/ops_stop_hook.rs) (80–122). [Main Stop operation](https://github.com/aaif-goose/goose/blob/4facf56cbab049142809d9afa4648ebe6823ba80/crates/goose-agent/src/stop_hook.rs) and lifecycle regression tests confirm veto/termination distinctions after refactoring. |
| U8 | [v1.57 native menu](https://github.com/aaif-goose/goose/blob/30bba95105e59bc3e7df624cf6b4d433690cfe12/crates/goose-cli/src/session/mod.rs), `prompt_tool_confirmation` (2262–2317); [main output](https://github.com/aaif-goose/goose/blob/4facf56cbab049142809d9afa4648ebe6823ba80/crates/goose-cli/src/session/output.rs), request formatting (678–711); [main approval operation](https://github.com/aaif-goose/goose/blob/4facf56cbab049142809d9afa4648ebe6823ba80/crates/goose/src/agents/state_machine/tool_approval.rs), persistent permission update. Locked cliclack 0.5.6 [published source archive](https://static.crates.io/crates/cliclack/cliclack-0.5.6.crate), `src/select.rs` (45–52, 131–152); archive SHA-256 checked against lockfile: `134778b6a125729ff495c23ba32f64e0c26d61edd52f1f6715a0d036785cf30b`. |
| U9 | [v1.57 CLI](https://github.com/aaif-goose/goose/blob/30bba95105e59bc3e7df624cf6b4d433690cfe12/crates/goose-cli/src/cli.rs), session identity/run/session definitions and handlers; [v1.55 CLI](https://github.com/aaif-goose/goose/blob/2bcb8583a18a0623eb78c9ed845d597ed99fae48/crates/goose-cli/src/cli.rs) equivalent public flags; [main builder](https://github.com/aaif-goose/goose/blob/4facf56cbab049142809d9afa4648ebe6823ba80/crates/goose-cli/src/session/builder.rs), saved model/provider resolution (289–434), hidden-session allocation (452–469), cwd resume (499–561), provider fallback (753–797). |
| U10 | [Main ACP server](https://github.com/aaif-goose/goose/blob/4facf56cbab049142809d9afa4648ebe6823ba80/crates/goose/src/acp/server.rs), own run/cancel and permission service; [load session](https://github.com/aaif-goose/goose/blob/4facf56cbab049142809d9afa4648ebe6823ba80/crates/goose/src/acp/server/load_session.rs), activation and resumed turn (367–451); [session metadata](https://github.com/aaif-goose/goose/blob/4facf56cbab049142809d9afa4648ebe6823ba80/crates/goose/src/acp/server/manage_sessions.rs), read-oriented session-info (152–175). |

Goose's inspected license is Apache-2.0, matching CC's license family. This research copied no upstream implementation into CC. Any future copied code must retain required attribution/notices and separately check dependencies.

## 11. Verification Completed and official documentation

Public Goose behavior and field/flag terminology were checked against these exact paths from the official documentation map. Internal schema, negative findings and version-dependent behavior are explicitly source-qualified above; proposed bridge fields are not claimed as current Goose schema. No operator configuration or new hook manifest is supplied.

| Ref | Official documentation actually read | Verified scope |
|---|---|---|
| D1 | [Logging system](https://goose-docs.ai/docs/guides/logs) | SQLite session storage, legacy JSONL migration, ID format and logs vs history. |
| D2 | [CLI commands](https://goose-docs.ai/docs/guides/goose-cli-commands), [Session management](https://goose-docs.ai/docs/guides/sessions/session-management), [Running tasks](https://goose-docs.ai/docs/guides/running-tasks) | Session/run, explicit resume, interactive text input, model/provider, export/edit/fork. Native source resolves implementation caveats. |
| D3 | [Environment variables](https://goose-docs.ai/docs/guides/environment-variables) | Path-root override and extension/shell-only session environment. |
| D4 | [Smart context management](https://goose-docs.ai/docs/guides/sessions/smart-context-management) | Visible history versus compacted model context. |
| D5 | [Providers: viewing model reasoning](https://goose-docs.ai/docs/getting-started/providers#viewing-model-reasoning), [In-session actions](https://goose-docs.ai/docs/guides/sessions/in-session-actions) | Exported thinking presentation and native interaction. Typed content/audience details are pinned-source findings. |
| D6 | [Hooks](https://goose-docs.ai/docs/guides/context-engineering/hooks) | Optional plugins, event payloads and blocking Stop semantics. No claim that hooks are installed or supply settled authority. |
| D7 | [Permission modes](https://goose-docs.ai/docs/guides/managing-tools/goose-permissions), [Tool permissions](https://goose-docs.ai/docs/guides/managing-tools/tool-permissions) | Mode/tool-permission scope; exact terminal choice keys are verified from source/dependency, not guessed from mode documentation. |
| D8 | [Build an app with Goose](https://goose-docs.ai/docs/gdk/acp/index), [ACP reference](https://goose-docs.ai/docs/gdk/acp/reference), [Remote Goose server](https://goose-docs.ai/docs/guides/remote-goose-server) | Application-owned runtime, updates/permissions and stored session-info; no native attach claim or additional server deployment recommended. |

### Next decision

Continue at [Task 0024](../tasks/pending/0024-goose-implementation-scope.md) and record the actual direction/scope in [ADR-0002](../decisions/0002-goose-integration-direction.md). The recommendation remains limited native observation first with separately gated native/approval integration; it is not yet accepted. If the intended target is CC-owned ACP agents, explicitly replan that architectural scope before implementation. Do not label partial observation, design completion or a second runtime as full existing-native-agent parity.
