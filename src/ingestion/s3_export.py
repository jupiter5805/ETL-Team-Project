import boto3
from src import extract_all_tables
from src import get_totesys_connection
from datetime import datetime


connection = get_totesys_connection()


for table_name, json_body in extract_all_tables(connection):

    current_time = datetime.now().isoformat()

    s3 = boto3.client("s3")

    s3.put_object(
        Bucket="",
        Key=f"{table_name}/{current_time}.json"
        Body=json_body,
        ContentType="application/json"
    )

