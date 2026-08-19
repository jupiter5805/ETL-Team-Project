import json
from datetime import datetime
from io import BytesIO
from unittest.mock import MagicMock, patch

from src.transformation.read_s3 import (
    read_current_table_state,
    read_latest_table_data,
    read_table_data_from_s3,
)


@patch("src.transformation.read_s3.boto3.client")
def test_read_table_data_from_exact_s3_key(mock_boto_client):
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3

    currency_data = [
        {
            "currency_id": 1,
            "currency_code": "GBP",
        }
    ]

    mock_s3.get_object.return_value = {
        "Body": BytesIO(
            json.dumps(currency_data).encode()
        )
    }

    result = read_table_data_from_s3(
        "test-ingestion-bucket",
        "raw/currency/exact-file.json",
    )

    assert result == currency_data

    mock_s3.get_object.assert_called_once_with(
        Bucket="test-ingestion-bucket",
        Key="raw/currency/exact-file.json",
    )

    mock_s3.list_objects_v2.assert_not_called()


@patch("src.transformation.read_s3.boto3.client")
def test_read_latest_table_data(mock_boto_client):
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3

    older_time = datetime(2026, 8, 18, 10, 0)
    newer_time = datetime(2026, 8, 19, 10, 0)

    mock_s3.list_objects_v2.return_value = {
        "Contents": [
            {
                "Key": "raw/department/older.json",
                "LastModified": older_time,
            },
            {
                "Key": "raw/department/newer.json",
                "LastModified": newer_time,
            },
        ]
    }

    department_data = [
        {
            "department_id": 1,
            "department_name": "Sales",
        }
    ]

    mock_s3.get_object.return_value = {
        "Body": BytesIO(
            json.dumps(department_data).encode()
        )
    }

    result = read_latest_table_data(
        "test-ingestion-bucket",
        "department",
    )

    assert result == department_data

    mock_s3.list_objects_v2.assert_called_once_with(
        Bucket="test-ingestion-bucket",
        Prefix="raw/department/",
    )

    mock_s3.get_object.assert_called_once_with(
        Bucket="test-ingestion-bucket",
        Key="raw/department/newer.json",
    )


@patch("src.transformation.read_s3.boto3.client")
def test_read_latest_table_data_returns_empty_list_when_no_files(
    mock_boto_client,
):
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3

    mock_s3.list_objects_v2.return_value = {}

    result = read_latest_table_data(
        "test-ingestion-bucket",
        "department",
    )

    assert result == []

    mock_s3.get_object.assert_not_called()


@patch("src.transformation.read_s3.boto3.client")
def test_read_current_table_state_rebuilds_latest_rows(
    mock_boto_client,
):
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3

    first_time = datetime(2026, 8, 18, 10, 0)
    second_time = datetime(2026, 8, 19, 10, 0)
    third_time = datetime(2026, 8, 19, 11, 0)

    mock_s3.list_objects_v2.return_value = {
        "Contents": [
            {
                "Key": "raw/department/first.json",
                "LastModified": first_time,
            },
            {
                "Key": "raw/department/second.json",
                "LastModified": second_time,
            },
            {
                "Key": "raw/department/third.json",
                "LastModified": third_time,
            },
        ]
    }

    first_data = [
        {
            "department_id": 1,
            "department_name": "Sales",
        },
        {
            "department_id": 2,
            "department_name": "Purchasing",
        },
    ]

    second_data = [
        {
            "department_id": 1,
            "department_name": "Commercial",
        }
    ]

    third_data = []

    mock_s3.get_object.side_effect = [
        {
            "Body": BytesIO(
                json.dumps(first_data).encode()
            )
        },
        {
            "Body": BytesIO(
                json.dumps(second_data).encode()
            )
        },
        {
            "Body": BytesIO(
                json.dumps(third_data).encode()
            )
        },
    ]

    result = read_current_table_state(
        "test-ingestion-bucket",
        "department",
        "department_id",
    )

    assert result == [
        {
            "department_id": 1,
            "department_name": "Commercial",
        },
        {
            "department_id": 2,
            "department_name": "Purchasing",
        },
    ]


@patch("src.transformation.read_s3.boto3.client")
def test_read_current_table_state_returns_empty_when_no_files(
    mock_boto_client,
):
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3

    mock_s3.list_objects_v2.return_value = {}

    result = read_current_table_state(
        "test-ingestion-bucket",
        "staff",
        "staff_id",
    )

    assert result == []
