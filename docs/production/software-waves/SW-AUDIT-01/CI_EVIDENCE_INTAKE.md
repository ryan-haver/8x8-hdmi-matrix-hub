# SW-AUDIT-01: existing CI evidence intake

The existing CI artifacts contain **56 of the 60 requested proof units**: 30 API V2, seven browser V3 and 19 Home Assistant V3. Four Flic V3 units are missing. All 56 records pass with gate `ok`, but **all 56 remain blocked for freshness admission** because their actual synthetic merge source is not an ancestor of the frozen base. This inventory qualifies no feature and closes no finding.

| Authority | Observation |
| --- | --- |
| Task / Dispatch | `task_1143adebca18` / `ctx_84eb3a122772` |
| Run / worker / coordinator | `run_37205f6095b3` / `term_d3a08f38-c21f-4b69-a35c-badc1e49fdea` / `term_dcf96b5a-bb99-4ecb-b887-eb53f7f01662` |
| Host / requested model | Windows localOrca 1.4.243, runtime `14c5d968-cfad-4ebc-b071-19d297a7c1f4`; Codex `gpt-6.1-sol` / high per dispatch; no helper or fallback |
| Worktree / branch | `wp-ci-proof-intake` / `ryan-haver/wp-ci-proof-intake` |
| Frozen base | `490a879bd346773cca64fac861eaaab29e703628` |
| Immutable input SHA-256 | `34be806ec99a4f66ca58628c7204e5c4b1e362e6c2544bf76378bc983c4764d3` |
| Intake observation | 2026-10-29 UTC; fresh official metadata/download at approximately 00:00Z |
| Accepted scope | [freshness delta](FRESHNESS_DELTA.md), [coordinator factual review](COORDINATOR_REVIEW.md): 60 units / 55 scenarios / 38 rows, plus separate F-API-034 assertion gap |

## Provenance and retained bytes

[CI run 40770556464](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/actions/runs/40770556464) is completed/success, event `pull_request`, published head `e16ec6af4d13c76c7024d42b605afec0c8ae9bf4`. Current job metadata confirms the 13 required jobs succeeded; the extra UI review comment job succeeded and GHCR publication was skipped. Those job conclusions alone are not the proof used below.

| Key / official artifact | Bytes / ZIP members | Current digest (SHA-256), verified against raw bytes | Expired / expiry |
| [A: validation-evidence](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/actions/runs/40770556464/artifacts/12853945294) | 30,334,482 / 1,743 | `54fbd594305ebecc9acdcdc25fd2524352d715129cf09448d4cc4cf1a1ca5774` | false / 2026-11-27T21:31:09Z |
| [H: validation-ha-evidence](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/actions/runs/40770556464/artifacts/12853275385) | 104,792 / 30 | `f30555eb92dcf9053bfa7f0e33047ec6b48dc75b4c63c19ca466416fa81b9825` | false / 2026-11-27T21:22:19Z |

Both downloads used Python `subprocess.run(["gh", "api", endpoint], capture_output=True)` followed by `Path.write_bytes(stdout)`. Digest equality and `ZipFile.testzip() is None` passed. All member names/modes were inspected: no absolute/parent traversal, drive/colon or symlink entries detected. No ZIP was extracted or artifact script executed; archive layout, logs and screenshot bytes remain intact. Raw payloads stay private and have not been cleared for public redistribution or VAL-15 redaction compliance.

Private artifacts are under `build/software-waves/SW-AUDIT-01-ci-proof-intake/`: `attempt-01/` holds both original ZIPs, official metadata, job/run metadata, member manifests and download commands; `attempt-03/` holds successful original job logs and command/hash receipts; `analysis-01/` holds `units.json`, `features.json`, `sources.json`, exact Git argv/exits, screenshot references/hashes, assertion-gap details and presence-only privacy diagnostics. These ignored artifacts must accompany coordinator preservation; they are not canonical evidence.

