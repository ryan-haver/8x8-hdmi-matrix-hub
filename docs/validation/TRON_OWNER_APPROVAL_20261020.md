# Tron paused-frame owner approval

The owner explicitly approved the three previously reported Tron paused-frame
differences on 2026-10-20 UTC. Physical validation was deferred. Approval covers
desktop, kiosk-tab-a11 and kiosk-iphone16promax only; other release gates remain
open.

Baseline-only commit `10f788f692881edf329d247de17c5679e1dba2eb` contains exactly
those three PNG changes. Captures were regenerated from a tracked-source export
of `bbeaae4a70752b65c131fe87f226b77c5f0e4187`, with hydrated baselines and isolated
test output. Root private data and historical evidence were excluded.

The pinned environment was
`mcr.microsoft.com/playwright:v1.63.0-noble@sha256:eff16c30e6f3f4af0a03fa4b706120d5e9b0891c344a27d64559aff5900a4a27`.
The scoped update passed three tests in 22.1 seconds. A separate normal comparison
passed three in 20.3 seconds: zero unexpected, flaky or skipped tests.

```text
node tools/ui/run-in-container.mjs test -- --grep special/tron-background/paused-frame --project=desktop --project=kiosk-tab-a11 --project=kiosk-iphone16promax --no-deps --workers=1
```

The [portable manifest](runs/tron-approved-20261020/manifest.json) preserves
before/after hashes and the comparison statistics. Original PNGs and complete
comparison reports remain under local `build/visual-approved-20261020/`;
the original baseline bytes also remain in Git/LFS history. The raw update JSON
was replaced by the normal comparison and is not claimed as separately archived.

The separate approval commit used invocation-only `git -c core.hooksPath= commit`;
persistent hooks were unchanged. These focused checks do not claim a full hook
or complete UI suite pass. Affected CI must pass at the subsequently published
head before the visual regression gate closes. Historical failed CI remains
attached to its original source. No main merge, tag or final release is approved.
