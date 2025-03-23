$source = "C:\Users\youruser\chromium_ai_browser\chromium_changes"
$destination = "C:\Users\youruser\chromium_ai_browser\src"

Get-ChildItem -Path $source -Recurse | ForEach-Object {
    $relativePath = $_.FullName.Substring($source.Length)
    $destPath = Join-Path $destination $relativePath

    if ($_.PSIsContainer) {
        if (!(Test-Path $destPath)) {
            New-Item -ItemType Directory -Path $destPath | Out-Null
        }
    } else {
        Copy-Item -Path $_.FullName -Destination $destPath -Force
    }
}

Write-Host "✅ All files copied back to src"