## Actual source and freshness consequence

Every one of the 1,513 A records and 19 H records declares source `bdcf06dc6723aad7da63ecfed3d3555ab0d02e55`; none was reassigned to the published head or base. Direct job logs corroborate checkout at that SHA: validation job 123106264167 line 227 and HA job 123106264102 line 160. The specifically authorized `entry-ci-full.log` independently agrees at lines 7983/7986 and 9104/9107; its byte hash is retained privately in `attempt-02/entry-ci-log-provenance.json`.

| Git fact against frozen base | Result |
| --- | --- |
| Source commit object available | `git cat-file -e bdcf06dc…^{commit}` exit 0 |
| Actual source ancestor of base | `git merge-base --is-ancestor bdcf06dc… 490a879b…` exit **1** |
| Published head ancestor of base | same check for `e16ec6af…`, exit 0 |
| Source tree = published-head tree | both `7fa5c9d99731349b0705fa2ef7818d5eb5a11350` |
| Frozen-base tree | `f70bcd4a51a68bd26dde80fab1e6070f10058b0f`; whole trees differ |
| Source → base diff | six documentation paths, no runtime/source/test/client path changes |
| Record-owned covers intersect changed paths | zero for each of the 56 matched records, across 11 distinct cover sets |

The six changed paths are `docs/agent-process/state/HANDOFF.md`, `docs/planning/RUNTIME_EXECUTION.md`, `docs/production/AGENT_ALLOCATION.md`, `docs/production/software-waves/SW-API-READ-03/INTAKE.md`, `docs/production/software-waves/SW-AUDIT-01/COORDINATOR_REVIEW.md` and `docs/production/software-waves/SW-AUDIT-01/FRESHNESS_DELTA.md`. One cached diff per actual record SHA was used, with the existing `gitinfo.matches` path/prefix/glob rule applied to each record’s own covers. No quadratic Git blob scan, reference modification or fetch was needed.

Under [current Git freshness](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tools/validate/gitinfo.py) and [ledger rules](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tools/validate/ledger.py), a nonancestor produces `unknown`; ledger computation places nonfresh records in its stale collection. Covered-path equivalence is useful evidence for a coordinator-owned admission decision but does not bypass that rule. All 56 have `dirty=false`, `dirty_files=[]`, exact current covers and exact scenario/client feature sets. The old source `1baac3dec660f41345869c126cfca94d6731c5a0` remains historical evidence with its original attribution.

## Sixty proof units

All matching rows below have exactly one record, target `sim`, result `pass`, gate `ok`, no blocked reason and no failed check. **B** means matched but blocked for ancestry admission; **M** means missing execution. `P/N` counts passing/nonapplicable checks; failed checks are zero. `Shot=1` means a referenced 1440×900 PNG exists with matching archive member, valid signature/chunk CRCs and retained SHA-256; zero means no screenshot was recorded, which is expected for API/HA. Screenshots were structurally checked, not visually approved.

The exact member for any matching row is `evidence/<Folder>/2026-10-28-<Level>-bdcf06dc-<Scenario>-<Client>.json` inside artifact A or H. Source-linked scenario names identify the declarative assertions; the private `units.json` retains each record’s full exact path/hash, all actual feature IDs, covers, checks, nonapplicable reason, start/finish timestamp, source/dirty/image metadata and screenshot references. Actual features equal `Scenario.features_for(client)` in every matching record; the 38-row feature map below names the requested subset.

