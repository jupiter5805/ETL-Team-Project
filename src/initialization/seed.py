from .connect_RDS import get_connection
from .create import create_tables
from .delete import delete_tables


def seed():
    connection = get_connection()

    try:
        delete_tables(connection)
        create_tables(connection)
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    seed()
