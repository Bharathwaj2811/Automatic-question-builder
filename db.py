import mysql.connector
from mysql.connector import Error

def create_connection():
    """ Create a database connection to the MySQL database """
    connection = None
    try:
        connection = mysql.connector.connect(
            host='localhost',         # Your host
            user='root',              # Your username
            password='67896789Bhargav@',  # Your password
            database='bhargavr_banking'  # Your database name
            
        )
        print("Connection to MySQL DB successful using MySQL Connector")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

def close_connection(connection):
    """ Close the database connection """
    if connection:
        connection.close()
        print("MySQL connection closed")

# Example usage
if __name__ == "__main__":
    # Create a connection
    conn = create_connection()

    # Check if the connection was successful
    if conn:
        # Perform database operations here (if needed)
        
        # For example, you could query the database
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")  # This will show the tables in the database
        tables = cursor.fetchall()
        print("Tables in the database:", tables)

        # Close the connection
        close_connection(conn)
