# ettiene-wium.co.za

Public CV and selected work. **No logins. No private family data.**

## Run locally

```bat
C:\projects\Ettiene-wium.co.za\start_server.bat
```

Open http://localhost:8097

## Content

| Path | Role |
|------|------|
| `content/profile.json` | CV fields (synced from UpSkill by wium-sync) |
| `content/projects.json` | Public project cards |
| `public/` | PHP site |
| `iac/` | Planned S3 + CloudFront + ACM — **do not apply until asked** |

## GitHub

Intended public repo: `https://github.com/EttieneW/ettiene-wium.co.za`

If Cursor GitHub MCP is not logged in, from Warp:

```bat
cd C:\projects\wium-sync
grok -p "Create GitHub repos per GITHUB.md"
```

Or: `gh auth login` then `pwsh C:\projects\wium-sync\create-github-repos.ps1`
