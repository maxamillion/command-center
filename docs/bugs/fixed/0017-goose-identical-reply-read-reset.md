# Bug 0017: Distinct identical Goose replies are silently marked read

Status: fixed
Found: 2026-11-09, Task 0050
Severity: P2
Location: `src/agent_remote.py:1045`

Append two visible assistant messages with different native message IDs and timestamps but identical text. Observe the first, then request a reply observation with its version/order. The second has a different cursor but reset=True. Attention.observe baselines reset observations as read. Text equality must not prove replacement when the original native row still exists.

Validation: reproduced with temporary synthetic schema-17 fixtures; no live provider data used.

Fixed in Task 0051. Regression coverage: `tests/test_agent_goose_history.py`; final Python agent suite 102 passed. See [task evidence](../../tasks/done/0051-goose-review-fixes.md).
