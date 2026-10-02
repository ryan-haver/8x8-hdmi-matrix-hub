# CEC capability reporting and Telnet dispatch baseline

`wp-cec-capability-telnet-validation` records **290 packaged-image scenarios:
288 pass and two fail**, with both failures linked to the new medium-severity
BE-37 finding. Application code is unchanged. The C0 campaign records failures
before remediation ([validation plan](VALIDATION_PLAN.md#5-campaigns)).

The **88 capability/catalogue checks** pass. They cover complete source/display
command-name lists, representative category membership, all four signal/CEC
flag combinations on every input, and all five raw scaler codes on every
output with both values of each connection/stream/ARC/CEC flag. Device code 4
alone is reported as audio-only. Three grouped reads verify all 16 port
records and every summary list, using independently seeded names and flags.
Invalid ports/types and failed CEC reads report errors without changing the
matrix. These reads do not exercise every flag combination with every scaler,
missing status fields, or input/output read failures hidden behind warm caches.
BE-15 remains open for hardware/write proof; its read-side mapping is proven here.

The **200 healthy Telnet cases** also pass: every one of the 19 source commands
on each input and all six display commands on each output. Literal expected
words include `enter`, `rew`, `ff`, `vol+` and `vol-`. Each target starts with
CEC disabled; an HTTP enable write preserves the other flags and precedes
exactly one Telnet CEC command. There is no HTTP CEC frame in these cases.
Matrix flag readback and unchanged unrelated state confirm the enable effect.
Successful Telnet acknowledgements use the simulator's documented HIL
assumption; physical effects and real acknowledgement shapes need hardware proof.

BE-37 occurs in the **two interrupted volume-reply cases**, on input/output 8.
The simulator processes `s cec ... 8 vol+`, then closes the connection halfway
through its reply. The hub sends the same volume command over HTTP (input
index 19, output index 4) and returns HTTP 200 success. Both desired safeguards
fail: reporting the ambiguous outcome as failure and avoiding the resend.
Each record retains exactly these two failures, linked to BE-37; the other
checks pass. This proves an ambiguous resend in software, not a measured
physical double volume increment. BE-37 remains open.

The [combined summary](evidence/F-CEC-010/2026-10-02-cec-capability-telnet/run-summary.json)
and [audit](evidence/F-CEC-010/2026-10-02-cec-capability-telnet/audit.json) retain
all outcomes, with separate original summaries and stack metadata for each
transport. Source: `a538a8ef4c52f79419f8a2c6514d05ff4a6ea7fc`. Image:
`hdmi-matrix-hub:wp-simulator-evidence-refresh`,
`sha256:1b7b72c01322972198e2660896ca6a4270cce740d4c32d701a16eaa12b580dc0`.
The image matches all 176 application/web/runtime/dependency files after
line-ending normalization. Every record has clean source, the measured image
identity, a valid schema and the configured CEC transport. The stack checks
its actual Docker environment: `OREI_USE_TELNET_CEC=false` for capability reads
and `true` for Telnet dispatch. A readiness helper waits for both transports
before running and after faults; externally managed hubs reconnect rather
than being restarted by the runner.

Ruff and **1,605 backend tests** passed through the implementation commit hook
in 363.57 seconds (3 skipped, 26 deselected), with strict route coverage
**163/163 (100%)**. The evidence commit runs the same mandatory hook.
The [ledger/gate snapshot](evidence/F-CEC-010/2026-10-02-cec-capability-telnet/ledger-check.json)
reports **137 fresh passing features**, **three fresh failing features**, and
**zero stale features**. F-CEC-010 and F-CEC-011 gain their first committed V2
proof from the passing cases. Levels are V0 27, V1 96, V2 53 and V3 92. Fresh
failures affect F-MTX-030 (BE-36) and F-CEC-010/F-API-015 (BE-37). The gate accepts
the explicitly linked known failures; it does not establish that ambiguous
fallback is safe. Recorded baselines and caps are preserved. C0 remains incomplete.

The [reproduction bundle](evidence/F-CEC-010/2026-10-02-cec-capability-telnet/REPRODUCE.md)
uses separate isolated stacks and fresh fixture data. Proof containers,
networks and volumes were removed; the work container is removed after
committing. Images and ignored build files remain.

Next: remaining profile/domain CRUD simulator gaps. BE-36/BE-37 remediation,
owner-present hardware checks, WP-C4 scene visual approval and the SEC-01-03
release-gate decision remain pending.
