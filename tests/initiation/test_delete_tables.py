from unittest.mock import Mock

from src.initiation.delete_tables import delete_tables


def test_delete_tables_drops_all_star_schema_tables():
    mock_cursor = Mock()

    delete_tables(mock_cursor)

    mock_cursor.execute.assert_called_once()
    mock_sql = mock_cursor.execute.call_args[0][0]

    for table in [
        "fact_sales_order", "dim_staff", "dim_date",
        "dim_location", "dim_counterparty", "dim_currency", "dim_design",
    ]:
        assert f"DROP TABLE IF EXISTS {table}" in mock_sql