resource "aws_iam_role" "lambda_execution" {
  name = "lambda_ingestion_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [{
      Effect = "Allow"

      Principal = {
        Service = "lambda.amazonaws.com"
      }

      Action = "sts:AssumeRole"
    }]
  })
}


resource "aws_iam_policy" "lambda_s3" {
  name = "lambda_ingestion_s3_policy"

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [{
      Effect = "Allow"

      Action = [
        "s3:PutObject"
      ]

      Resource = "${aws_s3_bucket.ingestion.arn}/*"
    }]
  })
}


resource "aws_iam_role_policy_attachment" "lambda_s3" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = aws_iam_policy.lambda_s3.arn
}


resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}


# THIS MUST BE OUTSIDE THE LAMBDA RESOURCE
data "archive_file" "lambda" {
  type        = "zip"
  source_dir  = "${path.module}/../../src"
  output_path = "${path.module}/../../ingestion_lambda.zip"
}


resource "aws_lambda_function" "ingestion" {
  function_name = "database-automated-ingestion"

  role = aws_iam_role.lambda_execution.arn

  runtime = "python3.13"

  handler = "ingestion.lambda_handler.lambda_handler"

  filename = data.archive_file.lambda.output_path

  source_code_hash = data.archive_file.lambda.output_base64sha256
}
