<#
.SYNOPSIS
    Scrape icons from Shaper Studio's icon API (powered by The Noun Project)

.DESCRIPTION
    This script queries the icons.shapertools.com API to download SVG icons.
    The API requires only an Origin header spoof - no authentication needed.
    
    Icons are licensed under Creative Commons Attribution.
    Attribution format: "{term} by {creator.name} from Noun Project"

.PARAMETER SearchTerms
    Array of search terms to scrape icons for (e.g., "tv", "gaming", "hdmi")

.PARAMETER OutputDir
    Directory to save downloaded SVG files

.PARAMETER LimitPerTerm
    Maximum icons to download per search term (default: 100)

.PARAMETER Styles
    Filter by icon style: "all", "line", "solid" (default: "all")

.EXAMPLE
    .\scrape-shaper-icons.ps1 -SearchTerms @("tv", "gaming", "projector") -OutputDir ".\icons"
#>

param(
    [Parameter(Mandatory = $false)]
    [string[]]$SearchTerms = @(
        # Displays
        "tv", "monitor", "projector", "screen", "display",
        # Gaming consoles
        "playstation", "xbox", "nintendo", "switch", "gaming console", "game controller",
        "ps5", "ps4", "wii", "gamepad", "joystick",
        # Streaming devices
        "roku", "chromecast", "fire tv", "apple tv", "streaming",
        # Video/Audio
        "hdmi", "video", "blu-ray", "dvd", "receiver", "speaker", "audio",
        # Computers
        "laptop", "computer", "pc", "mac", "desktop",
        # Rooms
        "living room", "bedroom", "home theater", "office",
        # Misc devices
        "cable box", "satellite", "antenna", "camera", "security"
    ),
    
    [Parameter(Mandatory = $false)]
    [string]$OutputDir = ".\scraped-icons",
    
    [Parameter(Mandatory = $false)]
    [int]$LimitPerTerm = 50,
    
    [Parameter(Mandatory = $false)]
    [ValidateSet("all", "line", "solid")]
    [string]$Styles = "all",
    
    [Parameter(Mandatory = $false)]
    [switch]$DownloadSvg,
    
    [Parameter(Mandatory = $false)]
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# API Configuration
$API_BASE = "https://icons.shapertools.com"
$HEADERS = @{
    "Accept"     = "application/json, text/plain, */*"
    "Origin"     = "https://studio.shapertools.com"
    "Referer"    = "https://studio.shapertools.com/"
    "User-Agent" = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Create output directories
$metadataDir = Join-Path $OutputDir "metadata"
$svgDir = Join-Path $OutputDir "svg"
$thumbnailDir = Join-Path $OutputDir "thumbnails"

New-Item -ItemType Directory -Path $metadataDir -Force | Out-Null
if ($DownloadSvg) {
    New-Item -ItemType Directory -Path $svgDir -Force | Out-Null
    New-Item -ItemType Directory -Path $thumbnailDir -Force | Out-Null
}

# Track all icons
$allIcons = @{}
$stats = @{
    TotalSearches   = 0
    TotalIconsFound = 0
    UniqueIcons     = 0
    DownloadedSvg   = 0
    Errors          = 0
}

function Search-Icons {
    param(
        [string]$Query,
        [int]$Limit = 30,
        [string]$NextPage = $null
    )
    
    $url = "$API_BASE/search?iconquery=$([uri]::EscapeDataString($Query))&limit=$Limit"
    if ($NextPage) {
        $url += "&next_page=$NextPage"
    }
    
    try {
        $response = Invoke-RestMethod -Uri $url -Headers $HEADERS -TimeoutSec 30
        return $response
    }
    catch {
        Write-Warning "API Error for '$Query': $_"
        $script:stats.Errors++
        return $null
    }
}

function Download-Svg {
    param(
        [hashtable]$Icon
    )
    
    $svgPath = Join-Path $svgDir "$($Icon.id).svg"
    
    if ((Test-Path $svgPath) -and -not $Force) {
        Write-Verbose "SVG already exists: $svgPath"
        return $true
    }
    
    try {
        # SVG URLs are time-limited signed URLs - use WebRequest to preserve content
        Invoke-WebRequest -Uri $Icon.icon_url -OutFile $svgPath -TimeoutSec 30
        return $true
    }
    catch {
        Write-Warning "Failed to download SVG $($Icon.id): $_"
        return $false
    }
}

function Filter-ByStyle {
    param(
        [array]$Icons,
        [string]$StyleFilter
    )
    
    if ($StyleFilter -eq "all") {
        return $Icons
    }
    
    return $Icons | Where-Object {
        $iconStyles = $_.styles | ForEach-Object { $_.style }
        $StyleFilter -in $iconStyles
    }
}

# Main scraping loop
Write-Host "`n=== Shaper Studio Icon Scraper ===" -ForegroundColor Cyan
Write-Host "Search terms: $($SearchTerms.Count)"
Write-Host "Limit per term: $LimitPerTerm"
Write-Host "Style filter: $Styles"
Write-Host "Download SVGs: $DownloadSvg"
Write-Host "Output: $OutputDir`n"

foreach ($term in $SearchTerms) {
    Write-Host "`nSearching: '$term'..." -ForegroundColor Yellow
    $stats.TotalSearches++
    
    $collected = 0
    $nextPage = $null
    
    while ($collected -lt $LimitPerTerm) {
        $remaining = $LimitPerTerm - $collected
        $batchSize = [Math]::Min(100, $remaining)
        
        $result = Search-Icons -Query $term -Limit $batchSize -NextPage $nextPage
        
        if (-not $result -or -not $result.icons -or $result.icons.Count -eq 0) {
            break
        }
        
        # Filter by style
        $filteredIcons = Filter-ByStyle -Icons $result.icons -StyleFilter $Styles
        
        foreach ($icon in $filteredIcons) {
            $stats.TotalIconsFound++
            
            # Skip duplicates
            if ($allIcons.ContainsKey($icon.id)) {
                continue
            }
            
            # Store icon metadata
            $iconData = @{
                id            = $icon.id
                term          = $icon.term
                search_term   = $term
                attribution   = $icon.attribution
                license       = $icon.license_description
                icon_url      = $icon.icon_url
                thumbnail_url = $icon.thumbnail_url
                permalink     = $icon.permalink
                tags          = $icon.tags
                styles        = $icon.styles
                creator       = $icon.creator
                collections   = $icon.collections
            }
            
            $allIcons[$icon.id] = $iconData
            $stats.UniqueIcons++
            $collected++
            
            # Download SVG if requested
            if ($DownloadSvg) {
                if (Download-Svg -Icon $iconData) {
                    $stats.DownloadedSvg++
                }
                # Rate limiting
                Start-Sleep -Milliseconds 100
            }
            
            if ($collected -ge $LimitPerTerm) {
                break
            }
        }
        
        # Pagination
        if ($result.next_page -and $collected -lt $LimitPerTerm) {
            $nextPage = $result.next_page
            Write-Host "  Fetching more... (${collected}/${LimitPerTerm})" -ForegroundColor DarkGray
        }
        else {
            break
        }
    }
    
    Write-Host "  Found $collected unique icons for '$term'" -ForegroundColor Green
    
    # Be nice to the API
    Start-Sleep -Milliseconds 500
}

# Save metadata catalog
$catalogPath = Join-Path $metadataDir "icon-catalog.json"
$catalog = @{
    generated_at = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    total_icons  = $allIcons.Count
    search_terms = $SearchTerms
    style_filter = $Styles
    icons        = $allIcons.Values | Sort-Object { $_.id }
}

$catalog | ConvertTo-Json -Depth 10 | Out-File -FilePath $catalogPath -Encoding UTF8

# Generate attribution file
$attributionPath = Join-Path $OutputDir "ATTRIBUTIONS.md"
$attribution = @"
# Icon Attributions

These icons are from The Noun Project via Shaper Studio.
All icons are licensed under **Creative Commons Attribution (CC BY)**.

## Required Attribution

When using these icons, you must provide attribution. Example:
> Icons by various creators from [The Noun Project](https://thenounproject.com/)

## Individual Attributions

| Icon ID | Attribution |
|---------|-------------|
"@

foreach ($icon in ($allIcons.Values | Sort-Object { $_.id })) {
    $attribution += "`n| $($icon.id) | $($icon.attribution) |"
}

$attribution | Out-File -FilePath $attributionPath -Encoding UTF8

# Summary
Write-Host "`n=== Scraping Complete ===" -ForegroundColor Cyan
Write-Host "Total searches: $($stats.TotalSearches)"
Write-Host "Total icons found: $($stats.TotalIconsFound)"
Write-Host "Unique icons: $($stats.UniqueIcons)" -ForegroundColor Green
if ($DownloadSvg) {
    Write-Host "SVGs downloaded: $($stats.DownloadedSvg)" -ForegroundColor Green
}
Write-Host "Errors: $($stats.Errors)" -ForegroundColor $(if ($stats.Errors -gt 0) { "Red" } else { "Green" })
Write-Host "`nCatalog saved to: $catalogPath"
Write-Host "Attributions saved to: $attributionPath"

# Return catalog for pipeline use
return $catalog
