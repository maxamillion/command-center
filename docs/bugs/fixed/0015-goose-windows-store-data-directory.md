# Bug 0015: Goose Windows store root omitted `data`

State: fixed.

## Reproduction

Resolve the Goose default data root on Windows from `%APPDATA%`. The resolver returned `%APPDATA%\Block\goose`, while the pinned Goose layout stores `sessions/sessions.db` beneath `%APPDATA%\Block\goose\data`.

## Impact

Windows process observation would fingerprint the wrong storage root, so Goose session discovery would report unavailable even when the supported session store existed.

## Fix

Append `data` to the Windows application-data root and update the platform path fixture. Keep the custom `GOOSE_PATH_ROOT` rule as `<root>/data`.

## Evidence

- [Plan 0002 U2](../../plans/0002-goose-agent-parity.md#10-source-evidence-index) pins Goose's platform path resolver; [official storage documentation](../../plans/0002-goose-agent-parity.md#11-verification-completed-and-official-documentation) records the Windows session-store layout.
- `python3 -m unittest discover -s tests -p 'test_agent_detection.py'` — passed, 17 tests, including the Windows `%APPDATA%\Block\goose\data` fixture.
- `python3 -m unittest discover -s tests -p 'test_agent*.py'` — passed, 86 tests; existing history fixtures emitted SQLite ResourceWarnings, with no failures.
