# 2026-11-06: Goose agent parity investigation

Completed research [Task 0022](../tasks/done/0022-goose-agent-parity-research.md); deliverable is proposed [Plan 0002](../plans/0002-goose-agent-parity.md). No runtime changes or Goose support shipped.

Compared CC's complete Claude/Codex capability surface with pinned Goose v1.55.0, latest release v1.57.0 and main (workspace 1.58.0). Release schemas are 17; main is 18. Installed version/help reports 1.55.0 without proving its build provenance. Official documentation and immutable source references are in the plan.

The substantive gaps are mutable shared SQLite history, non-UUID session identities, missing externally proven current-session/settled evidence, durable native-input acceptance provenance and native cursor+Enter approval arbitration. Startup resume argv becomes stale after a same-process session change. OSC/status hooks and vetoable Stop do not provide verified Ready. A separate ACP runtime cannot transparently control an existing native CLI.

Recommend native observation first, with honest project-history/Unknown labels and action capability gates. Full parity requires an agreed native integration contract or an explicitly different CC-managed ACP architecture. No decision, upstream patch, opt-in install or implementation is implicitly approved.

Validation: 70 existing Python provider tests passed; history emitted SQLite ResourceWarnings. Temporary schema-17 WAL/read-only/mutation probe passed after correcting a reader-transaction rollback in the probe. Locked approval-widget dependency checksum/source checked. Independent plan review found no actionable issues. Documentation whitespace/relative-link and pinned upstream source-reference checks passed. Runtime source unchanged. No live agent/input/configuration/deployment actions, Rust/browser/native SSH interoperability tests or device checks performed. See task/plan for evidence and limits.

Next: obtain the user's integration-scope decision, then allocate implementation tasks for the phased plan. Preserve legacy receipt semantics and all existing provider safety contracts.
