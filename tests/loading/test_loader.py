from datetime import date, time
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from src.loading.loader import (
    load_staff,
    load_location,
    load_design,
    load_currency,
    load_counterparty,
    load_date,
    load_sales_order,
    load_all,
)


def test_load_staff_executes_insert():
    cur = MagicMock()

    staff_data = [
        {
            "staff_id": 1,
            "first_name": "Jeremie",
            "last_name": "Franey",
            "department_name": "Purchasing",
            "location": "Manchester",
            "email_address": "jeremie.franey@terrifictotes.com",
        }
    ]

    load_staff(cur, staff_data)

    cur.execute.assert_called_once()

    parameters = cur.execute.call_args.args[1]

    assert parameters == (
        1,
        "Jeremie",
        "Franey",
        "Purchasing",
        "Manchester",
        "jeremie.franey@terrifictotes.com",
    )

    sql = cur.execute.call_args.args[0]

    assert "INSERT INTO dim_staff" in sql
    assert "ON CONFLICT (staff_id)" in sql


def test_load_location_executes_insert():
    cur = MagicMock()

    location_data = [
        {
            "location_id": 15,
            "address_line_1": "605 Haskell Trafficway",
            "address_line_2": "Axel Freeway",
            "district": None,
            "city": "East Bobbie",
            "postal_code": "88253-4257",
            "country": "Heard Island and McDonald Islands",
            "phone": "9687 937447",
        }
    ]

    load_location(cur, location_data)

    cur.execute.assert_called_once()

    parameters = cur.execute.call_args.args[1]

    assert parameters == (
        15,
        "605 Haskell Trafficway",
        "Axel Freeway",
        None,
        "East Bobbie",
        "88253-4257",
        "Heard Island and McDonald Islands",
        "9687 937447",
    )

    sql = cur.execute.call_args.args[0]

    assert "INSERT INTO dim_location" in sql
    assert "ON CONFLICT (location_id)" in sql


def test_load_design_executes_insert():
    cur = MagicMock()

    design_data = [
        {
            "design_id": 3,
            "design_name": "Steel",
            "file_location": "/usr",
            "file_name": "steel.json",
        }
    ]

    load_design(cur, design_data)

    cur.execute.assert_called_once()

    parameters = cur.execute.call_args.args[1]

    assert parameters == (
        3,
        "Steel",
        "/usr",
        "steel.json",
    )

    sql = cur.execute.call_args.args[0]

    assert "INSERT INTO dim_design" in sql
    assert "ON CONFLICT (design_id)" in sql


def test_load_currency_executes_insert():
    cur = MagicMock()

    currency_data = [
        {
            "currency_id": 1,
            "currency_code": "GBP",
            "currency_name": "Pound Sterling",
        }
    ]

    load_currency(cur, currency_data)

    cur.execute.assert_called_once()

    parameters = cur.execute.call_args.args[1]

    assert parameters == (
        1,
        "GBP",
        "Pound Sterling",
    )

    sql = cur.execute.call_args.args[0]

    assert "INSERT INTO dim_currency" in sql
    assert "ON CONFLICT (currency_id)" in sql


def test_load_counterparty_executes_insert():
    cur = MagicMock()

    counterparty_data = [
        {
            "counterparty_id": 1,
            "counterparty_legal_name": "Fahey and Sons",
            "counterparty_legal_address_line_1":
                "605 Haskell Trafficway",
            "counterparty_legal_address_line_2":
                "Axel Freeway",
            "counterparty_legal_district": None,
            "counterparty_legal_city": "East Bobbie",
            "counterparty_legal_postal_code": "88253-4257",
            "counterparty_legal_country":
                "Heard Island and McDonald Islands",
            "counterparty_legal_phone_number": "9687 937447",
        }
    ]

    load_counterparty(
        cur,
        counterparty_data,
    )

    cur.execute.assert_called_once()

    parameters = cur.execute.call_args.args[1]

    assert parameters == (
        1,
        "Fahey and Sons",
        "605 Haskell Trafficway",
        "Axel Freeway",
        None,
        "East Bobbie",
        "88253-4257",
        "Heard Island and McDonald Islands",
        "9687 937447",
    )

    sql = cur.execute.call_args.args[0]

    assert "INSERT INTO dim_counterparty" in sql
    assert "ON CONFLICT (counterparty_id)" in sql


def test_load_date_executes_insert():
    cur = MagicMock()

    date_data = [
        {
            "date_id": date(2022, 11, 3),
            "year": 2022,
            "month": 11,
            "day": 3,
            "day_of_week": 4,
            "day_name": "Thursday",
            "month_name": "November",
            "quarter": 4,
        }
    ]

    load_date(cur, date_data)

    cur.execute.assert_called_once()

    parameters = cur.execute.call_args.args[1]

    assert parameters == (
        date(2022, 11, 3),
        2022,
        11,
        3,
        4,
        "Thursday",
        "November",
        4,
    )

    sql = cur.execute.call_args.args[0]

    assert "INSERT INTO dim_date" in sql
    assert "ON CONFLICT (date_id) DO NOTHING" in sql


