from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from src.loading import lambda_function as loading_lambda


def test_get_recent_processed_files_filters_and_orders_files():
    now = datetime.now(timezone.utc)

    paginator = MagicMock()

    paginator.paginate.return_value = [
        {
            "Contents": [
                {
                    "Key": "fact_sales_order/fact.parquet",
                    "LastModified": now - timedelta(minutes=5),
                },
                {
                    "Key": "dim_currency/currency.parquet",
                    "LastModified": now - timedelta(minutes=10),
                },
                {
                    "Key": "dim_staff/staff.parquet",
                    "LastModified": now - timedelta(minutes=8),
                },
                {
                    "Key": "dim_design/old.parquet",
                    "LastModified": now - timedelta(minutes=70),
                },
                {
                    "Key": "dim_currency/not_parquet.json",
                    "LastModified": now - timedelta(minutes=5),
                },
                {
                    "Key": "unknown_table/test.parquet",
                    "LastModified": now - timedelta(minutes=5),
                },
            ]
        }
    ]

    with patch.object(
        loading_lambda.s3_client,
        "get_paginator",
        return_value=paginator,
    ) as mock_get_paginator:
        result = loading_lambda.get_recent_processed_files(
            "processed-bucket"
        )

    assert result == [
        "dim_currency/currency.parquet",
        "dim_staff/staff.parquet",
        "fact_sales_order/fact.parquet",
    ]

    mock_get_paginator.assert_called_once_with(
        "list_objects_v2"
    )

    paginator.paginate.assert_called_once_with(
        Bucket="processed-bucket"
    )


def test_get_recent_processed_files_handles_pagination():
    now = datetime.now(timezone.utc)

    paginator = MagicMock()

    paginator.paginate.return_value = [
        {
            "Contents": [
                {
                    "Key": "dim_currency/currency.parquet",
                    "LastModified": now,
                }
            ]
        },
        {
            "Contents": [
                {
                    "Key": "fact_sales_order/sales.parquet",
                    "LastModified": now,
                }
            ]
        },
    ]

    with patch.object(
        loading_lambda.s3_client,
        "get_paginator",
        return_value=paginator,
    ):
        result = loading_lambda.get_recent_processed_files(
            "processed-bucket"
        )

    assert result == [
        "dim_currency/currency.parquet",
        "fact_sales_order/sales.parquet",
    ]


@patch.object(
    loading_lambda,
    "load_object",
)
@patch.object(
    loading_lambda,
    "get_recent_processed_files",
)
def test_scheduled_lambda_loads_recent_files(
    mock_get_recent_files,
    mock_load_object,
):
    mock_get_recent_files.return_value = [
        "dim_currency/currency.parquet",
        "dim_staff/staff.parquet",
        "fact_sales_order/sales.parquet",
    ]

    mock_load_object.side_effect = [
        {
            "table_name": "dim_currency",
            "rows_loaded": 2,
        },
        {
            "table_name": "dim_staff",
            "rows_loaded": 3,
        },
        {
            "table_name": "fact_sales_order",
            "rows_loaded": 5,
        },
    ]

    event = {
        "mode": "scheduled",
        "bucket_name": "processed-bucket",
    }

    result = loading_lambda.lambda_handler(
        event,
        None,
    )

    mock_get_recent_files.assert_called_once_with(
        "processed-bucket"
    )

    assert mock_load_object.call_count == 3

    assert mock_load_object.call_args_list[0].args == (
        "processed-bucket",
        "dim_currency/currency.parquet",
    )

    assert mock_load_object.call_args_list[1].args == (
        "processed-bucket",
        "dim_staff/staff.parquet",
    )

    assert mock_load_object.call_args_list[2].args == (
        "processed-bucket",
        "fact_sales_order/sales.parquet",
    )

    assert result == {
        "mode": "scheduled",
        "files_processed": 3,
        "results": [
            {
                "table_name": "dim_currency",
                "rows_loaded": 2,
            },
            {
                "table_name": "dim_staff",
                "rows_loaded": 3,
            },
            {
                "table_name": "fact_sales_order",
                "rows_loaded": 5,
            },
        ],
    }


def test_scheduled_lambda_requires_bucket_name():
    event = {
        "mode": "scheduled"
    }

    try:
        loading_lambda.lambda_handler(
            event,
            None,
        )

        assert False

    except ValueError as error:
        assert str(error) == (
            "Scheduled event must contain bucket_name"
        )
