import os
import json
import boto3
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def _get_credentials_from_secrets_manager(secret_name):
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])


def get_totesys_connection():
    secret_name = os.getenv("TOTESYS_SECRET_NAME")
    if secret_name:
        creds = _get_credentials_from_secrets_manager(secret_name)
        return psycopg2.connect(
            host=creds["host"],
            port=creds["port"],
            dbname=creds["dbname"],
            user=creds["user"],
            password=creds["password"],
        )
    return psycopg2.connect(
        host=os.getenv("TOTESYS_HOST"),
        port=os.getenv("TOTESYS_PORT"),
        dbname=os.getenv("TOTESYS_DATABASE"),
        user=os.getenv("TOTESYS_USER"),
        password=os.getenv("TOTESYS_PASSWORD"),
    )


def check_connection():
    conn = get_totesys_connection()
    cur = conn.cursor()
    cur.execute("SELECT current_database(), current_user;")
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result
