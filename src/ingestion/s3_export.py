import boto3
import logging
from datetime import datetime
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


def upload_to_s3(table_name, json_body, bucket_name):
    s3 = boto3.client("s3")
    current_time = datetime.now().isoformat()

    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=f"{table_name}/{current_time}.json",
            Body=json_body,
            ContentType="application/json"
        )

    except ClientError:
        logger.exception(f"Failed to upload {table_name} to S3")
        raise