| Unit | Scenario (source) | Client / level | Archive / Folder | State | P/N | Shot | Substantive recorded assertions |
| --- | --- | --- | --- | --- | ---: | ---: | --- |
| U01 | [flic.all_outputs](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/flic_replay.py) | flic / V3 | — / — | M | — | — | generated Flic all-output request and routing assertions absent |
| U02 | [flic.power_off](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/flic_replay.py) | flic / V3 | — / — | M | — | — | generated Flic standby request and power assertions absent |
| U03 | [flic.power_on](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/flic_replay.py) | flic / V3 | — / — | M | — | — | generated Flic wake request and power assertions absent |
| U04 | [flic.preset](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/flic_replay.py) | flic / V3 | — / — | M | — | — | generated Flic preset request and routing assertions absent |
| U05 | [ha.config_flow](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/home_assistant.py) | ha / V3 | H / F-HA-001 | B | 14/0 | 0 | entry loaded; scan interval 5; one device; source options; entity states |
| U06 | [ha.display_unplugged](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/home_assistant.py) | ha / V3 | H / F-HA-009 | B | 3/0 | 0 | output 1 disconnected; HA connected sensor on→off |
| U07 | [ha.front_panel_route](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/home_assistant.py) | ha / V3 | H / F-HA-002 | B | 3/0 | 0 | output 2→input 6; HA select AppleTV→PS5 |
| U08 | [ha.input_signal](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/home_assistant.py) | ha / V3 | H / F-HA-008 | B | 3/0 | 0 | input 3 signal=1; HA sensor off→on |
| U09 | [ha.matrix_offline](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/home_assistant.py) | ha / V3 | H / F-HA-013 | B | 3/0 | 0 | HA source unavailable then AppleTV after recovery |
| U10 | [ha.matrix_unreachable](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/home_assistant.py) | ha / V3 | H / F-HA-013 | B | 6/0 | 0 | expected HA 500; unchanged device; HA entities unavailable |
| U11 | [ha.mute_switch](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/home_assistant.py) | ha / V3 | H / F-HA-004 | B | 6/0 | 0 | mute output 2; exact write; HA switch off→on |
| U12 | [ha.power_off](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/home_assistant.py) | ha / V3 | H / F-HA-003 | B | 6/0 | 0 | standby; exact write; HA power on→off |
| U13 | [ha.power_on](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/home_assistant.py) | ha / V3 | H / F-HA-003 | B | 5/0 | 0 | power=1; exact write; HA power off→on |
| U14 | [ha.preset_button](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/home_assistant.py) | ha / V3 | H / F-HA-006 | B | 6/0 | 0 | preset 3; routing all 6; HA source→PS5 |
| U15 | [ha.reboot_button](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/home_assistant.py) | ha / V3 | H / F-HA-007 | B | 3/0 | 0 | HA response 200; Telnet reboot command |
| U16 | [ha.reconfigure](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/home_assistant.py) | ha / V3 | H / F-HA-016 | B | 5/0 | 0 | entry loaded; HA source AppleTV; no device writes |
| U17 | [ha.select_source](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/home_assistant.py) | ha / V3 | H / F-HA-002 | B | 6/0 | 0 | output 1→6; exact write; HA source AppleTV→PS5 |
| U18 | [ha.service_cec_display](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/home_assistant.py) | ha / V3 | H / F-HA-012 | B | 4/0 | 0 | expected display CEC command once; unchanged device |
| U19 | [ha.service_cec_invalid](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/home_assistant.py) | ha / V3 | H / F-HA-012 | B | 4/0 | 0 | expected HA 400; no writes; unchanged device |
| U20 | [ha.service_cec_source](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/home_assistant.py) | ha / V3 | H / F-HA-012 | B | 3/0 | 0 | expected source CEC command once |
| U21 | [ha.service_recall_preset](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/home_assistant.py) | ha / V3 | H / F-HA-010 | B | 5/0 | 0 | preset 2; routing all 5; HA source→Shield |
| U22 | [ha.service_switch_input](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/home_assistant.py) | ha / V3 | H / F-HA-011 | B | 6/0 | 0 | output 2→5; exact write; HA source→Shield |
| U23 | [ha.stream_switch](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/home_assistant.py) | ha / V3 | H / F-HA-005 | B | 6/0 | 0 | output 3 stream=0; exact write; HA switch on→off |
| U24 | [kiosk.route_all_apply](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/kiosk.py) | browser / V3 | A / F-KIO-003 | B | 19/0 | 1 | all routes→5; parameters retained; no parameter writes; success toast |
| U25 | [kiosk.route_one_muted](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/kiosk.py) | browser / V3 | A / F-KIO-002 | B | 10/0 | 1 | output 3→3 and muted; exact mute; no unrelated writes; success toast |
| U26 | [preset_read.catalog_matches_device](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/preset_readback.py) | api / V2 | A / F-MTX-030 | B | 6/0 | 0 | all eight slots equal device; no writes/change/warnings |
| U27 | [preset_read.device_slot_1](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/preset_readback.py) | api / V2 | A / F-MTX-030 | B | 11/0 | 0 | slot 1 device routing=hub; matrix origin; exact Telnet read; no writes |
| U28 | [preset_read.device_slot_2](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/preset_readback.py) | api / V2 | A / F-MTX-030 | B | 11/0 | 0 | slot 2 device routing=hub; matrix origin; exact Telnet read; no writes |
| U29 | [preset_read.device_slot_3](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/preset_readback.py) | api / V2 | A / F-MTX-030 | B | 11/0 | 0 | slot 3 device routing=hub; matrix origin; exact Telnet read; no writes |
| U30 | [preset_read.device_slot_4](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/preset_readback.py) | api / V2 | A / F-MTX-030 | B | 11/0 | 0 | slot 4 device routing=hub; matrix origin; exact Telnet read; no writes |
| U31 | [preset_read.device_slot_5](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/preset_readback.py) | api / V2 | A / F-MTX-030 | B | 11/0 | 0 | slot 5 device routing=hub; matrix origin; exact Telnet read; no writes |
| U32 | [preset_read.device_slot_6](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/preset_readback.py) | api / V2 | A / F-MTX-030 | B | 11/0 | 0 | slot 6 device routing=hub; matrix origin; exact Telnet read; no writes |
| U33 | [preset_read.device_slot_7](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/preset_readback.py) | api / V2 | A / F-MTX-030 | B | 11/0 | 0 | slot 7 device routing=hub; matrix origin; exact Telnet read; no writes |
| U34 | [preset_read.device_slot_8](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/preset_readback.py) | api / V2 | A / F-MTX-030 | B | 11/0 | 0 | slot 8 device routing=hub; matrix origin; exact Telnet read; no writes |
| U35 | [preset_read.saved_current_1](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/preset_readback.py) | api / V2 | A / F-MTX-004 | B | 11/0 | 0 | saved slot 1; full device=hub routing; matrix origin; no writes |
| U36 | [preset_read.saved_current_2](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/preset_readback.py) | api / V2 | A / F-MTX-004 | B | 11/0 | 0 | saved slot 2; full device=hub routing; matrix origin; no writes |
| U37 | [preset_read.saved_current_3](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/preset_readback.py) | api / V2 | A / F-MTX-004 | B | 11/0 | 0 | saved slot 3; full device=hub routing; matrix origin; no writes |
| U38 | [preset_read.saved_current_4](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/preset_readback.py) | api / V2 | A / F-MTX-004 | B | 11/0 | 0 | saved slot 4; full device=hub routing; matrix origin; no writes |
| U39 | [preset_read.saved_current_5](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/preset_readback.py) | api / V2 | A / F-MTX-004 | B | 11/0 | 0 | saved slot 5; full device=hub routing; matrix origin; no writes |
| U40 | [preset_read.saved_current_6](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/preset_readback.py) | api / V2 | A / F-MTX-004 | B | 11/0 | 0 | saved slot 6; full device=hub routing; matrix origin; no writes |
| U41 | [preset_read.saved_current_7](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/preset_readback.py) | api / V2 | A / F-MTX-004 | B | 11/0 | 0 | saved slot 7; full device=hub routing; matrix origin; no writes |
| U42 | [preset_read.saved_current_8](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/preset_readback.py) | api / V2 | A / F-MTX-004 | B | 11/0 | 0 | saved slot 8; full device=hub routing; matrix origin; no writes |
| U43 | [preset_read.saved_partial_1](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/preset_readback.py) | api / V2 | A / F-DOM-034 | B | 11/0 | 0 | partial saved slot 1; device=hub; no fabricated routes/writes |
| U44 | [preset_read.saved_partial_2](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/preset_readback.py) | api / V2 | A / F-DOM-034 | B | 11/0 | 0 | partial saved slot 2; device=hub; no fabricated routes/writes |
| U45 | [preset_read.saved_partial_3](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/preset_readback.py) | api / V2 | A / F-DOM-034 | B | 11/0 | 0 | partial saved slot 3; device=hub; no fabricated routes/writes |
| U46 | [preset_read.saved_partial_4](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/preset_readback.py) | api / V2 | A / F-DOM-034 | B | 11/0 | 0 | partial saved slot 4; device=hub; no fabricated routes/writes |
| U47 | [preset_read.saved_partial_5](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/preset_readback.py) | api / V2 | A / F-DOM-034 | B | 11/0 | 0 | partial saved slot 5; device=hub; no fabricated routes/writes |
| U48 | [preset_read.saved_partial_6](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/preset_readback.py) | api / V2 | A / F-DOM-034 | B | 11/0 | 0 | partial saved slot 6; device=hub; no fabricated routes/writes |
| U49 | [preset_read.saved_partial_7](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/preset_readback.py) | api / V2 | A / F-DOM-034 | B | 11/0 | 0 | partial saved slot 7; device=hub; no fabricated routes/writes |
| U50 | [preset_read.saved_partial_8](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/preset_readback.py) | api / V2 | A / F-DOM-034 | B | 11/0 | 0 | partial saved slot 8; device=hub; no fabricated routes/writes |
| U51 | [presets.recall](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/presets.py) | api / V2 | A / F-MTX-003 | B | 6/0 | 0 | preset 3 command once; routing equals device slot; no unrelated changes |
| U52 | [presets.recall](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/presets.py) | browser / V3 | A / F-MTX-003 | B | 6/0 | 1 | preset 3 command once; routing equals device slot; no unrelated changes |
| U53 | [reboot.enabled_shortcut](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/reboot.py) | api / V2 | A / F-MTX-021 | B | 11/1 | 0 | one Telnet reboot; link loss/recovery; health/Telnet return; state retained |
| U54 | [reboot.enabled_shortcut](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/reboot.py) | browser / V3 | A / F-MTX-021 | B | 12/0 | 1 | one Telnet reboot; link loss/recovery; health/Telnet return; state retained |
| U55 | [routing.route_all](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/routing.py) | api / V2 | A / F-MTX-002 | B | 7/0 | 0 | all routes→4; exact command; routing_change; hub readback |
| U56 | [routing.route_all](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/routing.py) | browser / V3 | A / F-MTX-002 | B | 7/0 | 1 | all routes→4; exact command; routing_change; hub readback |
| U57 | [routing.switch_one](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/routing.py) | api / V2 | A / F-MTX-001 | B | 7/0 | 0 | output 1→6; exact command; routing_change; hub readback |
| U58 | [routing.switch_one](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/routing.py) | browser / V3 | A / F-MTX-001 | B | 7/0 | 1 | output 1→6; exact command; routing_change; hub readback |
| U59 | [shortcuts.preset_recall](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/shortcuts.py) | api / V2 | A / F-DOM-026 | B | 5/1 | 0 | routing all 6; preset 3 command once; unchanged other state |
| U60 | [shortcuts.preset_recall](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/shortcuts.py) | browser / V3 | A / F-DOM-026 | B | 6/0 | 1 | routing all 6; preset 3 command once; unchanged other state |

