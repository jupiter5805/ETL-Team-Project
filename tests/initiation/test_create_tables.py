from unittest.mock import MagicMock

from src.initialization.create import create_tables


def test_create_tables_executes_ddl_for_all_star_schema_tables():
    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_connection.cursor.return_value.__enter__.return_value = (
        mock_cursor
    )

    create_tables(mock_connection)

    mock_connection.cursor.assert_called_once_with()
    mock_cursor.execute.assert_called_once()

    mock_sql = mock_cursor.execute.call_args.args[0]

    expected_tables = [
        "dim_staff",
        "dim_date",
        "dim_location",
        "dim_counterparty",
        "dim_currency",
        "dim_design",
        "fact_sales_order",
    ]

    for table_name in expected_tables:
        assert (
            f"CREATE TABLE IF NOT EXISTS {table_name}"
            in mock_sql
        )