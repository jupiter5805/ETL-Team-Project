resource "aws_s3_bucket" "ingestion" { bucket = "marvel-etl-project-ingestion" }
resource "aws_s3_bucket" "processed" { bucket = "marvel-etl-project-processed" }

resource "aws_s3_bucket_versioning" "ingestion" {
  bucket = aws_s3_bucket.ingestion.id
  versioning_configuration { status = "Enabled" }
}
resource "aws_s3_bucket_versioning" "processed" {
  bucket = aws_s3_bucket.processed.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_public_access_block" "ingestion" {
  bucket                  = aws_s3_bucket.ingestion.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
resource "aws_s3_bucket_public_access_block" "processed" {
  bucket                  = aws_s3_bucket.processed.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_lambda_permission" "allow_s3_transform" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.transform.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.ingestion.arn
}

resource "aws_s3_bucket_notification" "transform_trigger" {
  bucket = aws_s3_bucket.ingestion.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.transform.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "raw/"
  }

  depends_on = [
    aws_lambda_permission.allow_s3_transform
  ]
}
