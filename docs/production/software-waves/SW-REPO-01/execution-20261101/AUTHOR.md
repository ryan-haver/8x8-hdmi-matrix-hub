# SW-REPO-01 — early bounded metadata intake (SEC-14 / SEC-15 / DEP-05)

**Task** `task_5486db7aed82` · **Dispatch** `ctx_e47c86a8e4ee` · **Run** `run_37205f6095b3` (gen5) · **Coordinator** `term_6ed8131e-3ab3-4693-8094-56cc10acd412` · **Entry** `61957a47cf91c504f48149a6c43a3dfea3cdd032` · **Branch** `ryan-haver/wp-exec-sw-repo-01` · **Author** native MiniMax-M3 (`minimax-coding-plan/MiniMax-M3`), thinking variant · 2026-11-02

Metadata intake only: no finding closure, feature level, package completion, legal, security or CI qualification; the final candidate does not exist.

## 1. Accepted sources reused, not re-run

Historical M3 inventory `SW-REPO-01/AUTHOR.md` at tip `b4736c2b` (original `73a9621c`, base `53e4b671`) + OpenAI `COORDINATOR_REVIEW.md`; findings delta `SW-FINDINGS-01/execution-20261101/AUTHOR.md` at `a2dab11c` (reviews `00b7b049`→`43356a0c`→`ac9c4d49`); CI attribution disposition (56 units non-ancestor → unknown/stale); register `docs/REMEDIATION_PLAN.md:200,201,232,546,549`.

## 2. Bounded method

Read-only `git show`/`cat-file`/`ls-tree` at the exact entry for three files only — `LICENSE`, `Dockerfile`, `.github/workflows/ci.yml` — plus cited `docker-publish.yml` existence and blob-id comparison against `53e4b671`. No history, dangling-blob or secret scan; no CI run; no legal reading.

## 3. Three rows

| ID | Exact existing condition (register) | Historical inventory vs newly accepted findings lead | Bounded current-entry corroboration (static source) | Outstanding proof / owner — no closure |
| --- | --- | --- | --- | --- |
| **SEC-14** H 0/D3 | `:200` "…manual committed (public) since the first commit; LICENSE is a stub"; loc `docs/BK-808 */`, `LICENSE` | Historical: 0 hits/10 vendor patterns; 129 `BK-808` paths under `tests/fixtures/device`; 0 purged paths in 84 unreachable-commit trees; 188 dangling blobs uninspected. New lead: stub clause stale; vendor element inherited. | `LICENSE` blob `d0a1fa14`: 16 726 B, 373 physical LF-terminated lines, 293 nonempty lines, line 1 title `Mozilla Public License Version 2.0`, "stub" 0 token occurrences (case-insensitive), equal to `53e4b671`. The 36 redacted `generic-api-key` candidates (4 files, 4 commits) keep their local full-history `--redact` scope — not a current no-secrets proof. | Coordinator exact-match check of the 36; no raw secret reading, no blanket suppression. Owner Support purge `:546` external/unknown — no server-side cache or legal claim; 188 blobs stay uninspected. |
| **SEC-15** L 6 | `:201` "gitleaks configured but never run; CI actions tag-pinned; base image not digest-pinned"; loc `.github/`, `Dockerfile` | Historical: static presence only — a job that exists is not a run that passed; no candidate-base remote run; prior receipt at `97e617c2` (run `39374096223`) covers the source tree only. New lead: 42/42 `uses:` SHA-pinned, base digest-pinned. | `ci.yml` blob `61ea6731`: 42/42 `uses:` lines carry a 40-hex SHA (0 tag-pinned), 14 distinct actions. `Dockerfile` blob `eff712a4`: 1/1 external base `python:3.12-slim@sha256:a6e34c…c11b1` (line 24), 3 internal stages. Both equal `53e4b671`. | No CI receipt at the exact candidate; no remote required-check list. Pins/digest are static declarations, not fresh CI or semantic supply-chain guarantee. Owner: coordinator + `:201` text. |
| **DEP-05** M 0 | `:232` "CI: no `pull_request` trigger; ruff only on `src/`; mypy non-blocking; no hassfest/HACS validation; no gitleaks; QEMU set up but no multi-arch platforms"; loc `.github/workflows/docker-publish.yml` | Historical: clauses contradicted against `ci.yml`; location already stale; `:549` `[x]` yet `:232` unresolved, so the parser keeps it open. New lead: six Ruff candidates plus existence filter, source declaration only (R5 accepted at `ac9c4d49`). | Cited `docker-publish.yml` absent at entry (`cat-file -e` exit 128) and at `53e4b671`. `on:` `pull_request:`(10), `push:` main/`v*`(11-15), `workflow_dispatch:`(16); ruff step loops six candidates `src` `tests` `custom_components` `tools` `run.py` `run_server.py`(55), keeping existing via `[ -e "$p" ]`(56); `mypy src/`(85-86), no `continue-on-error` in `typecheck` (4 occurrences elsewhere); `hassfest` `hacs` `hygiene` `gitleaks` declared; QEMU arm64 + multi-arch `publish`. | This intake ran no CI; declarations only, and the original condition is not closed. Owner: coordinator reconciliation at `:232`/`:549`; candidate CI receipt stays separate. |

