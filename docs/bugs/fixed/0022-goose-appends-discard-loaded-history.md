# Bug 0022: Goose appends discard loaded older history

Status: fixed (2026-11-10, task 0053)
Found: 2026-11-09, task 0052, branch HEAD 6983b63.
Severity: P2

Load two pages from a 230-message synthetic Goose session, then append one new assistant reply without editing any existing row. Poll with the previously observed `known_version`, as `AttentionQueue.loadDetail` does. The backend sets `history_reset=true` for every revision change, returning only the latest 100 messages. The browser's merge guards reject retention when history_reset is true, discarding the older page and disrupting the reader's position. Tool-result updates also change this revision, so a reader browsing active history can repeatedly lose loaded pages.

Affected: `src/agent_remote.py:1003` and merge guards in `web/src/queue.ts:468`. Distinguish append-only growth from edits/deletion/reinsertion, revalidate loaded rows, and preserve older pages/scroll position when they remain valid. Add a browser test combining older-page reading with a normal append and a separate true rewrite reset.

Validation: temporary `GooseHistory` fixture, 230 rows; after append reset=true, 100 rows returned, and the oldest previously loaded message absent. Existing reset tests cover intentional edits only.

## Fix and verification

[Task 0053](../../tasks/done/0053-goose-history-review-fixes.md) implements the fix and records failing-before/passing-after regression coverage. Python synthetic reproductions pass; the scroll-retention browser test is present but sandbox socket restrictions prevent execution.
