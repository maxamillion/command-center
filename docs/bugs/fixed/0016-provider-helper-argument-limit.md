# Bug 0016: Embedded provider helper exceeded the OS argument limit

State: fixed
Found: 2026-11-09 while validating Plan 0002 Task 0031

## Symptom

Agent discovery and conversation requests returned 502 once the embedded Python helper grew beyond the per-argument limit used by `execve`. `Transport::helper_request` placed the entire helper source in the `python3 -c` argument. Goose's helper was 158,877 bytes, so the OS rejected process creation with `Argument list too long` before the helper could run.

## Fix

Pass a small Python bootstrap in `-c`, then stream a decimal source length, the helper bytes, and the existing JSON request over stdin. The bootstrap executes only the source length it receives; helper scripts continue reading their request from the remaining stdin bytes. SSH invocations use the same bounded command and stdin protocol.

## Validation

- Local card rename/conflict and stale-process browser fixtures passed against the formerly failing large helper.
- `cargo test` passed 47 library, 2 binary, and 2 tmux integration tests after the transport change.
- The SSH card-scope fixture reached the remote helper but the environment's test `sshd` could not execute `/bin/bash` (`Permission denied`); remote transport coverage remains unavailable here.
