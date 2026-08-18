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

    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject"
        ]
        Resource = "${aws_s3_bucket.ingestion.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.ingestion.arn
      }
    ]
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


data "archive_file" "psycopg2_layer" {
  type        = "zip"
  source_dir  = "${path.module}/../../lambda_layer"
  output_path = "${path.module}/../../psycopg2_layer.zip"
}

# Creates a Lambda layer called psycopg2-layer using the ZIP weabove.
resource "aws_lambda_layer_version" "psycopg2" {
  filename            = data.archive_file.psycopg2_layer.output_path
  layer_name          = "psycopg2-layer"
  compatible_runtimes = ["python3.13"]

  source_code_hash = data.archive_file.psycopg2_layer.output_base64sha256
}

resource "aws_lambda_function" "ingestion" {
  function_name = "database-automated-ingestion"

  role = aws_iam_role.lambda_execution.arn

  runtime = "python3.13"

  handler = "ingestion.main.lambda_handler"

  timeout = 60 
  memory_size = 512

  filename = data.archive_file.lambda.output_path

  source_code_hash = data.archive_file.lambda.output_base64sha256

  layers = [aws_lambda_layer_version.psycopg2.arn]

  environment {
    variables = {
      INGESTION_BUCKET_NAME = aws_s3_bucket.ingestion.bucket
      TOTESYS_SECRET_NAME   = data.aws_secretsmanager_secret.totesys_db.name
    }
  }
}
