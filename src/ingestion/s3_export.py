import boto3
from src import extract_all_tables
from src import get_totesys_connection


connection = get_totesys_connection()


for table_name, json_body in extract_all_tables(connection):

    s3 = boto3.client("s3")

    s3.put_object(
        Bucket="",
        Key=f"{table_name}/data.json",
        Body=json_body,
        ContentType="application/json"
    )