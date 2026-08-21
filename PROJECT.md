# Ettiene-wium.co.za

Public CV and project profile for Ettiene Wium. No logins. No family or vault data.

## Summary

JSON-driven PHP site at **http://localhost:8097**. Production: **https://ettiene-wium.com** on S3 + CloudFront (us-east-1). Content is overwritten by `C:\projects\wium-sync` from the UpSkill CV draft.

## Description

This is the public hireable profile: headline, summary, skills, two jobs (Silicon Overdrive, RogerWilco), certs, education, and selected public work. Fleet is on **https://fleet.wiums.co.za**. Private systems (info.wium.co.za, dts.wium.co.za) are not hosted here.

The Windows folder and GitHub repo stay `Ettiene-wium.co.za` / `ettiene-wium.co.za`. The public URL is **ettiene-wium.com**.

## Status

- **Status:** active
- **Completeness:** 80%
- **Last dashboard sync:** 2026-08-21

## Goals

1. Local public profile that matches the UpSkill CV draft
2. GitHub repo `EttieneW/ettiene-wium.co.za` (public)
3. Cheap AWS hosting on ettiene-wium.com (S3 + CloudFront + ACM)
4. Fleet-shaped CI/CD: CodeCommit → CustomCodeScanner → static deploy
5. Stay in sync via wium-sync

## Next steps

1. Run `start_server.bat` and review copy
2. After content changes: `git push` then `scripts/push-codecommit.ps1`
3. Keep fleet on fleet.wiums.co.za — do not terraform apply fleet from this folder

## Tech stack

- PHP 8 (local preview + CodeBuild render)
- JSON content
- Terraform (S3, CloudFront, ACM, CodePipeline, CCS)
- CustomCodeScanner

## How to run

```bat
C:\projects\Ettiene-wium.co.za\start_server.bat
```

Local URL: http://localhost:8097

Production: https://ettiene-wium.com

## Dashboard registry

Listed as `ettiene-wium-co-za` in `C:\projects\projects-dashboard\data\projects.json`.
