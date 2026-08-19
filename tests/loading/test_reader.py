import io
from unittest.mock import patch

import pandas as pd
import pytest

from src.loading.reader import read_parquet_from_s3


def create_parquet_bytes(data):
    dataframe = pd.DataFrame(data)

    buffer = io.BytesIO()

    dataframe.to_parquet(
        buffer,
        index=False,
        engine="pyarrow",
    )

    buffer.seek(0)

    return buffer.read()


@patch("src.loading.reader.s3_client")
def test_read_parquet_from_s3(mock_s3):
    parquet_bytes = create_parquet_bytes(
        [
            {
                "currency_id": 1,
                "currency_code": "GBP",
                "currency_name": "Pound Sterling",
            },
            {
                "currency_id": 2,
                "currency_code": "USD",
                "currency_name": "US Dollar",
            },
        ]
    )

    mock_s3.get_object.return_value = {
        "Body": io.BytesIO(parquet_bytes)
    }

    result = read_parquet_from_s3(
        "test-processed-bucket",
        "dim_currency/test.parquet",
    )

    assert len(result) == 2

    assert result.iloc[0]["currency_id"] == 1
    assert result.iloc[0]["currency_code"] == "GBP"

    mock_s3.get_object.assert_called_once_with(
        Bucket="test-processed-bucket",
        Key="dim_currency/test.parquet",
    )


@patch("src.loading.reader.s3_client")
def test_read_parquet_from_s3_returns_dataframe(
    mock_s3,
):
    parquet_bytes = create_parquet_bytes(
        [
            {
                "currency_id": 1,
                "currency_code": "GBP",
                "currency_name": "Pound Sterling",
            }
        ]
    )

    mock_s3.get_object.return_value = {
        "Body": io.BytesIO(parquet_bytes)
    }

    result = read_parquet_from_s3(
        "test-bucket",
        "dim_currency/test.parquet",
    )

    assert isinstance(result, pd.DataFrame)


@patch("src.loading.reader.s3_client")
def test_read_parquet_from_s3_empty_file_raises_error(
    mock_s3,
):
    mock_s3.get_object.return_value = {
        "Body": io.BytesIO(b"")
    }

    with pytest.raises(
        ValueError,
        match="Empty S3 object",
    ):
        read_parquet_from_s3(
            "test-bucket",
            "dim_currency/empty.parquet",
        )
