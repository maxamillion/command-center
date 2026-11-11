# Bug 0020: Goose paging exceeds its cursor limit

Status: fixed (2026-11-10, task 0053)
Found: 2026-11-09, task 0052, branch HEAD 6983b63.
Severity: P2

Using `GooseHistory` synthetic fixtures, insert 510 short user messages with timestamps `1762400000+i`, distinct message IDs and session `20261106_1`. Follow each `history_page.next_cursor` through `goose_history_page`. Cursor lengths for pages one through three are 576, 726 and 877 bytes. Loading page four raises `Failure(500, 'Goose history cursor exceeded its limit')` while creating the cursor for page five. The details handler converts this into unavailable history and empty messages. The advertised five-page window cannot be reached.

Affected: `encode_goose_history_cursor` in `src/agent_remote.py`. Compress/restructure bounded page validation metadata or adopt an adequately bounded compatible cursor contract; add a five-page test with realistic timestamp and session-ID lengths.

Validation: reproduction executed using temporary synthetic SQLite stores; no live data/actions.

## Fix and verification

[Task 0053](../../tasks/done/0053-goose-history-review-fixes.md) implements the fix and records failing-before/passing-after regression coverage. Python synthetic reproductions pass; the scroll-retention browser test is present but sandbox socket restrictions prevent execution.
