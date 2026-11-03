# Runtime field validation gate

Status: **pending owner execution and sign-off**. This runbook contains no field
results. Simulator, scripted Remote, request replay and local container runs
cannot establish physical matrix/CEC effects or the deployment host's behavior.
Use the accepted candidate's immutable Git commit and image digest throughout.
Record firmware, matrix model, host architecture, client versions, operator and
timestamps. Keep credentials and private configuration out of committed evidence.

## Before the session

1. Complete software review, CI and the approved release sequence in the
   [master plan](../planning/UNIFIED_MASTER_PLAN.md). Confirm the image digest and
   `/api/info` version agree with the candidate. Do not move an existing tag.
2. Back up the deployment data volume and verify restore procedures. Record the
   starting routing, presets, audio/video settings and power state. Identify
   disruptive commands before enabling writes. Use the existing
   [HIL session runbook](HIL_SESSION_2_RUNBOOK.md) and
   [capture tool guide](../../tools/hil/README.md) for safe capture procedures.
3. Select scenarios with `python -m tools.validate list`. Hardware runs require
   `--target hardware`, an explicit `--matrix-host` and a named `--operator`.
   Enable `--allow-writes` only for the agreed session; check restoration reports.
   `--allow-unrestorable` is a separate decision for disruptive operations.

## Flic and Home Assistant preparation

This checklist prepares the existing HIL-E session; every row is **pending for
the eventual accepted candidate** until a matching execution receipt is attached.
Historical simulator and container passes keep their original source and scope.
Software checks can use a simulator and disposable Home Assistant installation;
the owner deployment is needed only for the field observations below. Follow the
current source-review and evidence-admission gates before running dependent
campaigns or promoting results.

| Preparation | Required software receipt | Later field observation |
| --- | --- | --- |
| Candidate and setup | Exact Git SHA, image digest/platform, hub version from `/api/info`, selected scenario list and client versions; reconcile guide examples with the accepted candidate | Record matrix/firmware, Flic Hub/SDK/button models, HA version and deployment host; confirm the agreed devices and starting state |
| Flic generated actions | Existing SDK replay and generated-request cases for presets, power, cycling/Twist, profiles/macros, registration and all-output switching; retain the actual method/path/body and allowed/denied outcomes without publishing credentials | Trigger each selected physical click/hold/rotation, observe the intended output and ensure one intended action rather than duplicate execution |
| HA installation and flows | HACS custom-repository packaging and hassfest results; disposable real-HA config, reconfigure and options-flow receipts, with the tested component and HA versions | Install through the agreed HACS custom repository, add the deployed hub, change its address/options and confirm the correct device/entities remain associated |
| HA entities and services | Selects, switches, buttons and binary sensors; `hdmi_matrix.recall_preset`, `hdmi_matrix.switch_input` and `hdmi_matrix.send_cec_command`, including unambiguous config-entry/device targeting | Confirm entity names and state updates on the owner installation, and verify that a selected service targets only the intended matrix |
| Authentication | Keyless and control-lock cases, valid and invalid/revoked API-key outcomes, and permitted versus refused operations; reviewed artifacts before admission | Exercise the agreed credential configuration on both clients; a denied action must not change routing/device state |
| Offline and recovery | Existing isolated outage/reconnect cases with unavailable state, recovery and duplicate-action checks; retain failures as well as passes | Observe loss and recovery on the deployment LAN, including entity availability and the absence of an unintended action after reconnect |
| CEC and restoration | Simulator/source assertions with their actual limits, plus a selected reversible action/restoration plan | Observe the attached TV/source/receiver effect; API success or matrix readback alone does not prove a CEC effect. Restore the recorded starting state |

The declared HA floor in `hacs.json` is 2025.1.0. The historical 2025.1.4
container pass does not test that exact floor; reconcile this explicitly in
SW-HA-PREP before making a minimum-version acceptance claim. HACS
custom-repository installation and inclusion in the default HACS catalog are
separate claims; this checklist requires the former and grants neither a
catalog listing nor a release approval.

