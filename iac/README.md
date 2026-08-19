# Planned public hosting (do not apply yet)

Target: **ettiene-wium.co.za** → S3 website bucket + CloudFront + ACM certificate in us-east-1 (CloudFront requirement) + Route53 records.

**Do not run `terraform apply` until Ettiene explicitly asks** and the domain DNS is under this account.

```powershell
cd C:\projects\Ettiene-wium.co.za\iac
terraform init
terraform plan
# terraform apply   # only when asked
```

Fleet (`tf-fleet-iac`) is a separate stack. Do not destroy or retarget it from this folder.
