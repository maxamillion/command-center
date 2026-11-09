# Bug 0018: Long tool arguments replace successful Goose results with errors

Status: fixed
Found: 2026-11-09, Task 0050
Severity: P2
Location: `src/agent_remote.py:848`

Persist a successful tool request with 4500 characters of arguments and a matching successful response. Projection reports error, replaces the real output with the argument suffix, and reports truncated=False. Separate argument truncation metadata from tool-call errors and preserve matched result status/output.

Validation: reproduced with temporary synthetic schema-17 fixtures; no live provider data used.

Fixed in Task 0051. Regression coverage: `tests/test_agent_goose_history.py`; final Python agent suite 102 passed. See [task evidence](../../tasks/done/0051-goose-review-fixes.md).
