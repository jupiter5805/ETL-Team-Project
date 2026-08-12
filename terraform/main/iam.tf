resource "aws_iam_user" "team" {
  for_each = toset(["jack", "rico", "shamini", "serhan", "zhaoyu"])
  name     = each.value
}

resource "aws_iam_group" "data_team" {
  name = "etl-project-team"
}

resource "aws_iam_group_policy" "s3_access" {
  name  = "s3-bucket-access"
  group = aws_iam_group.data_team.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:PutObject", "s3:ListBucket", "s3:DeleteObject"]
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
        Resource = "arn:aws:iam::*:role/lambda-*"
      }
    ]
  })
}

resource "aws_iam_user_group_membership" "members" {
  for_each = aws_iam_user.team
  user     = each.value.name
  groups   = [aws_iam_group.data_team.name]
}