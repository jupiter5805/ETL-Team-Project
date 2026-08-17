resource "aws_iam_role" "lambda_execution" {
    name = "lambda_transformation_role"

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

resource "aws_iam_policy" "transform_s3_access" {
    name = "lambda_transform_s3_policy"
    
    policy = jsonencode({
        Version = "2012-10-17"

        Statement = [
            {
            Effect = "Allow"

            Action = [
                "s3:GetObject"
            ]

            Resource = "${aws_s3_bucket.raw.arn}/*"
        },
        {
            Effect = "Allow"
            Action = ["s3:PutObject"]
            Resource = "${aws_s3_bucket.processed.arn}/*"
        }
        ]   
    })
}

resource "aws_iam_role_policy_attachment" "transform_s3" {
    role = aws_iam_role.lambda_exeuction.name
    policy_arn = aws_iam_policy.transform_s3_access.arn
}

resource "aws_iam_role_policy_attachment" "transform_logs" {
    role = aws_iam_role.lambda_execution.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "transformation" {
    function_name = "bucket-automated-transformation"

    role = aws_iam_role.lambda_exeuction.arn

    runtime = "python3.13"

    handler = "src.transformation.main.lambda_handler"

    filename = "${path.module}/../../transformation_lambda.zip"

    source_code_hash = filebase64sha256("${path.module}/../../transformation_lambda.zip")
}