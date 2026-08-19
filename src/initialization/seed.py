from src.initialization.connect_RDS import get_connection
from src.initialization.create import create_tables
from src.initialization.delete import delete_tables


def seed():
    conn = get_connection()
    try:
        delete_tables(conn)
        create_tables(conn)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    seed()