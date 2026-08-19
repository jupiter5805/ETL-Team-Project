import logging
from datetime import datetime, timedelta, timezone
from urllib.parse import unquote_plus

import boto3

from .connect_RDS import get_connection
from .reader import read_parquet_from_s3
from .loader import (
    load_staff,
    load_location,
    load_design,
    load_currency,
    load_counterparty,
    load_date,
    load_sales_order,
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3")


LOADERS = {
    "dim_staff": load_staff,
    "dim_location": load_location,
    "dim_design": load_design,
    "dim_currency": load_currency,
    "dim_counterparty": load_counterparty,
    "dim_date": load_date,
    "fact_sales_order": load_sales_order,
}


TABLE_ORDER = {
    "dim_staff": 1,
    "dim_location": 1,
    "dim_design": 1,
    "dim_currency": 1,
    "dim_counterparty": 1,
    "dim_date": 1,
    "fact_sales_order": 2,
}


LOOKBACK_MINUTES = 60


def load_object(bucket_name, object_key):
    object_key = unquote_plus(object_key)

    table_name = object_key.split("/", 1)[0]

    if table_name not in LOADERS:
        raise ValueError(
            f"Unsupported table: {table_name}"
        )

    logger.info(
        "Loading %s from s3://%s/%s",
        table_name,
        bucket_name,
        object_key,
    )

    dataframe = read_parquet_from_s3(
        bucket_name,
        object_key,
    )

    records = dataframe.to_dict(
        orient="records"
    )

    loader_function = LOADERS[table_name]

    connection = get_connection()

    try:
        with connection.cursor() as cur:
            loader_function(
                cur,
                records,
            )

        connection.commit()

        logger.info(
            "Successfully loaded %d rows into %s",
            len(records),
            table_name,
        )

    except Exception:
        connection.rollback()

        logger.exception(
            "Failed loading %s",
            table_name,
        )

        raise

    finally:
        connection.close()

    return {
        "table_name": table_name,
        "object_key": object_key,
        "rows_loaded": len(records),
    }


def get_recent_processed_files(bucket_name):
    cutoff = (
        datetime.now(timezone.utc)
        - timedelta(minutes=LOOKBACK_MINUTES)
    )

    files = []

    paginator = s3_client.get_paginator(
        "list_objects_v2"
    )

    for page in paginator.paginate(
        Bucket=bucket_name
    ):
        for item in page.get("Contents", []):
            object_key = item["Key"]

            if not object_key.endswith(".parquet"):
                continue

            table_name = object_key.split("/", 1)[0]

            if table_name not in LOADERS:
                continue

            if item["LastModified"] < cutoff:
                continue

            files.append(
                (
                    TABLE_ORDER[table_name],
                    item["LastModified"],
                    object_key,
                )
            )

    files.sort(
        key=lambda item: (
            item[0],
            item[1],
            item[2],
        )
    )

    return [
        object_key
        for _, _, object_key in files
    ]


def lambda_handler(event, context):
    if "Records" in event:
        bucket_name = (
            event["Records"][0]["s3"]["bucket"]["name"]
        )

        object_key = (
            event["Records"][0]["s3"]["object"]["key"]
        )

        return load_object(
            bucket_name,
            object_key,
        )

    bucket_name = event.get("bucket_name")

    if not bucket_name:
        raise ValueError(
            "Scheduled event must contain bucket_name"
        )

    logger.info(
        "Scheduled Loading run started for %s",
        bucket_name,
    )

    object_keys = get_recent_processed_files(
        bucket_name
    )

    results = []

    for object_key in object_keys:
        result = load_object(
            bucket_name,
            object_key,
        )

        results.append(result)

    logger.info(
        "Scheduled Loading run finished. "
        "Processed %d files.",
        len(results),
    )

    return {
        "mode": "scheduled",
        "files_processed": len(results),
        "results": results,
    }
