import json
from unittest.mock import patch
import boto3
from moto import mock_aws

from src.initialization.connect_RDS import get_connection


@mock_aws
def test_get_connection_uses_secret_and_env_vars(monkeypatch):
    monkeypatch.setenv("DB_HOST", "test-host")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "test-db")
    monkeypatch.setenv("DB_SECRET_ARN", "warehouse-secret")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-west-2")

    client = boto3.client("secretsmanager", region_name="eu-west-2")
    client.create_secret(
        Name="warehouse-secret",
        SecretString=json.dumps({"username": "test-user", "password": "test-pass"}),
    )

    with patch("src.initialization.connect_RDS.psycopg2.connect") as mock_connect:
        get_connection()
        mock_connect.assert_called_once_with(
            host="test-host", port=5432, dbname="test-db",
            user="test-user", password="test-pass",
            connect_timeout=10, sslmode="require",
        )