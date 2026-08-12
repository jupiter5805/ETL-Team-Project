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