import pytest
from unittest.mock import MagicMock, patch
from datetime import date, datetime, time
from decimal import Decimal
import json

from src.ingestion.extract import extract_table, rows_to_json, serialise_value

def test_extract_table_returns_rows_correctly():
    mock_rows = [{"id": 1, "name": "test"}]

    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.return_value = mock_rows

    result = extract_table(mock_conn, "staff")

    mock_cursor.execute.assert_called_once()
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
    parsed = json.loads(result)  # raises if not valid JSON
    assert parsed == [{"test": 1, "rows": 2}]

def test_rows_to_json_serialises_values():
        rows = [{"id": 1, "created_at": datetime(2024, 1, 1), "amount": Decimal("5.00")}]
        result = rows_to_json(rows)
        assert '"id": 1' in result
        assert '"amount": "5.00"' in result