There are **470 passing and two nonapplicable checks**, with zero failed checks, schema errors, missing expected assertion descriptions, feature/client mapping mismatches, cover mismatches or missing screenshot references among the 56 records. Every scenario expectation description occurs in its matching record; each record also contains the runner’s WebSocket schema check. This is static inspection of actual execution records and scenario assertions, not a repeat execution or a new independent evaluation of all check predicates.

The two nonapplicable rows are U53 and U59: `client shows toast.success == 'Shortcut executed'` is browser-only, with exact recorded reason `not checked for client 'api'`. Browser counterparts U54/U60 pass the toast assertion. HA U10’s HTTP 500 and U19’s HTTP 400 are expected negative responses with unchanged-device assertions, not failed runs. No known-failure waiver, blocked record or target reduction was applied.

The 56 selected executions span `2026-10-28T21:18:07.379Z` through `2026-10-28T21:27:22.981Z`. All record the hub entry `run.py -> hub.cli shared runtime (UC_ENABLED=false)` and **hub image_digest=null**: they prove source-run simulator behavior, not an executed release image. The seven browser records identify Playwright and `chromium 153.0.8010.12`, contain real browser screenshots and assertions; API labels were not used as browser proof. The 19 HA records identify a real `homeassistant/home-assistant:2026.9.3` container, component `custom_components/hdmi_matrix 1.0.0rc1`, and client image digest `homeassistant/home-assistant@sha256:d8922685169707fd91e8b9729902d975f06157d005e422874d201e0261dda196`. That client digest is not a hub image digest or exact HA minimum-version proof.

