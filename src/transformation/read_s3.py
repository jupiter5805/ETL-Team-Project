import json

import boto3


def read_table_data_from_s3(bucket_name, object_key):
    """Read JSON data from an exact S3 object key."""
    s3 = boto3.client("s3")

    response = s3.get_object(
        Bucket=bucket_name,
        Key=object_key,
    )

    data = response["Body"].read()

    return json.loads(data)


def read_latest_table_data(bucket_name, table_name):
    """Read the most recently uploaded raw file for a table."""
    s3 = boto3.client("s3")

    prefix = f"raw/{table_name}/"

    response = s3.list_objects_v2(
        Bucket=bucket_name,
        Prefix=prefix,
    )

    objects = response.get("Contents", [])

    if not objects:
        return []

    latest_object = max(
        objects,
        key=lambda item: item["LastModified"],
    )

    response = s3.get_object(
        Bucket=bucket_name,
        Key=latest_object["Key"],
    )

    data = response["Body"].read()

    return json.loads(data)


def read_current_table_state(
    bucket_name,
    table_name,
    primary_key,
):
    """
    Rebuild the latest state of a table from all raw incremental files.

    Later versions of the same primary key replace earlier versions.
    """
    s3 = boto3.client("s3")

    prefix = f"raw/{table_name}/"

    response = s3.list_objects_v2(
        Bucket=bucket_name,
        Prefix=prefix,
    )

    objects = response.get("Contents", [])

    if not objects:
        return []

    objects = sorted(
        objects,
        key=lambda item: item["LastModified"],
    )

    current_state = {}

    for item in objects:
        response = s3.get_object(
            Bucket=bucket_name,
            Key=item["Key"],
        )

        data = response["Body"].read()
        rows = json.loads(data)

        for row in rows:
            current_state[row[primary_key]] = row

    return list(current_state.values())
