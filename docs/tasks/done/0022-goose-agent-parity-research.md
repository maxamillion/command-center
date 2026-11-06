# Task 0022: Goose agent feature-parity investigation

- State: Done
- Owner: goose research coordinator
- Claimed: 2026-11-06
- Scope: Research and documentation only; no agent launches, input, hook installation, runtime changes or deployment.

## Acceptance criteria

- Inventory current Claude/Codex/pi Agent capabilities and their identity/safety contracts.
- Pin and inspect AAIF Goose upstream source and official documentation.
- Map Goose native process/session/history/activity/approval/launch/restart behavior to CC parity requirements, identifying unsupported or unproven cases.
- Deliver a file-level phased plan with security invariants, tests and explicit unknowns.
- Record actual research validation and leave an indexed handoff.

## Findings and evidence

Deliverable: [Plan 0002: Goose agent parity](../../plans/0002-goose-agent-parity.md).

All research acceptance criteria are met. Implementation is not started or authorized by this record.

- Inspected CC commit `188b7ce2e20bb14a56a514a80e78c20850017787`, relevant provider/Rust/UI code, API/feature documentation and fixture definitions.
- Pinned Goose main `4facf56cbab049142809d9afa4648ebe6823ba80` (workspace 1.58.0/schema 18), latest release v1.57.0 `30bba95105e59bc3e7df624cf6b4d433690cfe12` and v1.55.0 `2bcb8583a18a0623eb78c9ed845d597ed99fae48` (both schema 17). GitHub latest-release API and local version/help were checked. Local version is 1.55.0; tag source is not proof of binary provenance.
- Read official mapped storage/session/CLI/environment/hooks/permissions/context/providers/ACP docs. Immutable upstream links and documentation verification appear in the plan.
- Independent source investigations and design challenge found no inspected stock native process/current-session/settled registry or externally arbitrated approval interface. Same-process session switching, mutable shared SQLite and cursor+Enter approvals prevent safely treating Goose as another Claude parser.
- Recommended limited native observation first; full parity gated on a native current-session/settled/input-provenance/approval contract. ACP-owned runtime is an explicit alternative architecture, not native CLI attachment. No architectural decision was accepted by this research.

## Validation evidence

- Ran `python3 -m unittest discover -s tests -p "$f"` for each of `test_agent_detection.py`, `test_agent_history.py`, `test_agent_activity.py`, `test_agent_outbox.py`, `test_agent_restart.py`, `test_claude_continuation.py`, `test_agent_background.py`: **70 tests passed** (5/31/5/6/4/12/7). History printed ResourceWarnings for unclosed SQLite connections; no failure. These are preexisting regression tests, not Goose compatibility tests.
- Ran a temporary Python/sqlite3 probe using extracted release schema-17 DDL: WAL-aware read-only reads, write rejection, same-old-text reinsertion above a row baseline, and same-ID content mutation demonstrated. Initial probe assertion failed because the deliberately rejected write left an open reader transaction; added rollback and reran successfully twice. Probe is SQLite mechanics only, not native runtime validation.
- Independently downloaded locked cliclack 0.5.6 source: SHA-256 `134778b6a125729ff495c23ba32f64e0c26d61edd52f1f6715a0d036785cf30b` matches upstream lockfile; selection source confirms arrows/hjkl plus Enter.
- Independent read-only review of the final plan found no actionable issues; remaining interoperability limitations are explicit.
- Ran `git diff --exit-code -- src web tests integrations Cargo.toml Cargo.lock README.md AGENTS.md`: no runtime/source changes. Upstream tracked checkout remains clean. Final documentation whitespace/link/source-reference checks recorded at handoff.
- Rust/browser/SSH/native CLI/ACP behavior/device tests were not run. No live sessions, sends, approvals, restarts, closures, configuration edits, bridge installs or deployments occurred.

## Next useful action

User chooses observation-first implementation and the full-parity native integration dependency, or explicitly approves a CC-managed ACP architecture. Create new implementation task records only when authorized; do not treat this completed research as shipped Goose support.

## Constraints

No private provider transcripts or credentials are required. Upstream source is inspected in a temporary directory. Reference `checkouts/` projects are absent in this working copy.
