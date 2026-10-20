# SW-API-CLIENT-02-C1: disconnected routing failure event

Disposition: **actual reproduced contract defect**, provisional finding VAL-14;
registration and corrective dispatch remain pending. This is a bounded child of
SW-API-CLIENT-02 for F-API-033, with F-REL-009 as an affected feature. It creates
no additional primary feature owner and does not qualify either feature's full
target. No implementation worker has been launched for this child.

[CI39500840835](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/actions/runs/39500840835)
at published1a4f9f9457f85bdcc2eafb9c43e8e7cd4eecd109 completed12/13 required
checks successfully, including UI. Validation alone failed:1,415 API passes,
one API failure,54 browser passes and18 Remote passes. The actual clean synthetic
merge a7818f2054a57e4e5ee9176f2539e3155dff41d8 has the same tree as1a4f9f94.
The failed scenario is failures.unreachable_switch: a valid input3/output1 request
returns503 Matrix not connected and leaves the device unchanged, while the
observer sees matrix_connection/status and no switch_failed event. The original
record is preserved byte-for-byte under validation/runs/software-waves/
SW-API-CLIENT-02-C1/failed-ci; it is not imported as accepted feature evidence.

The existing handler returns503 before parsing a request when the matrix is
already disconnected. Its later failed-command branch emits switch_failed.
The documented WebSocket contract says a failed route emits that event. Product
and scenario bytes are unchanged from the earlier green2b10 run, so the failure
is not attributed to the new documentation or security adapter package.

The coordinator's disposable run.py/simulator probe first waits until health
actually reports disconnected, then submits a valid route. It reproduces503,
empty state diff, no routing write and no switch_failed. After fault removal,
the connected positive control returns200 and routes output1 to input3; observed
WebSocket messages pass the schema. The ordinary existing scenario also passes
locally when the connection fails inside the command. Both timing boundaries
must be covered. The first stricter diagnostic treated background reconnect
login entries as writes and failed its own assertion; those entries are not
routing mutations. Original diagnostics and all CI bytes remain retained.

Correction acceptance: preserve503/error behavior and no device mutation for a
valid offline request, emit the exact failed-route event (single and all outputs),
and preserve established malformed/invalid offline request behavior without
publishing invalid ports. Prove the actual already-offline branch and a connected
allowed control with independent state/command/event readback. Keep the existing
unreachable scenario and its event assertion. No retry-only CI waiver, weaker
assertion, transport/reconnect change or new owner/hardware action is authorized.

A future exact serial lease may include src/rest_api/control.py, an owned new
simulator regression test and the required simulator REST read-coverage update.
Registry/ledger/finding registration and integration remain coordinator-owned.
A qualified different-family source review, normal full hook/route inventory,
applicable combined CI and exact publication are required before closure.
