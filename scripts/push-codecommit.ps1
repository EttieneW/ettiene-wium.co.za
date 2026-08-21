# Push this GitHub repo to the CodeCommit pipeline source (us-east-1).
# Mirrors fleet: GitHub is the public remote; CodeCommit is what CodePipeline polls.
param(
    [string]$Region = "us-east-1",
    [string]$Repo = "ettiene-wium-profile"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

git config --local credential.helper '!aws codecommit credential-helper $@'
git config --local credential.UseHttpPath true

$url = "https://git-codecommit.$Region.amazonaws.com/v1/repos/$Repo"
$existing = git remote get-url codecommit 2>$null
if (-not $existing) {
    git remote add codecommit $url
} elseif ($existing -ne $url) {
    git remote set-url codecommit $url
}

Write-Host "Pushing main -> $url"
git push origin main
git push codecommit main