For each selected case, record the candidate SHA/digest, scenario, operator and
timestamps, client/device versions, expected and observed result, starting and
ending state, restoration result, and preserved evidence location. Keep secrets
and private deployment configuration out of committed receipts. Mark unavailable
equipment or an unexecuted case explicitly; do not turn it into a pass.

Use the [Flic setup guide](../FLIC_SETUP.md),
[Home Assistant guide](../HOME_ASSISTANT.md),
[runtime evidence index](RUNTIME_VALIDATION_INDEX.md) and the feature registry
to select the applicable cases. This preparation adds no execution result,
feature-level promotion, privacy clearance or owner sign-off.

## Required owner observations

| Gate | Record |
| --- | --- |
| HIL-B regression | Exact actions, matrix readback and observed input/output effects; restore starting state |
| HIL-C failure and recovery | Controlled network/device outage and recovery on the deployment host; last-known values, unavailable state, reconnect and absence of duplicate actions |
| HIL-E real clients | Physical Remote 3, deployed HA, browser/kiosk and available physical Flic hardware, including configured auth and denied-action behavior |
| Physical CEC | Source/TV/receiver power, navigation, playback, volume/mute and configuration readback; identify attached devices and firmware |
| HIL-D reliability | Continuous 72-hour resource record, outages/restarts and gaps, followed by the owner's week of daily-use sign-off |

Unavailable hardware must remain explicitly unvalidated. Device readback alone
does not prove that a TV or source performed the intended CEC effect.

## Collect deployment-host metrics

Run this on the deployment host after replacing the two required placeholders.
It polls health and Docker statistics only. It does not issue matrix actions.
Store the output outside the repository's runtime data volume. Retain failures
and timestamp gaps; a restarted collector does not imply an uninterrupted soak.

```powershell
$SoakHubUrl = '<owner deployment hub URL>'
$SoakContainer = '<owner deployment container name>'
$SoakOutput = Join-Path $PWD ('runtime-soak-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.jsonl')
$SoakUntil = [DateTimeOffset]::UtcNow.AddHours(72)
while ([DateTimeOffset]::UtcNow -lt $SoakUntil) {
    $sample = [ordered]@{ time = [DateTimeOffset]::UtcNow.ToString('o') }
    try {
        $health = (Invoke-RestMethod -Uri ($SoakHubUrl.TrimEnd('/') + '/api/health') -TimeoutSec 10).data
        $sample.status = $health.status
        $sample.connected = $health.matrix.connected
        $sample.runtime = $health.runtime
    } catch {
        $sample.health_error = $_.Exception.GetType().Name
    }
    $stats = docker stats --no-stream --format '{{json .}}' $SoakContainer 2>$null
    if ($LASTEXITCODE -eq 0) {
        $sample.docker = $stats | ConvertFrom-Json
    } else {
        $sample.docker_error = 'stats_failed'
    }
    $sample | ConvertTo-Json -Compress -Depth 6 | Add-Content -LiteralPath $SoakOutput
    Start-Sleep -Seconds 60
}
```

Record the image digest, container start time and restart count before and after
the soak. Review CPU, memory, PIDs, task count, event-loop lag and availability
over time; explain growth, every restart and missing samples. Preserve raw data
and a plotted report. A flat endpoint response without resource measurements
does not satisfy the reliability gate.

## Close the gate

Attach timestamped observations and approved media to the corresponding feature
evidence. Validate the evidence schema and run `python -m tools.validate check`
with the recorded summaries; regenerate the ledger only after evidence review.
The ledger must show every feature at its required target, with current evidence
and no unresolved blocking findings. Final publication also requires the visual
decision, independent review, CI and owner sign-off in the
[validation plan](VALIDATION_PLAN.md). Synchronize canonical metadata to `1.0.0`,
rebuild matching images and refresh affected evidence before the final tag.
