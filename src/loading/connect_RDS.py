import json
import os
import boto3
import psycopg2

def get_secret():
    secret_name = os.environ["RDS_SECRET_NAME"]
    region_name = os.environ.get("AWS_REGION", "eu-west-2")

    client = boto3.client(
        "secretsmanager",
        region_name=region_name,
    )

    response = client.get_secret_value(
        SecretId=secret_name,
    )

    return json.loads(response["SecretString"])

def get_connection():
    secret = get_secret()

    connection = psycopg2.connect(
        host=secret["host"],
        port=secret.get("port", 5432),
        database=secret["dbname"],
        user=secret["username"],
        password=secret["password"],
        connect_timeout=10,
        sslmode="require",
    )

    return connection


def close_connection(connection):
    if connection is not None and not connection.closed:
        connection.close()