Outside the selected units, A contains 1,433 API, 62 browser and 18 scripted UC records; all are `pass/ok`. UC metadata identifies `tools/uc_remote_sim.py (scripted Remote 3)` and a UC-enabled hub mode. Those executions do not replace a browser, Flic, physical Remote or HA proof unit. H contains 19 records, all selected here and `pass/ok`. A’s CI command selected only `api,browser,uc`; H selected `ha`, explaining the absent Flic units.

## Disposition for the 38 freshness rows

Targets and recorded baselines below are read from frozen-base `features.yaml` without edits. “Admission” means CI records exist but the synthetic-source ancestry issue remains; it is not a qualification or permission to import. V4/V5 targets still require their separately owned hardware/field evidence.

| Feature | Target / recorded | Requested units | Matched / missing | Next disposition |
| --- | --- | --- | ---: | --- |
| F-API-005 | V3 / V2 | U55, U57 | 2 / 0 | Coordinator ancestry/adoption decision |
| F-API-007 | V3 / V2 | U51 | 1 / 0 | Coordinator ancestry/adoption decision |
| F-API-008 | V2 / V1 | U35, U36, U37, U38, U39, U40, U41, U42, U43, U44, U45, U46, U47, U48, U49, U50 | 16 / 0 | Coordinator ancestry/adoption decision |
| F-API-013 | V2 / V1 | U53, U54 | 2 / 0 | Coordinator ancestry/adoption decision |
| F-API-035 | V3 / V2 | U51 | 1 / 0 | Coordinator ancestry/adoption decision |
| F-DOM-026 | V3 / V2 | U59, U60 | 2 / 0 | Coordinator ancestry/adoption decision |
| F-DOM-034 | V3 / V1 | U43, U44, U45, U46, U47, U48, U49, U50 | 8 / 0 | Coordinator ancestry/adoption decision |
| F-FLIC-001 | V3 / V1 | U04 | 0 / 1 | Flic execution refresh required |
| F-FLIC-002 | V3 / V1 | U02, U03 | 0 / 2 | Flic execution refresh required |
| F-FLIC-008 | V3 / V0 | U01 | 0 / 1 | Flic execution refresh required |
| F-HA-001 | V4 / V3 | U05 | 1 / 0 | Coordinator ancestry/adoption decision |
| F-HA-002 | V4 / V3 | U07, U17 | 2 / 0 | Coordinator ancestry/adoption decision |
| F-HA-003 | V4 / V3 | U12, U13 | 2 / 0 | Coordinator ancestry/adoption decision |
| F-HA-004 | V4 / V3 | U11 | 1 / 0 | Coordinator ancestry/adoption decision |
| F-HA-005 | V4 / V3 | U23 | 1 / 0 | Coordinator ancestry/adoption decision |
| F-HA-006 | V4 / V3 | U14 | 1 / 0 | Coordinator ancestry/adoption decision |
| F-HA-007 | V4 / V3 | U15 | 1 / 0 | Coordinator ancestry/adoption decision |
| F-HA-008 | V4 / V3 | U08 | 1 / 0 | Coordinator ancestry/adoption decision |
| F-HA-009 | V4 / V3 | U06 | 1 / 0 | Coordinator ancestry/adoption decision |
| F-HA-010 | V4 / V3 | U21 | 1 / 0 | Coordinator ancestry/adoption decision |
| F-HA-011 | V4 / V3 | U22 | 1 / 0 | Coordinator ancestry/adoption decision |
| F-HA-012 | V4 / V3 | U18, U19, U20 | 3 / 0 | Coordinator ancestry/adoption decision |
| F-HA-013 | V4 / V3 | U06, U07, U08, U09, U10 | 5 / 0 | Coordinator ancestry/adoption decision |
| F-HA-015 | V4 / V3 | U05 | 1 / 0 | Coordinator ancestry/adoption decision |
| F-HA-016 | V4 / V3 | U16 | 1 / 0 | Coordinator ancestry/adoption decision |
| F-HA-017 | V4 / V3 | U05 | 1 / 0 | Coordinator ancestry/adoption decision |
| F-HA-018 | V4 / V3 | U21, U22 | 2 / 0 | Coordinator ancestry/adoption decision |
| F-KIO-002 | V3 / V3 | U25 | 1 / 0 | Coordinator ancestry/adoption decision |
| F-KIO-003 | V3 / V3 | U24 | 1 / 0 | Coordinator ancestry/adoption decision |
| F-MTX-002 | V4 / V3 | U55, U56 | 2 / 0 | Coordinator ancestry/adoption decision |
| F-MTX-004 | V4 / V1 | U35, U36, U37, U38, U39, U40, U41, U42 | 8 / 0 | Coordinator ancestry/adoption decision |
| F-MTX-021 | V4 / V1 | U53, U54 | 2 / 0 | Coordinator ancestry/adoption decision |
| F-MTX-030 | V4 / V1 | U26, U27, U28, U29, U30, U31, U32, U33, U34 | 9 / 0 | Coordinator ancestry/adoption decision |
| F-REL-001 | V4 / V0 | U53, U54 | 2 / 0 | Coordinator ancestry/adoption decision |
| F-REL-005 | V4 / V0 | U53, U54 | 2 / 0 | Coordinator ancestry/adoption decision |
| F-UI-002 | V3 / V3 | U58 | 1 / 0 | Coordinator ancestry/adoption decision |
| F-UI-004 | V3 / V1 | U56 | 1 / 0 | Coordinator ancestry/adoption decision |
| F-UI-005 | V3 / V1 | U52 | 1 / 0 | Coordinator ancestry/adoption decision |

