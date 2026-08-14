data "aws_secretsmanager_secret" "totesys_db" {
  name = "totesys-db-credentials"
}

resource "aws_iam_policy" "lambda_secrets" {
  name = "lambda_ingestion_secrets_policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = data.aws_secretsmanager_secret.totesys_db.arn
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_secrets" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = aws_iam_policy.lambda_secrets.arn
}