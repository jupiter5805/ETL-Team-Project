import os

from .connection import get_totesys_connection
from .extract import extract_all_tables
from .s3_export import upload_to_s3


def lambda_handler(event, context):
    bucket_name = os.getenv("INGESTION_BUCKET_NAME")

    connection = get_totesys_connection()

    for table_name, json_body in extract_all_tables(connection):
        upload_to_s3(
            table_name,
            json_body,
            bucket_name
        )

    connection.close()