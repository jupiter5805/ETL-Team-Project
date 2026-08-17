from src.initiation.connection_RDS import get_warehouse_connection
from src.initiation.create_tables import create_tables
from src.initiation.delete_tables import delete_tables

def lambda_handler(event, context):
    conn = get_warehouse_connection()
    cur = conn.cursor()

    try:
        delete_tables(cur)
        create_tables(cur)

        conn.commit()

        return {
            "statusCode": 200,
            "body": "Database tables created successfully"
        }

    except Exception as e:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    seed()

