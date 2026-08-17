from unittest.mock import Mock

from src.initiation.create_tables import create_tables


def test_create_tables_executes_ddl_for_all_star_schema_tables():
    mock_cursor = Mock()

    create_tables(mock_cursor)

    mock_cursor.execute.assert_called_once()
    mock_sql = mock_cursor.execute.call_args[0][0]

    for table in [
        "dim_staff", "dim_date", "dim_location",
        "dim_counterparty", "dim_currency", "dim_design", "fact_sales_order",
    ]:
        assert f"CREATE TABLE IF NOT EXISTS {table}" in mock_sql