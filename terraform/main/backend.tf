terraform {
  backend "s3" {
    bucket         = "etl-project-tf-state"
    key            = "main/terraform.tfstate"
    region         = "eu-west-2"
    dynamodb_table = "etl-project-tf-locks"
    encrypt        = true
  }
}