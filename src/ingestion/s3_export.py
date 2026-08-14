import boto3
from datetime import datetime, timezone

from src.ingestion.connection import get_totesys_connection
from src.ingestion.extract import extract_all_tables


BUCKET_NAME = "marvel-etl-project-ingestion"


def upload_currency_to_s3(connection):
    rows = extract_table(connection, "currency")

    json_body = rows_to_json(rows)


connection = get_totesys_connection()

s3 = boto3.client("s3")


for table_name, json_body in extract_all_tables(connection):

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y-%m-%d_%H-%M-%S-%f"
    )

    object_key = f"{table_name}/{timestamp}.json"

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=object_key,
        Body=json_body,
        ContentType="application/json",
    )

    print(f"Uploaded: {object_key}")


connection.close()


# for testing
# import boto3
# from datetime import datetime


# def upload_to_s3(table_name, json_body, bucket_name):
#     s3 = boto3.client("s3")

#     current_time = datetime.now().isoformat()

#     s3.put_object(
#         Bucket=bucket_name,
#         Key=f"{table_name}/{current_time}.json",
#         Body=json_body,
#         ContentType="application/json"
#     )
