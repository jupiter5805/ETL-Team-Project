import os
import logging
from datetime import datetime

from .connection import get_totesys_connection
from .extract import extract_all_tables
from .s3_export import upload_to_s3, get_last_run, save_last_run

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Starting ingestion Lambda")

    bucket_name = os.getenv("INGESTION_BUCKET_NAME")

    last_run = get_last_run(bucket_name)
    current_run = datetime.now()

    connection = get_totesys_connection()
    logger.info("Database connection established")

    try:
        for table_name, json_body in extract_all_tables(connection, last_run):
            logger.info("Processing table: %s", table_name)

            upload_to_s3(
                table_name,
                json_body,
                bucket_name
            )

            logger.info("Uploaded table to S3: %s", table_name)

        logger.info("Ingestion Lambda completed successfully")
        save_last_run(bucket_name, current_run)
    finally:
        connection.close()
        logger.info("Database connection closed")