# Bug 0019: A tool-only tail clears Goose reply attention

Status: fixed
Found: 2026-11-09, Task 0050
Severity: P2
Location: `src/agent_remote.py:1039`

Persist a visible assistant reply, then append 101 tool-only rows. Reply observation with the previous version/order returns cursor=None and reset=True although the original reply still exists. Attention.observe clears and baselines its cursor on reset, so an unread reply disappears without acknowledgement. Preserve the last known reply when it merely falls outside the bounded page; distinguish omission from deletion.

Validation: reproduced with temporary synthetic schema-17 fixtures; no live provider data used.

Fixed in Task 0051. Regression coverage: `tests/test_agent_goose_history.py`; final Python agent suite 102 passed. See [task evidence](../../tasks/done/0051-goose-review-fixes.md).