## 4. Limits

61 findings stay open; core qualification 1 is a formal FAIL/no domain, owner retake choice pending. Original 3 Tron decisions stay closed; privacy, source, HIL, 72-hour, week and final-release gates stay held/open. Pins and names are static source declarations, not legal, security or CI qualification.

## 5. Checks and publication

One invocation of the five authorized existing documentation modules (`tests/test_core_documentation.py`, `tests/test_client_guides_docs.py`, `tests/test_openapi_and_config_docs.py`, `tests/test_security_docs.py`, `tests/test_license_and_protocol_docs.py`; `-q -p no:tests.route_inventory -p no:cacheprovider`), shared-root `.venv` Python, checkout root+`src` PYTHONPATH, UTF8, bytecode off, isolated data/config/temp, forward-slash `--basetemp`; direct exit, full stdout/stderr, JUnit and temp retained privately. Docs checks are not semantic proof, not a source-hook pass, not a CI result. Author-only prose; coordinator owns integration/publication.

```json
{
  "exact_entry_base": "61957a47cf91c504f48149a6c43a3dfea3cdd032",
  "scoped_ids": ["SEC-14", "SEC-15", "DEP-05"],
  "inherited_sources": [
    "SW-REPO-01/AUTHOR.md@b4736c2b (original 73a9621c, base 53e4b671) + COORDINATOR_REVIEW.md",
    "SW-FINDINGS-01/execution-20261101/AUTHOR.md@a2dab11c reviews 00b7b049/43356a0c/ac9c4d49",
    "EV-CI-ATTRIBUTION/execution-20261101/COORDINATOR_DISPOSITION.json",
    "docs/REMEDIATION_PLAN.md:200,201,232,546,549"
  ],
  "observations": {
    "SEC-14": "LICENSE d0a1fa14 = 16726 B/373 physical LF-terminated lines/293 nonempty lines, line 1 title Mozilla Public License Version 2.0, stub 0 token occurrences (case-insensitive), equals 53e4b671",
    "SEC-15": "ci.yml 61ea6731 = 42/42 uses SHA-pinned (14 actions); Dockerfile eff712a4 = 1/1 external base digest-pinned; both equal 53e4b671",
    "DEP-05": "docker-publish.yml absent at entry and 53e4b671; ci.yml declares pull_request+push+dispatch, 6 ruff candidates + existence filter, mypy without continue-on-error, hassfest/hacs/hygiene/gitleaks, QEMU arm64 + multi-arch publish"
  },
  "remaining_proof": [
    "SEC-14: exact-match check of the 36 redacted candidates; owner Support purge external/unknown; 188 dangling blobs uninspected",
    "SEC-15: CI run receipt at the exact candidate + remote required-check list",
    "DEP-05: candidate CI receipt + register location/clause reconciliation",
    "SW-REPO completion dependencies and the final-candidate rollup unsatisfied"
  ],
  "metadata_only": true,
  "package_completion": false,
  "finding_closure": false,
  "source_security_license_qualification": false
}
```
