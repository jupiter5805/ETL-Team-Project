import pandas as pd
import pytest
from unittest.mock import MagicMock, patch

from src.loading import lambda_function as loading_lambda


def make_s3_event(
    bucket="marvel-etl-project-processed",
    key="dim_currency/test.parquet",
):
    return {
        "Records": [
            {
                "s3": {
                    "bucket": {
                        "name": bucket
                    },
                    "object": {
                        "key": key
                    },
                }
            }
        ]
    }


@patch.object(
    loading_lambda,
    "get_connection",
)
@patch.object(
    loading_lambda,
    "read_parquet_from_s3",
)
def test_lambda_loads_currency(
    mock_read_parquet,
    mock_get_connection,
):
    dataframe = pd.DataFrame(
        [
            {
                "currency_id": 1,
                "currency_code": "GBP",
                "currency_name": "Pound Sterling",
            }
        ]
    )

    mock_read_parquet.return_value = dataframe

    connection = MagicMock()
    cursor = MagicMock()

    connection.cursor.return_value.__enter__.return_value = cursor
    mock_get_connection.return_value = connection

    mock_loader = MagicMock()

    event = make_s3_event(
        key="dim_currency/test.parquet"
    )

    with patch.dict(
        loading_lambda.LOADERS,
        {"dim_currency": mock_loader},
    ):
        result = loading_lambda.lambda_handler(
            event,
            None,
        )

    mock_read_parquet.assert_called_once_with(
        "marvel-etl-project-processed",
        "dim_currency/test.parquet",
    )

    mock_loader.assert_called_once_with(
        cursor,
        [
            {
                "currency_id": 1,
                "currency_code": "GBP",
                "currency_name": "Pound Sterling",
            }
        ],
    )

    connection.commit.assert_called_once()
    connection.rollback.assert_not_called()
    connection.close.assert_called_once()

    assert result == {
        "table_name": "dim_currency",
        "object_key": "dim_currency/test.parquet",
        "rows_loaded": 1,
    }


@patch.object(
    loading_lambda,
    "get_connection",
)
@patch.object(
    loading_lambda,
    "read_parquet_from_s3",
)
def test_lambda_loads_staff(
    mock_read_parquet,
    mock_get_connection,
):
    dataframe = pd.DataFrame(
        [
            {
                "staff_id": 1,
                "first_name": "Jeremie",
                "last_name": "Franey",
                "department_name": "Purchasing",
                "location": "Manchester",
                "email_address":
                    "jeremie.franey@terrifictotes.com",
            }
        ]
    )

    mock_read_parquet.return_value = dataframe

    connection = MagicMock()
    cursor = MagicMock()

    connection.cursor.return_value.__enter__.return_value = cursor
    mock_get_connection.return_value = connection

    mock_loader = MagicMock()

    event = make_s3_event(
        key="dim_staff/test.parquet"
    )

    with patch.dict(
        loading_lambda.LOADERS,
        {"dim_staff": mock_loader},
    ):
        loading_lambda.lambda_handler(
            event,
            None,
        )

    mock_loader.assert_called_once_with(
        cursor,
        [
            {
                "staff_id": 1,
                "first_name": "Jeremie",
                "last_name": "Franey",
                "department_name": "Purchasing",
                "location": "Manchester",
                "email_address":
                    "jeremie.franey@terrifictotes.com",
            }
        ],
    )

    connection.commit.assert_called_once()
    connection.close.assert_called_once()


@pytest.mark.parametrize(
    "table_name",
    [
        "dim_location",
        "dim_design",
        "dim_counterparty",
        "dim_date",
        "fact_sales_order",
    ],
)
@patch.object(
    loading_lambda,
    "get_connection",
)
@patch.object(
    loading_lambda,
    "read_parquet_from_s3",
)
def test_lambda_routes_to_correct_loader(
    mock_read_parquet,
    mock_get_connection,
    table_name,
):
    dataframe = pd.DataFrame(
        [
            {
                "test_column": "test_value"
            }
        ]
    )

    mock_read_parquet.return_value = dataframe

    connection = MagicMock()
    cursor = MagicMock()

    connection.cursor.return_value.__enter__.return_value = cursor
    mock_get_connection.return_value = connection

    mock_loader = MagicMock()

    event = make_s3_event(
        key=f"{table_name}/test.parquet"
    )

    with patch.dict(
        loading_lambda.LOADERS,
        {table_name: mock_loader},
    ):
        loading_lambda.lambda_handler(
            event,
            None,
        )

    mock_loader.assert_called_once_with(
        cursor,
        [
            {
                "test_column": "test_value"
            }
        ],
    )

    connection.commit.assert_called_once()
    connection.close.assert_called_once()


@patch.object(
    loading_lambda,
    "get_connection",
)
@patch.object(
    loading_lambda,
    "read_parquet_from_s3",
)
def test_lambda_rejects_unknown_table(
    mock_read_parquet,
    mock_get_connection,
):
    event = make_s3_event(
        key="random_table/test.parquet"
    )

    with pytest.raises(
        ValueError,
        match="Unsupported table",
    ):
        loading_lambda.lambda_handler(
            event,
            None,
        )

    mock_read_parquet.assert_not_called()
    mock_get_connection.assert_not_called()


@patch.object(
    loading_lambda,
    "get_connection",
)
@patch.object(
    loading_lambda,
    "read_parquet_from_s3",
)
def test_lambda_rolls_back_if_loader_fails(
    mock_read_parquet,
    mock_get_connection,
):
    dataframe = pd.DataFrame(
        [
            {
                "currency_id": 1,
                "currency_code": "GBP",
                "currency_name": "Pound Sterling",
            }
        ]
    )

    mock_read_parquet.return_value = dataframe

    connection = MagicMock()
    cursor = MagicMock()

    connection.cursor.return_value.__enter__.return_value = cursor
    mock_get_connection.return_value = connection

    mock_loader = MagicMock(
        side_effect=RuntimeError(
            "database error"
        )
    )

    event = make_s3_event(
        key="dim_currency/test.parquet"
    )

    with patch.dict(
        loading_lambda.LOADERS,
        {"dim_currency": mock_loader},
    ):
        with pytest.raises(
            RuntimeError,
            match="database error",
        ):
            loading_lambda.lambda_handler(
                event,
                None,
            )

    connection.rollback.assert_called_once()
    connection.commit.assert_not_called()
    connection.close.assert_called_once()


@patch.object(
    loading_lambda,
    "get_connection",
)
@patch.object(
    loading_lambda,
    "read_parquet_from_s3",
)
def test_lambda_converts_dataframe_to_records(
    mock_read_parquet,
    mock_get_connection,
):
    dataframe = pd.DataFrame(
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

    mock_read_parquet.return_value = dataframe

    connection = MagicMock()
    cursor = MagicMock()

    connection.cursor.return_value.__enter__.return_value = cursor
    mock_get_connection.return_value = connection

    mock_loader = MagicMock()

    event = make_s3_event(
        key="dim_currency/test.parquet"
    )

    with patch.dict(
        loading_lambda.LOADERS,
        {"dim_currency": mock_loader},
    ):
        loading_lambda.lambda_handler(
            event,
            None,
        )

    records = mock_loader.call_args.args[1]

    assert isinstance(records, list)
    assert len(records) == 2

    assert records[0] == {
        "currency_id": 1,
        "currency_code": "GBP",
        "currency_name": "Pound Sterling",
    }

    assert records[1] == {
        "currency_id": 2,
        "currency_code": "USD",
        "currency_name": "US Dollar",
    }
