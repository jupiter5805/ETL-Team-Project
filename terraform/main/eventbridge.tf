resource "aws_cloudwatch_event_rule" "ingestion_schedule" {
  name                = "database_ingestion_schedule"
  description         = "Triggers ingestion on a time basis"
  schedule_expression = "rate(10 minutes)" # run ingestion every 10 minutes to meet the under-30-minute pipeline requirements

} #establishes the functions renewal cycle

resource "aws_cloudwatch_event_target" "ingestion_target" {
  rule      = aws_cloudwatch_event_rule.ingestion_schedule.name
  target_id = "lambda-ingestion"
  arn       = aws_lambda_function.ingestion.arn
} #linking our renewal cycle to our lambda

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ingestion.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.ingestion_schedule.arn
} #configuring our lambda to be executed by eventbridge
