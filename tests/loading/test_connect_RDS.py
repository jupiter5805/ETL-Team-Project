import json
import boto3
from unittest.mock import patch
from moto import mock_aws

from src.loading.connect_RDS import get_secret, get_connection, close_connection


@mock_aws
def test_get_secret_parses_json(monkeypatch):
    monkeypatch.setenv("RDS_SECRET_NAME", "warehouse-db-credentials")
    client = boto3.client("secretsmanager", region_name="eu-west-2")
    client.create_secret(
        Name="warehouse-db-credentials",
        SecretString=json.dumps({"username": "admin", "password": "pw"}),
    )

    result = get_secret()

    assert result == {"username": "admin", "password": "pw"}


@patch("src.loading.connect_RDS.get_secret")
@patch("src.loading.connect_RDS.psycopg2.connect")
def test_get_connection_uses_secret_values(mock_connect, mock_get_secret):
    mock_get_secret.return_value = {
        "host": "test-host", "port": 5432, "dbname": "test-db",
        "username": "test-user", "password": "test-pass",
    }

    get_connection()

    mock_connect.assert_called_once_with(
        host="test-host", port=5432, database="test-db",
        user="test-user", password="test-pass",
        connect_timeout=10, sslmode="require",
    )


def test_close_connection_closes_open_connection():
    from unittest.mock import Mock
    mock_conn = Mock()
    mock_conn.closed = False

    close_connection(mock_conn)

    mock_conn.close.assert_called_once()


def test_close_connection_does_nothing_if_already_closed():
    from unittest.mock import Mock
    mock_conn = Mock()
    mock_conn.closed = True

    close_connection(mock_conn)

    mock_conn.close.assert_not_called()