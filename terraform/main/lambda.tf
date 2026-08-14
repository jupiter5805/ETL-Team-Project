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
} #establishing the lambda iam role

resource "aws_iam_policy" "lambda_s3" {
    name = "lambda_ingestion_s3_policy"

    policy = jsonencode({
        Version = "2012-10-17"

        Statement = [{
            Effect = "Allow"

            Action = [
                "s3:PutObject"
            ]

            Resource = "${aws_s3_bucket.ingestion.arn}/raw/*"
        }]
    })
} #creating the s3 policy for our lambda, that allows it to put objects inside of our bucket

resource "aws_iam_role_policy_attachment" "lambda_s3" {
    role    = aws_iam_role.lambda_execution.name
    policy_arn = aws_iam_policy.lambda_s3.arn
}
#attaching our created s3 policy
resource "aws_iam_role_policy_attachment" "lambda_logs" {
    role     = aws_iam_role.lambda_execution.name
    policy_arn =  "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
#attaching cloudwatch to allow logging and lambda

resource "aws_lambda_function" "ingestion" {

    function_name = "database-automated-ingestion"

    role = aws_iam_role.lambda_execution.arn

    runtime = "python3.13"
    
    handler = "src.ingestion.main.lambda_handler" #root to our lambda handler function

    filename = "${path.module}/../../ingestion_lambda.zip" #root to our lambda zip
    
    source_code_hash = filebase64sha256("${path.module}/../../ingestion_lambda.zip") #ensures that whenever a new zip is created, it updates that within our lambda
}

#intialising our lambda handler to be assigned to our lambda via filepath