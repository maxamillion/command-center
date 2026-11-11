# Bug 0021: Tool-only tail hides a new Goose reply

Status: fixed (2026-11-10, task 0053)
Found: 2026-11-09, task 0052, branch HEAD 6983b63.
Severity: P2

Baseline an assistant reply at timestamp 100. Before the next observation, insert a distinct assistant reply at 101 and 101 toolResponse-only user rows at timestamps 102 onward. `goose_reply_observation` reads only the latest 100 source rows, finds no assistant chat and falls back to the original known reply. Its cursor remains the baseline cursor, reset is false, and the next poll returns unchanged=true. The unseen reply is never discovered without another newer reply, so background attention/notifications miss it even if older pages expose it.

Affected: latest reply selection in `src/agent_remote.py:1030`. Preserve bounded IO but locate the most recent visible assistant reply independently of the latest display page, with explicit incomplete-observation handling. Add a test where the new reply and the tool-only tail arrive between polls; the existing tail regression only protects an already observed reply.

Validation: reproduction executed with `GooseHistory` temporary fixtures; no live data/actions.

## Fix and verification

[Task 0053](../../tasks/done/0053-goose-history-review-fixes.md) implements the fix and records failing-before/passing-after regression coverage. Python synthetic reproductions pass; the scroll-retention browser test is present but sandbox socket restrictions prevent execution.
