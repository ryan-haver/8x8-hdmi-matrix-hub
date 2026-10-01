$ErrorActionPreference = 'Stop'
$taskRoot = 'C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration'
New-Item -ItemType Directory -Path "$taskRoot/build/refresh-bin" -Force | Out-Null
$taskName = "refresh-cli-copy-$([Guid]::NewGuid().ToString('N').Substring(0,8))"
try {
    & docker create --name $taskName docker:29-cli
    if ($LASTEXITCODE -ne 0) { throw 'Docker CLI staging failed' }
    & docker cp "${taskName}:/usr/local/bin/docker" "$taskRoot/build/refresh-bin/docker"
    if ($LASTEXITCODE -ne 0) { throw 'Docker CLI copy failed' }
} finally {
    & docker rm $taskName
}