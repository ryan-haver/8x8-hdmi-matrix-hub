# Deployment evidence refresh

The seven deployment features now have fresh passing evidence on
`wp-deployment-evidence-refresh`. The regenerated ledger has **zero stale
features**, down from seven. It has 106 features with fresh passing scenario
evidence, 92 at V3 and 34 at V2. The recorded baselines and finding caps stay
unchanged; 217 features remain below their targets and C0 remains incomplete.

The unchanged `tests/deploy` suite passed **25 tests**, with one intentional
skip, in 89.36 seconds. The skipped test connects a Remote client in core mode,
where that integration is disabled. All four Compose checks ran and passed:
plain startup, the bridge driver URL, missing-host-IP refusal, and host
networking. This Docker Desktop run uses a Linux test runner with host
networking enabled. It adds host-networking proof previously left n/a in the
committed Windows deployment record.

Both image modes prove health, served UI/kiosk/static files, simulator routing
and switching, integration imports/listeners, non-root execution, read-only
application files, theme/profile persistence after restart and clean SIGTERM
shutdown. Core mode reads the simulator address from environment variables;
Remote-enabled mode uses seeded Remote setup data. Routing is restored after
switching in both modes. Compose startup checks use TEST-NET-1, not a real
matrix. The scripted Remote proves the WebSocket connection and metadata;
physical Remote discovery, LAN mDNS delivery, ARM deployment and restart
triggered by an unhealthy state remain unproven.

The [three-scenario summary](evidence/F-OPS-001/2026-10-01-deployment-refresh/run-summary.json)
links the schema-valid records for seven features:
F-OPS-001, 002, 003, 005, 006, 011 and 015. Every record identifies clean source
`1d0a4a948f84463acf2e5aa516eed4b2e06cc418`. The two image records contain the
measured image ID. The existing Compose recorder leaves that field empty;
the [runner metadata](evidence/F-OPS-001/2026-10-01-deployment-refresh/runner.json)
and test-only image override identify the image used by all Compose projects.
Evidence filenames use the UTC date, 2026-10-02; this handoff uses the local
session date, 2026-10-01.

Image: `hdmi-matrix-hub:wp-simulator-evidence-refresh`.
Image ID: `sha256:1b7b72c01322972198e2660896ca6a4270cce740d4c32d701a16eaa12b580dc0`.
The image comparison again matched all 176 source, web, runtime and requirement
files after line-ending normalization. No application changes were needed.

The validation gate passes with no known failures. The required commit hook
runs Ruff and the full backend suite before this evidence commit. The
[reproduction bundle](evidence/F-OPS-001/2026-10-01-deployment-refresh/REPRODUCE.md)
retains the runner, summaries and image comparison. Test containers, networks,
Compose projects and data volumes are removed by the fixtures; the task runner
is removed after committing. Local images and ignored test caches are retained.

Next: add simulator scenarios for matrix controls that still lack fresh feature
proof, starting with preset save, port names and front-panel settings. This
refresh establishes current deployment behavior; it does not complete C0.
WP-C4 scene visual approval, owner-present hardware checks and the SEC-01–03
release-gate decision remain pending.
