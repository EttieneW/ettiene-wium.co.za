# ettiene-wium.com

Public CV and selected work. **No logins. No private family data.**

Live site: **https://ettiene-wium.com** (S3 + CloudFront + editor API). Local folder/GitHub name stays `ettiene-wium.co.za`.

Editor: **https://ettiene-wium.com/admin/** — username `Ettiene.SRE`, password in SSM `/ettiene-wium-profile/admin/password`. Local: `config/admin.local.json`.

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
| `public/` | PHP site (rendered to static HTML at deploy) |
| `iac/` | S3 + CloudFront + ACM + CodePipeline + CCS |

## Deploy

```powershell
cd C:\projects\Ettiene-wium.co.za
git push origin main
.\scripts\push-codecommit.ps1
```

CodePipeline: Source (CodeCommit) → Review (CustomCodeScanner) → Deploy (PHP render + S3 + CloudFront invalidation).

Upload the CCS zip once after the CCS bucket exists:

```powershell
py C:\projects\CustomCodeScanner\scripts\pack_cli.py --upload ettiene-wium-profile-ccs-reports
```

## GitHub

Public repo: `https://github.com/EttieneW/ettiene-wium.co.za`

Fleet (separate project): https://fleet.wiums.co.za
