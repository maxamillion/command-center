# 2026-11-09: Goose observation UI

Task 0031 is complete. Goose cards now use the project name on compact layouts, expose project conversations only as unverified history, preserve Unknown live status and capability reasons, hide messaging/outbox/approval controls, and label inferred terminal prompts as possible approval prompts. Queue filters keep an explicitly opened conversation visible, and the fixture verifies exact reply-cursor acknowledgement without compact terminal traffic or desktop tmux changes.

The synthetic history fixtures now carry stable `order_key` values. During validation, the 158,877-byte Python agent helper exceeded the OS per-argument limit when sent through `python3 -c`; [Bug 0016](../bugs/fixed/0016-provider-helper-argument-limit.md) records the fix. The transport now streams the bounded helper source and then its JSON request over stdin.

Verification: Rust format, tests, Clippy and release build passed; the frontend build passed with existing Vite chunk/dynamic-import warnings. The full agent/navigation Playwright suite passed 33 of 38 cases. The five failures all use the synthetic SSH host; its shell could not execute (`/bin/bash: Permission denied` or broken pipe). Goose UI, local process-scoped card cases, compact isolation, and all navigation cases passed. No live Goose agent or history was used.

Next: Task 0032, reuse the reviewed Close-agent safeguards for Goose with isolated fixture windows only. The native lifecycle producer and guarded approval channel remain external blockers, and no live Goose close is authorized.
