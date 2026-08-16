import boto3
import logging
from datetime import datetime
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


def get_last_run(bucket_name):
    s3 = boto3.client("s3")

    try:
        response = s3.get_object(
            Bucket=bucket_name,
            Key="metadata/last_run.txt"
        )

        last_run = response["Body"].read().decode("utf-8")
        return datetime.fromisoformat(last_run)

    except ClientError as error:
        if error.response["Error"]["Code"] == "NoSuchKey":
            return None
        raise

def save_last_run(bucket_name, last_run):
    s3 = boto3.client("s3")

    s3.put_object(
        Bucket=bucket_name,
        Key="metadata/last_run.txt",
        Body=last_run.isoformat()
    )


def upload_to_s3(table_name, json_body, bucket_name):
    s3 = boto3.client("s3")
    current_time = datetime.now().isoformat()

    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=f"raw/{table_name}/{current_time}.json",
            Body=json_body,
            ContentType="application/json"
        )

    except ClientError:
        logger.exception(f"Failed to upload {table_name} to S3")
        raise