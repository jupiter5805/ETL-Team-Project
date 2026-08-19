resource "aws_sns_topic" "lambda_failure_alerts" {
  name = "lambda-failure-alerts"
}


resource "aws_sns_topic_subscription" "lambda_failure_email" {
  topic_arn = aws_sns_topic.lambda_failure_alerts.arn
  protocol  = "email"
  endpoint  = "jinnt@hotmail.co.uk"
}


resource "aws_cloudwatch_metric_alarm" "lambda_failure_alarm" {
  alarm_name          = "lambda-ingestion-failure"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 60
  statistic           = "Sum"
  threshold           = 1

  dimensions = {
    FunctionName = aws_lambda_function.ingestion.function_name
  }

  alarm_actions = [
    aws_sns_topic.lambda_failure_alerts.arn
  ]
}