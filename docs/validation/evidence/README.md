# Evidence records

Committed proof of function (`docs/validation/VALIDATION_PLAN.md` §4). CI runs regenerate simulator evidence on every PR and upload it as the `validation-evidence` artifact. Records are committed here only at milestones: a phase exit, a hardware (HIL) session, or a release.

## Layout

```
evidence/
  <feature id>/                                          # the record's first feature
    <YYYY-MM-DD>-<level>-<shortsha>-<scenario>-<client>.json   # the record (schema: ../evidence.schema.json)
    <YYYY-MM-DD>-<level>-<shortsha>-<scenario>-<client>/       # its artifacts, if any
      after.png                                          # browser screenshot after the action (Git LFS)
```

- **One record = one scenario × one client × one target.** A record can prove several features (`features`). It is stored once, under the first feature. The ledger indexes records by their `features` field, not by folder.
- `level` is what a PASS proves: `V2` = simulator with the api client, `V3` = simulator with a real client (browser, and later HA, Remote and Flic), `V4` = real matrix plus operator observation.
- `result` is `pass`, `fail` or `blocked`. On a fail, `gate` is `known-failure` when every failed check is linked to an open finding (`checks[].finding`), and `regression` when at least one isn't. A regression fails CI.
- `observations` holds everything that was seen: the HTTP exchanges, hub read-backs, the device state before and after, the state diff, the simulator command log excerpt, the WebSocket events (with times relative to the action), screenshots, operator answers and media paths, and the hardware restore report.
- `commit` (with any dirty files) and `covers` together decide freshness. Evidence goes stale when a covered file changes after `commit`.
- Secrets (passwords, passcodes, tokens) are redacted before writing.

## Adding records

```bash
python -m tools.validate run --client api --client browser --record          # simulator milestone
python -m tools.validate run --target hardware --matrix-host … --operator "Name" --allow-writes --record
python -m tools.validate ledger                                               # refresh LEDGER.md
```

Commit the records, their artifact folders (PNG files go to Git LFS through `.gitattributes` here), and the regenerated `LEDGER.md` together. When a record proves a level above a feature's recorded `current` in `features.yaml`, raise `current` in the same commit. Then list the record under `evidence:` and update the `basis:`.
