# Ettiene-wium.co.za

Public CV and project profile for Ettiene Wium. No family or vault data.

## Summary

Junior SRE / DevOps profile at **https://ettiene-wium.com**. Local **http://localhost:8097**. Editor at `/admin` updates CV and cover letter and regenerates PDF/DOCX.

## Description

Hireable profile: headline, summary, skills, jobs (Silicon Overdrive, RogerWilco), AWS certs, cover letter, selected public work. Fleet is on **https://fleet.wiums.co.za**. Private systems are not hosted here.

## Status

- **Status:** active
- **Completeness:** 92%
- **Last dashboard sync:** 2026-08-23

## Goals

1. Junior SRE positioning (honest: k3s lab in progress, not production K8s years)
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
