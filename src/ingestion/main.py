import os

from src.ingestion.connection import get_totesys_connection
from src.ingestion.extract import extract_all_tables
from src.ingestion.s3_export import upload_to_s3


def lambda_handler(event, context):
    bucket_name = os.getenv("INGESTION_BUCKET_NAME")

    connection = get_totesys_connection()

    try:
        for table_name, json_body in extract_all_tables(connection):
            upload_to_s3(
                table_name,
                json_body,
                bucket_name
            )
            
    finally:
        connection.close()