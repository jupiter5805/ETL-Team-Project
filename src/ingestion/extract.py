import json
from datetime import date, datetime, time
from decimal import Decimal

from psycopg2 import sql
from psycopg2.extras import RealDictCursor


TABLES = (
    "counterparty",
    "currency",
    "department",
    "design",
    "staff",
    "sales_order",
    "address",
    "payment",
    "purchase_order",
    "payment_type",
    "transaction",
    )


def extract_table(connection, table_name):
    query = sql.SQL("SELECT * FROM {}").format(
        sql.Identifier(table_name)
    )
    with connection.cursor(
        cursor_factory=RealDictCursor
    ) as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    return rows

def serialise_value(value):
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()

    if isinstance(value, Decimal):
        return str(value)

def rows_to_json(rows):
    return json.dumps(
        rows,
        default=serialise_value,
        ensure_ascii=False,
    )

def extract_all_tables(connection):
    for table_name in TABLES:
        rows = extract_table(connection, table_name)
        json_body = rows_to_json(rows)
        yield table_name, json_body