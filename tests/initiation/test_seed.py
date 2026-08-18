from unittest.mock import patch, Mock

from src.initiation.seed import seed


@patch("src.initiation.seed.get_warehouse_connection")
@patch("src.initiation.seed.create_tables")
@patch("src.initiation.seed.delete_tables")
def test_seed_deletes_then_creates_then_commits(
    mock_delete_tables, mock_create_tables, mock_get_conn
):
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_get_conn.return_value = mock_conn

    seed()

    mock_delete_tables.assert_called_once_with(mock_cursor)
    mock_create_tables.assert_called_once_with(mock_cursor)
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("src.initiation.seed.get_warehouse_connection")
@patch("src.initiation.seed.create_tables")
@patch("src.initiation.seed.delete_tables")
def test_seed_rolls_back_and_closes_on_failure(
    mock_delete_tables, mock_create_tables, mock_get_conn
):
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_get_conn.return_value = mock_conn
    mock_create_tables.side_effect = Exception("boom")

    try:
        seed()
        assert False, "expected seed() to re-raise"
    except Exception:
        pass

    mock_conn.rollback.assert_called_once()
    mock_conn.commit.assert_not_called()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()