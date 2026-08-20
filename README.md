# ETL Data Pipeline Project

A serverless ETL data engineering pipeline built on AWS.

The project extracts data from the ToteSys PostgreSQL database, stores raw data in Amazon S3, transforms the data into a dimensional star schema, and loads the transformed data into a PostgreSQL data warehouse hosted on Amazon RDS.

The warehouse is designed to support sales analysis and reporting.

---

## Architecture

The ETL pipeline follows this architecture:

```text
ToteSys PostgreSQL
        |
        v
Ingestion Lambda
        |
        v
Raw S3 Bucket
        |
        v
Transformation Lambda
        |
        v
Processed S3 Bucket
     (Parquet)
        |
        v
Loading Lambda
        |
        v
PostgreSQL RDS
Data Warehouse
        |
        v
Dashboard Query Lambda
        |
        v
Streamlit Dashboard
```

### Automated Pipeline

The pipeline is automated using Amazon EventBridge and S3 events.

```text
EventBridge
Every 10 minutes
        |
        v
Ingestion Lambda
        |
        v
Raw S3 JSON
        |
        | S3 ObjectCreated event
        v
Transformation Lambda
        |
        v
Processed S3 Parquet
        |
        | EventBridge
        | Every 10 minutes
        v
Loading Lambda
        |
        v
RDS Data Warehouse
```

The Ingestion Lambda runs every 10 minutes.

Transformation is triggered automatically whenever new raw data is written to the ingestion S3 bucket.

The Loading Lambda runs every 10 minutes and loads recently transformed Parquet files into the data warehouse.

Dimension files are loaded before fact files to maintain foreign-key integrity.

---

## AWS Services

The project uses the following AWS services:

- AWS Lambda
- Amazon S3
- Amazon RDS PostgreSQL
- Amazon EventBridge
- AWS Secrets Manager
- Amazon CloudWatch
- Amazon SNS
- AWS IAM
- Amazon VPC
- Terraform

---

# ETL Pipeline

## 1. Ingestion

The Ingestion Lambda connects to the ToteSys PostgreSQL database and extracts data from the following source tables:

```text
counterparty
currency
department
design
staff
sales_order
address
payment
purchase_order
payment_type
transaction
```

The ingestion process uses incremental extraction based on the `last_updated` column.

The extraction window follows:

```sql
WHERE last_updated > previous_run
AND last_updated <= current_run
```

This allows each run to extract only data that has changed since the previous ingestion cycle.

The extracted data is stored in the raw S3 bucket as JSON.

Raw files use the following structure:

```text
raw/<table>/<timestamp>.json
```

Example:

```text
raw/sales_order/2026-08-19T21:20:30.454652.json
```

---

## 2. Transformation

Raw S3 objects automatically trigger the Transformation Lambda.

The Transformation Lambda converts ToteSys source data into the dimensional model required by the warehouse.

The MVP produces:

```text
dim_staff
dim_location
dim_design
dim_currency
dim_counterparty
dim_date
fact_sales_order
```

The transformed data is written to the processed S3 bucket using Parquet format.

Processed objects use structures such as:

```text
dim_staff/<timestamp>.parquet
dim_location/<timestamp>.parquet
dim_design/<timestamp>.parquet
dim_currency/<timestamp>.parquet
dim_counterparty/<timestamp>.parquet
dim_date/<timestamp>.parquet
fact_sales_order/<timestamp>.parquet
```

Some dimensions require information from more than one ToteSys source table.

Examples include:

- `staff` combined with `department`
- `counterparty` combined with `address`
- `sales_order` transformed into the sales fact table
- sales-order dates transformed into `dim_date`

Sales-order timestamps are separated into date and time values for the warehouse.

The transformation layer also uses S3 pagination when rebuilding current-state dimension data, so it is not limited to the first 1,000 objects under a raw table prefix.

---

## 3. Loading

The Loading Lambda reads Parquet files from the processed S3 bucket and loads them into the PostgreSQL RDS warehouse.

The Loading Lambda runs every 10 minutes.

Files are processed in the following order:

```text
Dimensions
    |
    v
Facts
```

This prevents fact rows from being inserted before their referenced dimension rows exist.

The Loading Lambda connects to the private RDS database through the project VPC.

The loader supports safe retries.

A unique index protects sales fact versions using:

```text
sales_order_id
last_updated_date
last_updated_time
```

Repeated processing of the same fact version therefore does not create duplicate rows.

---

# S3 Data Lake

The project uses two S3 buckets.

## Raw Ingestion Bucket

```text
marvel-etl-project-ingestion
```

Stores data extracted from ToteSys as JSON.

Example:

