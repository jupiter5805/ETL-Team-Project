import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


SRC_DIR = Path(__file__).resolve().parents[2] / "src"
sys.path.insert(0, str(SRC_DIR))

import dashboard_query.lambda_function as dashboard  # noqa: E402


def test_rows_to_dicts():
    cursor = MagicMock()
    cursor.description = [
        ("id",),
        ("name",),
    ]
    cursor.fetchall.return_value = [
        (1, "Test"),
    ]

    result = dashboard.rows_to_dicts(cursor)

    assert result == [
        {
            "id": 1,
            "name": "Test",
        }
    ]


def test_fetch_rows():
    cursor = MagicMock()
    cursor.description = [
        ("id",),
    ]
    cursor.fetchall.return_value = [
        (1,),
    ]

    result = dashboard.fetch_rows(
        cursor,
        "SELECT id",
        [1],
    )

    cursor.execute.assert_called_once_with(
        "SELECT id",
        [1],
    )

    assert result == [
        {"id": 1}
    ]


def test_fetch_value():
    cursor = MagicMock()
    cursor.fetchone.return_value = (10,)

    result = dashboard.fetch_value(
        cursor,
        "SELECT COUNT(*)",
    )

    assert result == 10


def test_fetch_value_returns_zero():
    cursor = MagicMock()
    cursor.fetchone.return_value = None

    result = dashboard.fetch_value(
        cursor,
        "SELECT COUNT(*)",
    )

    assert result == 0


def test_build_filters_no_filters():
    filter_sql, parameters = dashboard.build_filters({})

    assert filter_sql == ""
    assert parameters == []


def test_build_filters_currency_and_countries():
    event = {
        "currency_code": "GBP",
        "countries": [
            "Austria",
            "Iceland",
        ],
    }

    filter_sql, parameters = dashboard.build_filters(
        event
    )

    assert "c.currency_code = %s" in filter_sql
    assert (
        "cp.counterparty_legal_country = ANY(%s)"
        in filter_sql
    )

    assert parameters == [
        "GBP",
        [
            "Austria",
            "Iceland",
        ],
    ]


@patch(
    "dashboard_query.lambda_function.fetch_rows"
)
def test_get_filter_options(mock_fetch_rows):
    mock_fetch_rows.side_effect = [
        [
            {
                "currency_code": "GBP",
                "currency_name": "Pound Sterling",
            }
        ],
        [
            {
                "country": "Austria",
            }
        ],
    ]

    result = dashboard.get_filter_options(
        MagicMock()
    )

    assert result == {
        "currencies": [
            {
                "currency_code": "GBP",
                "currency_name": "Pound Sterling",
            }
        ],
        "countries": [
            "Austria",
        ],
    }


@patch(
    "dashboard_query.lambda_function.fetch_rows"
)
def test_get_summary(mock_fetch_rows):
    mock_fetch_rows.return_value = [
        {
            "sales_orders": 5,
            "units_sold": 100,
            "sales_value": 250,
        }
    ]

    result = dashboard.get_summary(
        MagicMock(),
        "",
        [],
    )

    assert result == {
        "sales_orders": 5,
        "units_sold": 100,
        "sales_value": 250,
    }


@patch(
    "dashboard_query.lambda_function.fetch_rows"
)
def test_get_summary_empty(mock_fetch_rows):
    mock_fetch_rows.return_value = []

    result = dashboard.get_summary(
        MagicMock(),
        "",
        [],
    )

    assert result == {
        "sales_orders": 0,
        "units_sold": 0,
        "sales_value": 0,
    }


@patch(
    "dashboard_query.lambda_function.fetch_value"
)
def test_get_history_count(mock_fetch_value):
    mock_fetch_value.return_value = 12

    result = dashboard.get_history_count(
        MagicMock(),
        "",
        [],
    )

    assert result == 12


@patch(
    "dashboard_query.lambda_function.fetch_rows"
)
def test_dashboard_query_functions(mock_fetch_rows):
    mock_fetch_rows.return_value = [
        {"value": 1}
    ]

    cursor = MagicMock()

    functions = [
        dashboard.get_daily_sales,
        dashboard.get_top_designs,
        dashboard.get_top_counterparties,
        dashboard.get_staff_sales,
        dashboard.get_country_orders,
        dashboard.get_recent_orders,
    ]

    for function in functions:
        result = function(
            cursor,
            "",
            [],
        )

        assert result == [
            {"value": 1}
        ]


@patch(
    "dashboard_query.lambda_function.get_connection"
)
@patch(
    "dashboard_query.lambda_function.get_recent_orders"
)
@patch(
    "dashboard_query.lambda_function.get_country_orders"
)
@patch(
    "dashboard_query.lambda_function.get_staff_sales"
)
@patch(
    "dashboard_query.lambda_function.get_top_counterparties"
)
@patch(
    "dashboard_query.lambda_function.get_top_designs"
)
@patch(
    "dashboard_query.lambda_function.get_daily_sales"
)
@patch(
    "dashboard_query.lambda_function.get_history_count"
)
@patch(
    "dashboard_query.lambda_function.get_summary"
)
@patch(
    "dashboard_query.lambda_function.get_filter_options"
)
def test_lambda_handler(
    mock_filters,
    mock_summary,
    mock_history,
    mock_daily,
    mock_designs,
    mock_counterparties,
    mock_staff,
    mock_countries,
    mock_recent,
    mock_connection,
):
    connection = MagicMock()
    cursor = MagicMock()

    connection.cursor.return_value.__enter__.return_value = (
        cursor
    )
    mock_connection.return_value = connection

    mock_filters.return_value = {
        "currencies": [],
        "countries": [],
    }
    mock_summary.return_value = {
        "sales_orders": 1,
        "units_sold": 10,
        "sales_value": 20,
    }
    mock_history.return_value = 1
    mock_daily.return_value = []
    mock_designs.return_value = []
    mock_counterparties.return_value = []
    mock_staff.return_value = []
    mock_countries.return_value = []
    mock_recent.return_value = []

    result = dashboard.lambda_handler(
        {},
        None,
    )

    assert result["summary"]["sales_orders"] == 1
    assert result["fact_version_count"] == 1

    connection.close.assert_called_once()


@patch(
    "dashboard_query.lambda_function.get_connection"
)
def test_lambda_handler_closes_connection_on_error(
    mock_connection,
):
    connection = MagicMock()
    mock_connection.return_value = connection

    connection.cursor.side_effect = RuntimeError(
        "database error"
    )

    with pytest.raises(
        RuntimeError,
        match="database error",
    ):
        dashboard.lambda_handler(
            {},
            None,
        )

    connection.close.assert_called_once()
