param(
  [string]$RepoPath = "."
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

node (Join-Path $ScriptDir "collect-truth-pressure-live-source.mjs") $RepoPath

$ResolvedRepo = (Resolve-Path $RepoPath).Path
$Source = Join-Path $ResolvedRepo "_truth-pressure-live-source-extract"
$Zip = Join-Path $ResolvedRepo "truth-pressure-live-source-extract.zip"

if (Test-Path $Zip) {
  Remove-Item $Zip -Force
}

Compress-Archive -Path $Source -DestinationPath $Zip

Write-Host ""
Write-Host "Created:"
Write-Host "  $Zip"