```text
raw/sales_order/2026-08-19T21:20:30.454652.json
```

## Processed Bucket

```text
marvel-etl-project-processed
```

Stores transformed warehouse data in Parquet format.

Prefixes include:

```text
dim_staff/
dim_location/
dim_design/
dim_currency/
dim_counterparty/
dim_date/
fact_sales_order/
```

---

# Data Warehouse

The PostgreSQL data warehouse uses a star-schema design.

## Fact Table

The central fact table is:

```text
fact_sales_order
```

Important fields include:

```text
sales_record_id
sales_order_id
created_date
created_time
last_updated_date
last_updated_time
sales_staff_id
counterparty_id
units_sold
unit_price
currency_id
design_id
agreed_payment_date
agreed_delivery_date
agreed_delivery_location_id
```

## Dimension Tables

The warehouse contains:

```text
dim_staff
dim_location
dim_design
dim_currency
dim_counterparty
dim_date
```

Dimension tables represent the latest known state of their entities.

The sales fact table is designed to support multiple historical versions of a sales order.

---

# Networking

The PostgreSQL RDS warehouse is deployed inside private VPC subnets.

The Loading, Initialization, and Dashboard Query Lambdas are configured inside the VPC so they can connect securely to RDS.

The RDS database remains private and is not exposed directly to the local Streamlit application.

An S3 VPC endpoint allows the private Loading Lambda to access processed S3 data without requiring public internet access.

A Secrets Manager VPC endpoint allows private Lambdas to retrieve database credentials securely.

---

# Security

Database credentials are not stored directly in application code.

AWS Secrets Manager is used for database credentials.

IAM roles and policies provide the Lambdas with the permissions required for their individual responsibilities.

Examples include:

- S3 access
- Secrets Manager access
- CloudWatch logging
- VPC execution permissions
- Lambda invocation for the dashboard client

Security checks are also performed using Bandit and pip-audit.

---

# Monitoring

Amazon CloudWatch is used to monitor the ETL Lambda functions.

CloudWatch failure alarms exist for:

```text
lambda-ingestion-failure
lambda-transformation-failure
lambda-loading-failure
```

The alarms publish to an Amazon SNS topic.

SNS can send email notifications when a Lambda failure is detected.

CloudWatch Logs are also used to inspect individual ETL executions and troubleshoot pipeline failures.

---

# Infrastructure as Code

AWS infrastructure is managed using Terraform.

Terraform is separated into:

```text
terraform/bootstrap/
terraform/main/
```

## Bootstrap Infrastructure

`terraform/bootstrap/` creates the infrastructure needed for shared Terraform state.

This includes:

- S3 remote-state bucket
- DynamoDB state-locking table

The bootstrap configuration is normally run once by the AWS account administrator.

## Main Infrastructure

`terraform/main/` manages the main ETL infrastructure.

This includes:

- S3 buckets
- Lambda functions
- Lambda layers
- IAM roles and policies
- EventBridge schedules
- S3 Lambda triggers
- Lambda permissions
- VPC
- Private subnets
- Security groups
- VPC endpoints
- PostgreSQL RDS
- CloudWatch alarms
- SNS alerts
- Secrets Manager permissions
- Dashboard Query Lambda

Terraform state is stored remotely so that the team shares the same infrastructure state.

---

# Installation

## Requirements

- Python 3.13
- Terraform 1.x or later
- AWS CLI
- Git
- Access to the project AWS account

Clone the repository:

```bash
git clone https://github.com/jupiter5805/ETL-Team-Project
cd ETL-Team-Project
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

---

# Terraform Deployment

Move into the Terraform directory:

```bash
cd terraform/main
```

Initialise Terraform:

```bash
terraform init
```

Validate the Terraform configuration:

```bash
terraform validate
```

Review planned infrastructure changes:

```bash
terraform plan
```

Apply approved changes:

```bash
terraform apply
```

Terraform plans should always be reviewed before applying changes, especially to ensure there are no unexpected resource deletions.

---

# Testing

The project uses `pytest` for automated testing.

Run all tests:

```bash
python -m pytest tests
```

Run the full test suite with coverage:

```bash
python -m pytest tests --cov=src --cov-fail-under=90
```

The current verified test run contains:

```text
119 automated tests passed
92.90% overall test coverage
```

The `src/dashboard_query/lambda_function.py` module is covered at 100%.

The required minimum coverage is 90%.

---

# PEP8 and Code Quality

Flake8 is used for Python style and code-quality checks.

Run:

```bash
python -m flake8 src tests
```

The project currently passes the Flake8 check.

---

# Security Testing

## Bandit

Bandit is used to scan Python source code for common security issues.

Run:

```bash
python -m bandit -r src
```

The project currently passes the Bandit security scan with no identified issues.

## pip-audit

Python dependencies are checked for known vulnerabilities using:

```bash
python -m pip_audit
```

The current dependency audit reports no known vulnerabilities.

---

# Continuous Integration

GitHub Actions provides continuous integration for the project.

The CI workflow is located at:

```text
.github/workflows/ci.yml
```

The workflow runs automatically on pushes and pull requests.

The CI process performs:

```text
Checkout repository
        |
        v
