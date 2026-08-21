# Push this GitHub repo to the CodeCommit pipeline source (us-east-1).
# Mirrors fleet: GitHub is the public remote; CodeCommit is what CodePipeline polls.
# Uses git-remote-codecommit (pip install git-remote-codecommit) so Windows
# does not hang on the HTTPS credential helper.
param(
    [string]$Region = "us-east-1",
    [string]$Repo = "ettiene-wium-profile"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$url = "codecommit::${Region}://$Repo"
Write-Host "Pushing main -> origin and $url"
git push origin main
git push $url main
