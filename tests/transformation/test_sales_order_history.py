from src.transformation.sales_order_history import (
    find_sales_order_changes,
)


def make_sales_order(
    sales_order_id,
    units_sold,
    last_updated="2026-08-12T10:00:00.000000",
):
    return {
        "sales_order_id": sales_order_id,
        "created_at": "2026-08-12T09:00:00.000000",
        "last_updated": last_updated,
        "design_id": 3,
        "staff_id": 19,
        "counterparty_id": 8,
        "units_sold": units_sold,
        "unit_price": "3.94",
        "currency_id": 2,
        "agreed_delivery_date": "2026-08-15",
        "agreed_payment_date": "2026-08-16",
        "agreed_delivery_location_id": 8,
    }


def test_unchanged_sales_order_is_not_returned():
    previous_snapshot = [
        make_sales_order(2, 42972)
    ]

    current_snapshot = [
        make_sales_order(2, 42972)
    ]

    result = find_sales_order_changes(
        previous_snapshot,
        current_snapshot,
    )

    assert result == []


def test_changed_sales_order_is_returned():
    previous_snapshot = [
        make_sales_order(
            2,
            42972,
            "2026-08-12T10:00:00.000000",
        )
    ]

    current_snapshot = [
        make_sales_order(
            2,
            45000,
            "2026-08-13T10:00:00.000000",
        )
    ]

    result = find_sales_order_changes(
        previous_snapshot,
        current_snapshot,
    )

    assert len(result) == 1
    assert result[0]["sales_order_id"] == 2
    assert result[0]["units_sold"] == 45000


def test_new_sales_order_is_returned():
    previous_snapshot = [
        make_sales_order(2, 42972)
    ]

    current_snapshot = [
        make_sales_order(2, 42972),
        make_sales_order(3, 50000),
    ]

    result = find_sales_order_changes(
        previous_snapshot,
        current_snapshot,
    )

    assert len(result) == 1
    assert result[0]["sales_order_id"] == 3


def test_multiple_new_and_changed_orders_are_returned():
    previous_snapshot = [
        make_sales_order(1, 100),
        make_sales_order(2, 200),
        make_sales_order(3, 300),
    ]

    current_snapshot = [
        make_sales_order(1, 100),
        make_sales_order(
            2,
            250,
            "2026-08-13T10:00:00.000000",
        ),
        make_sales_order(3, 300),
        make_sales_order(4, 400),
    ]

    result = find_sales_order_changes(
        previous_snapshot,
        current_snapshot,
    )

    result_ids = [
        row["sales_order_id"]
        for row in result
    ]

    assert result_ids == [2, 4]


def test_empty_previous_snapshot_returns_all_current_orders():
    current_snapshot = [
        make_sales_order(1, 100),
        make_sales_order(2, 200),
    ]

    result = find_sales_order_changes(
        [],
        current_snapshot,
    )

    assert result == current_snapshot


def test_empty_current_snapshot_returns_empty_list():
    previous_snapshot = [
        make_sales_order(1, 100)
    ]

    result = find_sales_order_changes(
        previous_snapshot,
        [],
    )

    assert result == []


def test_missing_order_is_not_treated_as_new_version():
    previous_snapshot = [
        make_sales_order(1, 100),
        make_sales_order(2, 200),
    ]

    current_snapshot = [
        make_sales_order(1, 100)
    ]

    result = find_sales_order_changes(
        previous_snapshot,
        current_snapshot,
    )

    assert result == []
