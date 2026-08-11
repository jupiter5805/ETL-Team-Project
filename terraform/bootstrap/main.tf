provider "aws" {
  region  = "eu-west-2"
  profile = "bootstrap"
}

resource "aws_s3_bucket" "tf_state" {
  bucket = "etl-project-tf-state"
}

resource "aws_s3_bucket_versioning" "tf_state" {
  bucket = aws_s3_bucket.tf_state.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_dynamodb_table" "tf_locks" {
  name         = "etl-project-tf-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  attribute {
    name = "LockID"
    type = "S"
  }
}