def test_load_sales_order_executes_insert():
    cur = MagicMock()

    sales_order_data = [
        {
            "sales_order_id": 2,
            "created_date": date(2022, 11, 3),
            "created_time": time(14, 20, 52, 186000),
            "last_updated_date": date(2022, 11, 3),
            "last_updated_time": time(14, 20, 52, 186000),
            "sales_staff_id": 19,
            "counterparty_id": 8,
            "units_sold": 42972,
            "unit_price": Decimal("3.94"),
            "currency_id": 2,
            "design_id": 3,
            "agreed_payment_date": date(2022, 11, 8),
            "agreed_delivery_date": date(2022, 11, 7),
            "agreed_delivery_location_id": 8,
        }
    ]

    load_sales_order(
        cur,
        sales_order_data,
    )

    cur.execute.assert_called_once()

    parameters = cur.execute.call_args.args[1]

    assert parameters == (
        2,
        date(2022, 11, 3),
        time(14, 20, 52, 186000),
        date(2022, 11, 3),
        time(14, 20, 52, 186000),
        19,
        8,
        42972,
        Decimal("3.94"),
        2,
        3,
        date(2022, 11, 8),
        date(2022, 11, 7),
        8,
    )

    sql = cur.execute.call_args.args[0]

    assert "INSERT INTO fact_sales_order" in sql
    assert "sales_record_id" not in sql


@pytest.mark.parametrize(
    "loader_function",
    [
        load_staff,
        load_location,
        load_design,
        load_currency,
        load_counterparty,
        load_date,
        load_sales_order,
    ],
)
def test_loader_handles_empty_data(
    loader_function,
):
    cur = MagicMock()

    loader_function(cur, [])

    cur.execute.assert_not_called()


@patch("src.loading.loader.load_sales_order")
@patch("src.loading.loader.load_date")
@patch("src.loading.loader.load_counterparty")
@patch("src.loading.loader.load_currency")
@patch("src.loading.loader.load_design")
@patch("src.loading.loader.load_location")
@patch("src.loading.loader.load_staff")
@patch("src.loading.loader.get_connection")
def test_load_all_loads_tables_and_commits(
    mock_get_connection,
    mock_load_staff,
    mock_load_location,
    mock_load_design,
    mock_load_currency,
    mock_load_counterparty,
    mock_load_date,
    mock_load_sales_order,
):
    connection = MagicMock()
    cursor = MagicMock()

    connection.cursor.return_value.__enter__.return_value = cursor

    mock_get_connection.return_value = connection

    staff_data = [{"staff_id": 1}]
    location_data = [{"location_id": 1}]
    design_data = [{"design_id": 1}]
    currency_data = [{"currency_id": 1}]
    counterparty_data = [{"counterparty_id": 1}]
    date_data = [{"date_id": date(2022, 11, 3)}]
    sales_order_data = [{"sales_order_id": 1}]

    load_all(
        staff_data,
        location_data,
        design_data,
        currency_data,
        counterparty_data,
        date_data,
        sales_order_data,
    )

    mock_load_staff.assert_called_once_with(
        cursor,
        staff_data,
    )

    mock_load_location.assert_called_once_with(
        cursor,
        location_data,
    )

    mock_load_design.assert_called_once_with(
        cursor,
        design_data,
    )

    mock_load_currency.assert_called_once_with(
        cursor,
        currency_data,
    )

    mock_load_counterparty.assert_called_once_with(
        cursor,
        counterparty_data,
    )

    mock_load_date.assert_called_once_with(
        cursor,
        date_data,
    )

    mock_load_sales_order.assert_called_once_with(
        cursor,
        sales_order_data,
    )

    connection.commit.assert_called_once()
    connection.rollback.assert_not_called()
    connection.close.assert_called_once()


@patch(
    "src.loading.loader.load_staff",
    side_effect=RuntimeError("database error"),
)
@patch("src.loading.loader.get_connection")
def test_load_all_rolls_back_on_error(
    mock_get_connection,
    mock_load_staff,
):
    connection = MagicMock()
    cursor = MagicMock()

    connection.cursor.return_value.__enter__.return_value = cursor
    mock_get_connection.return_value = connection

    with pytest.raises(
        RuntimeError,
        match="database error",
    ):
        load_all(
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        )

    connection.rollback.assert_called_once()
    connection.commit.assert_not_called()
    connection.close.assert_called_once()
