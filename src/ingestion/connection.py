import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_totesys_connection():
    return psycopg2.connect(
        host=os.getenv("TOTESYS_HOST"),
        port=os.getenv("TOTESYS_PORT"),
        dbname=os.getenv("TOTESYS_DATABASE"),
        user=os.getenv("TOTESYS_USER"),
        password=os.getenv("TOTESYS_PASSWORD")
    )

def check_connection():
    conn = get_totesys_connection()
    cur = conn.cursor()
    cur.execute("SELECT current_database(), current_user;")
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result

def get_warehouse_connection():
    return psycopg2.connect(
        host=os.getenv("WAREHOUSE_HOST"),
        port=os.getenv("WAREHOUSE_PORT"),
        dbname=os.getenv("WAREHOUSE_DATABASE"),
        user=os.getenv("WAREHOUSE_USER"),
        password=os.getenv("WAREHOUSE_PASSWORD")
    )