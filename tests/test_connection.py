from src.ingestion.connection import check_connection
from unittest.mock import patch, Mock


@patch("src.ingestion.connection.get_totesys_connection")
def test_check_connection_returns_database_and_user(mock_get_conn):
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = ("totesys", "test_user")
    mock_conn.cursor.return_value = mock_cursor
    mock_get_conn.return_value = mock_conn

    result = check_connection()

    assert result == ("totesys", "test_user")
    mock_conn.close.assert_called_once()