# Public profile hosting (ettiene-wium.com)

Cheap static hosting in **us-east-1**: private S3 bucket + CloudFront (OAC) + ACM + Route53 aliases.

The PHP site is rendered to `dist/` at deploy time (`php public/index.php`). No EC2, no RDS.

**CI/CD (same shape as fleet):** CodeCommit `main` → CodeBuild **CustomCodeScanner** → CodeBuild render + `s3 sync` + CloudFront invalidation.

## Apply

```powershell
cd C:\projects\Ettiene-wium.co.za\iac
terraform init
terraform plan
terraform apply
```

`attach_apex_dns` is **true** (apex + www alias to CloudFront). Fleet terraform must not recreate those A records.

Then upload the CCS CLI zip (once per bucket):

```powershell
py C:\projects\CustomCodeScanner\scripts\pack_cli.py --upload (terraform output -raw ccs_report_bucket)
```

Push the app into the pipeline source:

```powershell
cd C:\projects\Ettiene-wium.co.za
.\scripts\push-codecommit.ps1
```

GitHub `EttieneW/ettiene-wium.co.za` stays the public remote. CodeCommit is what CodePipeline polls.

## Local

```bat
C:\projects\Ettiene-wium.co.za\start_server.bat
```

http://localhost:8097
