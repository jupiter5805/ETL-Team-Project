import json
from unittest.mock import patch

from src.initialization.connection_RDS import (
    get_connection,
    get_database_credentials,
)


@patch(
    "src.initialization.connection_RDS.get_database_credentials"
)
@patch(
    "src.initialization.connection_RDS.psycopg2.connect"
)
def test_get_connection_uses_env_vars(
    mock_connect,
    mock_get_credentials,
    monkeypatch,
):
    monkeypatch.setenv("DB_HOST", "test-host")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "test-db")

    mock_get_credentials.return_value = {
        "username": "test-user",
        "password": "test-pass",
    }

    result = get_connection()

    mock_get_credentials.assert_called_once_with()

    mock_connect.assert_called_once_with(
        host="test-host",
        port=5432,
        dbname="test-db",
        user="test-user",
        password="test-pass",
        connect_timeout=10,
        sslmode="require",
    )

    assert result == mock_connect.return_value


@patch(
    "src.initialization.connection_RDS.boto3.client"
)
def test_get_database_credentials_reads_secret(
    mock_boto_client,
    monkeypatch,
):
    monkeypatch.setenv(
        "DB_SECRET_ARN",
        "test-secret-arn",
    )

    mock_secrets_client = mock_boto_client.return_value

    mock_secrets_client.get_secret_value.return_value = {
        "SecretString": json.dumps({
            "username": "test-user",
            "password": "test-pass",
        })
    }

    result = get_database_credentials()

    mock_boto_client.assert_called_once_with(
        "secretsmanager"
    )

    mock_secrets_client.get_secret_value.assert_called_once_with(
        SecretId="test-secret-arn"
    )

    assert result == {
        "username": "test-user",
        "password": "test-pass",
    }