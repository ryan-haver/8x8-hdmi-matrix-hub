#!/usr/bin/env pwsh
# Helper script to cleanly restart the integration driver
# Note: mDNS conflicts are a dev-environment issue only; Docker handles this cleanly

$projectRoot = Split-Path -Parent $PSScriptRoot

Write-Host "Stopping any running driver processes..." -ForegroundColor Yellow

# Kill all Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Remove any stale lock files
$lockFile = Join-Path (Join-Path $projectRoot "src") "driver.lock"
if (Test-Path $lockFile) {
    Remove-Item $lockFile -Force -ErrorAction SilentlyContinue
    Write-Host "Removed stale lock file" -ForegroundColor Yellow
}

# Wait for mDNS TTL to expire (5 seconds is sufficient)
Write-Host "Waiting 5 seconds for mDNS cache to clear..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "Starting driver..." -ForegroundColor Green
Set-Location $projectRoot
python run.py
