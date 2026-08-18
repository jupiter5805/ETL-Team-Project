import json
import os

import boto3
import psycopg2


def get_database_credentials():
    """Get the RDS username and password from Secrets Manager."""
    secret_arn = os.environ["DB_SECRET_ARN"]

    secrets_client = boto3.client("secretsmanager")

    response = secrets_client.get_secret_value(
        SecretId=secret_arn
    )

    return json.loads(response["SecretString"])


def get_connection():
    """Create and return a PostgreSQL connection."""
    credentials = get_database_credentials()

    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", "5432")),
        dbname=os.environ["DB_NAME"],
        user=credentials["username"],
        password=credentials["password"],
        connect_timeout=10,
        sslmode="require",
    )