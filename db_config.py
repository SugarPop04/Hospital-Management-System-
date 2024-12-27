import mysql.connector
from mysql.connector import Error

def get_database_connection():
    """
    Establishes and returns a connection to the MySQL database.
    Returns:
        connection (mysql.connector.connection.MySQLConnection): The database connection object.
    """
    try:
        print("Attempting to connect to the database...")
        connection = mysql.connector.connect(
            host='127.0.0.1',
            user='hospital_user',  
            password='6305978196',  
            database='hospital_db',  
            connection_timeout=5
        )
        if connection.is_connected():
            print("Connection to MySQL database successful.")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def close_connection(connection):
    """
    Closes the provided database connection.
    Args:
        connection (mysql.connector.connection.MySQLConnection): The database connection object to close.
    """
    if connection and connection.is_connected():
        connection.close()
        print("Database connection closed successfully.")
