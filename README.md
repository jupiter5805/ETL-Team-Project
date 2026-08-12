# ETL Data Pipeline Project

A data engineering pipeline which extracts data from the `totesys` database, extracts it into an S3 data lake, transforms it into a star-schema
and loads it into a data warehouse hosted on AWS, ready for analysis.

## Terraform Infrastructure

The terraform state is stored remotely in S3 so that the whole team works from the same state rather than local copies. 
This is bootstrapped in two stages:

- `terraform/bootstrap/` 
    Creates an S3 bucket and a DynamoDB table used for remote state. This is run once by the admin of the AWS account.
- `terraform/main/` 
    Day-to-day project infrastructure (S3 data buckets, IAM, Lambda). Reads and writes its state to the backend created above.

Team members are added as individual IAM users in a shared `etl-project-team` group.

## Installation & Setup

Requirements:
- Python 3.12+
- Terraform >= 1.x
- AWS CLI, configured with a named profile for this project
- Access to a user on the shared AWS account


Clone the repo and cd to it:

```bash
git clone https://github.com/jupiter5805/ETL-Team-Project
cd ETL-Team-Project
```

Create the virtual environment, activate it, and install required libraries:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Configure your AWS CLI profile (access and secret keys provided by admin):
```bash
aws configure --profile etl-team
```

Making updates with terraform:
```bash
cd terraform/main
AWS_PROFILE=etl-team terraform init
AWS_PROFILE=etl-team terraform plan
AWS_PROFILE=etl-team terraform apply
```