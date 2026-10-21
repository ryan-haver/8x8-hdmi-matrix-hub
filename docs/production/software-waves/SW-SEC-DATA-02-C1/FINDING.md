# Validation request-header redaction gap

Disposition: reproduced existing tooling defect; proposed finding VAL-15,
registration and corrective dispatch pending. This bounded child belongs to
SW-SEC-DATA-02, with F-SEC-014 as an affected feature. It creates no additional
primary feature owner and does not qualify product logging behavior.

The SW-API-READ-04-C1 author used synthetic values to check the existing
`tools.validate.evidence.redact` and `Action.describe` boundaries. A literal
`X-Admin-PIN` value survives both, while the same marker under `X-API-Key`,
`Authorization` and `Cookie` is masked. The current secret-key regex recognizes
bare `pin`, but not the header name. No owner credentials or environment values
were used. The boolean-only original diagnostic is retained under
`docs/validation/runs/software-waves/SW-SEC-DATA-02-C1/`.

This behavior predates the header package. Its new response capture masks all
non-allowlisted values, including cookies and PIN headers, before persistence.
Its CORS scenarios send public origin, host and preflight metadata only. That
bounded package must not be credited with fixing this separate request boundary.

Correction acceptance: mask supported credential header names in nested request
records and action descriptions before evidence, diagnostics or procedure text
is persisted; retain public header values and request behavior. Use synthetic
markers and meaningful negative controls, including actual artifact writing.
Preserve historical evidence bytes and private runtime data. Do not print marker
values in public diagnostics or infer that a synthetic test found an owner leak.

The source lease, exact published base and provider quota will be recorded before
dispatch. New tests/tooling require normal configured verification and qualified
independent review from a different underlying model family. No worker has been
launched, no implementation changed and no finding is closed by this report.
