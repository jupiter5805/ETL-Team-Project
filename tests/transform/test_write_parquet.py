from unittest.mock import patch, MagicMock

import pandas as pd

from src.transformation.write_parquet import (
    create_parquet,
    upload_parquet_to_s3
)


def test_create_parquet(tmp_path):
    data = [
        {
            "currency_id": 1,
            "currency_code": "GBP",
            "currency_name": "Pound Sterling"
        }
    ]

    file_path = tmp_path / "dim_currency.parquet"

    create_parquet(
        data,
        file_path
    )

    result = pd.read_parquet(file_path)

    assert result.to_dict("records") == data


@patch("src.transformation.write_parquet.boto3.client")
def test_upload_parquet_to_s3(mock_boto_client):
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3

    result = upload_parquet_to_s3(
        "dim_currency.parquet",
        "dim_currency",
        "marvel-etl-project-processed"
    )

    mock_s3.upload_file.assert_called_once()

    arguments = mock_s3.upload_file.call_args[0]

    assert arguments[0] == "dim_currency.parquet"
    assert arguments[1] == "marvel-etl-project-processed"

    assert arguments[2].startswith("dim_currency/")
    assert arguments[2].endswith(".parquet")

    assert result.startswith("dim_currency/")
    assert result.endswith(".parquet")
