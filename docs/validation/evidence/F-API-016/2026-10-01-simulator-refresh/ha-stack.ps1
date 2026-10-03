param([ValidateSet('api','browser','ha')][string]$TaskClient = 'api')
$ErrorActionPreference = 'Stop'
$taskRoot = 'C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration'
$taskImage = 'hdmi-matrix-hub:wp-simulator-evidence-refresh'
$taskSuffix = [Guid]::NewGuid().ToString('N').Substring(0, 12)
$taskNetwork = "refresh-proof-net-$taskSuffix"
$taskVolume = "refresh-proof-data-$taskSuffix"
$taskSim = "refresh-proof-sim-$taskSuffix"
$taskHub = "refresh-proof-hub-$taskSuffix"
$taskRunner = "refresh-proof-runner-$taskSuffix"
function Invoke-TaskDocker {
    & docker @args
    if ($LASTEXITCODE -ne 0) { throw "Docker failed: $($args[0])" }
}
function Get-TaskPort {
    $taskListener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 0)
    $taskListener.Start()
    $taskPort = $taskListener.LocalEndpoint.Port
    $taskListener.Stop()
    return $taskPort
}
function Wait-TaskHealth([string] $taskUrl) {
    $taskDeadline = [DateTime]::UtcNow.AddSeconds(90)
    do {
        try { Invoke-RestMethod -Uri $taskUrl -TimeoutSec 2 | Out-Null; return } catch { Start-Sleep -Milliseconds 500 }
    } while ([DateTime]::UtcNow -lt $taskDeadline)
    throw "Health check timed out: $taskUrl"
}
$taskControl = Get-TaskPort
$taskApi = Get-TaskPort
try {
    Invoke-TaskDocker network create $taskNetwork
    Invoke-TaskDocker volume create $taskVolume
    Invoke-TaskDocker run --rm --user root -v "${taskVolume}:/data" -v "${taskRoot}/tests/e2e/fixtures/data:/fixtures:ro" --entrypoint sh $taskImage -c 'cp /fixtures/*.json /data/; chown -R appuser:app /data'
    Invoke-TaskDocker run -d --name $taskSim --network $taskNetwork --network-alias domain-matrix -p "127.0.0.1:${taskControl}:8444" --no-healthcheck hdmi-matrix-hub-sim:deploy-test python -m tools.simulator --host 0.0.0.0 --https-port 8443 --telnet-port 2323 --control-port 8444 --reboot-seconds 3
    Wait-TaskHealth "http://127.0.0.1:${taskControl}/_sim/health"
    Invoke-TaskDocker run -d --name $taskHub --network $taskNetwork -p "127.0.0.1:${taskApi}:8080" -v "${taskVolume}:/data" -e MATRIX_HOST=domain-matrix -e MATRIX_PORT=8443 -e OREI_TELNET_PORT=2323 -e UC_ENABLED=false -e TRUST_PROXY_HEADERS=true -e 'TRUSTED_PROXY_IPS=127.0.0.1,172.16.0.0/12,192.168.0.0/16' $taskImage
    Wait-TaskHealth "http://127.0.0.1:${taskApi}/api/health"
    $taskDigest = Invoke-TaskDocker image inspect -f '{{.Id}}' $taskImage
    $taskSource = & git rev-parse HEAD
    @{ image = $taskImage; digest = $taskDigest; source_commit = $taskSource; simulator = $taskSim; hub = $taskHub; scope = 'Disposable simulator and fixture data; no real hardware'; client = $TaskClient; selection = "build/refresh-selection-$TaskClient.json" } | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath "$taskRoot/build/refresh-image-stack-$TaskClient.json" -Encoding utf8
    $taskClientMounts = @()
    if ($TaskClient -eq 'ha') {
        $taskClientMounts = @('-v', '/var/run/docker.sock:/var/run/docker.sock', '-e', 'PATH=/work/build/refresh-bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin')
    }
    Invoke-TaskDocker run @taskClientMounts --rm --init --name $taskRunner --shm-size=1g -v "${taskRoot}:/work" -v hdmi-hub-ui-node-modules:/work/node_modules -v hdmi-hub-ui-cache:/cache -w /work mcr.microsoft.com/playwright:v1.63.0-noble bash build/refresh-ha-record.sh --client $TaskClient --target sim --sim-control-url "http://host.docker.internal:$taskControl" --hub-url "http://host.docker.internal:$taskApi" --hub-image-digest $taskDigest
} finally {
    $taskRemaining = @(& docker ps -a --format '{{.Names}}')
    foreach ($taskName in @($taskRunner, $taskHub, $taskSim)) {
        if ($taskRemaining -contains $taskName) { Invoke-TaskDocker rm -f $taskName }
    }
    & docker volume rm $taskVolume 2>$null
    & docker network rm $taskNetwork 2>$null
}
