from src.ingestion.connection import get_totesys_connection


def test_connection():
    try:
        conn = get_totesys_connection()

        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user;")
            result = cur.fetchone()

        print("Database connection successful!")
        print(f"Database: {result[0]}")
        print(f"User: {result[1]}")

        conn.close()

    except Exception as e:
        print("Database connection failed!")
        print(f"Error: {e}")


if __name__ == "__main__":
    test_connection()