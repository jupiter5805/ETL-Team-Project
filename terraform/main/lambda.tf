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


# Creates a Lambda layer called psycopg2-layer.
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

  timeout     = 60
  memory_size = 512

  filename = data.archive_file.lambda.output_path

  source_code_hash = data.archive_file.lambda.output_base64sha256

  layers = [
    aws_lambda_layer_version.psycopg2.arn
  ]

  environment {
    variables = {
      INGESTION_BUCKET_NAME = aws_s3_bucket.ingestion.bucket
      TOTESYS_SECRET_NAME   = data.aws_secretsmanager_secret.totesys_db.name
    }
  }
}


# Initialization Lambda
data "archive_file" "initialization_lambda" {
  type = "zip"

  source_dir = (
    "${path.module}/../../src"
  )

  output_path = (
    "${path.module}/../../initialization_lambda.zip"
  )

  excludes = [
    "__pycache__",
    "*.pyc",
  ]
}


resource "aws_lambda_function" "initialization" {
  function_name = "totesys-dev-initialization"

  filename = (
    data.archive_file.initialization_lambda.output_path
  )

  source_code_hash = (
    data.archive_file.initialization_lambda.output_base64sha256
  )

  role = aws_iam_role.initialization_lambda.arn

  runtime = "python3.13"
  handler = "initialization.lambda_function.lambda_handler"

  layers = [
    aws_lambda_layer_version.psycopg2.arn
  ]

  timeout     = 60
  memory_size = 256

  environment {
    variables = {
      DB_HOST = aws_db_instance.warehouse.address
      DB_PORT = tostring(aws_db_instance.warehouse.port)
      DB_NAME = aws_db_instance.warehouse.db_name

      DB_SECRET_ARN = (
        aws_db_instance.warehouse
        .master_user_secret[0]
        .secret_arn
      )
    }
  }

  vpc_config {
    subnet_ids = [
      aws_subnet.private_a.id,
      aws_subnet.private_b.id
    ]

    security_group_ids = [
      aws_security_group.lambda.id
    ]
  }
}


# Transformation Lambda
resource "aws_iam_role" "transform_lambda_execution" {
  name = "lambda_transform_role"

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


resource "aws_iam_policy" "transform_lambda_s3" {
  name = "lambda_transform_s3_policy"

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"
        Action = [
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
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.processed.arn}/*"
      }
    ]
  })
}


resource "aws_iam_role_policy_attachment" "transform_lambda_s3" {
  role       = aws_iam_role.transform_lambda_execution.name
  policy_arn = aws_iam_policy.transform_lambda_s3.arn
}


resource "aws_iam_role_policy_attachment" "transform_lambda_logs" {
  role       = aws_iam_role.transform_lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}


data "archive_file" "transform_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/../../src"
  output_path = "${path.module}/../../transform_lambda.zip"
}


resource "aws_lambda_function" "transform" {
  function_name = "database-automated-transform"

  role = aws_iam_role.transform_lambda_execution.arn

  runtime = "python3.13"

  handler = "transformation.lambda_function.lambda_handler"

  timeout     = 60
  memory_size = 512

  filename = data.archive_file.transform_lambda.output_path

  source_code_hash = data.archive_file.transform_lambda.output_base64sha256

  layers = [
    "arn:aws:lambda:eu-west-2:336392948345:layer:AWSSDKPandas-Python313:16"
  ]

  environment {
    variables = {
      INGESTION_BUCKET_NAME = aws_s3_bucket.ingestion.bucket
      PROCESSED_BUCKET_NAME = aws_s3_bucket.processed.bucket
    }
  }
}


# Loading Lambda package
data "archive_file" "loading_lambda" {
  type = "zip"

  source_dir = (
    "${path.module}/../../src"
  )

  output_path = (
    "${path.module}/../../loading_lambda.zip"
  )

  excludes = [
    "__pycache__",
    "*.pyc",
  ]
}


resource "aws_lambda_function" "loading" {
  function_name = "database-automated-loading"

  filename = (
    data.archive_file.loading_lambda.output_path
  )

  source_code_hash = (
    data.archive_file.loading_lambda.output_base64sha256
  )

  role = aws_iam_role.loading_lambda.arn

  runtime = "python3.13"
  handler = "loading.lambda_function.lambda_handler"

  layers = [
    aws_lambda_layer_version.psycopg2.arn,
    "arn:aws:lambda:eu-west-2:336392948345:layer:AWSSDKPandas-Python313:16"
  ]

  timeout     = 180
  memory_size = 1024

  environment {
    variables = {
      DB_HOST = aws_db_instance.warehouse.address
      DB_PORT = tostring(aws_db_instance.warehouse.port)
      DB_NAME = aws_db_instance.warehouse.db_name

      DB_SECRET_ARN = (
        aws_db_instance.warehouse
        .master_user_secret[0]
        .secret_arn
      )
    }
  }

  vpc_config {
    subnet_ids = [
      aws_subnet.private_a.id,
      aws_subnet.private_b.id
    ]

    security_group_ids = [
      aws_security_group.lambda.id
    ]
  }
}


# Run Loading Lambda automatically every 10 minutes.
resource "aws_cloudwatch_event_rule" "loading_schedule" {
  name                = "database-loading-schedule"
  description         = "Run Loading Lambda every 10 minutes"
  schedule_expression = "rate(10 minutes)"
}


# Allow EventBridge to invoke the Loading Lambda.
resource "aws_lambda_permission" "allow_eventbridge_loading" {
  statement_id  = "AllowExecutionFromEventBridgeLoading"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.loading.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.loading_schedule.arn
}


# Connect the 10-minute schedule to the Loading Lambda.
resource "aws_cloudwatch_event_target" "loading_target" {
  rule = aws_cloudwatch_event_rule.loading_schedule.name
  arn  = aws_lambda_function.loading.arn

  input = jsonencode({
    mode        = "scheduled"
    bucket_name = aws_s3_bucket.processed.id
  })

  depends_on = [
    aws_lambda_permission.allow_eventbridge_loading
  ]
}
# Dashboard Query Lambda package
data "archive_file" "dashboard_query_lambda" {
  type = "zip"

  source_dir = (
    "${path.module}/../../src"
  )

  output_path = (
    "${path.module}/../../dashboard_query_lambda.zip"
  )

  excludes = [
    "__pycache__",
    "*.pyc",
  ]
}


# Dashboard Query Lambda
resource "aws_lambda_function" "dashboard_query" {
  function_name = "warehouse-dashboard-query"

  filename = (
    data.archive_file.dashboard_query_lambda.output_path
  )

  source_code_hash = (
    data.archive_file.dashboard_query_lambda.output_base64sha256
  )

  role = aws_iam_role.dashboard_query_lambda.arn

  runtime = "python3.13"

  handler = (
    "dashboard_query.lambda_function.lambda_handler"
  )

  layers = [
    aws_lambda_layer_version.psycopg2.arn
  ]

  timeout     = 30
  memory_size = 256

  environment {
    variables = {
      DB_HOST = aws_db_instance.warehouse.address
      DB_PORT = tostring(aws_db_instance.warehouse.port)
      DB_NAME = aws_db_instance.warehouse.db_name

      DB_SECRET_ARN = (
        aws_db_instance.warehouse
        .master_user_secret[0]
        .secret_arn
      )
    }
  }

  vpc_config {
    subnet_ids = [
      aws_subnet.private_a.id,
      aws_subnet.private_b.id
    ]

    security_group_ids = [
      aws_security_group.lambda.id
    ]
  }
}
