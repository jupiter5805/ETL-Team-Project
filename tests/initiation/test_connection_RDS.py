from unittest.mock import patch

from src.initialization.connection_RDS import get_warehouse_connection


@patch("src.initiation.connection_RDS.psycopg2.connect")
def test_get_warehouse_connection_uses_env_vars(mock_connect, monkeypatch):
    monkeypatch.setenv("WAREHOUSE_HOST", "test-host")
    monkeypatch.setenv("WAREHOUSE_PORT", "5432")
    monkeypatch.setenv("WAREHOUSE_DATABASE", "test-db")
    monkeypatch.setenv("WAREHOUSE_USER", "test-user")
    monkeypatch.setenv("WAREHOUSE_PASSWORD", "test-pass")

    get_warehouse_connection()

    mock_connect.assert_called_once_with(
        host="test-host", port="5432", dbname="test-db",
        user="test-user", password="test-pass",
    )