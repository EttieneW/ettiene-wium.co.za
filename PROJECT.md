# Ettiene-wium.co.za

Public CV and project profile for Ettiene Wium. No family or vault data.

## Summary

Production software engineer moving into SRE / DevOps at **https://ettiene-wium.com**. Local **http://localhost:8097**. Editor at `/admin` updates CV and cover letter and regenerates PDF/DOCX.

## Description

Hireable profile: 8y production software engineer, DevOps for clients, SRE via homelab streaming and freelance fleet. Jobs: Silicon Overdrive, RogerWilco. Fleet is on **https://fleet.wiums.co.za**. Private/family systems are not hosted here.

## Status

- **Status:** active
- **Completeness:** 93%
- **Last dashboard sync:** 2026-09-14

## Goals

1. Production software engineer moving into SRE (K8s: 2y homelab, not at-work cluster)
2. HTTPS + CSP + HSTS
3. Professional public UI
4. Authenticated editor for CV/cover letter
5. PDF and DOCX downloads
6. Cheap S3/CloudFront + Lambda API
7. CCS pipeline

## Next steps

1. After UI/code changes: `git push` then `scripts/push-codecommit.ps1`
2. Edit copy at https://ettiene-wium.com/admin/
3. Keep fleet on fleet.wiums.co.za

## Tech stack

- Static HTML/CSS/JS
- Python API (local + Lambda)
- Terraform (S3, CloudFront, ACM, API Gateway, Lambda, CodePipeline, CCS)

## How to run

```bat
C:\projects\Ettiene-wium.co.za\start_server.bat
```

Local URL: http://localhost:8097  
Production: https://ettiene-wium.com  
Editor: https://ettiene-wium.com/admin/

## Dashboard registry

Listed as `ettiene-wium-co-za` in `C:\projects\projects-dashboard\data\projects.json`.
