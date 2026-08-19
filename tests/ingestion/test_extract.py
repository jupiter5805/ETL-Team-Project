from unittest.mock import MagicMock, patch
from datetime import date, datetime, time
from decimal import Decimal
import json

from src.ingestion.extract import (
    TABLES,
    extract_all_tables,
    extract_table,
    extract_updated_rows,
    rows_to_json,
    serialise_value,
)


def test_extract_table_returns_rows_correctly():
    mock_rows = [{"id": 1, "name": "test"}]

    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.return_value = mock_rows

    result = extract_table(mock_conn, "staff")

    mock_cursor.execute.assert_called_once()
    assert result == mock_rows


def test_extract_updated_rows_returns_rows_correctly():
    mock_rows = [{"id": 1, "name": "test"}]

    last_run = datetime(2026, 8, 15, 12, 0)
    current_run = datetime(2026, 8, 15, 12, 10)

    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.return_value = mock_rows

    result = extract_updated_rows(
        mock_conn,
        "staff",
        last_run,
        current_run,
    )

    mock_cursor.execute.assert_called_once()

    query_parameters = mock_cursor.execute.call_args.args[1]

    assert query_parameters == (
        last_run,
        current_run,
    )

    assert result == mock_rows


def test_serialise_value_converts_date_time_formats():
    dt = datetime(2024, 1, 1, 12, 30)
    d = date(2024, 1, 1)
    t = time(12, 30)

    assert serialise_value(dt) == dt.isoformat()
    assert serialise_value(d) == d.isoformat()
    assert serialise_value(t) == t.isoformat()


def test_serialise_value_converts_decimal_to_string():
    assert serialise_value(Decimal("10.50")) == "10.50"


def test_rows_to_json_returns_json():
    rows = [{"test": 1, "rows": 2}]

    result = rows_to_json(rows)
    parsed = json.loads(result)

    assert parsed == [{"test": 1, "rows": 2}]


def test_rows_to_json_serialises_values():
    rows = [
        {
            "id": 1,
            "created_at": datetime(2024, 1, 1),
            "amount": Decimal("5.00"),
        }
    ]

    result = rows_to_json(rows)

    assert '"id": 1' in result
    assert '"amount": "5.00"' in result


@patch("src.ingestion.extract.rows_to_json")
@patch("src.ingestion.extract.extract_table")
def test_extract_all_tables_yields_for_each_table(
    mock_extract_table,
    mock_rows_to_json,
):
    mock_extract_table.return_value = [{"id": 1}]
    mock_rows_to_json.return_value = '[{"id": 1}]'
    mock_conn = MagicMock()

    results = list(extract_all_tables(mock_conn))

    assert results == [
        (table, '[{"id": 1}]')
        for table in TABLES
    ]
    assert mock_extract_table.call_count == len(TABLES)


@patch("src.ingestion.extract.rows_to_json")
@patch("src.ingestion.extract.extract_updated_rows")
def test_extract_all_tables_uses_incremental_window(
    mock_extract_updated_rows,
    mock_rows_to_json,
):
    mock_conn = MagicMock()

    last_run = datetime(2026, 8, 15, 12, 0)
    current_run = datetime(2026, 8, 15, 12, 10)

    mock_extract_updated_rows.return_value = [{"id": 1}]
    mock_rows_to_json.return_value = '[{"id": 1}]'

    results = list(
        extract_all_tables(
            mock_conn,
            last_run,
            current_run,
        )
    )

    assert len(results) == len(TABLES)
    assert mock_extract_updated_rows.call_count == len(TABLES)

    for table_name in TABLES:
        mock_extract_updated_rows.assert_any_call(
            mock_conn,
            table_name,
            last_run,
            current_run,
        )