Thus 35 feature rows have all requested execution units available, pending admission, and three Flic rows lack four execution units. Neither availability nor a fresh V2/V3 record fulfills a higher target automatically.

## Separate F-API-034 assertion gap and next action

[routing.route_all](https://github.com/ryan-haver/8x8-hdmi-matrix-hub/blob/bdcf06dc6723aad7da63ecfed3d3555ab0d02e55/tests/validation/scenarios/routing.py) records HTTP 200, all eight routes→4, one `video switch` command, `routing_change`, hub readback and WebSocket schema compliance. No discovered scenario expectation declares `switch_all_failed`. The feature ID on that success record does **not** prove the named all-output failure event. F-API-034 remains a separate assertion gap requiring separately authorized scenario/assertion work, qualified different-family review and an actual negative-path execution; no implementation was made here.

The coordinator should first preserve and independently check these raw archives and 56 record mappings, then decide the synthetic-merge ancestry admission route under repository policy. A documented inspected source/tree equivalence could inform an explicitly authorized policy/adoption decision, while retaining the actual source SHA; it is not admitted by current freshness code. If no compliant admission is available, refresh those 56 units from the current approved integration source so normal ancestry succeeds. Do not rewrite SHA metadata or make the synthetic merge an ancestor through history manipulation.

The four Flic units genuinely need new execution for this CI intake scope; use the existing generated-request/Node replay client with its actual provenance, not an API or physical-button label. No rerun was launched. The unsupported all-output failure assertion needs its own scoped follow-up. The unintegrated redaction source/review gate remains independent, its quota unknown, and VAL-15 remains open; this report neither inspected that author checkout nor certifies artifact redaction.

## Commands, checks and limits

| Invocation / check | Exit / result |
| --- | --- |
| `orca skills get orchestration --json`, `orca skills get orca-cli --json`, status and own FIFO checks | 0; existing Run/runtime and empty checkpoint inbox verified |
| `gh api repos/ryan-haver/8x8-hdmi-matrix-hub/actions/artifacts/{12853945294,12853275385}` and each `/zip`; run/jobs metadata | 0; raw binary writes, both digest matches and ZIP CRC pass |
| `gh api …/actions/jobs/{123106264167,123106264102}/logs` (first two attempts) | 1 each: gh refused terminal escape sequences; empty stdout attempts retained, second-attempt stderr retained |
| Same two job-log commands with `--allow-escape-sequences` and binary capture | 0 each; original successful bytes retained in fresh attempt-03 |
| Frozen-base scenario discovery; Draft202012Validator with FormatChecker; exact descriptions/features/covers comparison | 0; 56 schemas valid, no missing expected descriptions; private analysis invocation only |
| Cached `git cat-file`, `merge-base --is-ancestor`, `diff --name-only`, `rev-parse` via subprocess argv | 0 except source ancestor=1, intentionally reported as nonancestor; exact argv/exits retained |
| First PowerShell unquoted `^{tree}` probe | failed from brace/argument interpretation; numeric exit was not separately captured, corrected subprocess-argv probes exit 0, no ref mutation |
| Optional Pillow PNG probe | 1: `ModuleNotFoundError: No module named 'PIL'`; no dependency install; standard-library PNG signature/chunk CRC verification subsequently passed for all seven |
| First status notification using unsupported Orca type `note` | 1, rejected without delivery; corrected `status` message succeeded |
| Report UTF-8, local link/anchor and remote-link structure checks; CR-aware `git diff --check` | Run before report commit; final receipt retained privately |

The only tracked deliverable is this new report. Ignored invocation scripts and diagnostics are confined to the assigned task directory; immutable input, source, tests, schemas, scenarios, registry, canonical records, findings, ledger, manifests and lockfiles are unchanged. No source hooks, full suite, validation campaign, canonical validator/ledger generation, deployment, push, merge, tag, cleanup or release was run. The report-only commit uses the documented **invocation-only** `git -c core.hooksPath= commit` exception after actual report checks; no hook configuration is changed and no source-hook/full-suite pass is claimed. The coordinator owns independent report acceptance, publication, preservation and worker release.

Boundaries remain open: artifact adoption/freshness, four missing Flic executions, the F-API-034 negative-path assertion, unintegrated privacy implementation/review, hardware HIL, owner visual approval, 72-hour soak, week field sign-off and final version/artifact release. This is a bounded continuation of P1 SW-AUDIT-01 evidence preparation, not parent completion or a new phase.
