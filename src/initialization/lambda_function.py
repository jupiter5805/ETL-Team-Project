from src.initialization.connection_RDS import get_connection
from src.initialization.delete import delete_tables
from src.initialization.create import create_tables

def lambda_handler(event, context):
    connection = get_connection()
    delete_tables(connection)
    create_tables(connection)
    connection.commit()
    connection.close()