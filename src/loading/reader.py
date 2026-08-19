import io
import logging

import boto3
import pandas as pd


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3")


def read_parquet_from_s3(
    bucket_name: str,
    object_key: str,
) -> pd.DataFrame:
    """
    Read a Parquet file from S3.

    Args:
        bucket_name: Name of the processed S3 bucket.
        object_key: Key of the Parquet file.

    Returns:
        A pandas DataFrame containing the Parquet data.
    """

    logger.info(
        "Reading s3://%s/%s",
        bucket_name,
        object_key,
    )

    response = s3_client.get_object(
        Bucket=bucket_name,
        Key=object_key,
    )

    file_content = response["Body"].read()

    if not file_content:
        raise ValueError(
            f"Empty S3 object: {object_key}"
        )

    dataframe = pd.read_parquet(
        io.BytesIO(file_content),
        engine="pyarrow",
    )

    logger.info(
        "Read %d rows from %s",
        len(dataframe),
        object_key,
    )

    return dataframe
