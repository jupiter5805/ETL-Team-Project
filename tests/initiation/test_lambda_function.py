from unittest.mock import MagicMock, patch

from src.initialization.lambda_function import lambda_handler


def test_lambda_handler_resets_and_creates_tables():
    mock_connection = MagicMock()

    with (
        patch(
            "src.initialization.lambda_function.get_connection"
        ) as mock_get_connection,
        patch(
            "src.initialization.lambda_function.delete_tables"
        ) as mock_delete_tables,
        patch(
            "src.initialization.lambda_function.create_tables"
        ) as mock_create_tables,
    ):
        mock_get_connection.return_value = mock_connection

        result = lambda_handler({}, None)

    mock_get_connection.assert_called_once_with()

    mock_delete_tables.assert_called_once_with(
        mock_connection
    )

    mock_create_tables.assert_called_once_with(
        mock_connection
    )

    mock_connection.commit.assert_called_once_with()
    mock_connection.close.assert_called_once_with()

    assert result is None