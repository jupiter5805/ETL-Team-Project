from src.initialization.connect_rds import get_connection
from src.initialization.delete_table import delete_tables
from src.initialization.create_table import create_tables

def lambda_handler(event, context):
    connection = get_connection()
    delete_tables(connection)
    create_tables(connection)
    connection.commit()
    connection.close()