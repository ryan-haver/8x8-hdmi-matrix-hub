# SW-API-READ-01 candidate preparation

Prepared from Sol submission `0dd2c25ea866fd56fbe6046e03f0172499b70080`,
implementation `afe344a0e6a17392ccda90bab140284dd512267e`, original base
`97e617c2276c7b1e015bb4a9419cb9820deafdee`. Independent different-family
review and integration are pending; this is a proposed evidence/registry update.

The author normally ran the configured implementation hook: repository Ruff,
4,041 tests passed, four documented platform/dependency skips, 35 deselected,
177/177 REST routes. Its 81 direct/source/simulator read tests passed. Product
routes, direct reads and shared clients/tooling did not change. The package
adds API root/alias scenarios and reuses existing API-info identity assertions;
no REST product change or new route requires another read-suite implementation.

Three final clean source-simulator records are copied byte-for-byte, with
original source SHA, API client, V2 level, timestamps/environment and null image
digest retained. Manifest and summary under
`docs/validation/runs/software-waves/SW-API-READ-01/` identify original hashes.
No API pass is a V3 client, browser render, image or hardware qualification.
The earlier untracked-scenario diagnostic remains private and excluded.

Coordinator changes only F-API-002 current V1 to V2, basis and evidence list,
preserving target, interfaces, claim and findings; the earlier symmetric
scenario mapping is unchanged. All other feature objects are semantically
identical. Scoped -text attributes preserve new original records. Canonical
ledger generation ran alone to completion before registry tests: numerical
below-target count 205 to 204, stale remains 57, F-API-002 fresh V2. These are
proposed numerical outcomes, not fresh release acceptance for every row.

Verification: all three records pass the existing schema and original hash
comparison; existing registry and evidence-schema tests **33 passed**. An initial
coordinator test invocation failed before all 33 test bodies because its chosen
basetemp parent did not exist. That setup failure is retained in the coordinator
transcript; creating a short new isolated build parent fixed it. Successful
run uses isolated MATRIX_DATA_DIR and UC_CONFIG_HOME, disables the partial-run
route-report writer and retains logs/JUnit under `build/swapi-checks/`.
No source change was needed for this invocation error.

Only evidence/registry/ledger/attributes/prose are added after the tested source
commit. The documented invocation-only metadata/documentation hook exception is
used after the normal source hook, actual registry/schema and whitespace checks;
this is not a second full-suite pass. The exact resulting combined candidate
requires a qualified DeepSeek independent review, scenario replay and acceptance
before integration. Further material corrections require re-review.
