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

## LuckyLuke (local offload)

When LuckyLuke MCP tools are available, **delegate** simple/medium coding, tests, mechanical refactors, greps, and long file busywork (`luckyluke_health` then `luckyluke_delegate`). Keep architecture, Unreal/Aura, secrets, and ambiguous decisions on Grok. If health is down or `gpu_busy`, do the work yourself. Policy: `~/.grok/rules/luckyluke.md`.

## Project dashboard sync (mandatory)

This project lives under `C:\projects\`. The multi-project hub is:

| Item | Path |
|------|------|
| Dashboard UI | `C:\projects\projects-dashboard\` |
| **Registry (source of truth)** | `C:\projects\projects-dashboard\data\projects.json` |
| Local URL | http://localhost:5050 (run `projects-dashboard\start-dashboard.bat`) |

## Git

This project should have its own git repo and a GitHub remote (`EttieneW`). After meaningful work: commit, then push. Prefer the dashboard Git pills (Commit / Push / Pull) or `git` in this folder. Never force-push unless the user clearly asked. Do not commit `.env`, `config/token`, `.venv`, or `node_modules`.

The universal starter files (`AGENTS.md`, `PROJECT.md`, `README.md`) come from `C:\projects\_project-template`. When cloning a repo onto a new PC, the dashboard **All repos** flow refreshes missing universal sections from that template.
