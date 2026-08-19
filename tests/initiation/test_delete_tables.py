from unittest.mock import MagicMock

from src.initialization.delete import delete_tables


def test_delete_tables_drops_all_star_schema_tables():
    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_connection.cursor.return_value.__enter__.return_value = (
        mock_cursor
    )

    delete_tables(mock_connection)

    mock_connection.cursor.assert_called_once_with()
    mock_cursor.execute.assert_called_once()

    mock_sql = mock_cursor.execute.call_args.args[0]

    expected_tables = [
        "fact_sales_order",
        "dim_staff",
        "dim_date",
        "dim_location",
        "dim_counterparty",
        "dim_currency",
        "dim_design",
    ]

    for table_name in expected_tables:
        assert (
            f"DROP TABLE IF EXISTS {table_name}"
            in mock_sql
        )