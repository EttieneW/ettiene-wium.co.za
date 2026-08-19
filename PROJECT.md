# Ettiene-wium.co.za

Public CV and project profile for Ettiene Wium. No logins. No family or vault data.

## Summary

JSON-driven PHP site at **http://localhost:8097**. Production target: **https://ettiene-wium.co.za** on S3 + CloudFront (Terraform in `iac/` — do not apply until asked). Content is overwritten by `C:\projects\wium-sync` from the UpSkill CV draft.

## Description

This is the public hireable profile: headline, summary, skills, two jobs (Silicon Overdrive, RogerWilco), certs, education, and selected public work. Fleet stays on its current hostname until an explicit cutover. Private systems (info.wium.co.za, dts.wium.co.za) are not hosted here.

## Status

- **Status:** active
- **Completeness:** 35%
- **Last dashboard sync:** 2026-08-19

## Goals

1. Local public profile that matches the UpSkill CV draft
2. GitHub repo `EttieneW/ettiene-wium.co.za` (public)
3. Terraform plan for S3/CloudFront/ACM/Route53 — apply only when DNS is owned and the user asks
4. Stay in sync via wium-sync

## Next steps

1. Run `start_server.bat` and review copy
2. After `gh auth login` (or Grok CLI GitHub MCP), create/push the public repo
3. Point ettiene-wium.co.za at this stack when ready — do not terraform apply fleet

## Tech stack

- PHP 8 (built-in server)
- JSON content
- Terraform (planned, not applied)

## How to run

```bat
C:\projects\Ettiene-wium.co.za\start_server.bat
```

Local URL: http://localhost:8097

## Dashboard registry

Listed as `ettiene-wium-co-za` in `C:\projects\projects-dashboard\data\projects.json`.
