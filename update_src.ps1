# Define relative paths (assuming the script is inside the BrowZee-AI root folder)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$source = Join-Path $scriptDir "chromium_changes"
$destination = Join-Path $scriptDir "src"

# Copy all modified files while preserving folder structure
Get-ChildItem -Path $source -Recurse | ForEach-Object {
    if (-not $_.PSIsContainer) {
        $relativePath = $_.FullName.Substring($source.Length).TrimStart('\')
        $destPath = Join-Path $destination $relativePath
        $destDir = Split-Path $destPath

        if (-Not (Test-Path $destDir)) {
            New-Item -Path $destDir -ItemType Directory -Force | Out-Null
        }

        Copy-Item -Path $_.FullName -Destination $destPath -Force
    }
}

Write-Host "✅ All changes copied into BrowZee-AI/src"