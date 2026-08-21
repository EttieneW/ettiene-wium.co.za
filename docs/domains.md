See the canonical runbook: `C:\projects\wium-sync\docs\domains.md`

- This site owns **ettiene-wium.com** (S3 + CloudFront)
- Fleet owns **fleet.wiums.co.za** (EC2 + Apache in `tf-fleet-iac`)
- The `ettiene-wium.com` Route53 hosted zone was created by the fleet stack; this stack uses it as a data source
- Do not terraform apply fleet from this folder
