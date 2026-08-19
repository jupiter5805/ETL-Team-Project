import json
import boto3
from moto import mock_aws
from unittest.mock import patch, Mock

from src.ingestion.connection import check_connection, get_totesys_connection


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


@mock_aws
def test_get_totesys_connection_uses_secrets_manager(monkeypatch):
    monkeypatch.setenv("TOTESYS_SECRET_NAME", "totesys-db-credentials")

    client = boto3.client("secretsmanager", region_name="eu-west-2")
    client.create_secret(
        Name="totesys-db-credentials",
        SecretString=json.dumps({
            "host": "test-host", "port": "5432",
            "dbname": "test-db", "user": "test-user", "password": "test-pass",
        }),
    )

    with patch("src.ingestion.connection.psycopg2.connect") as mock_connect:
        get_totesys_connection()
        mock_connect.assert_called_once_with(
            host="test-host", port="5432", dbname="test-db",
            user="test-user", password="test-pass",
        )
