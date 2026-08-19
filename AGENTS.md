# AI agent instructions — Ettiene-wium.co.za

## Always ask when unsure

- Do not invent certs, employers, or Kubernetes years.
- Do not put vault, banking, or family data on this public site.
- Do not `terraform apply` / destroy here or on tf-fleet-iac unless the user explicitly asks.

## What this project is

Public CV/profile for **ettiene-wium.co.za**. Content lives in `content/profile.json` and `content/projects.json`. `wium-sync` overwrites profile JSON from UpSkill.

## Dashboard sync

| Item | Value |
|------|--------|
| Registry | `C:\projects\projects-dashboard\data\projects.json` |
| Entry id | `ettiene-wium-co-za` |
| Hub | http://localhost:5050 |

After heavy changes, update `summary`, `description`, `goals`, `completeness`, `next_steps`, `status`, `links`, `how_to_run`, and top-level `updated_at`.

## Working style

- Keep the site static-shaped (no auth).
- IaC under `iac/` is planned only until apply is requested.
- Prefer editing `content/*.json` over hard-coding copy in PHP.
