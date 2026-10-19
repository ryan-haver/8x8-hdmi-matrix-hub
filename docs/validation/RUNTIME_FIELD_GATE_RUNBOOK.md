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
