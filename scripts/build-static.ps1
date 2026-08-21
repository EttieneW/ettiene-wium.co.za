# Render the PHP profile to a static dist/ tree for S3 + CloudFront.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$dist = Join-Path $root "dist"
if (Test-Path $dist) { Remove-Item -Recurse -Force $dist }
New-Item -ItemType Directory -Path $dist | Out-Null

$index = Join-Path $dist "index.html"
cmd /c "php public\index.php > `"$index`""
if ($LASTEXITCODE -ne 0) { throw "php public/index.php failed" }
Copy-Item -Recurse public\assets $dist\assets -Force
Copy-Item public\robots.txt $dist\robots.txt
Copy-Item $index (Join-Path $dist "404.html")
Write-Host "Wrote $dist"
