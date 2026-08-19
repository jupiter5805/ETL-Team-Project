resource "aws_iam_user" "team" {
  for_each = toset(["jack", "rico", "shamini", "serhan", "zhaoyu"])
  name     = each.value
}

resource "aws_iam_group" "data_team" {
  name = "etl-project-team"
}

resource "aws_iam_group_policy" "tf_state_access" {
  name  = "terraform-state-access"
  group = aws_iam_group.data_team.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"]
        Resource = [
          "arn:aws:s3:::etl-project-tf-state",
          "arn:aws:s3:::etl-project-tf-state/*"
        ]
      },
      {
        Effect   = "Allow"
        Action   = ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:DeleteItem"]
        Resource = "arn:aws:dynamodb:eu-west-2:872709212089:table/etl-project-tf-locks"
      }
    ]
  })
}

resource "aws_iam_group_policy" "s3_access" {
  name  = "s3-bucket-access"
  group = aws_iam_group.data_team.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:GetObject", "s3:PutObject", "s3:ListBucket", "s3:DeleteObject",
        "s3:GetBucketPolicy", "s3:GetBucketVersioning", "s3:GetBucketPublicAccessBlock", "s3:GetBucketLocation"
      ]
      Resource = [
        aws_s3_bucket.ingestion.arn, "${aws_s3_bucket.ingestion.arn}/*",
        aws_s3_bucket.processed.arn, "${aws_s3_bucket.processed.arn}/*"
      ]
    }]
  })
}

resource "aws_iam_group_policy" "pipeline_access" {
  name  = "pipeline-services-access"
  group = aws_iam_group.data_team.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["lambda:*", "events:*", "logs:*", "cloudwatch:*", "sns:*", "secretsmanager:*", "rds:*"]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = "iam:PassRole"
        Resource = "arn:aws:iam::*:role/lambda*"
      },
      {
        Effect   = "Allow"
        Action   = ["iam:CreatePolicyVersion", "iam:DeletePolicyVersion"]
        Resource = "arn:aws:iam::*:policy/lambda*"
      }
    ]
  })
}

resource "aws_iam_group_policy_attachment" "read_only" {
  group      = aws_iam_group.data_team.name
  policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}

resource "aws_iam_user_group_membership" "members" {
  for_each = aws_iam_user.team
  user     = each.value.name
  groups   = [aws_iam_group.data_team.name]
}

resource "aws_iam_role" "initialization_lambda" {
  name = "totesys-dev-initialization-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "lambda.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "initialization_vpc_access" {
  role       = aws_iam_role.initialization_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role_policy" "initialization_secret_access" {
  name = "totesys-dev-initialization-secret-access"
  role = aws_iam_role.initialization_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]

        Resource = (
          aws_db_instance.warehouse
          .master_user_secret[0]
          .secret_arn
        )
      }
    ]
  })
}
resource "aws_iam_role" "loading_lambda" {
  name = "totesys-dev-loading-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "lambda.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })
}


resource "aws_iam_role_policy_attachment" "loading_vpc_access" {
  role       = aws_iam_role.loading_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}


resource "aws_iam_role_policy" "loading_secret_access" {
  name = "totesys-dev-loading-secret-access"
  role = aws_iam_role.loading_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]

        Resource = (
          aws_db_instance.warehouse
          .master_user_secret[0]
          .secret_arn
        )
      }
    ]
  })
}


resource "aws_iam_role_policy" "loading_s3_access" {
  name = "totesys-dev-loading-s3-access"
  role = aws_iam_role.loading_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "s3:GetObject"
        ]

        Resource = "${aws_s3_bucket.processed.arn}/*"
      },
      {
        Effect = "Allow"

        Action = [
          "s3:ListBucket"
        ]

        Resource = aws_s3_bucket.processed.arn
      }
    ]
  })
}
