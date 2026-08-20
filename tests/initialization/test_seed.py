from unittest.mock import Mock, patch

import pytest

from src.initialization.seed import seed


@patch("src.initialization.seed.get_connection")
@patch("src.initialization.seed.create_tables")
def test_seed_creates_tables_and_commits(
    mock_create_tables,
    mock_get_connection,
):
    mock_connection = Mock()
    mock_get_connection.return_value = mock_connection

    seed()

    mock_create_tables.assert_called_once_with(mock_connection)
    mock_connection.commit.assert_called_once()
    mock_connection.rollback.assert_not_called()
    mock_connection.close.assert_called_once()


@patch("src.initialization.seed.get_connection")
@patch("src.initialization.seed.create_tables")
def test_seed_rolls_back_and_closes_on_failure(
    mock_create_tables,
    mock_get_connection,
):
    mock_connection = Mock()
    mock_get_connection.return_value = mock_connection
    mock_create_tables.side_effect = Exception("boom")

    with pytest.raises(Exception, match="boom"):
        seed()

    mock_connection.rollback.assert_called_once()
    mock_connection.commit.assert_not_called()
    mock_connection.close.assert_called_once()