Set up Python 3.13
        |
        v
Install requirements
        |
        v
Run Pytest
        |
        v
Check coverage >= 90%
        |
        v
Run Flake8
        |
        v
Run Bandit
        |
        v
Run pip-audit
```

If any check fails, the GitHub Actions workflow fails.

The CI workflow has been successfully executed on GitHub.

AWS infrastructure deployment is managed separately through Terraform rather than automatically applying Terraform through GitHub Actions.

---

# Scheduling

The Ingestion Lambda is scheduled using EventBridge:

```text
rate(10 minutes)
```

The Loading Lambda is also scheduled using EventBridge:

```text
rate(10 minutes)
```

Transformation does not require a schedule because it is automatically triggered by S3 when new raw objects are created.

The pipeline is therefore designed to process source changes within the project's 30-minute processing requirement.

---

# Verified End-to-End Pipeline

The deployed infrastructure has been tested against the real ToteSys source database.

The following path has been successfully demonstrated:

```text
ToteSys PostgreSQL
        |
        v
Ingestion Lambda
        |
        v
Raw S3 JSON
        |
        v
Transformation Lambda
        |
        v
Processed S3 Parquet
        |
        v
Loading Lambda
        |
        v
PostgreSQL RDS Warehouse
```

Real ToteSys sales-order records have successfully passed through Transformation and Loading into the warehouse.

The pipeline also successfully loads dimension data before fact data.

The deployed Transformation Lambda has also been smoke-tested after the S3 pagination update and successfully produced fresh Parquet outputs.

---

# Dashboard

The project includes a Streamlit sales dashboard in:

```text
dashboard/app.py
```

The dashboard does not connect directly to the private RDS database.

Instead it uses this architecture:

```text
Streamlit Dashboard
        |
        | AWS Lambda Invoke
        v
warehouse-dashboard-query
        |
        | Private VPC connection
        v
PostgreSQL RDS Warehouse
```

The `warehouse-dashboard-query` Lambda is implemented in:

```text
src/dashboard_query/lambda_function.py
```

It queries the warehouse directly and returns dashboard data including:

- available currency and country filters
- sales-order count
- historical fact-version count
- units sold
- sales value
- daily sales values
- top designs
- top counterparties
- sales by staff
- orders by country
- recent sales orders

Headline business metrics use the latest version of each sales order.

Historical fact rows remain available separately in the warehouse.

Currency is selected explicitly in the dashboard so values from GBP, EUR, and USD are not added together into one monetary total.

Run the dashboard from the project root with:

```bash
streamlit run dashboard/app.py
```

The local AWS credentials used to run the dashboard must have permission to invoke the `warehouse-dashboard-query` Lambda.

---

# Project Structure

```text
ETL-Team-Project/
|
├── .github/
│   └── workflows/
│       └── ci.yml
|
├── dashboard/
│   └── app.py
|
├── src/
│   ├── dashboard_query/
│   ├── ingestion/
│   ├── transformation/
│   ├── loading/
│   └── initialization/
|
├── tests/
│   ├── dashboard_query/
│   ├── ingestion/
│   ├── transform/
│   ├── loading/
│   └── initialization/
|
├── terraform/
│   ├── bootstrap/
│   └── main/
|
├── requirements.txt
└── README.md
```

---

# Project Scope

The current implementation focuses on the ToteSys sales ETL MVP.

The warehouse contains:

```text
fact_sales_order
dim_staff
dim_location
dim_design
dim_currency
dim_counterparty
dim_date
```

Optional extension functionality is outside the scope of the current implementation.

---

# Current Quality Status

| Check | Status |
|---|---|
| Automated tests | 119 passed |
| Test coverage | 92.90% |
| Dashboard Query Lambda coverage | 100% |
| Flake8 / PEP8 | Passed |
| Bandit security scan | Passed |
| pip-audit | Passed |
| GitHub Actions CI | Passed |
| ToteSys to RDS pipeline | Verified |
| RDS-backed Streamlit dashboard | Verified |
| S3 pagination | Implemented and smoke-tested |
| CloudWatch monitoring | Implemented |
| EventBridge scheduling | Implemented |