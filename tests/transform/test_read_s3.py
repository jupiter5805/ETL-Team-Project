import json
from io import BytesIO
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.transformation.read_s3 import read_latest_table_data


@patch("src.transformation.read_s3.boto3.client")
def test_read_latest_table_data(mock_boto_client):
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3

    mock_s3.list_objects_v2.return_value = {
        "Contents": [
            {
                "Key": "raw/currency/old.json",
                "LastModified": datetime(2026, 8, 16, 10, 0)
            },
            {
                "Key": "raw/currency/new.json",
                "LastModified": datetime(2026, 8, 17, 10, 0)
            }
        ]
    }

    currency_data = [
        {
            "currency_id": 1,
            "currency_code": "GBP"
        }
    ]

    mock_s3.get_object.return_value = {
        "Body": BytesIO(
            json.dumps(currency_data).encode()
        )
    }

    result = read_latest_table_data(
        "marvel-etl-project-ingestion",
        "currency"
    )

    assert result == currency_data

    mock_s3.list_objects_v2.assert_called_once_with(
        Bucket="marvel-etl-project-ingestion",
        Prefix="raw/currency/"
    )

    mock_s3.get_object.assert_called_once_with(
        Bucket="marvel-etl-project-ingestion",
        Key="raw/currency/new.json"
    )
