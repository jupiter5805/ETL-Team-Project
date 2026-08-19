import boto3
from moto import mock_aws
from unittest.mock import patch
from botocore.exceptions import ClientError
from datetime import datetime

from src.ingestion.s3_export import (
    upload_to_s3,
    get_last_run,
    save_last_run
)


@mock_aws
def test_upload_to_s3_creates_object():

    # arrange
    s3 = boto3.client("s3", region_name="eu-west-2")

    s3.create_bucket(
        Bucket="test-bucket",
        CreateBucketConfiguration={
            "LocationConstraint": "eu-west-2"
        }
    )

    table_name = "currency"
    json_body = '[{"currency_id": 1, "currency_code": "GBP"}]'

    # act
    upload_to_s3(
        table_name,
        json_body,
        "test-bucket"
    )

    # assert
    response = s3.list_objects_v2(
        Bucket="test-bucket"
    )

    uploaded_key = response["Contents"][0]["Key"]

    uploaded_object = s3.get_object(
        Bucket="test-bucket",
        Key=uploaded_key
    )

    uploaded_body = (
        uploaded_object["Body"]
        .read()
        .decode("utf-8")
    )

    assert uploaded_key.startswith("raw/currency/")
    assert uploaded_key.endswith(".json")
    assert uploaded_body == json_body


@mock_aws
@patch("src.ingestion.s3_export.datetime")
def test_upload_to_s3_creates_different_files_for_different_times(
    mocked_datetime
):

    # arrange
    s3 = boto3.client("s3", region_name="eu-west-2")

    s3.create_bucket(
        Bucket="test-bucket",
        CreateBucketConfiguration={
            "LocationConstraint": "eu-west-2"
        }
    )

    table_name = "currency"
    json_body = '[{"currency_id": 1}]'

    mocked_datetime.now.return_value.isoformat.return_value = (
        "2026-08-13T10:00:00"
    )

    # act
    upload_to_s3(
        table_name,
        json_body,
        "test-bucket"
    )

    mocked_datetime.now.return_value.isoformat.return_value = (
        "2026-08-13T10:15:00"
    )

    upload_to_s3(
        table_name,
        json_body,
        "test-bucket"
    )

    # assert
    response = s3.list_objects_v2(
        Bucket="test-bucket"
    )

    assert len(response["Contents"]) == 2


@patch("src.ingestion.s3_export.boto3.client")
def test_upload_to_s3_raises_error_when_upload_fails(mocked_boto_client):

    # arrange
    mocked_s3 = mocked_boto_client.return_value

    mocked_s3.put_object.side_effect = ClientError(
        {
            "Error": {
                "Code": "AccessDenied",
                "Message": "Access Denied"
            }
        },
        "PutObject"
    )

    # act + assert
    try:
        upload_to_s3(
            "currency",
            '[{"currency_id": 1}]',
            "test-bucket"
        )

        assert False

    except ClientError as error:
        assert error.response["Error"]["Code"] == "AccessDenied"


@mock_aws
def test_save_last_run_saves_timestamp_to_s3():

    # arrange
    s3 = boto3.client("s3", region_name="eu-west-2")

    s3.create_bucket(
        Bucket="test-bucket",
        CreateBucketConfiguration={
            "LocationConstraint": "eu-west-2"
        }
    )

    last_run = datetime(2026, 8, 16, 20, 0)

    # act
    save_last_run(
        "test-bucket",
        last_run
    )

    # assert
    response = s3.get_object(
        Bucket="test-bucket",
        Key="metadata/last_run.txt"
    )

    saved_time = (
        response["Body"]
        .read()
        .decode("utf-8")
    )

    assert saved_time == "2026-08-16T20:00:00"


@mock_aws
def test_get_last_run_returns_saved_timestamp():

    # arrange
    s3 = boto3.client("s3", region_name="eu-west-2")

    s3.create_bucket(
        Bucket="test-bucket",
        CreateBucketConfiguration={
            "LocationConstraint": "eu-west-2"
        }
    )

    s3.put_object(
        Bucket="test-bucket",
        Key="metadata/last_run.txt",
        Body="2026-08-16T20:00:00"
    )

    # act
    result = get_last_run("test-bucket")

    # assert
    assert result == datetime(2026, 8, 16, 20, 0)


@mock_aws
def test_get_last_run_returns_none_when_no_timestamp_exists():

    # arrange
    s3 = boto3.client("s3", region_name="eu-west-2")

    s3.create_bucket(
        Bucket="test-bucket",
        CreateBucketConfiguration={
            "LocationConstraint": "eu-west-2"
        }
    )

    # act
    result = get_last_run("test-bucket")

    # assert
    assert result is None
