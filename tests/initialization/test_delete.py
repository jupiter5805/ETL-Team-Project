from unittest.mock import MagicMock

from src.initialization.delete import delete_tables


def test_create_tables_executes_ddl_for_all_star_schema_tables():
    mock_connection = MagicMock()
    mock_cursor = mock_connection.cursor.return_value.__enter__.return_value

    delete_tables(mock_connection)

    mock_cursor.execute.assert_called_once()
    mock_sql = mock_cursor.execute.call_args[0][0]

    for table in [
        "dim_staff", "dim_date", "dim_location",
        "dim_counterparty", "dim_currency", "dim_design", "fact_sales_order",
    ]:
        assert f"DROP TABLE IF EXISTS {table}" in mock_sql