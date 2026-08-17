import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_warehouse_connection():
    return psycopg2.connect(
        host=os.getenv("WAREHOUSE_HOST"),
        port=os.getenv("WAREHOUSE_PORT"),
        dbname=os.getenv("WAREHOUSE_DATABASE"),
        user=os.getenv("WAREHOUSE_USER"),
        password=os.getenv("WAREHOUSE_PASSWORD")
    )