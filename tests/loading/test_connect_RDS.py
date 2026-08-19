import json
from unittest.mock import patch

import boto3
from moto import mock_aws

from src.loading.connect_RDS import (
    get_database_credentials,
    get_connection,
)


@mock_aws
def test_get_database_credentials(monkeypatch):
    monkeypatch.setenv(
        "AWS_DEFAULT_REGION",
        "eu-west-2",
    )

    client = boto3.client(
        "secretsmanager",
        region_name="eu-west-2",
    )

    response = client.create_secret(
        Name="warehouse-db-credentials",
        SecretString=json.dumps(
            {
                "username": "test-user",
                "password": "test-pass",
            }
        ),
    )

    monkeypatch.setenv(
        "DB_SECRET_ARN",
        response["ARN"],
    )

    result = get_database_credentials()

    assert result == {
        "username": "test-user",
        "password": "test-pass",
    }


@patch(
    "src.loading.connect_RDS.get_database_credentials"
)
@patch(
    "src.loading.connect_RDS.psycopg2.connect"
)
def test_get_connection_uses_correct_values(
    mock_connect,
    mock_get_credentials,
    monkeypatch,
):
    mock_get_credentials.return_value = {
        "username": "test-user",
        "password": "test-pass",
    }

    monkeypatch.setenv(
        "DB_HOST",
        "test-host",
    )
    monkeypatch.setenv(
        "DB_PORT",
        "5432",
    )
    monkeypatch.setenv(
        "DB_NAME",
        "test-database",
    )

    get_connection()

    mock_connect.assert_called_once_with(
        host="test-host",
        port=5432,
        dbname="test-database",
        user="test-user",
        password="test-pass",
        connect_timeout=10,
        sslmode="require",
    )


@patch(
    "src.loading.connect_RDS.get_database_credentials"
)
@patch(
    "src.loading.connect_RDS.psycopg2.connect"
)
def test_get_connection_uses_default_port(
    mock_connect,
    mock_get_credentials,
    monkeypatch,
):
    mock_get_credentials.return_value = {
        "username": "test-user",
        "password": "test-pass",
    }

    monkeypatch.setenv(
        "DB_HOST",
        "test-host",
    )
    monkeypatch.setenv(
        "DB_NAME",
        "test-database",
    )
    monkeypatch.delenv(
        "DB_PORT",
        raising=False,
    )

    get_connection()

    mock_connect.assert_called_once_with(
        host="test-host",
        port=5432,
        dbname="test-database",
        user="test-user",
        password="test-pass",
        connect_timeout=10,
        sslmode="require",
    )
