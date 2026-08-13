import boto3
from datetime import datetime, timezone

from src.ingestion.connection import get_totesys_connection
from src.ingestion.extract import extract_all_tables


BUCKET_NAME = "marvel-etl-project-ingestion"


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
